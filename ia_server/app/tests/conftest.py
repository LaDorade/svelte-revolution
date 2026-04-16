"""Shared fixtures for unit and integration tests."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app import state
from app.pb_client import PBClient


def pytest_configure(config: Any) -> None:
	config.addinivalue_line("markers", "integration: requires a running PocketBase instance")
	config.addinivalue_line("markers", "llm: requires a valid MISTRAL_API_KEY (real LLM calls)")


# ---------------------------------------------------------------------------
# Module-scoped PocketBase client (login once per test module)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def event_loop():
	"""Module-scoped event loop so module-scoped async fixtures work."""
	loop = asyncio.new_event_loop()
	yield loop
	loop.close()


@pytest.fixture(scope="module")
async def pb_client() -> PBClient:
	"""Authenticated PBClient. Auto-skips the module if PB is unreachable."""
	pb = PBClient()
	try:
		await pb.login()
	except Exception:
		pytest.skip("PocketBase not available or bot credentials not configured")
	return pb


@pytest.fixture(scope="module")
async def bot_user_id(pb_client: PBClient) -> str:
	"""The authenticated bot user's PocketBase record ID."""
	model = pb_client.raw.auth_store.model
	uid = getattr(model, "id", None)
	if not uid:
		pytest.skip("Could not resolve bot user ID from auth store")
	return uid


# ---------------------------------------------------------------------------
# Function-scoped fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_state():
	"""Clear the in-memory fired-rules state before and after every test."""
	state._fired.clear()
	yield
	state._fired.clear()


@pytest.fixture()
async def cleanup(pb_client: PBClient):
	"""Collects (collection_name, record_id) tuples and deletes them in LIFO
	order during teardown, respecting foreign-key constraints."""
	items: list[tuple[str, str]] = []
	yield items
	for collection, record_id in reversed(items):
		try:
			pb_client.raw.collection(collection).delete(record_id)
		except Exception:
			pass  # already deleted by cascade or previous cleanup
