"""COC 7th Edition Rules Module

Complete COC rules engine implementation including:
- Skills: 80+ skills with percentile check resolution
- Combat: Initiative, fighting, shooting, dodge, damage with DB
- Sanity: Loss, madness, phobia/mania, recovery
- Magic: Spells, casting, MP costs, Cthulhu Mythos
- Derived Attributes: HP, MP, Luck, MOV, Build, DB
- Experience: Skill improvement, occupational/interest points

Usage:
    from dm_bot.rules.coc import (
        # Skills
        resolve_skill_check, COC_SKILLS, SkillCategory,
        # Combat
        resolve_fighting_attack, resolve_shooting_attack, calculate_damage_bonus,
        # Sanity
        resolve_sanity_check, roll_insanity_break, calculate_sanity_recovery,
        # Magic
        resolve_spell_cast, COC_SPELLS, Spellbook,
        # Derived
        calculate_all_derived_attributes, apply_age_modifiers,
        # Experience
        roll_skill_improvement, calculate_new_session_skill_points,
    )
"""

# =============================================================================
# Skills Module
# =============================================================================
from dm_bot.rules.coc.skills import (
    SkillCategory,
    SkillDefinition,
    COC_SKILLS,
    SuccessRank,
    SkillCheckResult,
    resolve_skill_check,
    get_skills_by_category,
    get_skill_categories,
    is_specialized_skill,
    expand_specialized_skill,
    get_skill_display_name,
    OCCUPATIONAL_SKILL_POINTS,
    INTEREST_SKILL_POINTS,
    IMPROVEMENT_SKILL_POINTS,
)

# =============================================================================
# Combat Module
# =============================================================================
from dm_bot.rules.coc.combat import (
    CombatAction,
    WeaponType,
    CombatantStats,
    CombatCheckResult,
    roll_initiative,
    get_initiative_order,
    resolve_fighting_attack,
    resolve_shooting_attack,
    resolve_brawl_attack,
    resolve_grapple_attack,
    calculate_build,
    calculate_damage_bonus,
    get_damage_bonus_string,
    RANGE_MODIFIERS,
    get_range_modifier,
)

# =============================================================================
# Sanity Module
# =============================================================================
from dm_bot.rules.coc.sanity import (
    SanityLossType,
    InsanityType,
    COMMON_PHOBIAS,
    COMMON_MANIAS,
    SanityCheckResult,
    InsanityBreakResult,
    get_mythos_gain_for_encounter,
    get_sanity_loss_for_encounter,
    roll_insanity_break,
    resolve_sanity_check,
    calculate_sanity_recovery,
    spend_luck_for_sanity,
)

# =============================================================================
# Magic Module
# =============================================================================
from dm_bot.rules.coc.magic import (
    SpellSchool,
    SpellType,
    SpellDefinition,
    COC_SPELLS,
    SpellCastResult,
    SpellbookEntry,
    Spellbook,
    resolve_spell_cast,
    calculate_mp,
    get_mp_for_level,
)

# =============================================================================
# Derived Attributes Module
# =============================================================================
from dm_bot.rules.coc.derived import (
    DerivedAttributes,
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

# =============================================================================
# Experience Module
# =============================================================================
from dm_bot.rules.coc.experience import (
    CREDIT_RATING_OCCUPATIONAL_POINTS,
    INT_INTEREST_POINTS,
    SkillImprovementResult,
    roll_skill_improvement,
    roll_all_skill_improvements,
    NewSessionSkillPoints,
    calculate_new_session_skill_points,
    CharacterAdvancement,
    spend_occupational_point,
    spend_interest_point,
    STANDARD_BUILD_POINTS,
    calculate_build_points_spent,
    generate_standard_characteristics,
    OCCUPATION_SKILL_SUGGESTIONS,
    get_occupation_skills,
    get_occupational_skill_points,
    get_interest_skill_points,
)

__all__ = [
    # Skills
    "SkillCategory",
    "SkillDefinition",
    "COC_SKILLS",
    "SuccessRank",
    "SkillCheckResult",
    "resolve_skill_check",
    "get_skills_by_category",
    "get_skill_categories",
    "is_specialized_skill",
    "expand_specialized_skill",
    "get_skill_display_name",
    "OCCUPATIONAL_SKILL_POINTS",
    "INTEREST_SKILL_POINTS",
    "IMPROVEMENT_SKILL_POINTS",
    # Combat
    "CombatAction",
    "WeaponType",
    "CombatantStats",
    "CombatCheckResult",
    "roll_initiative",
    "get_initiative_order",
    "resolve_fighting_attack",
    "resolve_shooting_attack",
    "resolve_brawl_attack",
    "resolve_grapple_attack",
    "calculate_build",
    "calculate_damage_bonus",
    "get_damage_bonus_string",
    "RANGE_MODIFIERS",
    "get_range_modifier",
    # Sanity
    "SanityLossType",
    "InsanityType",
    "COMMON_PHOBIAS",
    "COMMON_MANIAS",
    "SanityCheckResult",
    "InsanityBreakResult",
    "get_mythos_gain_for_encounter",
    "get_sanity_loss_for_encounter",
    "roll_insanity_break",
    "resolve_sanity_check",
    "calculate_sanity_recovery",
    "spend_luck_for_sanity",
    # Magic
    "SpellSchool",
    "SpellType",
    "SpellDefinition",
    "COC_SPELLS",
    "SpellCastResult",
    "SpellbookEntry",
    "Spellbook",
    "resolve_spell_cast",
    "calculate_mp",
    "get_mp_for_level",
    # Derived
    "DerivedAttributes",
    "calculate_luck",
    "calculate_hp",
    "calculate_mp",
    "calculate_sanity",
    "calculate_move_rate",
    "calculate_build",
    "calculate_damage_bonus",
    "get_damage_bonus_dice_expression",
    "calculate_all_derived_attributes",
    "get_age_modifiers",
    "apply_age_modifiers",
    "roll_characteristic",
    "generate_characteristics",
    "spend_luck",
    "recover_luck",
    # Experience
    "CREDIT_RATING_OCCUPATIONAL_POINTS",
    "INT_INTEREST_POINTS",
    "SkillImprovementResult",
    "roll_skill_improvement",
    "roll_all_skill_improvements",
    "NewSessionSkillPoints",
    "calculate_new_session_skill_points",
    "CharacterAdvancement",
    "spend_occupational_point",
    "spend_interest_point",
    "STANDARD_BUILD_POINTS",
    "calculate_build_points_spent",
    "generate_standard_characteristics",
    "OCCUPATION_SKILL_SUGGESTIONS",
    "get_occupation_skills",
    "get_occupational_skill_points",
    "get_interest_skill_points",
]
