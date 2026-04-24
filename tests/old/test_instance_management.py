"""Tests for instance management (ILC-02, ILC-03)."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from dm_bot.coc.archive import InvestigatorArchiveProfile, InvestigatorArchiveRepository
from dm_bot.orchestrator.session_store import (
    CampaignCharacterInstance,
    CampaignRole,
    CampaignSession,
    SessionStore,
)


class TestCampaignCharacterInstanceStatus:
    """Task 1: Test status field on CampaignCharacterInstance."""

    def test_status_field_default_active(self):
        """Status defaults to 'active'."""
        instance = CampaignCharacterInstance(
            campaign_id="camp1",
            user_id="user1",
            character_name="Test",
        )
        assert instance.status == "active"

    def test_status_can_be_set_to_retired(self):
        """Status can be set to 'retired'."""
        instance = CampaignCharacterInstance(
            campaign_id="camp1",
            user_id="user1",
            character_name="Test",
            status="retired",
        )
        assert instance.status == "retired"

    def test_serialize_with_status(self):
        """Instance serializes/deserializes correctly with status."""
        instance = CampaignCharacterInstance(
            campaign_id="camp1",
            user_id="user1",
            character_name="Test",
            status="retired",
        )
        data = instance.model_dump(mode="json")
        assert data["status"] == "retired"

        restored = CampaignCharacterInstance.model_validate(data)
        assert restored.status == "retired"


class TestGetActiveInstancesForUser:
    """Task 2: Test get_active_instances_for_user checks status."""

    def test_returns_active_with_name(self):
        """Instance with status='active' and character_name is returned."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        # join creates an instance - use different user than owner
        store.join_campaign(channel_id="ch1", user_id="player1")
        instance = store.get_character_instance("ch1", "player1")
        assert instance is not None
        instance.character_name = "MyChar"
        instance.status = "active"

        results = store.get_active_instances_for_user("player1")
        assert len(results) == 1
        assert results[0][1].character_name == "MyChar"

    def test_skips_retired_instance(self):
        """Instance with status='retired' is NOT returned."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")
        instance = store.get_character_instance("ch1", "player1")
        assert instance is not None
        instance.character_name = "MyChar"
        instance.status = "retired"

        results = store.get_active_instances_for_user("player1")
        assert len(results) == 0

    def test_skips_active_without_character_name(self):
        """Instance with status='active' but empty character_name is NOT returned."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")
        instance = store.get_character_instance("ch1", "player1")
        assert instance is not None
        instance.character_name = ""
        instance.status = "active"

        results = store.get_active_instances_for_user("player1")
        assert len(results) == 0


class TestRetireInstance:
    """Task 3: Test retire_instance method."""

    def test_retire_sets_status_retired(self):
        """retire_instance sets status='retired'."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")
        instance = store.get_character_instance("ch1", "player1")
        assert instance is not None
        instance.character_name = "MyChar"
        instance.archive_profile_id = "profile1"
        instance.status = "active"

        result = store.retire_instance(channel_id="ch1", user_id="player1")

        assert result.status == "retired"
        assert result.character_name == ""
        assert result.archive_profile_id is None

    def test_retire_already_retired_is_noop(self):
        """Calling retire on already-retired instance is a no-op."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")
        instance = store.get_character_instance("ch1", "player1")
        assert instance is not None
        instance.status = "retired"

        result = store.retire_instance(channel_id="ch1", user_id="player1")
        assert result.status == "retired"

    def test_retire_no_session_raises(self):
        """Retire raises ValueError if no campaign bound."""
        store = SessionStore()

        with pytest.raises(ValueError, match="No campaign bound"):
            store.retire_instance(channel_id="ch1", user_id="player1")

    def test_retire_no_instance_raises(self):
        """Retire raises ValueError if user has no instance."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        # player1 never joined

        with pytest.raises(ValueError, match="no campaign character instance"):
            store.retire_instance(channel_id="ch1", user_id="player1")

    def test_retire_logs_event(self):
        """retire_instance logs instance_retire governance event."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")
        instance = store.get_character_instance("ch1", "player1")
        assert instance is not None
        instance.character_name = "MyChar"
        instance.status = "active"

        store.retire_instance(channel_id="ch1", user_id="player1")

        events = store.event_log.get_events_for_user("player1")
        retire_events = [e for e in events if e.operation == "instance_retire"]
        assert len(retire_events) == 1


