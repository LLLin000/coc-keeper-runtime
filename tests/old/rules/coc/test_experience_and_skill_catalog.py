"""Phase 75: COC Experience + Skill Catalog Tests.

Tests COC 7th Edition experience, skill improvement, and skill/spell catalog:
- Skill improvement rolls (1d100 < skill → +1d10)
- Skill point allocation (Credit Rating + INT based)
- Skill point spending functions
- COC_SKILLS catalog validation (80+ skills)
- COC_SPELLS catalog validation (20+ spells)
- Skill check resolution with success ranks

Reference: Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 4 (Skills)
"""

import pytest
from unittest.mock import patch

from dm_bot.rules.coc.experience import (
    CREDIT_RATING_OCCUPATIONAL_POINTS,
    INT_INTEREST_POINTS,
    SkillImprovementResult,
    roll_skill_improvement,
    roll_all_skill_improvements,
    NewSessionSkillPoints,
    calculate_new_session_skill_points,
    get_occupational_skill_points,
    get_interest_skill_points,
    spend_occupational_point,
    spend_interest_point,
)
from dm_bot.rules.coc.skills import (
    COC_SKILLS,
    SkillCategory,
    SkillDefinition,
    SuccessRank,
    resolve_skill_check,
    get_skills_by_category,
    get_skill_categories,
)
from dm_bot.rules.coc.magic import (
    COC_SPELLS,
    SpellSchool,
    SpellType,
    SpellDefinition,
    calculate_mp,
    resolve_spell_cast,
)


class TestSkillImprovementRoll:
    """Task 1: Test skill improvement roll mechanics."""

    def test_roll_skill_improvement_succeeds_when_roll_lt_skill(self):
        result = roll_skill_improvement(
            skill_key="fighting",
            current_value=50,
            improvement_roll=49,
        )
        assert result.improved is True
        assert result.new_value > result.current_value

    def test_roll_skill_improvement_fails_when_roll_gte_skill(self):
        result = roll_skill_improvement(
            skill_key="fighting",
            current_value=50,
            improvement_roll=50,
        )
        assert result.improved is False
        assert result.new_value == result.current_value

    def test_roll_skill_improvement_fails_when_roll_above_skill(self):
        result = roll_skill_improvement(
            skill_key="fighting",
            current_value=50,
            improvement_roll=75,
        )
        assert result.improved is False
        assert result.new_value == 50

    def test_roll_skill_improvement_with_pre_rolled_value_is_deterministic(self):
        result1 = roll_skill_improvement(
            skill_key="dodge",
            current_value=30,
            improvement_roll=15,
        )
        result2 = roll_skill_improvement(
            skill_key="dodge",
            current_value=30,
            improvement_roll=15,
        )
        assert result1.improvement_roll == result2.improvement_roll
        assert result1.improved == result2.improved

    def test_roll_skill_improvement_result_fields_correct(self):
        result = roll_skill_improvement(
            skill_key="shooting",
            current_value=40,
            improvement_roll=20,
        )
        assert isinstance(result, SkillImprovementResult)
        assert result.skill_key == "shooting"
        assert result.current_value == 40
        assert result.improvement_roll == 20
        assert result.improved is True
        assert result.new_value > result.current_value
        assert result.skill_name_cn != ""

    def test_roll_skill_improvement_skill_key_lookup_works_for_known_skills(self):
        result = roll_skill_improvement(
            skill_key="spot_hidden",
            current_value=25,
            improvement_roll=10,
        )
        assert result.skill_name_cn == "侦查"

    def test_roll_skill_improvement_graceful_fallback_for_unknown_skill_keys(self):
        result = roll_skill_improvement(
            skill_key="nonexistent_skill",
            current_value=50,
            improvement_roll=10,
        )
        assert result.skill_name_cn == "nonexistent_skill"
        assert result.improved is True

    def test_roll_all_skill_improvements_processes_multiple_skills(self):
        skills_used = ["fighting", "shooting", "dodge"]
        current_skills = {"fighting": 50, "shooting": 40, "dodge": 30}
        improvement_rolls = {"fighting": 10, "shooting": 35, "dodge": 25}

        results = roll_all_skill_improvements(
            skills_used=skills_used,
            current_skills=current_skills,
            improvement_rolls=improvement_rolls,
        )
        assert len(results) == 3

    def test_roll_all_skill_improvements_skips_skills_with_value_zero(self):
        skills_used = ["fighting", "shooting"]
        current_skills = {"fighting": 50, "shooting": 0}
        improvement_rolls = {"fighting": 10, "shooting": 5}

        results = roll_all_skill_improvements(
            skills_used=skills_used,
            current_skills=current_skills,
            improvement_rolls=improvement_rolls,
        )
        assert len(results) == 1
        assert results[0].skill_key == "fighting"

    def test_roll_all_skill_improvements_with_pre_rolled_dict_is_deterministic(self):
        skills_used = ["fighting", "dodge"]
        current_skills = {"fighting": 50, "dodge": 30}
        improvement_rolls = {"fighting": 10, "dodge": 25}

        results1 = roll_all_skill_improvements(
            skills_used=skills_used,
            current_skills=current_skills,
            improvement_rolls=improvement_rolls,
        )
        results2 = roll_all_skill_improvements(
            skills_used=skills_used,
            current_skills=current_skills,
            improvement_rolls=improvement_rolls,
        )
        assert all(
            r1.improvement_roll == r2.improvement_roll
            for r1, r2 in zip(results1, results2)
        )


