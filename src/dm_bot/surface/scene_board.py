"""Scene context and round state board."""

from typing import Any

from dm_bot.surface.board import Board


class SceneBoard(Board):
    """Renders current scene context, round state, and waiting reasons."""

    def render(self, state: dict[str, Any]) -> str:
        lines = [
            f"**Scene:** {state.get('scene_name', 'N/A')}",
            f"**Round:** {state.get('round_state', 'N/A')}",
            f"**Actions:** {state.get('action_count', 0)}",
        ]
        waiting = state.get("waiting_for")
        if waiting:
            lines.append(f"**Waiting:** {', '.join(waiting)}")
        return "\n".join(lines)
