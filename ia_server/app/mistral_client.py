"""Thin async wrapper around the Mistral SDK with JSON-mode + timeout."""

from __future__ import annotations

import json
import logging
from typing import Any

from mistralai.client.sdk import Mistral

from .config import settings

log = logging.getLogger(__name__)

_client = Mistral(api_key=settings.mistral_api_key)


async def chat_json(system: str, user: str) -> dict[str, Any] | None:
	"""Send a chat-completion request, expect a JSON object back, return parsed dict or None."""
	try:
		resp = await _client.chat.complete_async(
			model=settings.mistral_model,
			messages=[
				{"role": "system", "content": system},
				{"role": "user", "content": user},
			],
			response_format={"type": "json_object"},
			temperature=0.1,
			timeout_ms=int(settings.mistral_timeout_s * 1000),
		)
	except Exception as e:  # noqa: BLE001 - log everything from upstream
		log.error("Mistral request failed: %s", e)
		return None

	try:
		content = resp.choices[0].message.content  # type: ignore[union-attr,index]
	except (AttributeError, IndexError, TypeError):
		log.error("Mistral response missing content: %r", resp)
		return None
	if not isinstance(content, str):
		log.error("Mistral content is not a string: %r", content)
		return None
	try:
		return json.loads(content)
	except json.JSONDecodeError as e:
		log.error("Mistral returned invalid JSON: %s — content=%r", e, content)
		return None
