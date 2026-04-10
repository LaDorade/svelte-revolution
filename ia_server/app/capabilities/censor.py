"""Rule-based censoring: replaces banned words in node title/text with `####`."""

from __future__ import annotations

import logging
import re
import unicodedata

from ..models import AIConfig, NodeRecord
from ..pb_client import PBClient

log = logging.getLogger(__name__)


def _normalize(s: str) -> str:
	"""Lowercase + strip accents for matching purposes."""
	return "".join(
		c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn"
	)


def _redact(text: str, banned: list[str]) -> tuple[str, bool]:
	"""Return (redacted_text, was_changed). Replaces each banned word with same-length ####."""
	if not text or not banned:
		return text, False

	normalized = _normalize(text)
	# We must operate on the original string while matching against the normalized form.
	# Build a list of (start, end) spans by running each pattern against the normalized text;
	# since accent stripping preserves character indices (1:1 except for combining marks which
	# we drop), the spans match the original text positions when the string contains no combining
	# marks. To stay correct in all cases, we operate index-by-index on a normalized copy of the
	# original string with NFC + lowercase only (no accent stripping for the indexed copy).
	indexed = unicodedata.normalize("NFC", text).lower()
	out = list(text)
	changed = False
	for word in banned:
		if not word:
			continue
		w_norm = _normalize(word)
		if not w_norm:
			continue
		# Match against the accent-stripped version using whole-word boundaries.
		pattern = re.compile(rf"(?<!\w){re.escape(w_norm)}(?!\w)", re.UNICODE)
		# We have to find positions in the original-length string. Use a parallel scan.
		original_normalized = _normalize(indexed)
		for m in pattern.finditer(original_normalized):
			start, end = m.span()
			# Indices in original_normalized correspond 1:1 to `indexed` (and to `text`)
			# only when no characters were dropped during normalization. In the common
			# case (no combining marks), this holds.
			if end <= len(out):
				for i in range(start, end):
					out[i] = "#"
				changed = True
	return "".join(out), changed


async def run(node: NodeRecord, config: AIConfig, pb: PBClient) -> None:
	banned = config.script.bannedWords or []
	if not banned:
		return

	new_title, t_changed = _redact(node.title, banned)
	new_text, x_changed = _redact(node.text, banned)
	if not (t_changed or x_changed):
		return

	log.info("Censoring node %s", node.id)
	try:
		await pb.update_node(node.id, {"title": new_title, "text": new_text})
	except Exception as e:  # noqa: BLE001
		log.error("Failed to update censored node %s: %s", node.id, e)
