import pytest
from datetime import datetime
from dm_bot.orchestrator.session_store import CampaignSession, SessionPhase
from dm_bot.coc.panels import InvestigatorPanel
from dm_bot.orchestrator.visibility import (
    VisibilitySnapshot,
    CampaignVisibility,
    AdventureVisibility,
    SessionVisibility,
    WaitingVisibility,
    PlayerVisibility,
    PlayerSnapshot,
    WaitingReasonCode,
    RoutingOutcome,
    RoutingHistoryEntry,
)
from dm_bot.orchestrator.kp_ops_renderer import KPOpsRenderer
from dm_bot.orchestrator.routing_history import RoutingHistoryStore


def make_test_snapshot(
    phase=SessionPhase.SCENE_ROUND_OPEN,
    round_number=None,
    ready_count=3,
    total_members=5,
    admin_started=True,
    pending_user_ids=None,
    adventure_id=None,
    scene_id=None,
    routing_history=None,
):
    session = SessionVisibility(
        phase=phase,
        ready_count=ready_count,
        total_members=total_members,
        admin_started=admin_started,
        round_number=round_number,
    )
    waiting = WaitingVisibility(
        reason_code=WaitingReasonCode.WAITING_FOR_PLAYER_ACTIONS,
        message="Waiting for player action declarations.",
        metadata={"pending_user_ids": pending_user_ids or []},
    )
    campaign = CampaignVisibility(
        campaign_id="test_campaign",
        channel_id="test_channel",
        guild_id="test_guild",
        owner_id="admin1",
    )
    adventure = AdventureVisibility(
        adventure_id=adventure_id,
        scene_id=scene_id,
    )
    return VisibilitySnapshot(
        campaign=campaign,
        adventure=adventure,
        session=session,
        waiting=waiting,
        players=PlayerVisibility(players=[]),
        routing_history=routing_history or [],
    )


class TestOPS01Overview:
    """OPS-01: Session Phase, Round State, Blockers, Runtime State"""

    def test_ops_overview_shows_phase_and_round(self):
        """Overview should show current phase with round number."""
        snapshot = make_test_snapshot(
            phase=SessionPhase.SCENE_ROUND_OPEN, round_number=3
        )
        renderer = KPOpsRenderer()
        output = renderer.render_overview(snapshot)

        assert "scene_round_open" in output
        assert "Round 3" in output

    def test_ops_overview_shows_no_round_when_none(self):
        """Overview should not show round when None."""
        snapshot = make_test_snapshot(phase=SessionPhase.LOBBY, round_number=None)
        renderer = KPOpsRenderer()
        output = renderer.render_overview(snapshot)

        assert "SCENE_ROUND_OPEN" not in output or "Round" not in output

    def test_ops_overview_shows_blockers(self):
        """Overview shows what's blocking progress."""
        snapshot = make_test_snapshot(
            phase=SessionPhase.SCENE_ROUND_OPEN,
            pending_user_ids=["player1", "player2"],
        )
        renderer = KPOpsRenderer()
        output = renderer.render_overview(snapshot)

        assert "Pending" in output
        assert "player1" in output or "player2" in output

    def test_ops_overview_shows_runtime_state(self):
        """Overview shows adventure, scene, admin started."""
        snapshot = make_test_snapshot(
            phase=SessionPhase.SCENE_ROUND_OPEN,
            admin_started=True,
            adventure_id="mad_mansion",
            scene_id="entrance_hall",
        )
        renderer = KPOpsRenderer()
        output = renderer.render_overview(snapshot)

        assert "mad_mansion" in output
        assert "entrance_hall" in output
        assert "Admin Started: Yes" in output

    def test_ops_overview_high_density(self):
        """D-03: Ops surface has higher information density."""
        snapshot = make_test_snapshot(
            phase=SessionPhase.SCENE_ROUND_OPEN,
            round_number=2,
            ready_count=4,
            total_members=5,
            admin_started=True,
            pending_user_ids=["player1"],
            adventure_id="fuzhe",
            scene_id="intro",
        )
        renderer = KPOpsRenderer(active_characters={"player1": "Dr. Smith"})
        output = renderer.render_overview(snapshot)

        lines = output.split("\n")
        assert len(lines) <= 6
        assert "Round 2" in output
        assert "Ready: 4/5" in output
        assert "fuzhe" in output


