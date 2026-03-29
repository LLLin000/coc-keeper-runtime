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
    """REQ-002: Member with selected profile can ready up."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="chan-1", user_id="user-2")
    # Simulate profile already selected (bypass select_archive_profile for unit test)
    session = store.get_by_channel("chan-1")
    session.members["user-2"].selected_profile_id = "prof-1"
    session.selected_profiles["user-2"] = "prof-1"
    result = store.validate_ready(channel_id="chan-1", user_id="user-2")
    assert result.error is None


def test_ready_succeeds_with_active_character_name():
    """REQ-002: Member with ad-hoc character name (no profile) can ready up."""
    store = SessionStore()
    store.bind_campaign(
        campaign_id="c1", channel_id="chan-1", guild_id="g1", owner_id="owner"
    )
    store.join_campaign(channel_id="chan-1", user_id="user-2")
    session = store.get_by_channel("chan-1")
    session.members["user-2"].active_character_name = "AdHoc Investigator"
    result = store.validate_ready(channel_id="chan-1", user_id="user-2")
    assert result.error is None


def test_ready_no_session():
    """Should reject when no session exists for channel."""
    store = SessionStore()
    result = store.validate_ready(channel_id="no-chan", user_id="user-1")
    assert result.error == ReadyGateError.NO_SESSION
