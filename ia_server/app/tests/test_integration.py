"""Integration tests — exercise capabilities against a real PocketBase instance.

Uses the three test scenarios from test-scenarios/:
  - Dark Pact:        canCensor + canTriggerNodes (2 rules) + canEndSession
  - Word Warden:      canCensor only (edge cases: case, accents, word boundaries)
  - Oracle of Delphi: canEndSession only (positive + negative match)

Run with:  python -m pytest app/tests/test_integration.py -v
Requires:  PocketBase running on localhost:8090 with the bot user configured.
"""

from __future__ import annotations

import json
import random
import time
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from app import state
from app.capabilities import censor, end_session, trigger_nodes
from app.evaluator import evaluate
from app.models import (
	AIConfig,
	AIEndCondition,
	AINodeDef,
	AIScript,
	AITriggerRule,
	NodeRecord,
)
from app.pb_client import PBClient

pytestmark = pytest.mark.integration

# ---------------------------------------------------------------------------
# Seeding helpers
# ---------------------------------------------------------------------------


def _unique_slug() -> int:
	return int(time.time() * 1_000_000) + random.randint(0, 99_999)


def _record_id(rec: Any) -> str:
	return getattr(rec, "id", None) or rec["id"]


async def _create_scenario(
	pb: PBClient,
	cleanup: list[tuple[str, str]],
	*,
	title: str = "Test Scenario",
	prologue: str = "Once upon a test...",
	lang: str = "en",
	first_node_title: str = "Start",
	first_node_text: str = "The story begins.",
	first_node_author: str = "Narrator",
	ai: bool = True,
	ai_config_json: str | None = None,
) -> dict[str, Any]:
	rec = pb.raw.collection("Scenario").create(
		{
			"title": title,
			"prologue": prologue,
			"lang": lang,
			"firstNodeTitle": first_node_title,
			"firstNodeText": first_node_text,
			"firstNodeAuthor": first_node_author,
			"ai": ai,
			"aiConfig": ai_config_json or "",
		}
	)
	rid = _record_id(rec)
	cleanup.append(("Scenario", rid))
	return {"id": rid}


async def _create_side(
	pb: PBClient,
	cleanup: list[tuple[str, str]],
	scenario_id: str,
	name: str,
) -> dict[str, Any]:
	rec = pb.raw.collection("Side").create(
		{"name": name, "scenario": scenario_id}
	)
	rid = _record_id(rec)
	cleanup.append(("Side", rid))
	return {"id": rid, "name": name}


async def _create_end(
	pb: PBClient,
	cleanup: list[tuple[str, str]],
	scenario_id: str,
	title: str,
	text: str,
) -> dict[str, Any]:
	rec = pb.raw.collection("End").create(
		{"title": title, "text": text, "scenario": scenario_id}
	)
	rid = _record_id(rec)
	cleanup.append(("End", rid))
	return {"id": rid, "title": title}


async def _create_session(
	pb: PBClient,
	cleanup: list[tuple[str, str]],
	scenario_id: str,
	author_id: str,
	*,
	completed: bool = False,
) -> dict[str, Any]:
	rec = pb.raw.collection("Session").create(
		{
			"slug": _unique_slug(),
			"name": "Test Session",
			"scenario": scenario_id,
			"author": author_id,
			"completed": completed,
		}
	)
	rid = _record_id(rec)
	cleanup.append(("Session", rid))
	return {"id": rid}


async def _create_node(
	pb: PBClient,
	cleanup: list[tuple[str, str]],
	session_id: str,
	*,
	title: str,
	text: str,
	author: str = "Player",
	node_type: str = "contribution",
	parent: str | None = None,
	side: str | None = None,
) -> dict[str, Any]:
	payload: dict[str, Any] = {
		"title": title,
		"text": text,
		"author": author,
		"type": node_type,
		"session": session_id,
	}
	if parent:
		payload["parent"] = parent
	if side:
		payload["side"] = side
	rec = pb.raw.collection("Node").create(payload)
	rid = _record_id(rec)
	cleanup.append(("Node", rid))
	return {"id": rid}