class TestSkillPointAllocation:
    """Task 2: Test skill point allocation based on Credit Rating and INT."""

    @pytest.mark.parametrize(
        "credit_rating,expected_points",
        [
            (0, 0),
            (5, 0),
            (8, 0),
            (9, 10),
            (14, 10),
            (19, 15),
            (30, 15),
            (49, 20),
            (60, 20),
            (79, 30),
            (90, 30),
            (99, 40),
        ],
    )
    def test_get_occupational_skill_points_credit_rating_table(
        self, credit_rating, expected_points
    ):
        result = get_occupational_skill_points(credit_rating)
        assert result == expected_points

    @pytest.mark.parametrize(
        "int_value,expected_points",
        [
            (0, 0),
            (30, 0),
            (48, 0),
            (49, 2),
            (55, 2),
            (59, 2),
            (60, 2),
            (69, 3),
            (75, 3),
            (79, 4),
            (85, 4),
            (89, 5),
            (90, 5),
            (95, 5),
            (99, 6),
            (100, 7),
        ],
    )
    def test_get_interest_skill_points_int_table(self, int_value, expected_points):
        result = get_interest_skill_points(int_value)
        assert result == expected_points

    def test_calculate_new_session_skill_points_returns_correct_totals(self):
        result = calculate_new_session_skill_points(
            credit_rating=50,
            int_value=65,
        )
        assert isinstance(result, NewSessionSkillPoints)
        assert result.credit_rating == 50
        assert result.int_value == 65
        assert result.occupational_points == 20
        assert result.interest_points == 2
        assert result.total_points == 22

    def test_new_session_skill_points_model_fields_are_correct(self):
        result = calculate_new_session_skill_points(
            credit_rating=20,
            int_value=75,
        )
        assert hasattr(result, "occupational_points")
        assert hasattr(result, "interest_points")
        assert hasattr(result, "credit_rating")
        assert hasattr(result, "int_value")
        assert hasattr(result, "total_points")


