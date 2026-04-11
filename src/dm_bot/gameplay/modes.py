from pydantic import BaseModel, Field

from dm_bot.orchestrator.session_store import SceneLifecycle, PlayerFocusScope


class GameModeState(BaseModel):
    """Runtime gameplay mode state consumed by the orchestration layer.

    Gameplay state tracks mode (dm/scene) and scene speakers separately
    from the canonical session_store models so that:
    1. Session lifecycle and scene lifecycle remain distinct concepts
    2. Player focus scope is tracked independently from scene lifecycle
    """

    mode: str = "dm"
    scene_speakers: list[str] = Field(default_factory=list)

    # Lifecycle and focus alignment with session_store models (v1.0 Phase 1)
    # These fields provide gameplay-specific view of scene state
    scene_lifecycle: str = SceneLifecycle.COLLECTING.value
    player_focus: str = PlayerFocusScope.SINGLE.value

    def enter_scene(self, *, speakers: list[str]) -> None:
        self.mode = "scene"
        self.scene_speakers = speakers

    def enter_dm(self) -> None:
        self.mode = "dm"
        self.scene_speakers = []

    def sync_from_session(
        self, *, scene_lifecycle: SceneLifecycle, player_focus: PlayerFocusScope
    ) -> None:
        """Sync scene lifecycle and focus from canonical session state.

        Called by the orchestration layer when session state changes
        so gameplay runtime reflects the canonical models.
        """
        self.scene_lifecycle = scene_lifecycle.value
        self.player_focus = player_focus.value

    def is_scene_collecting(self) -> bool:
        """Check if scene is in COLLECTING state."""
        return self.scene_lifecycle == SceneLifecycle.COLLECTING.value

    def is_scene_locked(self) -> bool:
        """Check if scene is in LOCKED state (no new submissions accepted)."""
        return self.scene_lifecycle == SceneLifecycle.LOCKED.value

    def is_shared_focus(self) -> bool:
        """Check if scene uses shared focus (multiple players act together)."""
        return self.player_focus == PlayerFocusScope.SHARED.value
