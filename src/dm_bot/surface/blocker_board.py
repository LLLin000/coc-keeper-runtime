"""Blocker summary board — KP-readable checkpoint list."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, ViewSection
from dm_bot.surface.discord_formatter import DiscordFormatter


class BlockerBoard(Board):
    """Renders unresolved blocker checkpoints."""

    def render(self, state: dict) -> str:
        blockers: list[dict] = state.get("blockers", [])
        if not blockers:
            return "No unresolved blockers."

        sections = [
            ViewSection(heading=b.get("reason", "?"), body=f"Scene: {b.get('scene_id', '?')} | ID: {b.get('blocker_id', '?')}")
            for b in blockers
        ]
        payload = ViewPayload(title=f"Blockers ({len(blockers)})", sections=sections)
        return DiscordFormatter.format(payload)
