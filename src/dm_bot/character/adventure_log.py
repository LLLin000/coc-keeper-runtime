"""Structured adventure session log."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """A single entry in the adventure log."""

    session_id: str
    entry_type: str  # skill_improvement, checkpoint, scene_enter, clue_found
    detail: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AdventureLog:
    """In-memory adventure log (persisted via Store later)."""

    def __init__(self) -> None:
        self._entries: list[LogEntry] = []

    def add_entry(self, entry: LogEntry) -> None:
        self._entries.append(entry)

    def get_entries(self, session_id: str | None = None) -> list[LogEntry]:
        if session_id:
            return [e for e in self._entries if e.session_id == session_id]
        return list(self._entries)
