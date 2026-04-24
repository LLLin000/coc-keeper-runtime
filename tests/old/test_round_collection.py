import pytest
from dm_bot.orchestrator.session_store import (
    CampaignSession,
    SessionStore,
    SessionPhase,
)


class TestRoundCollectionState:
    def test_pending_actions_initial_empty(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
        )
        assert session.pending_actions == {}
        assert session.action_submitters == set()

    def test_set_player_action(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids={"player1", "player2"},
        )
        session.set_player_action("player1", "我调查书架")
        assert session.pending_actions["player1"] == "我调查书架"
        assert "player1" in session.action_submitters
        assert "player2" not in session.action_submitters

    def test_set_player_action_ignores_empty(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids={"player1"},
        )
        session.set_player_action("player1", "")
        session.set_player_action("player1", "   ")
        assert "player1" not in session.action_submitters

    def test_duplicate_submission_replaces_previous(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids={"player1"},
        )
        session.set_player_action("player1", "第一次行动")
        assert session.pending_actions["player1"] == "第一次行动"
        session.set_player_action("player1", "第二次行动")
        assert session.pending_actions["player1"] == "第二次行动"
        assert session.action_submitters == {"player1"}

    def test_clear_player_action(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids={"player1", "player2"},
        )
        session.set_player_action("player1", "行动1")
        session.set_player_action("player2", "行动2")
        session.clear_player_action("player1")
        assert "player1" not in session.pending_actions
        assert "player1" not in session.action_submitters
        assert session.pending_actions["player2"] == "行动2"
        assert "player2" in session.action_submitters

    def test_clear_all_actions(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids={"player1", "player2"},
        )
        session.set_player_action("player1", "行动1")
        session.set_player_action("player2", "行动2")
        session.clear_all_actions()
        assert session.pending_actions == {}
        assert session.action_submitters == set()

    def test_has_submitted(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids={"player1", "player2"},
        )
        session.set_player_action("player1", "行动")
        assert session.has_submitted("player1") is True
        assert session.has_submitted("player2") is False

    def test_get_pending_members(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids={"player1", "player2", "player3"},
        )
        session.set_player_action("player1", "行动")
        pending = session.get_pending_members()
        assert "player2" in pending
        assert "player3" in pending
        assert "player1" not in pending

    def test_all_submitted(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids={"player1", "player2"},
        )
        assert session.all_submitted() is False
        session.set_player_action("player1", "行动1")
        assert session.all_submitted() is False
        session.set_player_action("player2", "行动2")
        assert session.all_submitted() is True

    def test_all_submitted_empty_members(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids=set(),
        )
        assert session.all_submitted() is True

    def test_get_submitter_names(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids={"player1", "player2"},
            active_characters={"player1": "张三", "player2": "李四"},
        )
        session.set_player_action("player1", "行动")
        names = session.get_submitter_names()
        assert "张三" in names
        assert "李四" not in names

    def test_get_pending_member_names(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids={"player1", "player2"},
            active_characters={"player1": "张三", "player2": "李四"},
        )
        session.set_player_action("player1", "行动")
        names = session.get_pending_member_names()
        assert "李四" in names
        assert "张三" not in names


class TestRoundCollectionPhaseTransitions:
    def test_scene_round_open_phase(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
        )
        session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
        assert session.session_phase == SessionPhase.SCENE_ROUND_OPEN

    def test_scene_round_resolving_phase(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
        )
        session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
        session.transition_to(SessionPhase.SCENE_ROUND_RESOLVING)
        assert session.session_phase == SessionPhase.SCENE_ROUND_RESOLVING

    def test_round_resolution_clears_actions(self):
        session = CampaignSession(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
            member_ids={"player1"},
        )
        session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
        session.set_player_action("player1", "行动")
        assert session.all_submitted() is True
        session.clear_all_actions()
        session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
        assert session.pending_actions == {}


class TestSessionStoreRoundCollection:
    def test_leave_campaign_clears_actions(self):
        store = SessionStore()
        store.bind_campaign(
            campaign_id="test-campaign",
            channel_id="test-channel",
            guild_id="test-guild",
            owner_id="owner",
        )
        store.join_campaign(channel_id="test-channel", user_id="player1")
        session = store.get_by_channel("test-channel")
        session.set_player_action("player1", "我的行动")
        assert "player1" in session.action_submitters
        store.leave_campaign(channel_id="test-channel", user_id="player1")
        assert "player1" not in session.action_submitters
        assert "player1" not in session.pending_actions
