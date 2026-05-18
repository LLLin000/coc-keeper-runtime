"""Reveal gate and knowledge tracking models."""

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class RevealGate(BaseModel):
    """A condition that must be met before a clue is revealed."""

    gate_id: str = Field(default_factory=lambda: f"rg_{uuid.uuid4().hex[:12]}")
    clue_id: str
    gate_type: str  # skill_check, trigger, scene_state, manual
    condition: dict[str, Any] = Field(default_factory=dict)
    is_open: bool = False
    opened_at: datetime | None = None
    opened_by: str = ""

    def open(self, opened_by: str = "") -> None:
        self.is_open = True
        self.opened_at = datetime.now(timezone.utc)
        self.opened_by = opened_by


class KnowledgeState(BaseModel):
    """Per-player knowledge tracking within a session."""

    player_id: str
    known_clue_ids: list[str] = Field(default_factory=list)

    def learn_clue(self, clue_id: str) -> None:
        if clue_id not in self.known_clue_ids:
            self.known_clue_ids.append(clue_id)

    def knows_clue(self, clue_id: str) -> bool:
        return clue_id in self.known_clue_ids

    def forget_clue(self, clue_id: str) -> None:
        if clue_id in self.known_clue_ids:
            self.known_clue_ids.remove(clue_id)
