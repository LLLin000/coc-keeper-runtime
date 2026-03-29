from enum import Enum
from pydantic import BaseModel, Field

from dm_bot.orchestrator.session_store import CampaignSession, SessionPhase
from dm_bot.coc.panels import InvestigatorPanel
from dm_bot.router.intent_handler import IntentHandlingResult


class CampaignVisibility(BaseModel):
    campaign_id: str
    channel_id: str
    guild_id: str
    owner_id: str


class AdventureVisibility(BaseModel):
    # D-12: Expose current adventure reference (not currently deep in session_store, but placeholder or ID)
    adventure_id: str | None = None
    scene_id: str | None = None


class SessionVisibility(BaseModel):
    phase: SessionPhase
    ready_count: int
    total_members: int
    admin_started: bool


class WaitingReasonCode(str, Enum):
    NONE = "none"
    WAITING_FOR_READY = "waiting_for_ready"
    WAITING_FOR_ADMIN_START = "waiting_for_admin_start"
    WAITING_FOR_PLAYER_ACTIONS = "waiting_for_player_actions"
    RESOLVING_SCENE = "resolving_scene"
    IN_COMBAT = "in_combat"
    ONBOARDING_IN_PROGRESS = "onboarding_in_progress"
    PAUSED = "paused"


class WaitingVisibility(BaseModel):
    reason_code: WaitingReasonCode
    message: str
    metadata: dict[str, object] = Field(default_factory=dict)


class PlayerSnapshot(BaseModel):
    user_id: str
    name: str
    role: str
    occupation: str
    hp: int
    san: int
    mp: int
    luck: int
    is_ready: bool
    has_submitted_action: bool
    onboarding_complete: bool


class PlayerVisibility(BaseModel):
    players: list[PlayerSnapshot] = Field(default_factory=list)


class RoutingOutcome(str, Enum):
    PROCESSED = "processed"
    BUFFERED = "buffered"
    IGNORED = "ignored"
    DEFERRED = "deferred"
    UNKNOWN = "unknown"


class RoutingVisibility(BaseModel):
    outcome: RoutingOutcome
    explanation: str | None = None


class VisibilitySnapshot(BaseModel):
    campaign: CampaignVisibility
    adventure: AdventureVisibility
    session: SessionVisibility
    waiting: WaitingVisibility
    players: PlayerVisibility
    routing: RoutingVisibility | None = None


def _compute_waiting_state(session: CampaignSession) -> WaitingVisibility:
    if session.session_phase == SessionPhase.ONBOARDING:
        pending = [uid for uid in session.member_ids if not session.is_onboarding_complete(uid)]
        return WaitingVisibility(
            reason_code=WaitingReasonCode.ONBOARDING_IN_PROGRESS,
            message="Waiting for players to complete onboarding.",
            metadata={"pending_user_ids": pending}
        )
    elif session.session_phase == SessionPhase.AWAITING_READY:
        pending = [uid for uid in session.member_ids if not session.player_ready.get(uid)]
        return WaitingVisibility(
            reason_code=WaitingReasonCode.WAITING_FOR_READY,
            message="Waiting for players to ready up.",
            metadata={"pending_user_ids": pending}
        )
    elif session.session_phase == SessionPhase.AWAITING_ADMIN_START:
        return WaitingVisibility(
            reason_code=WaitingReasonCode.WAITING_FOR_ADMIN_START,
            message="Waiting for admin to start the session.",
            metadata={"admin_id": session.owner_id}
        )
    elif session.session_phase == SessionPhase.SCENE_ROUND_OPEN:
        pending = session.get_pending_members()
        return WaitingVisibility(
            reason_code=WaitingReasonCode.WAITING_FOR_PLAYER_ACTIONS,
            message="Waiting for player action declarations.",
            metadata={"pending_user_ids": pending}
        )
    elif session.session_phase == SessionPhase.SCENE_ROUND_RESOLVING:
        return WaitingVisibility(
            reason_code=WaitingReasonCode.RESOLVING_SCENE,
            message="Keeper is resolving the scene round.",
            metadata={"submitted_user_ids": list(session.action_submitters)}
        )
    elif session.session_phase == SessionPhase.COMBAT:
        return WaitingVisibility(
            reason_code=WaitingReasonCode.IN_COMBAT,
            message="Combat in progress.",
            metadata={}
        )
    elif session.session_phase == SessionPhase.PAUSED:
        return WaitingVisibility(
            reason_code=WaitingReasonCode.PAUSED,
            message="Session is paused.",
            metadata={}
        )
    
    return WaitingVisibility(
        reason_code=WaitingReasonCode.NONE,
        message="Session is open.",
        metadata={}
    )


def build_visibility_snapshot(
    session: CampaignSession,
    panels: dict[str, InvestigatorPanel],
    intent_result: IntentHandlingResult | None = None
) -> VisibilitySnapshot:
    """Build a canonical visibility snapshot from runtime state."""
    campaign_vis = CampaignVisibility(
        campaign_id=session.campaign_id,
        channel_id=session.channel_id,
        guild_id=session.guild_id,
        owner_id=session.owner_id,
    )
    
    # Adventure tracking might be added later, currently placeholder
    adventure_vis = AdventureVisibility()
    
    session_vis = SessionVisibility(
        phase=session.session_phase,
        ready_count=sum(1 for r in session.player_ready.values() if r),
        total_members=len(session.member_ids),
        admin_started=session.admin_started,
    )
    
    waiting_vis = _compute_waiting_state(session)
    
    player_snapshots = []
    for user_id in session.member_ids:
        panel = panels.get(user_id)
        if panel:
            snap = PlayerSnapshot(
                user_id=user_id,
                name=panel.name,
                role=panel.role,
                occupation=panel.occupation,
                hp=panel.hp,
                san=panel.san,
                mp=panel.mp,
                luck=panel.luck,
                is_ready=session.player_ready.get(user_id, False),
                has_submitted_action=session.has_submitted(user_id),
                onboarding_complete=session.is_onboarding_complete(user_id)
            )
            player_snapshots.append(snap)
            
    players_vis = PlayerVisibility(players=player_snapshots)
    
    routing_vis = None
    if intent_result:
        outcome = RoutingOutcome.UNKNOWN
        if intent_result.should_buffer:
            outcome = RoutingOutcome.BUFFERED
        elif intent_result.should_process:
            outcome = RoutingOutcome.PROCESSED
        elif intent_result.deferred_content:
            outcome = RoutingOutcome.DEFERRED
        else:
            outcome = RoutingOutcome.IGNORED
            
        routing_vis = RoutingVisibility(
            outcome=outcome,
            explanation=intent_result.feedback_message
        )
        
    return VisibilitySnapshot(
        campaign=campaign_vis,
        adventure=adventure_vis,
        session=session_vis,
        waiting=waiting_vis,
        players=players_vis,
        routing=routing_vis,
    )