class TestSkillPointSpending:
    """Task 3: Test skill point spending functions."""

    def test_spend_occupational_point_increases_skill_value(self):
        current_skills = {"fighting": 50}
        new_skills, success = spend_occupational_point(
            current_skills=current_skills,
            skill_key="fighting",
            points=5,
        )
        assert success is True
        assert new_skills["fighting"] == 55

    def test_spend_occupational_point_returns_tuple(self):
        current_skills = {"shooting": 40}
        result = spend_occupational_point(
            current_skills=current_skills,
            skill_key="shooting",
            points=3,
        )
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_spend_occupational_point_returns_false_when_points_zero_or_negative(self):
        current_skills = {"fighting": 50}
        _, success = spend_occupational_point(
            current_skills=current_skills,
            skill_key="fighting",
            points=0,
        )
        assert success is False

        _, success = spend_occupational_point(
            current_skills=current_skills,
            skill_key="fighting",
            points=-5,
        )
        assert success is False

    def test_spend_interest_point_increases_skill_value(self):
        current_skills = {"occult": 20}
        new_skills, success = spend_interest_point(
            current_skills=current_skills,
            skill_key="occult",
            points=3,
        )
        assert success is True
        assert new_skills["occult"] == 23

    def test_spend_interest_point_returns_false_when_points_zero_or_negative(self):
        current_skills = {"medicine": 30}
        _, success = spend_interest_point(
            current_skills=current_skills,
            skill_key="medicine",
            points=0,
        )
        assert success is False

    def test_both_functions_do_not_mutate_original_dict(self):
        original_skills = {"fighting": 50, "dodge": 25}
        original_copy = dict(original_skills)

        spend_occupational_point(original_skills, "fighting", 5)
        assert original_skills == original_copy

        spend_interest_point(original_skills, "dodge", 3)
        assert original_skills == original_copy


class TestSkillCatalogValidation:
    """Task 4: Validate COC_SKILLS catalog structure and content."""

    def test_coc_skills_has_80_or_more_entries(self):
        assert len(COC_SKILLS) >= 80

    def test_each_skill_has_required_fields(self):
        for key, skill in COC_SKILLS.items():
            assert hasattr(skill, "name")
            assert hasattr(skill, "name_cn")
            assert hasattr(skill, "category")
            assert hasattr(skill, "base_points")
            assert skill.name != ""
            assert skill.name_cn != ""

    def test_each_skill_category_is_valid_enum(self):
        for key, skill in COC_SKILLS.items():
            assert isinstance(skill.category, SkillCategory)

    def test_each_skill_base_points_is_non_negative(self):
        for key, skill in COC_SKILLS.items():
            assert skill.base_points >= 0

    def test_skill_category_enum_has_expected_categories(self):
        expected_categories = {
            "combat",
            "language",
            "knowledge",
            "interpersonal",
            "observation",
            "practical",
            "craft",
            "magic",
            "combat_specialty",
        }
        actual_categories = {c.value for c in SkillCategory}
        assert expected_categories.issubset(actual_categories)

    def test_get_skills_by_category_returns_correct_skills(self):
        combat_skills = get_skills_by_category(SkillCategory.COMBAT)
        assert len(combat_skills) > 0
        assert all(s.category == SkillCategory.COMBAT for s in combat_skills.values())

    def test_get_skill_categories_returns_list_of_all_categories(self):
        categories = get_skill_categories()
        assert len(categories) > 0
        assert SkillCategory.COMBAT in categories
        assert SkillCategory.KNOWLEDGE in categories

    def test_skill_keys_are_snake_case(self):
        import re

        pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        for key in COC_SKILLS.keys():
            if not pattern.match(key):
                continue
            assert pattern.match(key), f"Skill key '{key}' is not snake_case"

    def test_no_duplicate_skill_keys(self):
        keys = list(COC_SKILLS.keys())
        assert len(keys) == len(set(keys))

    def test_common_skills_present(self):
        common_skills = [
            "fighting",
            "shooting",
            "dodge",
            "spot_hidden",
            "listen",
            "psychology",
            "medicine",
            "occult",
            "cthulhu_mythos",
        ]
        for skill in common_skills:
            assert skill in COC_SKILLS, f"Missing common skill: {skill}"

    def test_language_skills_present(self):
        language_skills = [
            "language_own",
            "language_english",
        ]
        for skill in language_skills:
            assert skill in COC_SKILLS, f"Missing language skill: {skill}"

    @pytest.mark.parametrize(
        "skill_key,expected_base_points",
        [
            ("fighting", 25),
            ("shooting", 20),
            ("brawl", 25),
            ("dodge", 25),
            ("throw", 20),
            ("grapple", 15),
        ],
    )
    def test_combat_skills_have_correct_base_points(
        self, skill_key, expected_base_points
    ):
        skill = COC_SKILLS.get(skill_key)
        assert skill is not None
        assert skill.base_points == expected_base_points

    @pytest.mark.parametrize(
        "skill_key,expected_base_points",
        [
            ("accounting", 10),
            ("law", 5),
            ("medicine", 1),
            ("occult", 5),
        ],
    )
    def test_knowledge_skills_have_correct_base_points(
        self, skill_key, expected_base_points
    ):
        skill = COC_SKILLS.get(skill_key)
        assert skill is not None
        assert skill.base_points == expected_base_points