class TestSelectInstanceProfile:
    """Task 4: Test select_instance_profile method."""

    def test_select_sets_instance_fields(self):
        """select_instance_profile updates instance correctly."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        # Create a mock profile
        mock_profile = MagicMock()
        mock_profile.name = "ArchivedChar"
        mock_profile.status = "active"

        mock_repo = MagicMock(spec=InvestigatorArchiveRepository)
        mock_repo.get_profile.return_value = mock_profile

        result = store.select_instance_profile(
            channel_id="ch1",
            user_id="player1",
            profile_id="profile1",
            archive_repo=mock_repo,
        )

        assert result.archive_profile_id == "profile1"
        assert result.character_name == "ArchivedChar"
        assert result.status == "active"

    def test_select_validates_active_profile(self):
        """select_instance_profile rejects non-active profile."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        mock_profile = MagicMock()
        mock_profile.name = "ArchivedChar"
        mock_profile.status = "archived"  # Not active

        mock_repo = MagicMock(spec=InvestigatorArchiveRepository)
        mock_repo.get_profile.return_value = mock_profile

        with pytest.raises(ValueError, match="已归档"):
            store.select_instance_profile(
                channel_id="ch1",
                user_id="player1",
                profile_id="profile1",
                archive_repo=mock_repo,
            )

    def test_select_profile_not_found_raises(self):
        """select_instance_profile raises if profile doesn't exist."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        mock_repo = MagicMock(spec=InvestigatorArchiveRepository)
        mock_repo.get_profile.return_value = None

        with pytest.raises(ValueError, match="does not exist"):
            store.select_instance_profile(
                channel_id="ch1",
                user_id="player1",
                profile_id="nonexistent",
                archive_repo=mock_repo,
            )

    def test_select_no_session_raises(self):
        """select_instance_profile raises if no campaign bound."""
        store = SessionStore()

        with pytest.raises(ValueError, match="No campaign bound"):
            store.select_instance_profile(
                channel_id="ch1",
                user_id="player1",
                profile_id="profile1",
            )

    def test_select_no_instance_raises(self):
        """select_instance_profile raises if user has no instance."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )

        with pytest.raises(ValueError, match="no campaign character instance"):
            store.select_instance_profile(
                channel_id="ch1",
                user_id="player1",
                profile_id="profile1",
            )

    def test_select_logs_event(self):
        """select_instance_profile logs instance_select governance event."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        mock_profile = MagicMock()
        mock_profile.name = "ArchivedChar"
        mock_profile.status = "active"

        mock_repo = MagicMock(spec=InvestigatorArchiveRepository)
        mock_repo.get_profile.return_value = mock_profile

        store.select_instance_profile(
            channel_id="ch1",
            user_id="player1",
            profile_id="profile1",
            archive_repo=mock_repo,
        )

        events = store.event_log.get_events_for_user("player1")
        select_events = [e for e in events if e.operation == "instance_select"]
        assert len(select_events) == 1

    def test_select_without_validation(self):
        """select_instance_profile can update without validation (archive_repo=None)."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        result = store.select_instance_profile(
            channel_id="ch1",
            user_id="player1",
            profile_id="profile_no_validate",
            archive_repo=None,
        )

        assert result.archive_profile_id == "profile_no_validate"
        assert result.status == "active"


