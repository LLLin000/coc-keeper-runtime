"""Clue board — presents runtime-approved shared knowledge."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, ViewSection


class ClueBoard(Board):
    """Renders visible clues filtered by runtime visibility rules."""

    def render(self, state: dict) -> str:
        clues: list[dict] = state.get("clues", [])
        visible_ids: list[str] = state.get("visible_clue_ids", [])
        known_ids: list[str] = state.get("known_clue_ids", [])
        player_id: str = state.get("player_id", "")

        visible = [c for c in clues if c.get("clue_id") in visible_ids]
        if not visible:
            return "No visible clues."

        sections: list[ViewSection] = []
        for clue in visible:
            cid = clue.get("clue_id", "")
            label = clue.get("title", "Unknown")
            if cid in known_ids:
                label = f"{label} [Known]"
            sections.append(ViewSection(
                heading=label,
                body=clue.get("description", ""),
            ))

        payload = ViewPayload(
            title=f"Clues — {player_id}" if player_id else "Clues",
            sections=sections,
            footer=f"{len(visible)} clue(s) visible" if not player_id else "",
        )
        from dm_bot.surface.discord_formatter import DiscordFormatter
        return DiscordFormatter.format(payload)
