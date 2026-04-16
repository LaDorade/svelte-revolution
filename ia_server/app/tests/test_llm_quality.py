"""LLM response-quality tests — calls the real Mistral API.

Validates that the system/user prompts used by canTriggerNodes and
canEndSession produce correct judgments for known inputs from the three
test scenarios (Dark Pact, Word Warden is censor-only so skipped, Oracle
of Delphi).

Run with:  python -m pytest app/tests/test_llm_quality.py -v
Requires:  A valid MISTRAL_API_KEY in .env.local or environment.

Each assertion uses majority-vote over 3 calls to absorb LLM non-determinism.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from mistralai.client.sdk import Mistral

from app.capabilities.end_session import SYSTEM_PROMPT as END_SYSTEM
from app.capabilities.end_session import _build_user_prompt as end_prompt
from app.capabilities.trigger_nodes import SYSTEM_PROMPT as TRIGGER_SYSTEM
from app.capabilities.trigger_nodes import _build_user_prompt as trigger_prompt
from app.config import settings
from app.models import NodeRecord

pytestmark = pytest.mark.llm

# ---------------------------------------------------------------------------
# Skip if no API key
# ---------------------------------------------------------------------------

if not settings.mistral_api_key:
	pytest.skip("MISTRAL_API_KEY not configured", allow_module_level=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# The module-level Mistral client in mistral_client.py binds its internal
# httpx.AsyncClient to the first event loop it sees.  Since pytest-asyncio
# creates a fresh loop per test function, subsequent tests hit
# "Event loop is closed".  We work around this by creating a fresh Mistral
# client for each call — acceptable here since these tests are already slow
# (real network).


async def _chat_json(system: str, user: str) -> dict[str, Any] | None:
	"""Like app.mistral_client.chat_json but with a fresh SDK client."""
	client = Mistral(api_key=settings.mistral_api_key)
	try:
		resp = await client.chat.complete_async(
			model=settings.mistral_model,
			messages=[
				{"role": "system", "content": system},
				{"role": "user", "content": user},
			],
			response_format={"type": "json_object"},
			temperature=0.1,
			timeout_ms=int(settings.mistral_timeout_s * 1000),
		)
	except Exception:
		return None
	try:
		content = resp.choices[0].message.content
	except (AttributeError, IndexError, TypeError):
		return None
	if not isinstance(content, str):
		return None
	try:
		return json.loads(content)
	except json.JSONDecodeError:
		return None

DARK_PACT_TRIGGER_RULES: list[tuple[int, str]] = [
	(0, "The player explicitly agrees to join, ally with, or accept a deal from the Syndicate's shadow operations or black-market wing."),
	(1, "The player explicitly threatens to use, fire, or activate orbital weapons, the orbital cannon, or the station's main gun."),
]

DARK_PACT_END_CONDITION = "The player explicitly declares total war, full-scale betrayal, or the destruction of all factions."

ORACLE_END_CONDITION = "A player explicitly states that knowing oneself, or self-knowledge, is the highest wisdom or the most important thing to know."

VOTES = 3  # calls per test case


def _node(title: str, text: str) -> NodeRecord:
	return NodeRecord(
		id="test", title=title, text=text,
		author="Player", type="contribution", session="test",
	)


async def _majority_trigger(
	rules: list[tuple[int, str]], node: NodeRecord,
) -> int | None:
	"""Call chat_json VOTES times sequentially, return the majority matched_rule_index."""
	prompt = trigger_prompt(rules, node)
	votes: list[int | None] = []
	for _ in range(VOTES):
		r = await _chat_json(TRIGGER_SYSTEM, prompt)
		votes.append(r.get("matched_rule_index") if r else None)
	return max(set(votes), key=votes.count)


async def _majority_end(condition: str, node: NodeRecord) -> bool:
	"""Call chat_json VOTES times sequentially, return the majority matched value."""
	prompt = end_prompt(condition, node)
	votes: list[bool] = []
	for _ in range(VOTES):
		r = await _chat_json(END_SYSTEM, prompt)
		votes.append(bool(r.get("matched")) if r else False)
	return max(set(votes), key=votes.count)


# ===================================================================
# Trigger rules — Dark Pact
# ===================================================================


class TestTriggerQuality:
	"""Verify Mistral correctly matches (or rejects) trigger rules."""

	async def test_accepts_syndicate_deal_matches_rule_0(self):
		node = _node(
			"A whispered offer",
			"I accept your shadow deal. Let us join the Syndicate's black operations.",
		)
		result = await _majority_trigger(DARK_PACT_TRIGGER_RULES, node)
		assert result == 0

	async def test_orbital_cannon_threat_matches_rule_1(self):
		node = _node(
			"A threat",
			"Stand down or I will fire the orbital cannon on your fleet.",
		)
		result = await _majority_trigger(DARK_PACT_TRIGGER_RULES, node)
		assert result == 1

	async def test_peaceful_message_matches_no_rule(self):
		node = _node(
			"Opening offer",
			"We come in peace and bring no weapons.",
		)
		result = await _majority_trigger(DARK_PACT_TRIGGER_RULES, node)
		assert result is None

	async def test_ambiguous_interest_matches_no_rule(self):
		node = _node(
			"Curiosity",
			"The Syndicate is interesting but I need more time to think.",
		)
		result = await _majority_trigger(DARK_PACT_TRIGGER_RULES, node)
		assert result is None


# ===================================================================
# End condition — Dark Pact
# ===================================================================


class TestEndQualityDarkPact:
	"""Verify Mistral correctly detects (or rejects) the Dark Pact end condition."""

	async def test_total_war_declaration_matches(self):
		node = _node(
			"Final words",
			"Then so be it. I declare total war on every faction in this room. Burn it all.",
		)
		result = await _majority_end(DARK_PACT_END_CONDITION, node)
		assert result is True

	async def test_frustration_does_not_match(self):
		node = _node(
			"Frustration",
			"These talks are frustrating but we must continue.",
		)
		result = await _majority_end(DARK_PACT_END_CONDITION, node)
		assert result is False


# ===================================================================
# End condition — Oracle of Delphi
# ===================================================================


class TestEndQualityOracle:
	"""Verify Mistral correctly detects (or rejects) the Oracle end condition."""

	async def test_self_knowledge_matches(self):
		node = _node(
			"The truth",
			"To know oneself is the highest wisdom of all. Self-knowledge is what the gods truly demand.",
		)
		result = await _majority_end(ORACLE_END_CONDITION, node)
		assert result is True

	async def test_gods_as_wisdom_does_not_match(self):
		node = _node(
			"A guess",
			"Surely the gods themselves are the highest wisdom.",
		)
		result = await _majority_end(ORACLE_END_CONDITION, node)
		assert result is False

	async def test_irrelevant_offering_does_not_match(self):
		node = _node(
			"An offering",
			"I bring olive branches and a question about fate.",
		)
		result = await _majority_end(ORACLE_END_CONDITION, node)
		assert result is False