class TestOPS02Detailed:
    """OPS-02: Per-Player Participation State"""

    def test_ops_detailed_shows_player_ready_status(self):
        """Detailed shows each player's ready status."""
        players = [
            PlayerSnapshot(
                user_id="user1",
                name="Alice",
                role="investigator",
                occupation="Detective",
                hp=12,
                san=50,
                mp=10,
                luck=40,
                is_ready=True,
                has_submitted_action=True,
                onboarding_complete=True,
            ),
            PlayerSnapshot(
                user_id="user2",
                name="Bob",
                role="investigator",
                occupation="Journalist",
                hp=10,
                san=55,
                mp=8,
                luck=45,
                is_ready=False,
                has_submitted_action=False,
                onboarding_complete=True,
            ),
        ]
        snapshot = make_test_snapshot()
        snapshot.players = PlayerVisibility(players=players)

        renderer = KPOpsRenderer(active_characters={"user1": "Alice", "user2": "Bob"})
        output = renderer.render_detailed(snapshot)

        assert "Alice" in output
        assert "Bob" in output
        assert "✓ Ready" in output
        assert "✗ Not Ready" in output

    def test_ops_detailed_shows_player_action_status(self):
        """Detailed shows submitted/pending action status."""
        players = [
            PlayerSnapshot(
                user_id="user1",
                name="Alice",
                role="investigator",
                occupation="Detective",
                hp=12,
                san=50,
                mp=10,
                luck=40,
                is_ready=True,
                has_submitted_action=True,
                onboarding_complete=True,
            ),
            PlayerSnapshot(
                user_id="user2",
                name="Bob",
                role="investigator",
                occupation="Journalist",
                hp=10,
                san=55,
                mp=8,
                luck=45,
                is_ready=True,
                has_submitted_action=False,
                onboarding_complete=True,
            ),
        ]
        snapshot = make_test_snapshot()
        snapshot.players = PlayerVisibility(players=players)

        renderer = KPOpsRenderer()
        output = renderer.render_detailed(snapshot)

        assert "✓ Action Submitted" in output
        assert "⏳ Pending Action" in output

    def test_ops_detailed_shows_onboarding_status(self):
        """Detailed shows onboarding completion."""
        players = [
            PlayerSnapshot(
                user_id="user1",
                name="Alice",
                role="investigator",
                occupation="Detective",
                hp=12,
                san=50,
                mp=10,
                luck=40,
                is_ready=True,
                has_submitted_action=True,
                onboarding_complete=True,
            ),
            PlayerSnapshot(
                user_id="user2",
                name="Bob",
                role="investigator",
                occupation="Journalist",
                hp=10,
                san=55,
                mp=8,
                luck=45,
                is_ready=True,
                has_submitted_action=True,
                onboarding_complete=False,
            ),
        ]
        snapshot = make_test_snapshot()
        snapshot.players = PlayerVisibility(players=players)

        renderer = KPOpsRenderer()
        output = renderer.render_detailed(snapshot)

        assert "✓ Onboarded" in output
        assert "✗ Not Onboarded" in output


class TestOPS03RoutingHistory:
    """OPS-03: Routing Outcomes"""

    def test_ops_routing_history_shows_last_10(self):
        """Routing history limited to 10 entries."""
        history = []
        for i in range(15):
            history.append(
                RoutingHistoryEntry(
                    timestamp=datetime.now(),
                    user_id=f"user{i}",
                    intent="ACTION",
                    outcome=RoutingOutcome.PROCESSED,
                    explanation=f"Processed {i}",
                )
            )
        snapshot = make_test_snapshot(routing_history=history)

        renderer = KPOpsRenderer()
        output = renderer.render_routing_history(snapshot)

        lines = output.split("\n")
        routing_lines = [l for l in lines if "🕐" in l]
        assert len(routing_lines) == 10

    def test_ops_routing_history_shows_all_fields(self):
        """Each entry has timestamp, user, intent, outcome, explanation."""
        history = [
            RoutingHistoryEntry(
                timestamp=datetime(2024, 1, 1, 14, 32),
                user_id="user1",
                intent="OOC",
                outcome=RoutingOutcome.BUFFERED,
                explanation="OOC在行动收集阶段被缓存",
            )
        ]
        snapshot = make_test_snapshot(routing_history=history)

        renderer = KPOpsRenderer(active_characters={"user1": "Dr. Smith"})
        output = renderer.render_routing_history(snapshot)

        assert "14:32" in output
        assert "user1" in output or "Dr. Smith" in output
        assert "OOC" in output
        assert "buffered" in output
        assert "OOC在行动收集阶段被缓存" in output


class TestRoutingHistoryStore:
    """Test RoutingHistoryStore class"""

    def test_routing_history_store_limits_entries(self):
        """RoutingHistoryStore should limit to max entries (default 10)."""
        store = RoutingHistoryStore(max_entries=10)
        for i in range(15):
            store.add_entry(
                user_id=f"user{i}",
                intent="TEST",
                outcome=RoutingOutcome.PROCESSED,
            )
        assert len(store.get_recent()) == 10

    def test_routing_history_store_get_recent(self):
        """get_recent returns entries in order."""
        store = RoutingHistoryStore(max_entries=5)
        for i in range(3):
            store.add_entry(
                user_id=f"user{i}",
                intent="TEST",
                outcome=RoutingOutcome.PROCESSED,
            )
        recent = store.get_recent()
        assert len(recent) == 3

    def test_routing_history_store_clear(self):
        """clear removes all entries."""
        store = RoutingHistoryStore()
        store.add_entry("user1", "TEST", RoutingOutcome.PROCESSED)
        store.clear()
        assert len(store) == 0


class TestSessionVisibility:
    """Test SessionVisibility round_number field"""

    def test_session_visibility_includes_round_number(self):
        """SessionVisibility should include optional round_number field."""
        from dm_bot.orchestrator.visibility import SessionVisibility

        vis = SessionVisibility(
            phase=SessionPhase.SCENE_ROUND_OPEN,
            ready_count=3,
            total_members=5,
            admin_started=True,
            round_number=3,
        )
        assert vis.round_number == 3

    def test_session_visibility_round_number_defaults_none(self):
        """round_number defaults to None."""
        from dm_bot.orchestrator.visibility import SessionVisibility

        vis = SessionVisibility(
            phase=SessionPhase.LOBBY,
            ready_count=0,
            total_members=1,
            admin_started=False,
        )
        assert vis.round_number is None
