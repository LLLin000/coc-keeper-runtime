"""Tests for skill usage tracking system (E79)."""

import pytest
from dm_bot.orchestrator.session_store import SkillUsageTracker, CampaignSession
from dm_bot.rules.coc.combat import (
    CombatantStats,
    resolve_fighting_attack,
    resolve_shooting_attack,
    resolve_brawl_attack,
    resolve_grapple_attack,
)


class TestSkillUsageTracker:
    """Unit tests for SkillUsageTracker."""

    def test_tracker_initializes_empty(self):
        """Tracker starts with empty usage and successes."""
        tracker = SkillUsageTracker()
        assert tracker.usage == {}
        assert tracker.successes == {}

    def test_record_usage_increments_count(self):
        """Recording usage increments the count."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting")
        assert tracker.get_usage_count("player1", "fighting") == 1

    def test_record_usage_tracks_success(self):
        """Recording with success=True increments both usage and successes."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting", success=True)
        assert tracker.get_usage_count("player1", "fighting") == 1
        assert tracker.get_success_count("player1", "fighting") == 1

    def test_record_usage_tracks_failure(self):
        """Recording with success=False only increments usage."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting", success=False)
        assert tracker.get_usage_count("player1", "fighting") == 1
        assert tracker.get_success_count("player1", "fighting") == 0

    def test_multiple_uses_accumulate(self):
        """Multiple uses accumulate counts."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting", success=True)
        tracker.record_usage("player1", "fighting", success=False)
        tracker.record_usage("player1", "fighting", success=True)
        assert tracker.get_usage_count("player1", "fighting") == 3
        assert tracker.get_success_count("player1", "fighting") == 2

    def test_get_eligible_skills_returns_used(self):
        """Eligible skills are those that have been used."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting")
        tracker.record_usage("player1", "dodge")
        eligible = tracker.get_eligible_skills("player1")
        assert "fighting" in eligible
        assert "dodge" in eligible
        assert len(eligible) == 2

    def test_get_eligible_skills_empty_when_no_usage(self):
        """No eligible skills when nothing used."""
        tracker = SkillUsageTracker()
        assert tracker.get_eligible_skills("player1") == []

    def test_clear_resets_all_data(self):
        """Clear resets usage and successes."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting", success=True)
        tracker.record_usage("player2", "shooting")
        tracker.clear()
        assert tracker.usage == {}
        assert tracker.successes == {}
        assert tracker.get_eligible_skills("player1") == []

    def test_multiple_players_tracked_independently(self):
        """Multiple players' skills tracked separately."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting", success=True)
        tracker.record_usage("player2", "fighting", success=False)
        tracker.record_usage("player2", "dodge")

        assert tracker.get_usage_count("player1", "fighting") == 1
        assert tracker.get_success_count("player1", "fighting") == 1
        assert tracker.get_usage_count("player2", "fighting") == 1
        assert tracker.get_success_count("player2", "fighting") == 0
        assert tracker.get_usage_count("player2", "dodge") == 1

    def test_unknown_player_returns_zero(self):
        """Unknown player returns zero counts."""
        tracker = SkillUsageTracker()
        assert tracker.get_usage_count("unknown", "fighting") == 0
        assert tracker.get_success_count("unknown", "fighting") == 0


class TestCombatSkillRecording:
    """Tests for combat resolution skill recording."""

    def test_fighting_attack_records_usage_via_callback(self):
        """Fighting attack records usage when callback provided."""
        recorded = []

        def callback(player_id: str, skill: str, success: bool):
            recorded.append((player_id, skill, success))

        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=50,
            hp=10,
            hp_max=10,
        )
        defender = CombatantStats(
            name="Defender",
            dex=50,
            dodge=25,
            hp=10,
            hp_max=10,
        )

        # Attacker wins with roll 30 vs defender roll 60
        resolve_fighting_attack(
            attacker,
            defender,
            attacker_roll=30,
            defender_roll=60,
            attacker_id="player1",
            usage_callback=callback,
        )

        assert len(recorded) == 1
        assert recorded[0][0] == "player1"
        assert recorded[0][1] == "fighting"
        assert recorded[0][2] == True  # Success

    def test_fighting_attack_handles_no_callback(self):
        """Fighting attack works without callback."""
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=50,
            hp=10,
            hp_max=10,
        )
        defender = CombatantStats(
            name="Defender",
            dex=50,
            dodge=25,
            hp=10,
            hp_max=10,
        )

        # Should not raise error
        result = resolve_fighting_attack(
            attacker,
            defender,
            attacker_roll=30,
            defender_roll=60,
        )
        assert result.success == True

    def test_shooting_attack_records_usage_via_callback(self):
        """Shooting attack records usage when callback provided."""
        recorded = []

        def callback(player_id: str, skill: str, success: bool):
            recorded.append((player_id, skill, success))

        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            shooting=50,
            hp=10,
            hp_max=10,
            weapon_damage="1d6",
        )
        defender = CombatantStats(
            name="Defender",
            dex=50,
            hp=10,
            hp_max=10,
        )

        resolve_shooting_attack(
            attacker,
            defender,
            attacker_roll=25,
            attacker_id="player1",
            usage_callback=callback,
        )

        assert len(recorded) == 1
        assert recorded[0][0] == "player1"
        assert recorded[0][1] == "shooting"
        assert recorded[0][2] == True

    def test_grapple_attack_records_usage_via_callback(self):
        """Grapple attack records usage when callback provided."""
        recorded = []

        def callback(player_id: str, skill: str, success: bool):
            recorded.append((player_id, skill, success))

        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            grapple=50,
            hp=10,
            hp_max=10,
        )
        defender = CombatantStats(
            name="Defender",
            dex=50,
            grapple=25,
            hp=10,
            hp_max=10,
        )

        resolve_grapple_attack(
            attacker,
            defender,
            attacker_roll=30,
            defender_roll=60,
            attacker_id="player1",
            usage_callback=callback,
        )

        assert len(recorded) == 1
        assert recorded[0][0] == "player1"
        assert recorded[0][1] == "grapple"


class TestSkillTrackerInCampaignSession:
    """Tests for SkillTracker integration with CampaignSession."""

    def test_session_has_skill_tracker(self):
        """CampaignSession has skill_tracker field."""
        session = CampaignSession(
            campaign_id="test",
            channel_id="chan1",
            guild_id="guild1",
            owner_id="owner1",
        )
        assert session.skill_tracker is not None
        assert isinstance(session.skill_tracker, SkillUsageTracker)

    def test_session_skill_tracker_records_usage(self):
        """Can record usage through session's tracker."""
        session = CampaignSession(
            campaign_id="test",
            channel_id="chan1",
            guild_id="guild1",
            owner_id="owner1",
        )
        session.skill_tracker.record_usage("player1", "fighting", success=True)
        assert session.skill_tracker.get_usage_count("player1", "fighting") == 1