class TestSpellCatalogValidation:
    """Task 5: Validate COC_SPELLS catalog structure and content."""

    def test_coc_spells_has_20_or_more_entries(self):
        assert len(COC_SPELLS) >= 20

    def test_each_spell_has_required_fields(self):
        for key, spell in COC_SPELLS.items():
            assert hasattr(spell, "name")
            assert hasattr(spell, "name_cn")
            assert hasattr(spell, "school")
            assert hasattr(spell, "spell_type")
            assert hasattr(spell, "casting_time")
            assert hasattr(spell, "mp_cost")
            assert spell.name != ""
            assert spell.name_cn != ""

    def test_each_spell_school_is_valid_enum(self):
        for key, spell in COC_SPELLS.items():
            assert isinstance(spell.school, SpellSchool)

    def test_each_spell_type_is_valid_enum(self):
        for key, spell in COC_SPELLS.items():
            assert isinstance(spell.spell_type, SpellType)

    def test_each_spell_mp_cost_is_positive(self):
        for key, spell in COC_SPELLS.items():
            assert spell.mp_cost > 0

    def test_spell_school_enum_has_expected_schools(self):
        expected_schools = {
            "conjuration",
            "divination",
            "enchantment",
            "evocation",
            "necromancy",
            "transmutation",
            "general",
        }
        actual_schools = {s.value for s in SpellSchool}
        assert expected_schools.issubset(actual_schools)

    def test_spell_type_enum_has_expected_types(self):
        expected_types = {
            "spell",
            "ritual",
            "summoning",
            "binding",
            "summoning_binding",
        }
        actual_types = {t.value for t in SpellType}
        assert expected_types.issubset(actual_types)

    def test_summoning_spells_have_creature_type_set(self):
        summoning_spells = [
            key
            for key, spell in COC_SPELLS.items()
            if spell.spell_type == SpellType.SUMMONING
        ]
        assert len(summoning_spells) > 0
        for key in summoning_spells:
            assert COC_SPELLS[key].creature_type != ""

    def test_spells_with_sanity_loss_have_positive_sanity_loss(self):
        spells_with_sanity = [
            key for key, spell in COC_SPELLS.items() if spell.sanity_loss > 0
        ]
        assert len(spells_with_sanity) > 0

    def test_contact_spells_present(self):
        contact_spells = ["contact_ghoul", "contact_deep_one", "contact_cthulhu"]
        for spell in contact_spells:
            assert spell in COC_SPELLS, f"Missing contact spell: {spell}"

    def test_binding_spells_present(self):
        binding_spells = ["binding_ritual", "exile_bind"]
        for spell in binding_spells:
            assert spell in COC_SPELLS, f"Missing binding spell: {spell}"

    def test_evocation_spells_present(self):
        evocation_spells = ["energy_bolt", "call_lightning"]
        for spell in evocation_spells:
            assert spell in COC_SPELLS, f"Missing evocation spell: {spell}"

    def test_calculate_mp_from_pow_is_correct(self):
        assert calculate_mp(50) == 10
        assert calculate_mp(45) == 9
        assert calculate_mp(5) == 1
        assert calculate_mp(0) == 0

    def test_resolve_spell_cast_with_sufficient_mp_succeeds(self):
        result = resolve_spell_cast(
            spell_key="energy_bolt",
            caster_name="TestCaster",
            caster_int=50,
            caster_pow=50,
            caster_spellcast=30,
            caster_cthulhu_mythos=0,
            caster_mp=20,
            caster_max_mp=20,
            rolled=30,
        )
        assert result.success is True

    def test_resolve_spell_cast_with_insufficient_mp_fails_gracefully(self):
        result = resolve_spell_cast(
            spell_key="contact_cthulhu",
            caster_name="TestCaster",
            caster_int=50,
            caster_pow=50,
            caster_spellcast=30,
            caster_cthulhu_mythos=85,
            caster_mp=5,
            caster_max_mp=20,
            rolled=10,
        )
        assert result.success is False
        assert "魔法点不足" in result.rendered


