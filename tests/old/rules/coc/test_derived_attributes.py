"""Phase 73: COC Derived Attributes — Unit Tests.

Tests COC 7e derived attribute calculations:
- HP, MP, SAN, LUCK, MOV, Build, Damage Bonus
- Age modifiers
- Characteristic rolling
- Luck system

Reference: Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 2
"""

import pytest
from unittest.mock import patch

from dm_bot.rules.coc.derived import (
    calculate_luck,
    calculate_hp,
    calculate_mp,
    calculate_sanity,
    calculate_move_rate,
    calculate_build,
    calculate_damage_bonus,
    get_damage_bonus_dice_expression,
    calculate_all_derived_attributes,
    get_age_modifiers,
    apply_age_modifiers,
    roll_characteristic,
    generate_characteristics,
    spend_luck,
    recover_luck,
)
from dm_bot.rules.coc.sanity import (
    get_mythos_gain_for_encounter,
    get_sanity_loss_for_encounter,
    roll_insanity_break,
    resolve_sanity_check,
    calculate_sanity_recovery,
    spend_luck_for_sanity,
    InsanityType,
)
from dm_bot.characters.models import COCAttributes


class TestCalculateLuck:
    def test_calculate_luck_standard(self):
        assert calculate_luck(50) == 250

    def test_calculate_luck_zero(self):
        assert calculate_luck(0) == 0

    def test_calculate_luck_low(self):
        assert calculate_luck(21) == 105


class TestCalculateHP:
    def test_calculate_hp_standard(self):
        assert calculate_hp(50, 50) == 10

    def test_calculate_hp_large(self):
        assert calculate_hp(90, 65) == 15

    def test_calculate_hp_minimum(self):
        assert calculate_hp(1, 1) == 0

    def test_calculate_hp_fractional_rounds_down(self):
        assert calculate_hp(15, 20) == 3


class TestCalculateMP:
    def test_calculate_mp_standard(self):
        assert calculate_mp(50) == 10

    def test_calculate_mp_low(self):
        assert calculate_mp(5) == 1

    def test_calculate_mp_zero(self):
        assert calculate_mp(0) == 0

    def test_calculate_mp_fractional_rounds_down(self):
        assert calculate_mp(7) == 1


class TestCalculateSanity:
    def test_calculate_sanity_standard(self):
        assert calculate_sanity(50) == 250

    def test_calculate_sanity_zero(self):
        assert calculate_sanity(0) == 0

    def test_calculate_sanity_same_as_luck(self):
        pow_val = 35
        assert calculate_sanity(pow_val) == calculate_luck(pow_val)


class TestCalculateMoveRate:
    @pytest.mark.parametrize(
        "str_val,dex_val,siz_val,expected",
        [
            (10, 10, 20, 7),
            (25, 25, 10, 9),
            (15, 15, 15, 8),
        ],
    )
    def test_calculate_move_rate_base(self, str_val, dex_val, siz_val, expected):
        assert calculate_move_rate(str_val, dex_val, siz_val, age=0) == expected

    def test_calculate_move_rate_age_40_penalty(self):
        assert calculate_move_rate(15, 15, 15, age=45) == 7

    def test_calculate_move_rate_age_50_penalty(self):
        assert calculate_move_rate(15, 15, 15, age=55) == 6

    def test_calculate_move_rate_age_60_penalty(self):
        assert calculate_move_rate(15, 15, 15, age=65) == 5

    def test_calculate_move_rate_age_70_penalty(self):
        assert calculate_move_rate(15, 15, 15, age=75) == 5

    def test_calculate_move_rate_minimum_enforced(self):
        assert calculate_move_rate(15, 15, 15, age=90) == 5


class TestCalculateBuild:
    @pytest.mark.parametrize(
        "str_val,siz_val,expected",
        [
            (30, 30, -2),
            (40, 40, -1),
            (50, 40, 0),
            (70, 70, 1),
            (100, 80, 2),
            (120, 90, 3),
        ],
    )
    def test_calculate_build_bands(self, str_val, siz_val, expected):
        assert calculate_build(str_val, siz_val) == expected


class TestCalculateDamageBonus:
    @pytest.mark.parametrize(
        "str_val,siz_val,numeric,string",
        [
            (30, 30, -1, "-1"),
            (40, 40, 0, "0"),
            (50, 40, 0, "0"),
            (70, 70, 1, "+1d4"),
            (100, 80, 1, "+1d6"),
            (120, 90, 2, "+2d6"),
        ],
    )
    def test_calculate_damage_bonus(self, str_val, siz_val, numeric, string):
        result_numeric, result_string = calculate_damage_bonus(str_val, siz_val)
        assert result_numeric == numeric
        assert result_string == string

    def test_get_damage_bonus_dice_expression(self):
        expr = get_damage_bonus_dice_expression(70, 70)
        assert expr == "+1d4"


