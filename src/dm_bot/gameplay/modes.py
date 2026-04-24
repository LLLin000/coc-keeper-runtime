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

    # --- Cross-cut tracking (v1.0 Phase 2) ---
    # Signals for narrator to produce cutaway narration
    cross_cut_signal: bool = False
    cross_cut_from_scene: str | None = None
    cross_cut_to_scene: str | None = None

    # --- Batch collection and resolution state (v1.0 Phase 3 - RTR-03, RTR-04, RTR-05) ---
    # Pending blocker state from runtime (RTR-05)
    pending_blocker: dict = Field(default_factory=dict)  # Mirrors CampaignSession.pending_blocker
    # Current merge proposal if one exists (RTR-04)
    merge_proposal: dict | None = None  # Mirrors CampaignSession.merge_proposals[scene_id]
    # Batch submission count for quick visibility (RTR-03)
    batch_submission_count: int = 0
    # Resolved actions in current round (RTR-03, RTR-04)
    resolved_actions: list[dict] = Field(default_factory=list)

    def enter_scene(self, *, speakers: list[str]) -> None:
        self.mode = "scene"
        self.scene_speakers = speakers

    def enter_dm(self) -> None:
        self.mode = "dm"
        self.scene_speakers = []

    def sync_from_session(
        self,
        *,
        scene_lifecycle: SceneLifecycle,
        player_focus: PlayerFocusScope,
        pending_blocker: dict | None = None,
        merge_proposal: dict | None = None,
        batch_submission_count: int = 0,
        resolved_actions: list | None = None,
    ) -> None:
        """Sync scene lifecycle and focus from canonical session state.

        Also syncs batch resolution state for narrator consumption.
        """
        self.scene_lifecycle = scene_lifecycle.value
        self.player_focus = player_focus.value
        self.pending_blocker = pending_blocker or {}
        self.merge_proposal = merge_proposal
        self.batch_submission_count = batch_submission_count
        self.resolved_actions = resolved_actions or []

    def is_scene_collecting(self) -> bool:
        """Check if scene is in COLLECTING state."""
        return self.scene_lifecycle == SceneLifecycle.COLLECTING.value

    def is_scene_locked(self) -> bool:
        """Check if scene is in LOCKED state (no new submissions accepted)."""
        return self.scene_lifecycle == SceneLifecycle.LOCKED.value

    def is_shared_focus(self) -> bool:
        """Check if scene uses shared focus (multiple players act together)."""
        return self.player_focus == PlayerFocusScope.SHARED.value