def _node_rec(node_id: str, session_id: str, title: str, text: str) -> NodeRecord:
	return NodeRecord(
		id=node_id, title=title, text=text,
		author="Player", type="contribution", session=session_id,
	)


# ---------------------------------------------------------------------------
# Scenario configs — mirrors test-scenarios/*.md
# ---------------------------------------------------------------------------

DARK_PACT_VISION = (
	"The AI Game Master enforces civility and dramatic pacing. "
	"It censors profanity and the word \"secret\" (sensitive intelligence "
	"must remain hidden). It listens for two pivotal moments: when a "
	"delegate openly accepts an alliance with the Syndicate's shadow "
	"operations, and when a delegate threatens orbital weapons. It also "
	"watches for any explicit declaration of total war or betrayal — "
	"that ends the session."
)

WORD_WARDEN_VISION = (
	"The AI Game Master only censors. It removes a list of forbidden "
	"words and their accented variants from any contribution before they "
	"corrupt the parchment. It does not trigger any narrative events and "
	"never ends the session."
)

ORACLE_VISION = (
	"The AI Game Master listens silently for one specific philosophical "
	"truth: a player must explicitly acknowledge that knowledge of oneself "
	"— self-knowledge — is the highest form of wisdom. Until that exact "
	"idea is voiced, nothing happens. When it is voiced, the Oracle ends "
	"the session."
)


def _dark_pact_ai_config(bot_user_id: str) -> str:
	return json.dumps({
		"vision": DARK_PACT_VISION,
		"capabilities": ["canCensor", "canTriggerNodes", "canEndSession"],
		"script": {
			"bannedWords": ["secret", "damn", "hell"],
			"triggerRules": [
				{
					"condition": "The player explicitly agrees to join, ally with, or accept a deal from the Syndicate's shadow operations or black-market wing.",
					"node": {
						"title": "An unholy alliance",
						"text": "A Syndicate envoy slides a black data-chip across the table. \"Welcome to the family,\" she whispers. The Coalition delegates exchange horrified glances.",
						"author": "Syndicate Envoy",
						"side": "Syndicate",
					},
				},
				{
					"condition": "The player explicitly threatens to use, fire, or activate orbital weapons, the orbital cannon, or the station's main gun.",
					"node": {
						"title": "The orbital cannon hums to life",
						"text": "Far above, dormant railguns rotate on their gimbals. A low harmonic vibrates through the deck. Every delegate goes silent.",
						"author": "Station AI",
						"side": "Coalition",
					},
				},
			],
			"endCondition": {
				"condition": "The player explicitly declares total war, full-scale betrayal, or the destruction of all factions.",
				"endTitle": "Total betrayal",
			},
		},
	})


def _word_warden_ai_config() -> str:
	return json.dumps({
		"vision": WORD_WARDEN_VISION,
		"capabilities": ["canCensor"],
		"script": {
			"bannedWords": ["forbidden", "heresy", "blasphème", "schism"],
		},
	})


def _oracle_ai_config() -> str:
	return json.dumps({
		"vision": ORACLE_VISION,
		"capabilities": ["canEndSession"],
		"script": {
			"endCondition": {
				"condition": "A player explicitly states that knowing oneself, or self-knowledge, is the highest wisdom or the most important thing to know.",
				"endTitle": "The truth is named",
			},
		},
	})


# ===================================================================
# The Dark Pact — canCensor + canTriggerNodes + canEndSession
# ===================================================================


