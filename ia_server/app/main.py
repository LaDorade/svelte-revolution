"""FastAPI entry point.

Exposes a single /api/health endpoint and runs the polling subscriber as a
background task via the FastAPI lifespan context.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .pb_client import pb_client
from .subscriber import subscriber

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
	try:
		await pb_client.login()
	except Exception as e:  # noqa: BLE001
		log.error("Bot login failed; subscriber will not start: %s", e)
	else:
		await subscriber.start()
	try:
		yield
	finally:
		await subscriber.stop()


app = FastAPI(title="Babel Révolution AI Game Master", lifespan=lifespan)


@app.get("/api/health")
async def health() -> dict:
	return {"ok": True, "pb_authed": pb_client.authed}
