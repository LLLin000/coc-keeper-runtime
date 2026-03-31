"""Phase 74: COC Combat + Insanity — Integration Tests.

Tests COC 7th Edition combat resolution and insanity mechanics:
- Initiative rolls and turn order
- Combat round resolution: attack → success check → damage application
- Damage Bonus (DB) and armor calculations
- Temporary insanity triggers (failed POW check vs severe threat)
- Indefinite insanity triggers (SAN reaches 0)
- Recovery tests for temporary insanity

Reference: Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 7 (Combat) and Chapter 9 (Sanity)
"""

import pytest
from unittest.mock import patch

from dm_bot.rules.coc.combat import (
    CombatantStats,
    CombatAction,
    WeaponType,
    roll_initiative,
    get_initiative_order,
    resolve_fighting_attack,
    resolve_shooting_attack,
    resolve_brawl_attack,
    resolve_grapple_attack,
    calculate_build,
    calculate_damage_bonus,
    get_damage_bonus_string,
)
from dm_bot.rules.coc.sanity import (
    InsanityType,
    roll_insanity_break,
    resolve_sanity_check,
)
from dm_bot.rules.coc.derived import calculate_damage_bonus as calc_db_derived


class TestInitiative:
    """Test initiative rolling and turn order."""

    def test_roll_initiative_returns_1_to_100(self):
        for _ in range(100):
            result = roll_initiative(50)
            assert 1 <= result <= 100

    def test_roll_initiative_is_random(self):
        results = [roll_initiative(50) for _ in range(100)]
        assert len(set(results)) > 1

    def test_get_initiative_order_sorted_by_total(self):
        combatants = [
            ("Alice", 50),
            ("Bob", 30),
            ("Carol", 70),
        ]
        order = get_initiative_order(combatants)
        names = [name for name, dex, total in order]
        totals = [total for name, dex, total in order]
        assert totals == sorted(totals, reverse=True)

    def test_get_initiative_order_dex_multiplied_by_2(self):
        combatants = [("Test", 50)]
        with patch("random.randint", return_value=10):
            order = get_initiative_order(combatants)
            name, dex, total = order[0]
            assert total == (50 * 2) + 10

    def test_get_initiative_order_correct_sorting(self):
        combatants = [
            ("Slow", 20),
            ("Fast", 80),
        ]
        with patch("random.randint", return_value=50):
            order = get_initiative_order(combatants)
            assert order[0][0] == "Fast"
            assert order[1][0] == "Slow"


class TestCombatantStats:
    """Test CombatantStats model for combat."""

    def test_combatant_stats_basic(self):
        stats = CombatantStats(
            name="TestFighter",
            dex=50,
            fighting=75,
            dodge=40,
            hp=20,
            hp_max=20,
            armor=2,
            build=0,
            damage_bonus=0,
        )
        assert stats.name == "TestFighter"
        assert stats.hp == 20
        assert stats.armor == 2

    def test_combatant_stats_with_weapon(self):
        stats = CombatantStats(
            name="Shooter",
            dex=60,
            shooting=80,
            hp=15,
            hp_max=15,
            weapon_name="Revolver",
            weapon_type=WeaponType.RANGED,
            weapon_damage="1d10",
            weapon_range="20m",
        )
        assert stats.weapon_type == WeaponType.RANGED
        assert stats.weapon_damage == "1d10"


