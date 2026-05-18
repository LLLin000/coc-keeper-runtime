"""Scene context and round state board."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, FieldEntry
from dm_bot.surface.discord_formatter import DiscordFormatter


class SceneBoard(Board):
    """Renders focused scene context and round state."""

    def render(self, state: dict) -> str:
        fields = [
            FieldEntry(name="Scene", value=state.get("scene_name", "?")),
            FieldEntry(name="Round State", value=state.get("round_state", "?")),
            FieldEntry(name="Actions", value=str(state.get("action_count", 0))),
        ]
        waiting = state.get("waiting_for")
        if waiting:
            fields.append(FieldEntry(name="Waiting", value=", ".join(waiting) if isinstance(waiting, list) else str(waiting)))
        payload = ViewPayload(
            title=state.get("scene_desc", "Scene")[:80],
            fields=fields,
        )
        return DiscordFormatter.format(payload)