class TestForceArchiveInstanceAdmin:
    """Tests for admin force-archive instance (AV-06)."""

    def test_force_archive_instance_logs_event_with_reason(self):
        """Admin force_archive_instance logs instance_force_archive event with reason."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")
        instance = store.get_character_instance("ch1", "player1")
        assert instance is not None
        instance.character_name = "MyChar"
        instance.archive_profile_id = "profile1"
        instance.status = "active"

        store.force_archive_instance(
            channel_id="ch1",
            admin_id="owner1",
            target_user_id="player1",
            reason="spam abuse",
        )

        events = store.event_log.get_events_for_user("player1")
        force_events = [e for e in events if e.operation == "instance_force_archive"]
        assert len(force_events) == 1
        assert force_events[0].reason == "spam abuse"
        assert force_events[0].operator_id == "owner1"

    def test_force_archive_instance_admin_must_be_owner(self):
        """Only campaign owner can force-archive an instance."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")
        # Add admin
        store.join_campaign(channel_id="ch1", user_id="admin1")
        session = store.get_by_channel("ch1")
        session.members["admin1"].role = CampaignRole.ADMIN

        instance = store.get_character_instance("ch1", "player1")
        instance.character_name = "MyChar"
        instance.status = "active"

        # Admin (not owner) cannot force archive
        with pytest.raises(PermissionError, match="Only campaign owner"):
            store.force_archive_instance(
                channel_id="ch1",
                admin_id="admin1",
                target_user_id="player1",
                reason="test",
            )

    def test_force_archive_instance_target_not_member_raises(self):
        """ValueError when target user is not a member."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        # player1 never joined

        with pytest.raises(ValueError, match="not a member"):
            store.force_archive_instance(
                channel_id="ch1",
                admin_id="owner1",
                target_user_id="player1",
                reason="test",
            )


class TestReassignOwnership:
    """Tests for ownership reassignment (AV-07)."""

    def test_reassign_ownership_owner_to_member(self):
        """Owner reassigns to member: new owner gets OWNER, old owner gets ADMIN."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        new_owner, old_owner = store.reassign_ownership(
            channel_id="ch1",
            current_owner_id="owner1",
            new_owner_id="player1",
            reason="delegation",
        )

        assert new_owner.role == CampaignRole.OWNER
        assert old_owner.role == CampaignRole.ADMIN

    def test_reassign_ownership_logs_event(self):
        """Ownership reassignment logs ownership_reassign event."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="player1")

        store.reassign_ownership(
            channel_id="ch1",
            current_owner_id="owner1",
            new_owner_id="player1",
            reason="delegation",
        )

        events = store.event_log.get_events_for_user("player1")
        reassign_events = [e for e in events if e.operation == "ownership_reassign"]
        assert len(reassign_events) == 1
        assert reassign_events[0].reason == "delegation"

    def test_reassign_ownership_admin_forbidden(self):
        """Admin cannot reassign ownership - only owner can."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        store.join_campaign(channel_id="ch1", user_id="admin1")
        session = store.get_by_channel("ch1")
        session.members["admin1"].role = CampaignRole.ADMIN

        with pytest.raises(PermissionError, match="Only the current owner"):
            store.reassign_ownership(
                channel_id="ch1",
                current_owner_id="admin1",
                new_owner_id="owner1",
                reason="test",
            )

    def test_reassign_ownership_target_not_member_raises(self):
        """ValueError when target user is not a member."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )
        # player1 never joined

        with pytest.raises(ValueError, match="not a member"):
            store.reassign_ownership(
                channel_id="ch1",
                current_owner_id="owner1",
                new_owner_id="player1",
                reason="test",
            )

    def test_reassign_ownership_to_self_forbidden(self):
        """Cannot reassign ownership to self."""
        store = SessionStore()
        store.bind_campaign(
            campaign_id="camp1",
            channel_id="ch1",
            guild_id="guild1",
            owner_id="owner1",
        )

        with pytest.raises(ValueError, match="yourself"):
            store.reassign_ownership(
                channel_id="ch1",
                current_owner_id="owner1",
                new_owner_id="owner1",
                reason="test",
            )
