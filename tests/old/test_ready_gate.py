"""TDD tests for select_archive_profile and validate_ready gates.

Tests ownership and membership validation:
1. Non-member cannot select a profile
2. User cannot select a profile owned by another user
3. Member can select their own profile
4. Cannot select nonexistent/inactive profiles
5. Non-member cannot ready up
6. Member without selected profile cannot ready up
7. Member with selected profile can ready up
8. Member with active_character_name (ad-hoc) can ready up
"""

import pytest
from dataclasses import dataclass
from unittest.mock import MagicMock
from dm_bot.orchestrator.session_store import (
    SessionStore,
    SelectProfileError,
    ReadyGateError,
)


@dataclass
class MockProfile:
    user_id: str
    status: str = "active"


def test_select_profile_rejects_non_member():
    """REQ-003: Non-member cannot select a profile."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )
    # user-2 has NOT joined
    result = store.select_archive_profile(
        channel_id="chan-1", user_id="user-2", profile_id="prof-1"
    )
    assert result.error == SelectProfileError.NOT_MEMBER


def test_select_profile_rejects_wrong_owner():
    """REQ-003/REQ-008: User cannot select a profile that belongs to someone else."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="chan-1", user_id="user-2")
    # profile prof-1 belongs to "owner", not "user-2"
    profiles = {"prof-1": MockProfile(user_id="owner")}
    result = store.select_archive_profile(
        channel_id="chan-1",
        user_id="user-2",
        profile_id="prof-1",
        profiles=profiles,
    )
    assert result.error == SelectProfileError.NOT_PROFILE_OWNER


def test_select_profile_succeeds_for_member_owning_profile():
    """REQ-003/REQ-008: Member can select their own profile."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="chan-1", user_id="user-2")
    profiles = {"prof-1": MockProfile(user_id="user-2")}
    result = store.select_archive_profile(
        channel_id="chan-1",
        user_id="user-2",
        profile_id="prof-1",
        profiles=profiles,
    )
    assert result.error is None
    session = store.get_by_channel("chan-1")
    assert session.selected_profiles["user-2"] == "prof-1"
    assert session.members["user-2"].selected_profile_id == "prof-1"


def test_select_profile_rejects_nonexistent_profile():
    """REQ-008: Cannot select a profile that doesn't exist."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="chan-1", user_id="user-2")
    profiles = {}  # no profiles
    result = store.select_archive_profile(
        channel_id="chan-1",
        user_id="user-2",
        profile_id="prof-missing",
        profiles=profiles,
    )
    assert result.error == SelectProfileError.PROFILE_NOT_FOUND


def test_select_profile_rejects_inactive_profile():
    """REQ-008: Cannot select an archived/inactive profile."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="chan-1", user_id="user-2")
    profiles = {"prof-1": MockProfile(user_id="user-2", status="archived")}
    result = store.select_archive_profile(
        channel_id="chan-1",
        user_id="user-2",
        profile_id="prof-1",
        profiles=profiles,
    )
    assert result.error == SelectProfileError.PROFILE_INACTIVE


def test_select_profile_no_session():
    """Should reject when no session exists for channel."""
    store = SessionStore()
    result = store.select_archive_profile(
        channel_id="no-chan", user_id="user-1", profile_id="prof-1"
    )
    assert result.error == SelectProfileError.NO_SESSION


# --- Ready Gate Validation ---


def test_ready_rejects_non_member():
    """REQ-002: Non-member cannot ready up."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )
    result = store.validate_ready(channel_id="chan-1", user_id="user-2")
    assert result.error == ReadyGateError.NOT_MEMBER


