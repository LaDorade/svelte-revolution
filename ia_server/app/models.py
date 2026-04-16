"""Pydantic models mirroring src/types/ai/index.ts and src/lib/zschemas/aiConfig.schema.ts."""

from typing import Literal

from pydantic import BaseModel, Field

AICapability = Literal["canCensor", "canTriggerNodes", "canEndSession"]


class AINodeDef(BaseModel):
	title: str
	text: str
	author: str
	side: str  # side name (matches Side.name in PocketBase)


class AITriggerRule(BaseModel):
	condition: str
	node: AINodeDef
	requiresFired: list[int] = Field(default_factory=list)


class AIEndCondition(BaseModel):
	condition: str
	endTitle: str


class AIScript(BaseModel):
	bannedWords: list[str] = Field(default_factory=list)
	triggerRules: list[AITriggerRule] = Field(default_factory=list)
	endCondition: AIEndCondition | None = None


class AIConfig(BaseModel):
	vision: str
	capabilities: list[AICapability] = Field(default_factory=list)
	script: AIScript = Field(default_factory=AIScript)


class NodeRecord(BaseModel):
	"""Subset of a PocketBase Node record we care about."""

	id: str
	title: str
	text: str
	author: str
	type: Literal["contribution", "event", "startNode"]
	session: str
	parent: str | None = None
	side: str | None = None
