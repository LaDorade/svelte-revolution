"""PocketBase client wrapper.

The official-ish `pocketbase` Python SDK is synchronous and does not implement
real-time subscriptions reliably, so we use polling instead. The polling interval
is short enough (default 2s) to feel real-time while staying simple and resilient.

All blocking calls are dispatched through `asyncio.to_thread` so they don't
block the FastAPI event loop.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pocketbase import PocketBase
from pocketbase.utils import ClientResponseError

from .config import settings

log = logging.getLogger(__name__)


class PBClient:
	def __init__(self) -> None:
		self._pb = PocketBase(settings.db_url)
		self._authed = False

	@property
	def authed(self) -> bool:
		return self._authed

	@property
	def raw(self) -> PocketBase:
		return self._pb

	async def login(self) -> None:
		def _login() -> None:
			self._pb.collection("users").auth_with_password(
				settings.pb_bot_email, settings.pb_bot_password
			)

		try:
			await asyncio.to_thread(_login)
			self._authed = True
			log.info("Authenticated as %s", settings.pb_bot_email)
		except ClientResponseError as e:
			self._authed = False
			log.error("Failed to authenticate as %s: %s", settings.pb_bot_email, e)
			raise

	async def list_new_contributions(self, since_iso: str | None) -> list[dict[str, Any]]:
		"""Return contribution-type nodes created strictly after `since_iso`."""

		def _list() -> list[dict[str, Any]]:
			filt = 'type = "contribution"'
			if since_iso:
				filt = f'created > "{since_iso}" && {filt}'
			records = self._pb.collection("Node").get_full_list(
				query_params={"filter": filt, "sort": "created"}
			)
			return [_record_to_dict(r) for r in records]

		return await asyncio.to_thread(_list)

	async def get_session_with_scenario(self, session_id: str) -> dict[str, Any] | None:
		def _get() -> dict[str, Any] | None:
			try:
				rec = self._pb.collection("Session").get_one(
					session_id, query_params={"expand": "scenario"}
				)
			except ClientResponseError as e:
				log.warning("Session %s not found: %s", session_id, e)
				return None
			data = _record_to_dict(rec)
			# pocketbase-python stores expand on the record object
			expand = getattr(rec, "expand", None) or {}
			scenario = expand.get("scenario")
			if scenario is not None:
				data["expand"] = {"scenario": _record_to_dict(scenario)}
			return data

		return await asyncio.to_thread(_get)

	async def update_node(self, node_id: str, payload: dict[str, Any]) -> None:
		def _update() -> None:
			self._pb.collection("Node").update(node_id, payload)

		await asyncio.to_thread(_update)

	async def create_node(self, payload: dict[str, Any]) -> dict[str, Any]:
		def _create() -> dict[str, Any]:
			rec = self._pb.collection("Node").create(payload)
			return _record_to_dict(rec)

		return await asyncio.to_thread(_create)

	async def find_side_id(self, scenario_id: str, side_name: str) -> str | None:
		def _find() -> str | None:
			try:
				rec = self._pb.collection("Side").get_first_list_item(
					f'scenario = "{scenario_id}" && name = "{side_name}"'
				)
			except ClientResponseError:
				return None
			return getattr(rec, "id", None)

		return await asyncio.to_thread(_find)

	async def find_end_id(self, scenario_id: str, end_title: str) -> str | None:
		def _find() -> str | None:
			try:
				rec = self._pb.collection("End").get_first_list_item(
					f'scenario = "{scenario_id}" && title = "{end_title}"'
				)
			except ClientResponseError:
				return None
			return getattr(rec, "id", None)

		return await asyncio.to_thread(_find)

	async def update_session(self, session_id: str, payload: dict[str, Any]) -> None:
		def _update() -> None:
			self._pb.collection("Session").update(session_id, payload)

		await asyncio.to_thread(_update)


def _snake_to_camel(name: str) -> str:
	parts = name.split("_")
	return parts[0] + "".join(p.title() for p in parts[1:])


def _record_to_dict(rec: Any) -> dict[str, Any]:
	"""Best-effort conversion of a pocketbase Record into a plain dict.

	The Python pocketbase SDK rewrites camelCase field names to snake_case
	(e.g. `aiConfig` → `ai_config`). We convert them back so downstream
	consumers (evaluator, Pydantic models, capabilities) can use the same
	field names as the TypeScript side and the raw PocketBase API.
	"""
	if isinstance(rec, dict):
		return rec
	# pocketbase-python Record objects expose .__dict__ with the loaded fields
	d = {
		_snake_to_camel(k): v
		for k, v in vars(rec).items()
		if not k.startswith("_")
	}
	d.pop("expand", None)
	return d


# Module-level singleton, initialized in main.py lifespan
pb_client = PBClient()