def test_ready_rejects_no_profile_selected():
    """REQ-002: Member without selected profile cannot ready up."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="chan-1", user_id="user-2")
    # user-2 has NOT selected a profile
    result = store.validate_ready(channel_id="chan-1", user_id="user-2")
    assert result.error == ReadyGateError.NO_PROFILE_SELECTED


def test_ready_succeeds_with_selected_profile():
    """REQ-002: Member with selected profile can ready up (instance model - PV-04)."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="chan-1", user_id="user-2")
    # Set up instance with character_name (simulates select_instance_profile)
    instance = store.get_character_instance("chan-1", "user-2")
    assert instance is not None
    instance.character_name = "Test Investigator"
    instance.archive_profile_id = "prof-1"
    instance.status = "active"
    result = store.validate_ready(channel_id="chan-1", user_id="user-2")
    assert result.error is None


def test_ready_succeeds_with_active_character_name():
    """REQ-002: Member with ad-hoc character name (no profile) can ready up (instance model - PV-04)."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="chan-1", user_id="user-2")
    # Set up instance with character_name (ad-hoc character without archive)
    instance = store.get_character_instance("chan-1", "user-2")
    assert instance is not None
    instance.character_name = "AdHoc Investigator"
    instance.status = "active"
    result = store.validate_ready(channel_id="chan-1", user_id="user-2")
    assert result.error is None


def test_ready_no_session():
    """Should reject when no session exists for channel."""
    store = SessionStore()
    result = store.validate_ready(channel_id="no-chan", user_id="user-1")
    assert result.error == ReadyGateError.NO_SESSION


# --- PV-04: Instance-based Ready Gate (Phase 61 TDD) ---


def _make_mock_archive_repo(
    user_id: str, profile_id: str, name: str = "TestChar"
) -> MagicMock:
    """Create a mock archive repository with a single profile."""
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

    repo = MagicMock()
    repo.get_profile.return_value = profile
    return repo


def test_ready_with_active_instance_via_select_profile():
    """PV-04: Member who selected a profile via select_instance_profile can ready.

    This tests the FIX: validate_ready should check instance.character_name,
    not member.active_character_name.
    """
    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="ch1", user_id="player1")

    # Simulate: player selected profile via select_instance_profile
    mock_repo = _make_mock_archive_repo("player1", "prof1", "张三")
    instance = store.get_character_instance("ch1", "player1")
    instance.character_name = "张三"  # This is what select_instance_profile does
    instance.archive_profile_id = "prof1"
    instance.status = "active"

    result = store.validate_ready(channel_id="ch1", user_id="player1")
    assert result.success is True, f"Expected success but got: {result.error_message}"
    assert result.error is None


def test_ready_with_retired_instance_fails():
    """PV-04: Member with retired instance cannot ready."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="ch1", user_id="player1")

    # Simulate: instance was created then retired
    instance = store.get_character_instance("ch1", "player1")
    instance.character_name = "张三"
    instance.archive_profile_id = "prof1"
    instance.status = "retired"

    result = store.validate_ready(channel_id="ch1", user_id="player1")
    assert result.success is False
    assert result.error == ReadyGateError.NO_PROFILE_SELECTED


def test_ready_with_active_instance_but_empty_character_name():
    """PV-04: Instance with status='active' but empty character_name cannot ready."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="ch1", user_id="player1")

    # Instance exists but was never given a character name
    instance = store.get_character_instance("ch1", "player1")
    assert instance is not None
    instance.character_name = ""  # Empty - never selected profile
    instance.status = "active"

    result = store.validate_ready(channel_id="ch1", user_id="player1")
    assert result.success is False
    assert result.error == ReadyGateError.NO_PROFILE_SELECTED


def test_ready_still_rejects_non_member():
    """PV-04: Non-member still cannot ready (unchanged behavior)."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp1", channel_id="ch1", guild_id="g1", owner_id="owner"
    )
    # player1 never joined
    result = store.validate_ready(channel_id="ch1", user_id="player1")
    assert result.success is False
    assert result.error == ReadyGateError.NOT_MEMBER


def test_ready_still_rejects_no_session():
    """PV-04: No session still rejects (unchanged behavior)."""
    store = SessionStore()
    result = store.validate_ready(channel_id="no-chan", user_id="user-1")
    assert result.error == ReadyGateError.NO_SESSION