class TestCalculateAllDerivedAttributes:
    def test_calculate_all_derived_attributes_standard(self):
        attrs = COCAttributes(
            str=50, con=50, dex=50, app=50, pow=50, siz=50, int=50, edu=50
        )
        result = calculate_all_derived_attributes(attrs, age=0)

        assert result.luck == 250
        assert result.hp == 10
        assert result.hp_max == 10
        assert result.mp == 10
        assert result.mp_max == 10
        assert result.san == 250
        assert result.san_max == 250
        assert result.move_rate == 8
        assert result.build == 0

    def test_calculate_all_derived_attributes_with_age(self):
        attrs = COCAttributes(
            str=50, con=50, dex=50, app=50, pow=50, siz=50, int=50, edu=50
        )
        result = calculate_all_derived_attributes(attrs, age=50)

        assert result.move_rate == 6


class TestAgeModifiers:
    @pytest.mark.parametrize(
        "age,expected",
        [
            (
                25,
                {"str": 0, "con": 0, "dex": 0, "app": 0, "pow": 0, "int": 0, "edu": 0},
            ),
            (
                35,
                {"str": 0, "con": 0, "dex": 0, "app": 0, "pow": 0, "int": 1, "edu": 1},
            ),
            (
                45,
                {
                    "str": -5,
                    "con": -10,
                    "dex": -10,
                    "app": -10,
                    "pow": 0,
                    "int": 2,
                    "edu": 3,
                },
            ),
            (
                55,
                {
                    "str": -10,
                    "con": -15,
                    "dex": -15,
                    "app": -15,
                    "pow": 0,
                    "int": 3,
                    "edu": 6,
                },
            ),
            (
                65,
                {
                    "str": -15,
                    "con": -20,
                    "dex": -20,
                    "app": -20,
                    "pow": 0,
                    "int": 4,
                    "edu": 8,
                },
            ),
            (
                75,
                {
                    "str": -20,
                    "con": -25,
                    "dex": -25,
                    "app": -25,
                    "pow": 0,
                    "int": 5,
                    "edu": 10,
                },
            ),
            (
                85,
                {
                    "str": -25,
                    "con": -30,
                    "dex": -30,
                    "app": -30,
                    "pow": 0,
                    "int": 6,
                    "edu": 12,
                },
            ),
            (
                95,
                {
                    "str": -30,
                    "con": -35,
                    "dex": -35,
                    "app": -35,
                    "pow": 0,
                    "int": 7,
                    "edu": 14,
                },
            ),
        ],
    )
    def test_get_age_modifiers(self, age, expected):
        assert get_age_modifiers(age) == expected


class TestApplyAgeModifiers:
    def test_apply_age_modifiers_minimum_one(self):
        attrs = COCAttributes(
            str=10, con=10, dex=10, app=10, pow=10, siz=10, int=10, edu=10
        )
        result = apply_age_modifiers(attrs, age=95)

        assert result.str == 1
        assert result.con == 1
        assert result.dex == 1
        assert result.app == 1

    def test_apply_age_modifiers_standard(self):
        attrs = COCAttributes(
            str=50, con=50, dex=50, app=50, pow=50, siz=50, int=50, edu=50
        )
        result = apply_age_modifiers(attrs, age=25)

        assert result.str == 50
        assert result.int == 50
        assert result.edu == 50


class TestRollCharacteristic:
    def test_roll_characteristic_range(self):
        for _ in range(100):
            result = roll_characteristic()
            assert 3 <= result <= 18


class TestGenerateCharacteristics:
    def test_generate_characteristics_siz_is_2d6_plus_6(self):
        with patch("random.randint", return_value=6):
            result = generate_characteristics()
            assert result["siz"] == 18

    def test_generate_characteristics_all_seven(self):
        result = generate_characteristics()
        expected = {"str", "con", "dex", "app", "pow", "int", "edu", "siz"}
        assert set(result.keys()) == expected


class TestSpendLuck:
    def test_spend_luck_success(self):
        new_luck, success = spend_luck(50, 10)
        assert new_luck == 40
        assert success is True

    def test_spend_luck_insufficient(self):
        new_luck, success = spend_luck(5, 10)
        assert new_luck == 5
        assert success is False

    def test_spend_luck_exact(self):
        new_luck, success = spend_luck(50, 50)
        assert new_luck == 0
        assert success is True


class TestRecoverLuck:
    def test_recover_luck_standard(self):
        result = recover_luck(max_luck=50, current_luck=40, rest_periods=3)
        assert result == 43

    def test_recover_luck_capped_at_max(self):
        result = recover_luck(max_luck=50, current_luck=48, rest_periods=10)
        assert result == 50

    def test_recover_luck_no_periods(self):
        result = recover_luck(max_luck=50, current_luck=40, rest_periods=0)
        assert result == 40


