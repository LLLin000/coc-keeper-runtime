"""Session identity board."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, FieldEntry
from dm_bot.surface.discord_formatter import DiscordFormatter


class SessionBoard(Board):
    """Renders session identity and participant list."""

    def render(self, state: dict) -> str:
        payload = ViewPayload(
            title=f"Session: {state.get('module_name', 'Unknown')}",
            fields=[
                FieldEntry(name="ID", value=state.get("session_id", "")),
                FieldEntry(name="Phase", value=state.get("phase", "idle")),
                FieldEntry(name="Participants", value=", ".join(state.get("participants", [])) or "None"),
            ],
        )
        return DiscordFormatter.format(payload)
