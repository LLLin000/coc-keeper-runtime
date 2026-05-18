"""Publication event models with partitioned visibility."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class PublicationPath(str, Enum):
    TABLE_VISIBLE = "table_visible"
    KP_ONLY = "kp_only"
    PRIVATE = "private"


class PublicationEvent(BaseModel):
    event_type: str
    session_id: str
    visibility: PublicationPath = PublicationPath.TABLE_VISIBLE
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActionSubmittedEvent(PublicationEvent):
    event_type: Literal["action.submitted"] = "action.submitted"
    user_id: str
    action_text: str
    scene_id: str


class RoundResolvedEvent(PublicationEvent):
    event_type: Literal["round.resolved"] = "round.resolved"
    scene_id: str
    round_number: int = 0
    ordered_actions: list[str] = Field(default_factory=list)


class ClueRevealedEvent(PublicationEvent):
    event_type: Literal["clue.revealed"] = "clue.revealed"
    visibility: PublicationPath = PublicationPath.PRIVATE
    clue_id: str
    description: str = ""
    player_id: str = ""


class SceneTransitionEvent(PublicationEvent):
    event_type: Literal["scene.transition"] = "scene.transition"
    from_scene_id: str = ""
    to_scene_id: str = ""
    reason: str = ""


class BlockerCreatedEvent(PublicationEvent):
    event_type: Literal["blocker.created"] = "blocker.created"
    blocker_id: str
    reason: str = ""


class BlockerResolvedEvent(PublicationEvent):
    event_type: Literal["blocker.resolved"] = "blocker.resolved"
    blocker_id: str
    reason: str = ""


class NarrationRequestedEvent(PublicationEvent):
    event_type: Literal["narration.requested"] = "narration.requested"
    visibility: PublicationPath = PublicationPath.KP_ONLY
    context: dict[str, Any] = Field(default_factory=dict)
    prompt_text: str = ""
