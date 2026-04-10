"""Per-node evaluator: orchestrates the three capabilities for one new contribution."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pydantic import ValidationError

from .capabilities import censor, end_session, trigger_nodes
from .models import AIConfig, NodeRecord
from .pb_client import PBClient

log = logging.getLogger(__name__)


async def evaluate(raw_node: dict[str, Any], pb: PBClient) -> None:
	try:
		node = NodeRecord.model_validate(raw_node)
	except ValidationError as e:
		log.warning("Skipping invalid node payload: %s", e)
		return

	if node.type != "contribution":
		return

	session = await pb.get_session_with_scenario(node.session)
	if session is None:
		log.warning("Session %s not found, skipping node %s", node.session, node.id)
		return

	scenario = (session.get("expand") or {}).get("scenario")
	if not scenario:
		log.warning("Session %s has no scenario expand, skipping", node.session)
		return

	if not scenario.get("ai"):
		return

	raw_cfg = scenario.get("aiConfig")
	if not raw_cfg:
		log.info("Scenario %s has ai=true but no aiConfig", scenario.get("id"))
		return

	try:
		config = AIConfig.model_validate_json(raw_cfg)
	except ValidationError as e:
		log.warning("Scenario %s has invalid aiConfig: %s", scenario.get("id"), e)
		return

	caps = set(config.capabilities)
	tasks: list = []
	if "canCensor" in caps:
		tasks.append(censor.run(node, config, pb))
	if "canTriggerNodes" in caps:
		tasks.append(trigger_nodes.run(node, config, session, scenario, pb))
	if "canEndSession" in caps:
		tasks.append(end_session.run(node, config, session, scenario, pb))

	if not tasks:
		return

	results = await asyncio.gather(*tasks, return_exceptions=True)
	for r in results:
		if isinstance(r, Exception):
			log.error("Capability raised: %s", r)