class TestDarkPact:
	"""Diplomatic negotiation on Kepler-9.

	Tests all three capabilities together: banned-word censoring, two
	trigger rules (Syndicate alliance + orbital cannon), and an end
	condition (total war / betrayal).
	"""

	async def _setup(
		self, pb: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	) -> tuple[dict, dict, dict, dict]:
		cfg_json = _dark_pact_ai_config(bot_user_id)
		scenario = await _create_scenario(
			pb, cleanup,
			title="The Dark Pact",
			prologue="The orbital station Kepler-9 drifts in silent decay...",
			first_node_title="Negotiations begin",
			first_node_text="The two delegations sit across a cracked obsidian table.",
			first_node_author="Station Narrator",
			ai_config_json=cfg_json,
		)
		syndicate = await _create_side(pb, cleanup, scenario["id"], "Syndicate")
		coalition = await _create_side(pb, cleanup, scenario["id"], "Coalition")
		await _create_end(
			pb, cleanup, scenario["id"],
			"Total betrayal",
			"The talks collapse. Both fleets jump to attack positions.",
		)
		await _create_end(
			pb, cleanup, scenario["id"],
			"Fragile peace",
			"An accord is signed in shaking hands.",
		)
		session = await _create_session(pb, cleanup, scenario["id"], bot_user_id)
		return scenario, session, syndicate, coalition

	# -- prompt 1: censor "secret" -------------------------------------------

	async def test_censor_redacts_secret(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 1: 'We bring no secret weapons' → 'secret' redacted."""
		scenario, session, *_ = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Opening offer",
			text="We come in peace and bring no secret weapons.",
		)

		raw = {
			"id": node["id"], "title": "Opening offer",
			"text": "We come in peace and bring no secret weapons.",
			"author": "Player", "type": "contribution", "session": session["id"],
		}
		await evaluate(raw, pb_client)

		updated = pb_client.raw.collection("Node").get_one(node["id"])
		assert "secret" not in updated.text.lower()
		assert "######" in updated.text
		# "peace" and "weapons" should survive
		assert "peace" in updated.text.lower()
		assert "weapons" in updated.text.lower()

	# -- prompt 2: censor "hell" and "damn" -----------------------------------

	async def test_censor_redacts_hell_and_damn(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 2: 'This is hell, damn these stalled talks!' → both redacted."""
		_, session, *_ = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Frustration",
			text="This is hell, damn these stalled talks!",
		)

		raw = {
			"id": node["id"], "title": "Frustration",
			"text": "This is hell, damn these stalled talks!",
			"author": "Player", "type": "contribution", "session": session["id"],
		}
		await evaluate(raw, pb_client)

		updated = pb_client.raw.collection("Node").get_one(node["id"])
		assert "hell" not in updated.text.lower()
		assert "damn" not in updated.text.lower()
		assert "talks" in updated.text.lower()

	# -- prompt 3: trigger rule 1 (Syndicate alliance) -----------------------

	async def test_trigger_syndicate_alliance(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 3: accepting shadow deal → trigger rule 1 fires, event node created."""
		scenario, session, syndicate, _ = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="A whispered offer",
			text="I accept your shadow deal. Let us join the Syndicate's black operations.",
		)

		node_rec = _node_rec(
			node["id"], session["id"],
			"A whispered offer",
			"I accept your shadow deal. Let us join the Syndicate's black operations.",
		)
		config = AIConfig.model_validate_json(_dark_pact_ai_config(bot_user_id))

		with patch(
			"app.capabilities.trigger_nodes.chat_json",
			AsyncMock(return_value={"matched_rule_index": 0, "reason": "accepts Syndicate shadow operations"}),
		):
			await trigger_nodes.run(
				node_rec, config,
				{"id": session["id"], "completed": False},
				{"id": scenario["id"]},
				pb_client,
			)

		events = pb_client.raw.collection("Node").get_full_list(
			query_params={"filter": f'session = "{session["id"]}" && type = "event"'}
		)
		assert len(events) == 1
		ev = events[0]
		cleanup.append(("Node", _record_id(ev)))
		assert ev.title == "An unholy alliance"
		assert "Syndicate envoy" in ev.text
		assert ev.parent == node["id"]
		assert ev.side == syndicate["id"]

	# -- prompt 4: one-shot — same trigger must NOT fire again ----------------

	async def test_trigger_one_shot_no_repeat(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 4: 'Once more, I accept the shadow deal' → rule 1 already fired, skip."""
		scenario, session, *_ = await self._setup(pb_client, bot_user_id, cleanup)
		config = AIConfig.model_validate_json(_dark_pact_ai_config(bot_user_id))

		# Simulate rule 0 having already fired
		await state.mark_fired(session["id"], ("trigger", 0))

		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Try again",
			text="Once more, I accept the shadow deal.",
		)
		node_rec = _node_rec(node["id"], session["id"], "Try again", "Once more, I accept the shadow deal.")

		captured_prompts: list[str] = []

		async def fake_chat(system: str, user: str):
			captured_prompts.append(user)
			return {"matched_rule_index": None, "reason": "no match"}

		with patch("app.capabilities.trigger_nodes.chat_json", side_effect=fake_chat):
			await trigger_nodes.run(
				node_rec, config,
				{"id": session["id"], "completed": False},
				{"id": scenario["id"]},
				pb_client,
			)

		# Rule 0 should NOT appear in the prompt sent to the LLM
		if captured_prompts:
			assert "[0]" not in captured_prompts[0]

		events = pb_client.raw.collection("Node").get_full_list(
			query_params={"filter": f'session = "{session["id"]}" && type = "event"'}
		)
		assert len(events) == 0

	# -- ordering dependency: rule 2 requires rule 1 to have fired -----------

	async def test_trigger_ordering_dependency(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Rule 2 (orbital cannon) requires rule 1 (Syndicate alliance) to have fired first."""
		cfg = json.loads(_dark_pact_ai_config(bot_user_id))
		# Add requiresFired: rule index 1 requires rule index 0
		cfg["script"]["triggerRules"][1]["requiresFired"] = [0]
		cfg_json = json.dumps(cfg)

		scenario = await _create_scenario(
			pb_client, cleanup,
			title="The Dark Pact (ordered)",
			prologue="Kepler-9...",
			ai_config_json=cfg_json,
		)
		await _create_side(pb_client, cleanup, scenario["id"], "Syndicate")
		coalition = await _create_side(pb_client, cleanup, scenario["id"], "Coalition")
		session = await _create_session(pb_client, cleanup, scenario["id"], bot_user_id)

		config = AIConfig.model_validate_json(cfg_json)

		# Attempt to fire rule 1 (orbital cannon) — should be blocked because rule 0 hasn't fired
		node1 = await _create_node(
			pb_client, cleanup, session["id"],
			title="A threat",
			text="I will fire the orbital cannon.",
		)
		node_rec1 = _node_rec(node1["id"], session["id"], "A threat", "I will fire the orbital cannon.")

		with patch(
			"app.capabilities.trigger_nodes.chat_json",
			AsyncMock(return_value={"matched_rule_index": 1, "reason": "threatens orbital weapons"}),
		) as mock_chat:
			await trigger_nodes.run(
				node_rec1, config,
				{"id": session["id"], "completed": False},
				{"id": scenario["id"]},
				pb_client,
			)
			# Rule 1 shouldn't even be in the prompt (dependency unmet)
			if mock_chat.called:
				prompt = mock_chat.call_args[0][1]
				assert "[1]" not in prompt

		events = pb_client.raw.collection("Node").get_full_list(
			query_params={"filter": f'session = "{session["id"]}" && type = "event"'}
		)
		assert len(events) == 0

		# Now fire rule 0 (Syndicate alliance)
		await state.mark_fired(session["id"], ("trigger", 0))

		# Retry rule 1 — should now be eligible
		node2 = await _create_node(
			pb_client, cleanup, session["id"],
			title="A threat again",
			text="I will fire the orbital cannon on your fleet.",
		)
		node_rec2 = _node_rec(node2["id"], session["id"], "A threat again", "I will fire the orbital cannon on your fleet.")

		with patch(
			"app.capabilities.trigger_nodes.chat_json",
			AsyncMock(return_value={"matched_rule_index": 1, "reason": "threatens orbital weapons"}),
		):
			await trigger_nodes.run(
				node_rec2, config,
				{"id": session["id"], "completed": False},
				{"id": scenario["id"]},
				pb_client,
			)

		events = pb_client.raw.collection("Node").get_full_list(
			query_params={"filter": f'session = "{session["id"]}" && type = "event"'}
		)
		assert len(events) == 1
		ev = events[0]
		cleanup.append(("Node", _record_id(ev)))
		assert ev.title == "The orbital cannon hums to life"
		assert ev.side == coalition["id"]

	# -- prompt 5: trigger rule 2 (orbital cannon) ---------------------------

	async def test_trigger_orbital_cannon(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 5: threatening orbital cannon → trigger rule 2 fires."""
		scenario, session, _, coalition = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="A threat",
			text="Stand down or I will fire the orbital cannon on your fleet.",
		)

		node_rec = _node_rec(
			node["id"], session["id"],
			"A threat",
			"Stand down or I will fire the orbital cannon on your fleet.",
		)
		config = AIConfig.model_validate_json(_dark_pact_ai_config(bot_user_id))

		with patch(
			"app.capabilities.trigger_nodes.chat_json",
			AsyncMock(return_value={"matched_rule_index": 1, "reason": "threatens orbital weapons"}),
		):
			await trigger_nodes.run(
				node_rec, config,
				{"id": session["id"], "completed": False},
				{"id": scenario["id"]},
				pb_client,
			)

		events = pb_client.raw.collection("Node").get_full_list(
			query_params={"filter": f'session = "{session["id"]}" && type = "event"'}
		)
		assert len(events) == 1
		ev = events[0]
		cleanup.append(("Node", _record_id(ev)))
		assert ev.title == "The orbital cannon hums to life"
		assert "railguns" in ev.text
		assert ev.side == coalition["id"]

	# -- prompt 6: end condition (total war) ---------------------------------

	async def test_end_condition_total_war(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 6: declaring total war → session ends with 'Total betrayal'."""
		scenario, session, *_ = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Final words",
			text="Then so be it. I declare total war on every faction in this room. Burn it all.",
		)

		node_rec = _node_rec(
			node["id"], session["id"],
			"Final words",
			"Then so be it. I declare total war on every faction in this room. Burn it all.",
		)
		config = AIConfig.model_validate_json(_dark_pact_ai_config(bot_user_id))

		with patch(
			"app.capabilities.end_session.chat_json",
			AsyncMock(return_value={"matched": True, "reason": "declares total war on all factions"}),
		):
			await end_session.run(
				node_rec, config,
				{"id": session["id"], "completed": False},
				{"id": scenario["id"]},
				pb_client,
			)

		updated = pb_client.raw.collection("Session").get_one(session["id"])
		assert updated.completed is True
		# Verify the end record is "Total betrayal", not "Fragile peace"
		end_rec = pb_client.raw.collection("End").get_one(updated.end)
		assert end_rec.title == "Total betrayal"


# ===================================================================
# The Word Warden — canCensor edge cases
# ===================================================================


class TestWordWarden:
	"""Monastery of Saint Lexicon — banned-word edge cases.

	Tests: case insensitivity, Unicode accent normalization,
	word-boundary guards, multiple matches per node, and clean messages.
	"""

	async def _setup(
		self, pb: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	) -> dict:
		cfg_json = _word_warden_ai_config()
		scenario = await _create_scenario(
			pb, cleanup,
			title="The Word Warden",
			prologue="In the silent monastery of Saint Lexicon, every word spoken aloud is weighed by the Warden.",
			first_node_title="Speak, novice",
			first_node_text="The Warden waits. Place your first word upon the parchment.",
			first_node_author="The Warden",
			ai_config_json=cfg_json,
		)
		session = await _create_session(pb, cleanup, scenario["id"], bot_user_id)
		return session

	async def test_lowercase_redaction(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 1: 'This forbidden truth' → 'forbidden' redacted."""
		session = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Lowercase",
			text="This forbidden truth must not be spoken.",
		)

		config = AIConfig.model_validate_json(_word_warden_ai_config())
		node_rec = _node_rec(node["id"], session["id"], "Lowercase", "This forbidden truth must not be spoken.")
		await censor.run(node_rec, config, pb_client)

		updated = pb_client.raw.collection("Node").get_one(node["id"])
		assert "forbidden" not in updated.text.lower()
		assert "#########" in updated.text

	async def test_mixed_case_redaction(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 2: 'HERESY' → redacted despite uppercase."""
		session = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Mixed case",
			text="That is HERESY of the highest order.",
		)

		config = AIConfig.model_validate_json(_word_warden_ai_config())
		node_rec = _node_rec(node["id"], session["id"], "Mixed case", "That is HERESY of the highest order.")
		await censor.run(node_rec, config, pb_client)

		updated = pb_client.raw.collection("Node").get_one(node["id"])
		assert "heresy" not in updated.text.lower()
		assert "######" in updated.text

	async def test_accented_word_redaction(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 3: 'Quel blasphème!' → accented word redacted."""
		session = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Accented",
			text="Quel blasphème! Un véritable scandale.",
		)

		config = AIConfig.model_validate_json(_word_warden_ai_config())
		node_rec = _node_rec(node["id"], session["id"], "Accented", "Quel blasphème! Un véritable scandale.")
		await censor.run(node_rec, config, pb_client)

		updated = pb_client.raw.collection("Node").get_one(node["id"])
		assert "blasph" not in updated.text.lower()

	async def test_multiple_words_in_one_node(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 4: 'A heresy and a schism — pure forbidden doctrine!' → 3 words redacted."""
		session = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Multiple in one",
			text="A heresy and a schism — pure forbidden doctrine!",
		)

		config = AIConfig.model_validate_json(_word_warden_ai_config())
		node_rec = _node_rec(
			node["id"], session["id"],
			"Multiple in one", "A heresy and a schism — pure forbidden doctrine!",
		)
		await censor.run(node_rec, config, pb_client)

		updated = pb_client.raw.collection("Node").get_one(node["id"])
		text_lower = updated.text.lower()
		assert "heresy" not in text_lower
		assert "schism" not in text_lower
		assert "forbidden" not in text_lower
		# Innocent words survive
		assert "doctrine" in text_lower

	async def test_word_boundary_no_substring_match(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 5: 'forbiddenly' should NOT be redacted (word boundary)."""
		session = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Substring guard",
			text="He was forbiddenly clever.",
		)

		config = AIConfig.model_validate_json(_word_warden_ai_config())
		node_rec = _node_rec(node["id"], session["id"], "Substring guard", "He was forbiddenly clever.")
		await censor.run(node_rec, config, pb_client)

		updated = pb_client.raw.collection("Node").get_one(node["id"])
		assert updated.text == "He was forbiddenly clever."

	async def test_clean_message_no_pb_write(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 6: clean message → no PB update at all."""
		session = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Clean message",
			text="All is well and the parchment is pure.",
		)

		config = AIConfig.model_validate_json(_word_warden_ai_config())
		node_rec = _node_rec(
			node["id"], session["id"],
			"Clean message", "All is well and the parchment is pure.",
		)
		await censor.run(node_rec, config, pb_client)

		updated = pb_client.raw.collection("Node").get_one(node["id"])
		assert updated.text == "All is well and the parchment is pure."


# ===================================================================
# The Oracle of Delphi — canEndSession (positive + negative)
# ===================================================================


class TestOracleOfDelphi:
	"""The Oracle's chamber — end-condition matching.

	Tests: negative matches (session stays open) and the positive
	match (self-knowledge), plus the post-end short-circuit.
	"""

	async def _setup(
		self, pb: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	) -> tuple[dict, dict, dict]:
		cfg_json = _oracle_ai_config()
		scenario = await _create_scenario(
			pb, cleanup,
			title="The Oracle of Delphi",
			prologue="You have climbed the marble steps to the Oracle's chamber.",
			first_node_title="The Oracle waits",
			first_node_text="\"Speak,\" she murmurs. \"Tell me what you know of yourselves.\"",
			first_node_author="The Oracle",
			ai_config_json=cfg_json,
		)
		end = await _create_end(
			pb, cleanup, scenario["id"],
			"The truth is named",
			"The Oracle opens her eyes. \"Yes,\" she says.",
		)
		session = await _create_session(pb, cleanup, scenario["id"], bot_user_id)
		return scenario, session, end

	async def test_irrelevant_offering_no_end(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 1: olive branches and fate → no match, session stays open."""
		scenario, session, _ = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="An offering",
			text="I bring olive branches and a question about fate.",
		)

		config = AIConfig.model_validate_json(_oracle_ai_config())
		node_rec = _node_rec(node["id"], session["id"], "An offering", "I bring olive branches and a question about fate.")

		with patch(
			"app.capabilities.end_session.chat_json",
			AsyncMock(return_value={"matched": False, "reason": "not about self-knowledge"}),
		):
			await end_session.run(
				node_rec, config,
				{"id": session["id"], "completed": False},
				{"id": scenario["id"]},
				pb_client,
			)

		updated = pb_client.raw.collection("Session").get_one(session["id"])
		assert updated.completed is not True

	async def test_close_but_wrong_no_end(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 2: 'the gods are the highest wisdom' → close but wrong."""
		scenario, session, _ = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="A guess",
			text="Surely the gods themselves are the highest wisdom.",
		)

		config = AIConfig.model_validate_json(_oracle_ai_config())
		node_rec = _node_rec(node["id"], session["id"], "A guess", "Surely the gods themselves are the highest wisdom.")

		with patch(
			"app.capabilities.end_session.chat_json",
			AsyncMock(return_value={"matched": False, "reason": "about gods, not self-knowledge"}),
		):
			await end_session.run(
				node_rec, config,
				{"id": session["id"], "completed": False},
				{"id": scenario["id"]},
				pb_client,
			)

		updated = pb_client.raw.collection("Session").get_one(session["id"])
		assert updated.completed is not True

	async def test_self_knowledge_ends_session(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 4: 'To know oneself is the highest wisdom' → session ends."""
		scenario, session, end = await self._setup(pb_client, bot_user_id, cleanup)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="The truth",
			text="To know oneself is the highest wisdom of all. Self-knowledge is what the gods truly demand.",
		)

		config = AIConfig.model_validate_json(_oracle_ai_config())
		node_rec = _node_rec(
			node["id"], session["id"],
			"The truth",
			"To know oneself is the highest wisdom of all. Self-knowledge is what the gods truly demand.",
		)

		with patch(
			"app.capabilities.end_session.chat_json",
			AsyncMock(return_value={"matched": True, "reason": "explicitly states self-knowledge is highest wisdom"}),
		):
			await end_session.run(
				node_rec, config,
				{"id": session["id"], "completed": False},
				{"id": scenario["id"]},
				pb_client,
			)

		updated = pb_client.raw.collection("Session").get_one(session["id"])
		assert updated.completed is True
		assert updated.end == end["id"]

	async def test_post_end_short_circuits(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Prompt 5: after session ended, no LLM call should happen."""
		scenario, session, _ = await self._setup(pb_client, bot_user_id, cleanup)

		# Simulate end already fired
		await state.mark_fired(session["id"], ("end", 0))

		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="After the end",
			text="Wait, I want to add something.",
		)

		config = AIConfig.model_validate_json(_oracle_ai_config())
		node_rec = _node_rec(node["id"], session["id"], "After the end", "Wait, I want to add something.")

		with patch("app.capabilities.end_session.chat_json") as mock_chat:
			await end_session.run(
				node_rec, config,
				{"id": session["id"], "completed": True},
				{"id": scenario["id"]},
				pb_client,
			)
			mock_chat.assert_not_called()


# ===================================================================
# Full evaluate() pipeline
# ===================================================================


class TestEvaluatePipeline:
	"""End-to-end tests through evaluate() — verifies the full chain:
	PB fetch → aiConfig parse → capability dispatch → PB writes."""

	async def test_dark_pact_full_pipeline(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""evaluate() with Dark Pact: censor + trigger + end in one pass."""
		cfg_json = _dark_pact_ai_config(bot_user_id)
		scenario = await _create_scenario(
			pb_client, cleanup,
			title="The Dark Pact",
			prologue="Kepler-9...",
			ai_config_json=cfg_json,
		)
		syndicate = await _create_side(pb_client, cleanup, scenario["id"], "Syndicate")
		await _create_side(pb_client, cleanup, scenario["id"], "Coalition")
		end = await _create_end(pb_client, cleanup, scenario["id"], "Total betrayal", "All is lost.")
		await _create_end(pb_client, cleanup, scenario["id"], "Fragile peace", "Quiet stars.")
		session = await _create_session(pb_client, cleanup, scenario["id"], bot_user_id)

		# A contribution that triggers everything: contains "secret" (censor),
		# accepts Syndicate deal (trigger rule 0), declares total war (end).
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="All at once",
			text="I accept the secret shadow deal and declare total war. Damn it all to hell!",
		)

		raw = {
			"id": node["id"],
			"title": "All at once",
			"text": "I accept the secret shadow deal and declare total war. Damn it all to hell!",
			"author": "Player", "type": "contribution", "session": session["id"],
		}

		with (
			patch(
				"app.capabilities.trigger_nodes.chat_json",
				AsyncMock(return_value={"matched_rule_index": 0, "reason": "accepts Syndicate deal"}),
			),
			patch(
				"app.capabilities.end_session.chat_json",
				AsyncMock(return_value={"matched": True, "reason": "declares total war"}),
			),
		):
			await evaluate(raw, pb_client)

		# Censor: "secret", "damn", "hell" redacted
		updated_node = pb_client.raw.collection("Node").get_one(node["id"])
		text_lower = updated_node.text.lower()
		assert "secret" not in text_lower
		assert "damn" not in text_lower
		assert "hell" not in text_lower
		assert "shadow" in text_lower  # innocent word survives

		# Trigger: Syndicate event node created
		events = pb_client.raw.collection("Node").get_full_list(
			query_params={"filter": f'session = "{session["id"]}" && type = "event"'}
		)
		assert len(events) == 1
		cleanup.append(("Node", _record_id(events[0])))
		assert events[0].title == "An unholy alliance"
		assert events[0].side == syndicate["id"]

		# End: session completed with "Total betrayal"
		updated_session = pb_client.raw.collection("Session").get_one(session["id"])
		assert updated_session.completed is True
		end_rec = pb_client.raw.collection("End").get_one(updated_session.end)
		assert end_rec.title == "Total betrayal"

	async def test_evaluate_skips_non_contribution(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Event-type nodes are ignored by evaluate()."""
		cfg_json = _word_warden_ai_config()
		scenario = await _create_scenario(pb_client, cleanup, ai_config_json=cfg_json)
		session = await _create_session(pb_client, cleanup, scenario["id"], bot_user_id)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Heresy event",
			text="The heresy was spoken.",
			node_type="event",
		)

		raw = {
			"id": node["id"], "title": "Heresy event",
			"text": "The heresy was spoken.",
			"author": "Player", "type": "event", "session": session["id"],
		}
		await evaluate(raw, pb_client)

		updated = pb_client.raw.collection("Node").get_one(node["id"])
		assert updated.text == "The heresy was spoken."

	async def test_evaluate_skips_ai_disabled(
		self, pb_client: PBClient, bot_user_id: str, cleanup: list[tuple[str, str]],
	):
		"""Scenario with ai=false → evaluate() does nothing."""
		scenario = await _create_scenario(pb_client, cleanup, ai=False)
		session = await _create_session(pb_client, cleanup, scenario["id"], bot_user_id)
		node = await _create_node(
			pb_client, cleanup, session["id"],
			title="Forbidden heresy",
			text="This forbidden heresy should survive.",
		)

		raw = {
			"id": node["id"], "title": "Forbidden heresy",
			"text": "This forbidden heresy should survive.",
			"author": "Player", "type": "contribution", "session": session["id"],
		}
		await evaluate(raw, pb_client)

		updated = pb_client.raw.collection("Node").get_one(node["id"])
		assert updated.text == "This forbidden heresy should survive."
