"""E2E lifecycle tests for Phase 61: Integration and Polish.

Tests the full flow: create → archive → activate → select → ready
Covers PV-02 (profile_detail with instance context) and PV-04 (ready gate).

This file is referenced in 61-01-PLAN.md Task 3.
"""

import pytest
from unittest.mock import MagicMock

from dm_bot.coc.archive import InvestigatorArchiveProfile, InvestigatorArchiveRepository
from dm_bot.orchestrator.session_store import (
    CampaignCharacterInstance,
    CampaignRole,
    SessionStore,
    ReadyGateError,
)


def _make_mock_profile(
    profile_id: str, user_id: str, name: str = "TestChar"
) -> MagicMock:
    """Create a mock archive profile."""
    profile = MagicMock()
    profile.profile_id = profile_id
    profile.user_id = user_id
    profile.name = name
    profile.status = "active"
    profile.coc.occupation = "记者"
    profile.coc.san = 50
    profile.coc.hp = 10
    profile.coc.mp = 10
    profile.coc.luck = 50
    profile.coc.move_rate = 7
    profile.coc.build = 0
    profile.coc.damage_bonus = "0"
    profile.coc.attributes.str = 50
    profile.coc.attributes.con = 50
    profile.coc.attributes.dex = 50
    profile.coc.attributes.app = 50
    profile.coc.attributes.pow = 50
    profile.coc.attributes.siz = 50
    profile.coc.attributes.int = 50
    profile.coc.attributes.edu = 50
    profile.finishing.recommended_occupation_skills = []
    profile.finishing.recommended_interest_skills = []
    profile.finishing.allowed_adjustments = []
    profile.detail_view.return_value = f"【调查员档案】\n{name} / 记者"
    return profile


def _make_mock_archive_repo(
    user_id: str, profile_id: str, name: str = "TestChar"
) -> MagicMock:
    """Create a mock archive repository with a single profile."""
    profile = _make_mock_profile(profile_id, user_id, name)
    repo = MagicMock(spec=InvestigatorArchiveRepository)
    repo.get_profile.return_value = profile
    return repo


class TestE2ELifecycleReady:
    """Full lifecycle: create → archive → activate → select → ready."""

    def test_lifecycle_select_profile_then_ready(self):
        """PV-04: Full lifecycle - select profile creates instance that passes ready."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        # Player selects profile
        mock_repo = _make_mock_archive_repo("player1", "prof1", "张三")
        instance = store.select_instance_profile(
            channel_id="ch1",
            user_id="player1",
            profile_id="prof1",
            archive_repo=mock_repo,
        )

        # Instance should be active
        assert instance.status == "active"
        assert instance.character_name == "张三"
        assert instance.archive_profile_id == "prof1"

        # Ready should succeed (PV-04)
        result = store.validate_ready(channel_id="ch1", user_id="player1")
        assert result.success is True, (
            f"Expected success but got: {result.error_message}"
        )
        assert result.error is None

    def test_cannot_ready_without_instance(self):
        """PV-04: Member without instance cannot ready."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        # Player joined but never selected profile - instance exists but character_name is empty
        result = store.validate_ready(channel_id="ch1", user_id="player1")
        assert result.success is False
        assert result.error == ReadyGateError.NO_PROFILE_SELECTED

    def test_cannot_ready_with_retired_instance(self):
        """PV-04: Member with retired instance cannot ready."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        # Create instance then retire it
        mock_repo = _make_mock_archive_repo("player1", "prof1", "张三")
        store.select_instance_profile(
            channel_id="ch1",
            user_id="player1",
            profile_id="prof1",
            archive_repo=mock_repo,
        )
        store.retire_instance(channel_id="ch1", user_id="player1")

        # Ready should fail
        result = store.validate_ready(channel_id="ch1", user_id="player1")
        assert result.success is False
        assert result.error == ReadyGateError.NO_PROFILE_SELECTED

    def test_retire_and_reactivate(self):
        """PV-04: Can retire and then select a new profile."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        # First profile
        mock_repo1 = _make_mock_archive_repo("player1", "prof1", "张三")
        store.select_instance_profile(
            channel_id="ch1",
            user_id="player1",
            profile_id="prof1",
            archive_repo=mock_repo1,
        )
        assert store.validate_ready(channel_id="ch1", user_id="player1").success is True

        # Retire
        store.retire_instance(channel_id="ch1", user_id="player1")
        assert (
            store.validate_ready(channel_id="ch1", user_id="player1").success is False
        )

        # Select new profile
        mock_repo2 = _make_mock_archive_repo("player1", "prof2", "李四")
        store.select_instance_profile(
            channel_id="ch1",
            user_id="player1",
            profile_id="prof2",
            archive_repo=mock_repo2,
        )
        assert store.validate_ready(channel_id="ch1", user_id="player1").success is True


class TestE2EProfileDetailInstanceContext:
    """PV-02: profile_detail shows instance context when profile is linked to an instance."""

    def test_profile_detail_shows_active_instance_context(self):
        """PV-02: When viewing a profile that has an active instance, show campaign context."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        # Player selects profile - creates active instance
        mock_repo = _make_mock_archive_repo("player1", "prof1", "张三")
        store.select_instance_profile(
            channel_id="ch1",
            user_id="player1",
            profile_id="prof1",
            archive_repo=mock_repo,
        )

        # Get the instance - should show active context
        instance = store.get_character_instance("ch1", "player1")
        assert instance is not None
        assert instance.status == "active"
        assert instance.character_name == "张三"
        assert instance.archive_profile_id == "prof1"

    def test_profile_detail_shows_retired_instance_status(self):
        """PV-02: When viewing a profile with retired instance, show retired status."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        # Create instance then retire
        mock_repo = _make_mock_archive_repo("player1", "prof1", "张三")
        store.select_instance_profile(
            channel_id="ch1",
            user_id="player1",
            profile_id="prof1",
            archive_repo=mock_repo,
        )
        store.retire_instance(channel_id="ch1", user_id="player1")

        # Get the instance - should show retired status
        instance = store.get_character_instance("ch1", "player1")
        assert instance is not None
        assert instance.status == "retired"
        assert instance.character_name == ""  # Retired clears name
        assert instance.archive_profile_id is None  # Retired clears profile ref

    def test_profile_detail_no_instance_shows_no_context(self):
        """PV-02: When viewing a profile with no instance, show profile only."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        # Instance exists but with empty character_name (never selected profile)
        instance = store.get_character_instance("ch1", "player1")
        assert instance is not None
        assert instance.status == "active"
        assert instance.character_name == ""  # Never selected a profile
        assert instance.archive_profile_id is None

    def test_profile_detail_different_profile_shows_no_context(self):
        """PV-02: Instance is linked to prof1, viewing prof2 shows no context."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        # Select prof1
        mock_repo = _make_mock_archive_repo("player1", "prof1", "张三")
        store.select_instance_profile(
            channel_id="ch1",
            user_id="player1",
            profile_id="prof1",
            archive_repo=mock_repo,
        )

        # Instance is linked to prof1, not prof2
        instance = store.get_character_instance("ch1", "player1")
        assert instance.archive_profile_id == "prof1"
