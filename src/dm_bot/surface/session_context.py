"""Session runtime context — holds active runtime state for board rendering."""

import uuid
from typing import Any

from dm_bot.trigger.engine import TriggerEngine
from dm_bot.publish.publisher import Publisher
from dm_bot.store.db import Store


class SessionContext:
    """Holds the active session's runtime components and metadata."""

    def __init__(
        self,
        session_id: str,
        module_name: str = "",
        store: Store | None = None,
        trigger_engine: TriggerEngine | None = None,
        publisher: Publisher | None = None,
    ) -> None:
        self.session_id = session_id
        self.module_name = module_name
        self.phase: str = "idle"
        self.participants: list[str] = []
        self.store = store or Store(":memory:")
        self.trigger_engine = trigger_engine or TriggerEngine()
        self.publisher = publisher or Publisher()

    def add_participant(self, user_id: str) -> None:
        if user_id not in self.participants:
            self.participants.append(user_id)

    def to_dict(self) -> dict[str, Any]:
        blockers: list[dict[str, str]] = []
        if self.store:
            try:
                blockers = [
                    {
                        "blocker_id": b.blocker_id,
                        "reason": b.reason,
                        "scene_id": b.scene_id,
                    }
                    for b in self.store.list_unresolved_blockers()
                ]
            except Exception:
                blockers = []
        return {
            "session_id": self.session_id,
            "module_name": self.module_name,
            "phase": self.phase,
            "participants": list(self.participants),
            "blockers": blockers,
        }
