from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class GovernanceEvent(BaseModel):
    """A single governance event in the audit trail."""

    timestamp: datetime = Field(default_factory=datetime.now)
    operation: str = Field(
        description="e.g., 'profile_activate', 'profile_archive', 'instance_retire'"
    )
    user_id: str = Field(description="Target user")
    profile_id: str | None = Field(default=None, description="Target profile")
    campaign_id: str | None = Field(default=None, description="Campaign context")
    operator_id: str = Field(
        description="Who performed the action (may differ from user_id for admin)"
    )
    before_state: dict | None = Field(
        default=None, description="State before operation"
    )
    after_state: dict | None = Field(default=None, description="State after operation")
    reason: str | None = Field(
        default=None, description="Reason/notes (required for admin actions)"
    )


class GovernanceEventLog:
    """Append-only audit trail for profile and instance lifecycle operations."""

    def __init__(self) -> None:
        self._events: list[GovernanceEvent] = []

    def append_event(self, event: GovernanceEvent) -> None:
        """Append a governance event (append-only)."""
        self._events.append(event)

    def get_events_for_user(self, user_id: str) -> list[GovernanceEvent]:
        """Filter events by target user."""
        return [e for e in self._events if e.user_id == user_id]

    def get_events_for_profile(self, profile_id: str) -> list[GovernanceEvent]:
        """Filter events by target profile."""
        return [e for e in self._events if e.profile_id == profile_id]

    def get_events_for_campaign(self, campaign_id: str) -> list[GovernanceEvent]:
        """Filter events by campaign."""
        return [e for e in self._events if e.campaign_id == campaign_id]

    def get_recent_events(
        self, campaign_id: str, limit: int = 20
    ) -> list[GovernanceEvent]:
        """Get recent events for a campaign (for /debug_status)."""
        events = self.get_events_for_campaign(campaign_id)
        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]

    def export_state(self) -> dict:
        """Export events for persistence."""
        return {"events": [e.model_dump(mode="json") for e in self._events]}

    def import_state(self, payload: dict) -> None:
        """Restore events from persistence."""
        self._events = [
            GovernanceEvent.model_validate(e) for e in payload.get("events", [])
        ]
