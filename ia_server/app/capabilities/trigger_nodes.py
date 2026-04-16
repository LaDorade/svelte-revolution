"""LLM-driven trigger-node capability.

Sends the player contribution + remaining (un-fired) trigger rules to Mistral
in JSON mode and asks which rule (if any) matches. On a match, creates a new
event-type node attached to the triggering contribution and marks the rule
as fired for that session.
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
Decide whether the player's contribution matches one of the configured trigger rules.

Respond ONLY with a JSON object of this exact shape, no extra text:
{"matched_rule_index": <integer or null>, "reason": "<short explanation>"}

Rules are 0-indexed. If no rule clearly matches, return null."""


def _build_user_prompt(rules: list[tuple[int, str]], node: NodeRecord) -> str:
	rules_block = "\n".join(f"  [{idx}] {cond}" for idx, cond in rules)
	return (
		f"Trigger rules:\n{rules_block}\n\n"
		f"Player contribution:\n  title: {node.title}\n  text: {node.text}"
	)


async def run(
	node: NodeRecord,
	config: AIConfig,
	session: dict[str, Any],
	scenario: dict[str, Any],
	pb: PBClient,
) -> None:
	rules = config.script.triggerRules or []
	if not rules:
		return

	# Filter out rules that have already fired or whose dependencies haven't fired yet.
	already_fired = await state.fired_set(node.session)
	pending = [
		(i, rule)
		for i, rule in enumerate(rules)
		if ("trigger", i) not in already_fired
		and all(("trigger", dep) in already_fired for dep in rule.requiresFired)
	]
	if not pending:
		return

	prompt_rules = [(i, rule.condition) for i, rule in pending]
	parsed = await chat_json(SYSTEM_PROMPT, _build_user_prompt(prompt_rules, node))
	if not parsed:
		return

	matched = parsed.get("matched_rule_index")
	if matched is None:
		log.info("Trigger: no rule matched for node %s", node.id)
		return
	if not isinstance(matched, int):
		log.warning("Trigger: matched_rule_index is not an int: %r", matched)
		return

	rule = next((r for i, r in pending if i == matched), None)
	if rule is None:
		log.warning("Trigger: Mistral picked unknown rule index %d", matched)
		return

	scenario_id = scenario.get("id")
	if not scenario_id:
		log.warning("Trigger: scenario record missing id")
		return

	side_id = await pb.find_side_id(scenario_id, rule.node.side)
	if not side_id:
		log.warning(
			"Trigger: side %r not found for scenario %s, skipping rule %d",
			rule.node.side,
			scenario_id,
			matched,
		)
		return

	payload = {
		"title": rule.node.title,
		"text": rule.node.text,
		"author": rule.node.author,
		"type": "event",
		"session": node.session,
		"parent": node.id,
		"side": side_id,
	}
	try:
		created = await pb.create_node(payload)
		log.info(
			"Trigger: rule %d fired in session %s, created node %s",
			matched,
			node.session,
			created.get("id"),
		)
		await state.mark_fired(node.session, ("trigger", matched))
	except Exception as e:  # noqa: BLE001
		log.error("Trigger: failed to create node for rule %d: %s", matched, e)