class TestGetMythosGainForEncounter:
    def test_get_mythos_gain_known_type(self):
        assert get_mythos_gain_for_encounter("cthulhu") == 8
        assert get_mythos_gain_for_encounter("book_of_shadows") == 5

    def test_get_mythos_gain_unknown_type(self):
        assert get_mythos_gain_for_encounter("unknown_type") == 1


class TestGetSanityLossForEncounter:
    def test_get_sanity_loss_with_rolled_value(self):
        result = get_sanity_loss_for_encounter("cthulhu", rolled_loss=5)
        assert result == 5

    def test_get_sanity_loss_clamps_to_max(self):
        result = get_sanity_loss_for_encounter("cthulhu", rolled_loss=15)
        assert result == 10

    def test_get_sanity_loss_clamps_to_min(self):
        result = get_sanity_loss_for_encounter("cthulhu", rolled_loss=0)
        assert result == 1

    def test_get_sanity_loss_unknown_type(self):
        result = get_sanity_loss_for_encounter("unknown_type")
        assert result == 1


class TestRollInsanityBreak:
    def test_roll_insanity_break_san_zero(self):
        result = roll_insanity_break(
            "TestChar", current_san=0, max_san=50, trigger_event="test"
        )
        assert result.insanity_type == InsanityType.INDEFINITE
        assert result.acquired_phobia or result.acquired_mania

    def test_roll_insanity_break_san_below_threshold(self):
        result = roll_insanity_break(
            "TestChar", current_san=5, max_san=50, trigger_event="test"
        )
        assert result.insanity_type == InsanityType.TEMPORARY
        assert result.acute_response != ""

    def test_roll_insanity_break_no_insanity(self):
        result = roll_insanity_break(
            "TestChar", current_san=30, max_san=50, trigger_event="test"
        )
        assert result.insanity_type == InsanityType.NONE


class TestResolveSanityCheck:
    def test_resolve_sanity_check_critical(self):
        result = resolve_sanity_check(
            actor_name="TestChar",
            current_san=50,
            max_san=50,
            rolled=1,
            loss_on_success=0,
            loss_on_failure=1,
        )
        assert result.success is True
        assert result.success_rank == "critical"

    def test_resolve_sanity_check_fumble(self):
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

    def test_resolve_sanity_check_success(self):
        result = resolve_sanity_check(
            actor_name="TestChar",
            current_san=50,
            max_san=50,
            rolled=25,
            loss_on_success=0,
            loss_on_failure=1,
        )
        assert result.success is True
        assert result.sanity_loss == 0

    def test_resolve_sanity_check_failure(self):
        result = resolve_sanity_check(
            actor_name="TestChar",
            current_san=50,
            max_san=50,
            rolled=75,
            loss_on_success=0,
            loss_on_failure=1,
        )
        assert result.success is False
        assert result.sanity_loss == 1


class TestCalculateSanityRecovery:
    def test_calculate_sanity_recovery_rest(self):
        result = calculate_sanity_recovery(
            current_san=40,
            max_san=50,
            rest_periods=1,
            therapy_sessions=0,
            real_world_experiences=0,
        )
        assert result == 1

    def test_calculate_sanity_recovery_therapy(self):
        with patch("d20.roll", return_value=type("MockRoll", (), {"total": 4})()):
            result = calculate_sanity_recovery(
                current_san=40,
                max_san=50,
                rest_periods=0,
                therapy_sessions=1,
                real_world_experiences=0,
            )
            assert result == 4

    def test_calculate_sanity_recovery_real_world(self):
        result = calculate_sanity_recovery(
            current_san=40,
            max_san=50,
            rest_periods=0,
            therapy_sessions=0,
            real_world_experiences=2,
        )
        assert result == 2

    def test_calculate_sanity_recovery_capped(self):
        result = calculate_sanity_recovery(
            current_san=48,
            max_san=50,
            rest_periods=10,
            therapy_sessions=10,
            real_world_experiences=10,
        )
        assert result == 2


class TestSpendLuckForSanity:
    def test_spend_luck_for_sanity_no_luck(self):
        luck_spent, new_loss, explanation = spend_luck_for_sanity(
            actor_name="TestChar",
            current_san=50,
            max_san=50,
            luck_available=0,
            sanity_loss=5,
            rolled=75,
        )
        assert luck_spent == 0
        assert new_loss == 5

    def test_spend_luck_for_sanity_success_no_re_roll_needed(self):
        luck_spent, new_loss, explanation = spend_luck_for_sanity(
            actor_name="TestChar",
            current_san=50,
            max_san=50,
            luck_available=10,
            sanity_loss=5,
            rolled=25,
        )
        assert luck_spent == 0
        assert new_loss == 5
