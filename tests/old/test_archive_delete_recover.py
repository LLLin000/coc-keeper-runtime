# Tests for Phase 57: Delete and Recovery Operations

import pytest
from datetime import datetime, timezone, timedelta

from dm_bot.coc.archive import (
    InvestigatorArchiveProfile,
    InvestigatorArchiveRepository,
    ArchiveFinishingRecommendation,
    GRACE_PERIOD_DAYS,
)
from dm_bot.characters.models import COCInvestigatorProfile, COCAttributes


def make_profile(
    user_id: str = "user1",
    profile_id: str = "prof1",
    name: str = "Test Investigator",
    status: str = "active",
    deleted_at: datetime | None = None,
) -> InvestigatorArchiveProfile:
    """Helper to create a test profile."""
    return InvestigatorArchiveProfile(
        schema_version=3,
        profile_id=profile_id,
        user_id=user_id,
        name=name,
        occupation="记者",
        age=30,
        disposition="勇敢",
        favored_skills=["侦查", "说服"],
        finishing=ArchiveFinishingRecommendation(),
        coc=COCInvestigatorProfile(
            occupation="记者",
            age=30,
            san=50,
            hp=10,
            mp=10,
            luck=50,
            build=0,
            damage_bonus="+0",
            move_rate=8,
            attributes=COCAttributes(
                str=50,
                con=50,
                dex=50,
                app=50,
                pow=50,
                siz=50,
                int=50,
                edu=50,
            ),
            skills={"侦查": 50, "说服": 50},
        ),
        status=status,
        deleted_at=deleted_at,
    )


class TestDeletedStatus:
    """Test deleted_at field and status handling."""

    def test_deleted_at_defaults_to_none(self):
        profile = make_profile(status="active")
        assert profile.deleted_at is None

    def test_deleted_at_can_be_set(self):
        deleted_time = datetime.now(timezone.utc)
        profile = make_profile(status="deleted", deleted_at=deleted_time)
        assert profile.deleted_at == deleted_time

    def test_summary_line_shows_red_for_deleted(self):
        profile = make_profile(status="deleted")
        summary = profile.summary_line()
        assert "🔴" in summary
        assert "deleted" in summary

    def test_detail_view_shows_deleted_status(self):
        profile = make_profile(status="deleted")
        detail = profile.detail_view()
        assert "🔴" in detail


class TestSoftDelete:
    """Test soft-delete behavior."""

    def test_delete_sets_status_to_deleted(self):
        repo = InvestigatorArchiveRepository()
        profile = make_profile(status="archived")
        repo._profiles["user1"] = {"prof1": profile}

        result = repo.delete_profile(user_id="user1", profile_id="prof1")

        assert result.status == "deleted"
        assert result.deleted_at is not None

    def test_delete_active_profile_raises(self):
        repo = InvestigatorArchiveRepository()
        profile = make_profile(status="active")
        repo._profiles["user1"] = {"prof1": profile}

        with pytest.raises(ValueError, match="Cannot delete an active profile"):
            repo.delete_profile(user_id="user1", profile_id="prof1")

    def test_delete_already_deleted_is_idempotent(self):
        deleted_time = datetime.now(timezone.utc)
        profile = make_profile(status="deleted", deleted_at=deleted_time)
        repo = InvestigatorArchiveRepository()
        repo._profiles["user1"] = {"prof1": profile}

        result = repo.delete_profile(user_id="user1", profile_id="prof1")

        assert result.status == "deleted"
        assert result.deleted_at == deleted_time  # Timestamp unchanged


class TestRecoverProfile:
    """Test profile recovery within grace period."""

    def test_recover_restores_to_active(self):
        deleted_time = datetime.now(timezone.utc) - timedelta(days=3)
        profile = make_profile(status="deleted", deleted_at=deleted_time)
        repo = InvestigatorArchiveRepository()
        repo._profiles["user1"] = {"prof1": profile}

        result = repo.recover_profile(user_id="user1", profile_id="prof1")

        assert result.status == "active"
        assert result.deleted_at is None

    def test_recover_non_deleted_raises(self):
        repo = InvestigatorArchiveRepository()
        profile = make_profile(status="archived")
        repo._profiles["user1"] = {"prof1": profile}

        with pytest.raises(ValueError, match="Can only recover a deleted profile"):
            repo.recover_profile(user_id="user1", profile_id="prof1")

    def test_recover_expired_grace_period_raises(self):
        deleted_time = datetime.now(timezone.utc) - timedelta(days=8)
        profile = make_profile(status="deleted", deleted_at=deleted_time)
        repo = InvestigatorArchiveRepository()
        repo._profiles["user1"] = {"prof1": profile}

        with pytest.raises(ValueError, match="Grace period expired"):
            repo.recover_profile(user_id="user1", profile_id="prof1")


class TestReplaceArchived:
    """Test replace_active_with sets old to archived (not replaced)."""

    def test_replace_sets_old_to_archived(self):
        repo = InvestigatorArchiveRepository()
        old_profile = make_profile(profile_id="old1", status="active")
        new_profile = make_profile(profile_id="new1", status="archived")
        repo._profiles["user1"] = {"old1": old_profile, "new1": new_profile}

        repo.replace_active_with(user_id="user1", profile_id="new1")

        assert old_profile.status == "archived"

    def test_replace_sets_new_to_active(self):
        repo = InvestigatorArchiveRepository()
        old_profile = make_profile(profile_id="old1", status="active")
        new_profile = make_profile(profile_id="new1", status="archived")
        repo._profiles["user1"] = {"old1": old_profile, "new1": new_profile}

        repo.replace_active_with(user_id="user1", profile_id="new1")

        assert new_profile.status == "active"


class TestPurgeExpiredDeleted:
    """Test auto-purge after grace period."""

    def test_purge_removes_expired_profiles(self):
        deleted_time = datetime.now(timezone.utc) - timedelta(days=8)
        profile = make_profile(status="deleted", deleted_at=deleted_time)
        repo = InvestigatorArchiveRepository()
        repo._profiles["user1"] = {"prof1": profile}

        purged = repo.purge_expired_deleted(user_id="user1")

        assert purged == 1
        assert "prof1" not in repo._profiles.get("user1", {})

    def test_purge_keeps_within_grace_period(self):
        deleted_time = datetime.now(timezone.utc) - timedelta(days=3)
        profile = make_profile(status="deleted", deleted_at=deleted_time)
        repo = InvestigatorArchiveRepository()
        repo._profiles["user1"] = {"prof1": profile}

        purged = repo.purge_expired_deleted(user_id="user1")

        assert purged == 0
        assert "prof1" in repo._profiles["user1"]

    def test_purge_calls_append_event(self):
        deleted_time = datetime.now(timezone.utc) - timedelta(days=8)
        profile = make_profile(status="deleted", deleted_at=deleted_time)
        repo = InvestigatorArchiveRepository()
        repo._profiles["user1"] = {"prof1": profile}

        events = []

        def capture_event(**kwargs):
            events.append(kwargs)

        purged = repo.purge_expired_deleted(user_id="user1", append_event=capture_event)

        assert purged == 1
        assert len(events) == 1
        assert events[0]["operation"] == "profile_purge"


class TestGracePeriodConstant:
    """Verify grace period is 7 days."""

    def test_grace_period_is_7_days(self):
        assert GRACE_PERIOD_DAYS == 7
