"""In-memory tracking of which trigger/end rules have already fired per session.

Lost on process restart. TODO: pre-populate on startup by querying existing AI-authored
event nodes per session against each scenario's trigger rules, or persist to a small
JSON file on the ia-server-data Docker volume.
"""

import asyncio

# Each session id maps to a set of fired rule keys.
# Keys: ("trigger", <rule_index>) or ("end", 0)
_fired: dict[str, set[tuple[str, int]]] = {}
_lock = asyncio.Lock()


async def has_fired(session_id: str, key: tuple[str, int]) -> bool:
	async with _lock:
		return key in _fired.get(session_id, set())


async def mark_fired(session_id: str, key: tuple[str, int]) -> None:
	async with _lock:
		_fired.setdefault(session_id, set()).add(key)


async def fired_set(session_id: str) -> set[tuple[str, int]]:
	async with _lock:
		return set(_fired.get(session_id, set()))
