"""Polling-based subscriber.

The PocketBase Python SDK does not have reliable real-time SSE support, so we
poll for new contribution-type nodes at a configurable interval. This achieves
the same async, decoupled behavior as a subscription with much less complexity.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from .config import settings
from .evaluator import evaluate
from .pb_client import pb_client

log = logging.getLogger(__name__)

POLL_INTERVAL_S = 2.0


class Subscriber:
	def __init__(self) -> None:
		self._task: asyncio.Task | None = None
		self._queue: asyncio.Queue[dict] = asyncio.Queue()
		self._workers: list[asyncio.Task] = []
		self._stop = asyncio.Event()

	async def start(self) -> None:
		self._stop.clear()
		self._task = asyncio.create_task(self._poll_loop(), name="subscriber-poll")
		for i in range(settings.worker_count):
			self._workers.append(
				asyncio.create_task(self._worker(i), name=f"evaluator-{i}")
			)
		log.info("Subscriber started with %d workers", settings.worker_count)

	async def stop(self) -> None:
		self._stop.set()
		if self._task:
			self._task.cancel()
		for w in self._workers:
			w.cancel()
		await asyncio.gather(
			*([self._task] if self._task else []),
			*self._workers,
			return_exceptions=True,
		)
		log.info("Subscriber stopped")

	async def _poll_loop(self) -> None:
		# Start by ignoring everything that already exists at boot time.
		since_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%fZ")
		log.info("Polling Node collection from %s every %ss", since_iso, POLL_INTERVAL_S)

		while not self._stop.is_set():
			try:
				new_nodes = await pb_client.list_new_contributions(since_iso)
			except Exception as e:  # noqa: BLE001
				log.error("Polling error: %s", e)
				new_nodes = []

			for n in new_nodes:
				created = n.get("created")
				if isinstance(created, datetime):
					created_str = created.strftime("%Y-%m-%d %H:%M:%S.%fZ")
				else:
					created_str = str(created)
				if created_str > since_iso:
					since_iso = created_str
				await self._queue.put(n)

			try:
				await asyncio.wait_for(self._stop.wait(), timeout=POLL_INTERVAL_S)
			except asyncio.TimeoutError:
				pass

	async def _worker(self, idx: int) -> None:
		while not self._stop.is_set():
			try:
				node = await self._queue.get()
			except asyncio.CancelledError:
				return
			try:
				await evaluate(node, pb_client)
			except Exception as e:  # noqa: BLE001
				log.exception("Worker %d failed on node %s: %s", idx, node.get("id"), e)
			finally:
				self._queue.task_done()


subscriber = Subscriber()
