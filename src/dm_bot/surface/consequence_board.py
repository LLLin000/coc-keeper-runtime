"""Consequence output board with visibility filtering."""

from typing import Any

from dm_bot.surface.board import Board


class ConsequenceBoard(Board):
    """Renders published events filtered by visibility path."""

    def render(self, state: dict[str, Any], **kwargs: Any) -> str:
        events = state.get("events", [])
        if not events:
            return "**Recent Events:** No events."

        visibility_filter = kwargs.get("visibility")
        if visibility_filter:
            events = [e for e in events if e.get("visibility") == visibility_filter]

        if not events:
            return f"**Recent Events:** (none with {visibility_filter} visibility)"

        lines = [f"**Recent Events ({len(events)}):**"]
        for e in events:
            ev_type = e.get("event_type", "?")
            summary = e.get("summary", "")
            vis = e.get("visibility", "table_visible")
            lines.append(f"- [{vis}] {summary} ({ev_type})")
        return "\n".join(lines)
