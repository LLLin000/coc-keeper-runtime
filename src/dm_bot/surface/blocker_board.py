from typing import Any

from dm_bot.surface.board import Board


class BlockerBoard(Board):
    def render(self, state: dict[str, Any]) -> str:
        blockers = state.get("blockers", [])
        if not blockers:
            return "**Blockers:** No unresolved blockers."
        lines = [f"**Blockers ({len(blockers)}):**"]
        for b in blockers:
            blocker_id = b.get("blocker_id", "?")
            reason = b.get("reason", "?")
            scene_id = b.get("scene_id", "")
            scene_info = f" (scene: {scene_id})" if scene_id else ""
            lines.append(f"- `{blocker_id}`{scene_info}: {reason}")
        return "\n".join(lines)
