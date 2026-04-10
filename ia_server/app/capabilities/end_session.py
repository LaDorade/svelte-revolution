"""LLM-driven end-condition capability.

Asks Mistral whether the contribution satisfies the configured end condition.
If so, sets `Session.completed = true` and `Session.end = <End.id>`.
"""

from __future__ import annotations

import logging
from typing import Any

from .. import state
from ..mistral_client import chat_json
from ..models import AIConfig, NodeRecord
from ..pb_client import PBClient

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI Game Master for a collaborative storytelling platform.
Decide whether the player's contribution satisfies the scenario's end condition.

Respond ONLY with a JSON object of this exact shape, no extra text:
{"matched": <true|false>, "reason": "<short explanation>"}"""


def _build_user_prompt(condition: str, node: NodeRecord) -> str:
	return (
		f"End condition:\n  {condition}\n\n"
		f"Player contribution:\n  title: {node.title}\n  text: {node.text}"
	)


async def run(
	node: NodeRecord,
	config: AIConfig,
	session: dict[str, Any],
	scenario: dict[str, Any],
	pb: PBClient,
) -> None:
	end_cfg = config.script.endCondition
	if end_cfg is None:
		return
	if session.get("completed"):
		return
	if await state.has_fired(node.session, ("end", 0)):
		return

	parsed = await chat_json(SYSTEM_PROMPT, _build_user_prompt(end_cfg.condition, node))
	if not parsed:
		return
	if not parsed.get("matched"):
		return

	scenario_id = scenario.get("id")
	if not scenario_id:
		log.warning("End: scenario record missing id")
		return

	end_id = await pb.find_end_id(scenario_id, end_cfg.endTitle)
	if not end_id:
		log.warning(
			"End: End record %r not found for scenario %s",
			end_cfg.endTitle,
			scenario_id,
		)
		return

	try:
		await pb.update_session(node.session, {"completed": True, "end": end_id})
		log.info("End: session %s ended with end %s", node.session, end_id)
		await state.mark_fired(node.session, ("end", 0))
	except Exception as e:  # noqa: BLE001
		log.error("End: failed to update session %s: %s", node.session, e)
