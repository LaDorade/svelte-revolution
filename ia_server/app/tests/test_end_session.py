from unittest.mock import AsyncMock, patch

import pytest

from app import state
from app.capabilities import end_session
from app.models import AIConfig, AIEndCondition, AIScript, NodeRecord


def _node() -> NodeRecord:
	return NodeRecord(
		id="contrib1",
		title="t",
		text="I betray everyone",
		author="alice",
		type="contribution",
		session="sess1",
	)


def _cfg(condition: str = "the player betrays everyone", end_title: str = "Betrayal") -> AIConfig:
	return AIConfig(
		vision="x" * 10,
		capabilities=["canEndSession"],
		script=AIScript(endCondition=AIEndCondition(condition=condition, endTitle=end_title)),
	)


@pytest.fixture(autouse=True)
def _reset_state():
	state._fired.clear()  # type: ignore[attr-defined]
	yield
	state._fired.clear()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_no_end_condition_is_noop():
	pb = AsyncMock()
	cfg = AIConfig(vision="x" * 10, capabilities=["canEndSession"], script=AIScript())
	with patch("app.capabilities.end_session.chat_json") as chat:
		await end_session.run(_node(), cfg, {"completed": False}, {"id": "sc1"}, pb)
	chat.assert_not_called()
	pb.update_session.assert_not_called()


@pytest.mark.asyncio
async def test_already_completed_session_short_circuits():
	pb = AsyncMock()
	with patch("app.capabilities.end_session.chat_json") as chat:
		await end_session.run(_node(), _cfg(), {"completed": True}, {"id": "sc1"}, pb)
	chat.assert_not_called()
	pb.update_session.assert_not_called()


@pytest.mark.asyncio
async def test_match_ends_session_and_marks_fired():
	pb = AsyncMock()
	pb.find_end_id.return_value = "end1"
	with patch(
		"app.capabilities.end_session.chat_json",
		AsyncMock(return_value={"matched": True, "reason": "yes"}),
	):
		await end_session.run(_node(), _cfg(), {"completed": False}, {"id": "sc1"}, pb)
	pb.update_session.assert_called_once_with("sess1", {"completed": True, "end": "end1"})
	assert ("end", 0) in await state.fired_set("sess1")


@pytest.mark.asyncio
async def test_already_fired_short_circuits():
	pb = AsyncMock()
	await state.mark_fired("sess1", ("end", 0))
	with patch("app.capabilities.end_session.chat_json") as chat:
		await end_session.run(_node(), _cfg(), {"completed": False}, {"id": "sc1"}, pb)
	chat.assert_not_called()
	pb.update_session.assert_not_called()


@pytest.mark.asyncio
async def test_no_match_does_nothing():
	pb = AsyncMock()
	with patch(
		"app.capabilities.end_session.chat_json",
		AsyncMock(return_value={"matched": False, "reason": "no"}),
	):
		await end_session.run(_node(), _cfg(), {"completed": False}, {"id": "sc1"}, pb)
	pb.update_session.assert_not_called()


@pytest.mark.asyncio
async def test_missing_end_record_aborts():
	pb = AsyncMock()
	pb.find_end_id.return_value = None
	with patch(
		"app.capabilities.end_session.chat_json",
		AsyncMock(return_value={"matched": True, "reason": "yes"}),
	):
		await end_session.run(_node(), _cfg(), {"completed": False}, {"id": "sc1"}, pb)
	pb.update_session.assert_not_called()