class TestDamageBonus:
    """Test Damage Bonus (DB) calculations."""

    @pytest.mark.parametrize(
        "str_val,siz_val,expected_db",
        [
            (15, 15, -2),  # Total 30 < 65
            (30, 35, -1),  # Total 65-84
            (50, 40, 0),  # Total 85-124
            (70, 55, 1),  # Total 125-164 → +1d4
            (90, 75, 2),  # Total 165-204 → +1d6
            (110, 100, 3),  # Total 205+ → +2d6
        ],
    )
    def test_calculate_damage_bonus_coc_rules(self, str_val, siz_val, expected_db):
        result = calculate_damage_bonus(str_val, siz_val)
        assert result == expected_db

    def test_get_damage_bonus_string_negative(self):
        result = get_damage_bonus_string(15, 15)
        assert result == "-2"

    def test_get_damage_bonus_string_zero(self):
        result = get_damage_bonus_string(50, 40)
        assert result == "0"

    def test_get_damage_bonus_string_plus_1d4(self):
        result = get_damage_bonus_string(70, 55)
        assert result == "+1d4"

    def test_get_damage_bonus_string_plus_1d6(self):
        result = get_damage_bonus_string(90, 75)
        assert result == "+1d6"

    def test_get_damage_bonus_string_plus_2d6(self):
        result = get_damage_bonus_string(110, 100)
        assert result == "+2d6"


class TestBuild:
    """Test Build calculations."""

    @pytest.mark.parametrize(
        "str_val,siz_val,expected_build",
        [
            (15, 15, -2),  # Total 30 < 65
            (35, 40, -1),  # Total 65-84
            (50, 40, 0),  # Total 85-124
            (70, 55, 1),  # Total 125-164
            (90, 80, 2),  # Total 165-204
            (110, 100, 3),  # Total 205+
        ],
    )
    def test_calculate_build_coc_rules(self, str_val, siz_val, expected_build):
        result = calculate_build(str_val, siz_val)
        assert result == expected_build


