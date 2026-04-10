from unittest.mock import AsyncMock

import pytest

from app.capabilities import censor
from app.models import AIConfig, AIScript, NodeRecord


def _node(title: str = "", text: str = "") -> NodeRecord:
	return NodeRecord(
		id="n1",
		title=title,
		text=text,
		author="alice",
		type="contribution",
		session="s1",
	)


def test_redact_simple_word():
	out, changed = censor._redact("a secret message", ["secret"])
	assert changed
	assert out == "a ###### message"


def test_redact_case_insensitive():
	out, changed = censor._redact("Top SECRET data", ["secret"])
	assert changed
	assert out == "Top ###### data"


def test_redact_strips_accents():
	out, changed = censor._redact("le café est bon", ["cafe"])
	assert changed
	assert "####" in out


def test_redact_word_boundary():
	# 'sec' should NOT match the substring inside 'second'
	out, changed = censor._redact("the second time", ["sec"])
	assert not changed
	assert out == "the second time"


def test_redact_no_banned_words():
	out, changed = censor._redact("hello world", [])
	assert not changed
	assert out == "hello world"


def test_redact_multiple_words():
	out, changed = censor._redact("alpha and beta", ["alpha", "beta"])
	assert changed
	assert out == "##### and ####"


@pytest.mark.asyncio
async def test_run_skips_when_no_change():
	pb = AsyncMock()
	cfg = AIConfig(vision="x" * 10, capabilities=["canCensor"], script=AIScript(bannedWords=["nope"]))
	await censor.run(_node(title="hi", text="there"), cfg, pb)
	pb.update_node.assert_not_called()


@pytest.mark.asyncio
async def test_run_updates_when_changed():
	pb = AsyncMock()
	cfg = AIConfig(
		vision="x" * 10, capabilities=["canCensor"], script=AIScript(bannedWords=["secret"])
	)
	await censor.run(_node(title="A secret", text="more secret stuff"), cfg, pb)
	pb.update_node.assert_called_once()
	args, _ = pb.update_node.call_args
	assert args[0] == "n1"
	assert "######" in args[1]["title"]
	assert "######" in args[1]["text"]


@pytest.mark.asyncio
async def test_run_skips_when_no_banned_words():
	pb = AsyncMock()
	cfg = AIConfig(vision="x" * 10, capabilities=["canCensor"], script=AIScript())
	await censor.run(_node(title="anything", text="goes"), cfg, pb)
	pb.update_node.assert_not_called()
