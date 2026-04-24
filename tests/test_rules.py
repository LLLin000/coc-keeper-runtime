"""Tests for COC rules and dice."""

import pytest

from dm_bot.rules.dice import SeededDiceRoller, D20DiceRoller
from dm_bot.rules.coc import resolve_skill_check, SuccessRank


class TestDice:
    def test_seeded_roller_consistency(self):
        roller = SeededDiceRoller(42)
        result1 = roller.roll_percentile(value=50)
        roller2 = SeededDiceRoller(42)
        result2 = roller2.roll_percentile(value=50)
        assert result1.rolled == result2.rolled

    def test_d20_roller_range(self):
        roller = D20DiceRoller()
        for _ in range(100):
            result = roller.roll_percentile(value=50)
            assert 1 <= result.rolled <= 100


class TestSkillCheck:
    def test_critical_success(self):
        result = resolve_skill_check(skill_key="spot_hidden", skill_value=50, rolled=1)
        assert result.success_rank == SuccessRank.CRITICAL

    def test_extreme_success(self):
        result = resolve_skill_check(skill_key="spot_hidden", skill_value=50, rolled=10)
        assert result.success_rank == SuccessRank.EXTREME

    def test_hard_success(self):
        result = resolve_skill_check(skill_key="spot_hidden", skill_value=50, rolled=25)
        assert result.success_rank == SuccessRank.HARD

    def test_success(self):
        result = resolve_skill_check(skill_key="spot_hidden", skill_value=50, rolled=50)
        assert result.success_rank == SuccessRank.REGULAR

    def test_failure(self):
        result = resolve_skill_check(skill_key="spot_hidden", skill_value=50, rolled=51)
        assert result.success_rank == SuccessRank.FAILURE

    def test_fumble(self):
        result = resolve_skill_check(skill_key="spot_hidden", skill_value=49, rolled=100)
        assert result.success_rank == SuccessRank.FUMBLE

    def test_fumble_boundary(self):
        # Roll 100 is always fumble regardless of skill value
        result = resolve_skill_check(skill_key="spot_hidden", skill_value=50, rolled=100)
        assert result.success_rank == SuccessRank.FUMBLE


class TestPercentileOutcome:
    def test_outcome_fields(self):
        roller = D20DiceRoller()
        outcome = roller.roll_percentile(value=60)
        assert 1 <= outcome.rolled <= 100
        assert outcome.value == 60
        assert isinstance(outcome.success, bool)

    def test_bonus_dice(self):
        roller = D20DiceRoller()
        outcome = roller.roll_percentile(value=50, bonus_dice=1)
        assert 1 <= outcome.rolled <= 100
        assert outcome.bonus_dice == 1

    def test_penalty_dice(self):
        roller = D20DiceRoller()
        outcome = roller.roll_percentile(value=50, penalty_dice=1)
        assert 1 <= outcome.rolled <= 100
        assert outcome.penalty_dice == 1
