"""
Visibility contract audit (E71-01 Task 2):
- Already covered: ONBOARDING + WaitingReasonCode.ONBOARDING_IN_PROGRESS + RoutingOutcome.BUFFERED;
                    SCENE_ROUND_OPEN + WaitingReasonCode.WAITING_FOR_PLAYER_ACTIONS + RoutingOutcome.PROCESSED
- Gap 1: AWAITING_READY phase + WaitingReasonCode.WAITING_FOR_READY + ready_count tracking
- Gap 2: RoutingOutcome.DEFERRED and IGNORED never exercised (only BUFFERED/PROCESSED tested)
- Gap 3: routing_history field in VisibilitySnapshot never populated or asserted
"""
import pytest
from dm_bot.orchestrator.session_store import CampaignSession, SessionPhase
from dm_bot.coc.panels import InvestigatorPanel
from dm_bot.router.intent_handler import IntentHandlingResult
from dm_bot.orchestrator.visibility import (
    build_visibility_snapshot,
    WaitingReasonCode,
    RoutingOutcome
)

def test_build_visibility_snapshot_onboarding():
    session = CampaignSession(
        campaign_id="camp1",
        channel_id="chan1",
        guild_id="guild1",
        owner_id="admin1",
        member_ids={"admin1", "player1"}
    )
    session.transition_to(SessionPhase.ONBOARDING)
    session.set_onboarding_complete("admin1", True)
    
    panel_player1 = InvestigatorPanel(
        user_id="player1",
        name="Alice",
        role="investigator",
        occupation="Detective",
        hp=12,
        san=60,
        mp=10,
        luck=55
    )
    
    intent_res = IntentHandlingResult(
        should_process=False,
        should_buffer=True,
        feedback_message="Buffered during onboarding"
    )
    
    snapshot = build_visibility_snapshot(
        session=session,
        panels={"player1": panel_player1},
        intent_result=intent_res
    )
    
    assert snapshot.campaign.campaign_id == "camp1"
    assert snapshot.session.phase == SessionPhase.ONBOARDING
    
    assert snapshot.waiting.reason_code == WaitingReasonCode.ONBOARDING_IN_PROGRESS
    assert snapshot.waiting.metadata["pending_user_ids"] == ["player1"]
    
    assert len(snapshot.players.players) == 1
    p1_snap = snapshot.players.players[0]
    assert p1_snap.user_id == "player1"
    assert p1_snap.name == "Alice"
    assert p1_snap.hp == 12
    assert p1_snap.san == 60
    assert p1_snap.onboarding_complete is False
    
    assert snapshot.routing is not None
    assert snapshot.routing.outcome == RoutingOutcome.BUFFERED
    assert snapshot.routing.explanation == "Buffered during onboarding"

def test_build_visibility_snapshot_scene_round():
    session = CampaignSession(
        campaign_id="camp1",
        channel_id="chan1",
        guild_id="guild1",
        owner_id="admin1",
        member_ids={"player1", "player2"}
    )
    session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    session.set_player_action("player1", "I search the room")
    
    panel_player1 = InvestigatorPanel(
        user_id="player1",
        name="Alice",
    )
    panel_player2 = InvestigatorPanel(
        user_id="player2",
        name="Bob",
    )
    
    intent_res = IntentHandlingResult(
        should_process=True,
        should_buffer=False,
        feedback_message="Action recorded"
    )
    
    snapshot = build_visibility_snapshot(
        session=session,
        panels={"player1": panel_player1, "player2": panel_player2},
        intent_result=intent_res
    )
    
    assert snapshot.waiting.reason_code == WaitingReasonCode.WAITING_FOR_PLAYER_ACTIONS
    assert snapshot.waiting.metadata["pending_user_ids"] == ["player2"]
    
    players_dict = {p.user_id: p for p in snapshot.players.players}
    assert players_dict["player1"].has_submitted_action is True
    assert players_dict["player2"].has_submitted_action is False
    
    assert snapshot.routing is not None
    assert snapshot.routing.outcome == RoutingOutcome.PROCESSED
    assert snapshot.routing.explanation == "Action recorded"
