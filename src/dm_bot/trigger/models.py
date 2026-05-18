"""Trigger, event, reaction, and blocker models."""

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class TriggerEvent(BaseModel):
    """Something that happened in the game that may trigger reactions."""

    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    event_type: str
    source: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)


class Reaction(BaseModel):
    """What happens when a trigger fires."""

    reaction_id: str
    effect_type: str
    params: dict[str, Any] = Field(default_factory=dict)
    priority: int = 100
    atomic_group: str | None = None


class Trigger(BaseModel):
    """A condition-reaction pair associated with a scene or adventure."""

    trigger_id: str
    event_type: str
    condition: dict[str, Any] = Field(default_factory=dict)
    reactions: list[Reaction] = Field(default_factory=list)


class BlockerCheckpoint(BaseModel):
    """A persisted checkpoint where trigger execution paused."""

    blocker_id: str = Field(default_factory=lambda: f"blk_{uuid.uuid4().hex[:12]}")
    trigger_chain_id: str
    scene_id: str = ""
    reason: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None

    def resolve(self) -> None:
        self.resolved_at = datetime.now(timezone.utc)
