from unittest.mock import AsyncMock, patch

import pytest

from app import state
from app.capabilities import trigger_nodes
from app.models import AIConfig, AINodeDef, AIScript, AITriggerRule, NodeRecord


def _cfg(rules: list[AITriggerRule]) -> AIConfig:
	return AIConfig(
		vision="x" * 10,
		capabilities=["canTriggerNodes"],
		script=AIScript(triggerRules=rules),
	)


def _node(session: str = "sess1") -> NodeRecord:
	return NodeRecord(
		id="contrib1",
		title="t",
		text="I accept the deal",
		author="alice",
		type="contribution",
		session=session,
	)


def _rule(condition: str, side: str = "QG", title: str = "Reaction") -> AITriggerRule:
	return AITriggerRule(
		condition=condition,
		node=AINodeDef(title=title, text="boom", author="bot", side=side),
	)


@pytest.fixture(autouse=True)
def _reset_state():
	state._fired.clear()  # type: ignore[attr-defined]
	yield
	state._fired.clear()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_no_rules_is_noop():
	pb = AsyncMock()
	with patch("app.capabilities.trigger_nodes.chat_json") as chat:
		await trigger_nodes.run(_node(), _cfg([]), {}, {"id": "sc1"}, pb)
	chat.assert_not_called()


@pytest.mark.asyncio
async def test_no_match_does_nothing():
	pb = AsyncMock()
	pb.find_side_id.return_value = "side1"
	with patch(
		"app.capabilities.trigger_nodes.chat_json",
		AsyncMock(return_value={"matched_rule_index": None, "reason": "no"}),
	):
		await trigger_nodes.run(
			_node(), _cfg([_rule("accepts the deal")]), {}, {"id": "sc1"}, pb
		)
	pb.create_node.assert_not_called()


@pytest.mark.asyncio
async def test_match_creates_node_and_marks_fired():
	pb = AsyncMock()
	pb.find_side_id.return_value = "side1"
	pb.create_node.return_value = {"id": "newnode"}
	cfg = _cfg([_rule("accepts the deal")])
	with patch(
		"app.capabilities.trigger_nodes.chat_json",
		AsyncMock(return_value={"matched_rule_index": 0, "reason": "match"}),
	):
		await trigger_nodes.run(_node(), cfg, {}, {"id": "sc1"}, pb)

	pb.create_node.assert_called_once()
	payload = pb.create_node.call_args[0][0]
	assert payload["type"] == "event"
	assert payload["session"] == "sess1"
	assert payload["parent"] == "contrib1"
	assert payload["side"] == "side1"
	assert ("trigger", 0) in await state.fired_set("sess1")


@pytest.mark.asyncio
async def test_already_fired_rule_is_filtered_out():
	pb = AsyncMock()
	pb.find_side_id.return_value = "side1"
	pb.create_node.return_value = {"id": "newnode"}
	cfg = _cfg([_rule("accepts the deal"), _rule("refuses the deal")])
	await state.mark_fired("sess1", ("trigger", 0))

	captured_prompts: list[str] = []

	async def fake_chat(system: str, user: str):
		captured_prompts.append(user)
		return {"matched_rule_index": 1, "reason": "match"}

	with patch("app.capabilities.trigger_nodes.chat_json", side_effect=fake_chat):
		await trigger_nodes.run(_node(), cfg, {}, {"id": "sc1"}, pb)

	assert len(captured_prompts) == 1
	# Only the un-fired rule (index 1) should appear in the prompt
	assert "[1]" in captured_prompts[0]
	assert "[0]" not in captured_prompts[0]
	pb.create_node.assert_called_once()


@pytest.mark.asyncio
async def test_unknown_side_aborts():
	pb = AsyncMock()
	pb.find_side_id.return_value = None
	with patch(
		"app.capabilities.trigger_nodes.chat_json",
		AsyncMock(return_value={"matched_rule_index": 0, "reason": "match"}),
	):
		await trigger_nodes.run(
			_node(), _cfg([_rule("accepts")]), {}, {"id": "sc1"}, pb
		)
	pb.create_node.assert_not_called()