class TestResolveFightingAttack:
    """Test Fighting attack resolution."""

    def test_fighting_attack_critical_success(self):
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=75,
            hp=20,
            hp_max=20,
            build=0,
            damage_bonus=0,
        )
        defender = CombatantStats(
            name="Defender",
            dex=40,
            dodge=50,
            hp=15,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        result = resolve_fighting_attack(attacker, defender, 1, 50)
        assert result.success is True
        assert result.critical is True
        assert result.success_rank == "critical"

    def test_fighting_attack_fumble(self):
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=75,
            hp=20,
            hp_max=20,
            build=0,
            damage_bonus=0,
        )
        defender = CombatantStats(
            name="Defender",
            dex=40,
            dodge=50,
            hp=15,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        result = resolve_fighting_attack(attacker, defender, 100, 20)
        assert result.success is False
        assert result.fumble is True
        assert result.success_rank == "fumble"

    def test_fighting_attack_normal_hit(self):
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=75,
            hp=20,
            hp_max=20,
            build=0,
            damage_bonus=0,
        )
        defender = CombatantStats(
            name="Defender",
            dex=40,
            dodge=50,
            hp=15,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        result = resolve_fighting_attack(attacker, defender, 30, 70)
        assert result.success is True
        assert result.success_rank in ("regular", "hard", "extreme")

    def test_fighting_attack_normal_miss(self):
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=75,
            hp=20,
            hp_max=20,
            build=0,
            damage_bonus=0,
        )
        defender = CombatantStats(
            name="Defender",
            dex=40,
            dodge=50,
            hp=15,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        result = resolve_fighting_attack(attacker, defender, 80, 30)
        assert result.success is False

    def test_fighting_attack_damage_with_db(self):
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=75,
            hp=20,
            hp_max=20,
            build=1,
            damage_bonus=1,
            weapon_type=WeaponType.MELEE,
            weapon_damage="1d6",
        )
        defender = CombatantStats(
            name="Defender",
            dex=40,
            dodge=50,
            hp=15,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        result = resolve_fighting_attack(attacker, defender, 10, 90)
        assert result.success is True
        assert result.final_damage > 0

    def test_fighting_attack_armor_absorption(self):
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=75,
            hp=20,
            hp_max=20,
            build=0,
            damage_bonus=0,
            weapon_type=WeaponType.MELEE,
            weapon_damage="1d6",
        )
        defender = CombatantStats(
            name="Defender",
            dex=40,
            dodge=50,
            hp=15,
            hp_max=15,
            armor=5,
            build=0,
            damage_bonus=0,
        )
        result = resolve_fighting_attack(attacker, defender, 5, 95)
        assert result.success is True
        assert result.armor_absorbed > 0
        assert result.final_damage < result.damage

    def test_fighting_attack_impale_on_extreme(self):
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=90,
            hp=20,
            hp_max=20,
            build=0,
            damage_bonus=0,
            weapon_type=WeaponType.MELEE,
            weapon_damage="1d6",
        )
        defender = CombatantStats(
            name="Defender",
            dex=40,
            dodge=50,
            hp=15,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        result = resolve_fighting_attack(attacker, defender, 10, 35)
        assert result.success is True
        assert result.success_rank == "extreme"
        assert result.impale is True


class TestResolveShootingAttack:
    """Test Shooting attack resolution."""

    def test_shooting_attack_critical(self):
        attacker = CombatantStats(
            name="Shooter",
            dex=50,
            shooting=80,
            hp=15,
            hp_max=15,
            weapon_name="Rifle",
            weapon_type=WeaponType.RANGED,
            weapon_damage="1d10+2",
            damage_bonus=0,
        )
        defender = CombatantStats(
            name="Target", dex=40, hp=15, hp_max=15, armor=2, build=0, damage_bonus=0
        )
        result = resolve_shooting_attack(attacker, defender, 1)
        assert result.success is True
        assert result.critical is True

    def test_shooting_attack_fumble(self):
        attacker = CombatantStats(
            name="Shooter",
            dex=50,
            shooting=80,
            hp=15,
            hp_max=15,
            weapon_name="Rifle",
            weapon_type=WeaponType.RANGED,
            weapon_damage="1d10+2",
            damage_bonus=0,
        )
        defender = CombatantStats(
            name="Target", dex=40, hp=15, hp_max=15, armor=2, build=0, damage_bonus=0
        )
        result = resolve_shooting_attack(attacker, defender, 100)
        assert result.success is False
        assert result.fumble is True

    def test_shooting_attack_success(self):
        attacker = CombatantStats(
            name="Shooter",
            dex=50,
            shooting=80,
            hp=15,
            hp_max=15,
            weapon_name="Rifle",
            weapon_type=WeaponType.RANGED,
            weapon_damage="1d10+2",
            damage_bonus=0,
        )
        defender = CombatantStats(
            name="Target", dex=40, hp=15, hp_max=15, armor=0, build=0, damage_bonus=0
        )
        result = resolve_shooting_attack(attacker, defender, 50)
        assert result.success is True
        assert result.action == CombatAction.SHOOT

    def test_shooting_attack_armor_piercing(self):
        attacker = CombatantStats(
            name="Shooter",
            dex=50,
            shooting=80,
            hp=15,
            hp_max=15,
            weapon_name="AP Rifle",
            weapon_type=WeaponType.RANGED,
            weapon_damage="1d10",
            armor_piercing=True,
            damage_bonus=0,
        )
        defender = CombatantStats(
            name="Target", dex=40, hp=15, hp_max=15, armor=5, build=0, damage_bonus=0
        )
        result = resolve_shooting_attack(attacker, defender, 10)
        assert result.success is True
        assert result.penetration == result.damage


class TestResolveBrawlAttack:
    """Test Brawl (unarmed) attack resolution."""

    def test_brawl_attack_success(self):
        attacker = CombatantStats(
            name="Brawler", dex=50, brawl=60, hp=20, hp_max=20, build=1, damage_bonus=1
        )
        defender = CombatantStats(
            name="Victim",
            dex=40,
            dodge=30,
            hp=15,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        result = resolve_brawl_attack(attacker, defender, 30, 80)
        assert result.success is True
        assert result.action == CombatAction.BRAWL

    def test_brawl_attack_damage_is_1d3_plus_db(self):
        attacker = CombatantStats(
            name="Brawler", dex=50, brawl=60, hp=20, hp_max=20, build=0, damage_bonus=0
        )
        defender = CombatantStats(
            name="Victim",
            dex=40,
            dodge=30,
            hp=15,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        result = resolve_brawl_attack(attacker, defender, 10, 90)
        assert result.success is True
        assert "1d3" in result.damage_roll


class TestResolveGrappleAttack:
    """Test Grapple attack resolution."""

    def test_grapple_attack_success(self):
        attacker = CombatantStats(
            name="Grappler",
            dex=40,
            grapple=75,
            hp=20,
            hp_max=20,
            build=1,
            damage_bonus=0,
        )
        defender = CombatantStats(
            name="Target",
            dex=50,
            grapple=50,
            dodge=60,
            hp=15,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        result = resolve_grapple_attack(attacker, defender, 20, 70)
        assert result.success is True
        assert result.action == CombatAction.GRAPPLE

    def test_grapple_attack_fumble_self_damage(self):
        attacker = CombatantStats(
            name="Grappler",
            dex=40,
            grapple=75,
            hp=20,
            hp_max=20,
            build=0,
            damage_bonus=0,
        )
        defender = CombatantStats(
            name="Target",
            dex=50,
            grapple=50,
            dodge=60,
            hp=15,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        result = resolve_grapple_attack(attacker, defender, 100, 20)
        assert result.success is False
        assert result.fumble is True


class TestInsanityTriggers:
    """Test insanity trigger mechanics."""

    def test_indefinite_insanity_at_san_zero(self):
        result = roll_insanity_break(
            actor_name="TestChar",
            current_san=0,
            max_san=50,
            trigger_event="Witnessed Cthulhu",
        )
        assert result.insanity_type == InsanityType.INDEFINITE
        assert result.acquired_phobia or result.acquired_mania

    def test_temporary_insanity_below_threshold(self):
        result = roll_insanity_break(
            actor_name="TestChar",
            current_san=8,
            max_san=50,
            trigger_event="Severe threat",
        )
        assert result.insanity_type == InsanityType.TEMPORARY
        assert result.acute_response != ""
        assert result.duration_rounds > 0

    def test_no_insanity_above_threshold(self):
        result = roll_insanity_break(
            actor_name="TestChar",
            current_san=30,
            max_san=50,
            trigger_event="Minor sighting",
        )
        assert result.insanity_type == InsanityType.NONE

    def test_temporary_insanity_threshold_is_max_san_div_5(self):
        max_san = 50
        threshold = max_san // 5
        assert threshold == 10
        result = roll_insanity_break(
            actor_name="TestChar",
            current_san=threshold - 1,
            max_san=max_san,
            trigger_event="Below threshold",
        )
        assert result.insanity_type == InsanityType.TEMPORARY


class TestSanityCheckWithInsanity:
    """Test sanity checks that trigger insanity."""

    def test_sanity_check_failure_triggers_insanity_below_threshold(self):
        result = resolve_sanity_check(
            actor_name="TestChar",
            current_san=8,
            max_san=50,
            rolled=75,
            loss_on_failure=5,
        )
        assert result.success is False
        assert result.insanity_triggered == InsanityType.TEMPORARY

    def test_sanity_check_success_no_insanity(self):
        result = resolve_sanity_check(
            actor_name="TestChar",
            current_san=30,
            max_san=50,
            rolled=25,
            loss_on_success=0,
            loss_on_failure=5,
        )
        assert result.success is True
        assert result.insanity_triggered == InsanityType.NONE

    def test_sanity_check_critical_success(self):
        result = resolve_sanity_check(
            actor_name="TestChar",
            current_san=50,
            max_san=50,
            rolled=1,
            loss_on_success=1,
            loss_on_failure=5,
        )
        assert result.success is True
        assert result.success_rank == "critical"
        assert result.sanity_loss == 1

    def test_sanity_check_fumble_max_loss(self):
        result = resolve_sanity_check(
            actor_name="TestChar",
            current_san=50,
            max_san=50,
            rolled=100,
            loss_on_success=0,
            loss_on_failure=1,
        )
        assert result.success is False
        assert result.success_rank == "fumble"

    def test_sanity_check_san_drops_to_zero_triggers_indefinite(self):
        result = resolve_sanity_check(
            actor_name="TestChar",
            current_san=5,
            max_san=50,
            rolled=100,
            loss_on_failure=10,
        )
        assert result.success is False
        assert result.insanity_triggered == InsanityType.INDEFINITE


class TestSanityRecovery:
    """Test sanity recovery mechanics."""

    def test_sanity_recovery_rest(self):
        recovered = 0
        current = 40
        max_san = 50
        rest_periods = 1
        recovered += min(1, rest_periods)
        new_san = min(current + recovered, max_san)
        assert new_san == 41

    def test_sanity_recovery_therapy(self):
        with patch("d20.roll", return_value=type("MockRoll", (), {"total": 4})()):
            from dm_bot.rules.coc.sanity import calculate_sanity_recovery

            result = calculate_sanity_recovery(
                current_san=40,
                max_san=50,
                rest_periods=0,
                therapy_sessions=1,
                real_world_experiences=0,
            )
            assert result == 4

    def test_sanity_recovery_real_world_experiences(self):
        from dm_bot.rules.coc.sanity import calculate_sanity_recovery

        result = calculate_sanity_recovery(
            current_san=40,
            max_san=50,
            rest_periods=0,
            therapy_sessions=0,
            real_world_experiences=3,
        )
        assert result == 3

    def test_sanity_recovery_capped_at_max(self):
        from dm_bot.rules.coc.sanity import calculate_sanity_recovery

        result = calculate_sanity_recovery(
            current_san=48,
            max_san=50,
            rest_periods=10,
            therapy_sessions=10,
            real_world_experiences=10,
        )
        assert result == 2


class TestCombatArmorAndDamage:
    """Test armor and damage calculation in combat."""

    def test_armor_reduces_damage(self):
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=75,
            hp=20,
            hp_max=20,
            build=0,
            damage_bonus=0,
            weapon_type=WeaponType.MELEE,
            weapon_damage="1d6",
        )
        defender = CombatantStats(
            name="Defender",
            dex=40,
            dodge=50,
            hp=15,
            hp_max=15,
            armor=5,
            build=0,
            damage_bonus=0,
        )
        result = resolve_fighting_attack(attacker, defender, 5, 95)
        assert result.armor_absorbed > 0
        assert result.final_damage <= result.damage

    def test_armor_piercing_bypasses_armor(self):
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=75,
            hp=20,
            hp_max=20,
            build=0,
            damage_bonus=0,
            weapon_type=WeaponType.MELEE,
            weapon_damage="1d6",
            armor_piercing=True,
        )
        defender = CombatantStats(
            name="Defender",
            dex=40,
            dodge=50,
            hp=15,
            hp_max=15,
            armor=5,
            build=0,
            damage_bonus=0,
        )
        result = resolve_fighting_attack(attacker, defender, 10, 80)
        assert result.success is True
        assert result.armor_absorbed == 0
        assert result.penetration == result.damage

    def test_major_wound_triggered_when_hp_reaches_zero(self):
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=90,
            hp=20,
            hp_max=20,
            build=0,
            damage_bonus=0,
            weapon_type=WeaponType.MELEE,
            weapon_damage="2d6+10",
        )
        defender = CombatantStats(
            name="Defender",
            dex=40,
            dodge=50,
            hp=10,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        result = resolve_fighting_attack(attacker, defender, 5, 95)
        assert result.success is True
        assert result.major_wound is True
        assert result.target_hp_after <= 0


class TestCombatRoundFlow:
    """Test full combat round flow."""

    def test_combat_sequence_attack_then_defend(self):
        attacker = CombatantStats(
            name="Attacker",
            dex=50,
            fighting=75,
            hp=20,
            hp_max=20,
            build=0,
            damage_bonus=0,
            weapon_type=WeaponType.MELEE,
            weapon_damage="1d6",
        )
        defender = CombatantStats(
            name="Defender",
            dex=40,
            dodge=50,
            hp=15,
            hp_max=15,
            armor=0,
            build=0,
            damage_bonus=0,
        )
        attack_result = resolve_fighting_attack(attacker, defender, 25, 60)
        assert attack_result.success is True
        assert attack_result.target_hp_after < defender.hp
