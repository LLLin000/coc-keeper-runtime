"""Consequence output board — visibility-filtered event display."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, ViewSection
from dm_bot.surface.discord_formatter import DiscordFormatter


class ConsequenceBoard(Board):
    """Renders events filtered by visibility path."""

    def render(self, state: dict, visibility: str | None = None) -> str:
        events: list[dict] = state.get("events", [])
        filtered = events
        if visibility:
            filtered = [e for e in events if e.get("visibility") == visibility]
        if not filtered:
            return "No events."

        sections = [
            ViewSection(heading=e.get("summary", e.get("event_type", "?")), body=f"Type: {e.get('event_type', '?')} | Visibility: {e.get('visibility', '?')}")
            for e in filtered
        ]
        label = visibility.replace("_", " ").title() if visibility else "All"
        payload = ViewPayload(title=f"{label} Events ({len(filtered)})", sections=sections)
        return DiscordFormatter.format(payload)