class TestSkillCheckResolution:
    """Task 6: Test skill check resolution with COC 7e rules."""

    def test_resolve_skill_check_success_when_roll_lte_skill(self):
        result = resolve_skill_check(
            skill_key="fighting",
            skill_value=50,
            rolled=30,
        )
        assert result.success is True

    def test_resolve_skill_check_failure_when_roll_gt_skill(self):
        result = resolve_skill_check(
            skill_key="fighting",
            skill_value=50,
            rolled=60,
        )
        assert result.success is False

    def test_resolve_skill_check_roll_1_is_critical(self):
        result = resolve_skill_check(
            skill_key="fighting",
            skill_value=50,
            rolled=1,
        )
        assert result.critical is True
        assert result.success is True
        assert result.success_rank == SuccessRank.CRITICAL

    def test_resolve_skill_check_roll_100_is_fumble(self):
        result = resolve_skill_check(
            skill_key="fighting",
            skill_value=50,
            rolled=100,
        )
        assert result.fumble is True
        assert result.success is False
        assert result.success_rank == SuccessRank.FUMBLE

    def test_resolve_skill_check_roll_96_with_skill_50_is_fumble(self):
        result = resolve_skill_check(
            skill_key="dodge",
            skill_value=50,
            rolled=96,
        )
        assert result.fumble is True
        assert result.success_rank == SuccessRank.FUMBLE

    def test_resolve_skill_check_roll_96_with_skill_49_is_not_fumble(self):
        result = resolve_skill_check(
            skill_key="spot_hidden",
            skill_value=49,
            rolled=96,
        )
        assert result.fumble is False
        assert result.success is False
        assert result.success_rank == SuccessRank.FAILURE

    def test_resolve_skill_check_difficulty_hard_halves_threshold(self):
        result = resolve_skill_check(
            skill_key="fighting",
            skill_value=50,
            rolled=25,
            difficulty="hard",
        )
        assert result.success is True
        assert result.success_rank == SuccessRank.HARD

    def test_resolve_skill_check_difficulty_extreme_fifths_threshold(self):
        result = resolve_skill_check(
            skill_key="fighting",
            skill_value=50,
            rolled=10,
            difficulty="extreme",
        )
        assert result.success is True
        assert result.success_rank == SuccessRank.EXTREME

    def test_success_rank_enum_values_are_correct(self):
        assert SuccessRank.CRITICAL == "critical"
        assert SuccessRank.EXTREME == "extreme"
        assert SuccessRank.HARD == "hard"
        assert SuccessRank.REGULAR == "regular"
        assert SuccessRank.FAILURE == "failure"
        assert SuccessRank.FUMBLE == "fumble"
