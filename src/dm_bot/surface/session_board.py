"""Session identity and phase board."""

from typing import Any

from dm_bot.surface.board import Board


class SessionBoard(Board):
    """Renders session identity, phase, and participant info."""

    def render(self, state: dict[str, Any]) -> str:
        lines = [
            f"**Session:** {state.get('session_id', 'N/A')}",
            f"**Module:** {state.get('module_name', 'N/A')}",
            f"**Phase:** {state.get('phase', 'N/A')}",
        ]
        participants = state.get("participants", [])
        if participants:
            lines.append(f"**Players:** {', '.join(participants)}")
        else:
            lines.append("**Players:** (none)")
        return "\n".join(lines)
