"""COC 7th Edition Skill System.

This module provides:
- COC_SKILLS database with 80+ COC7 skills
- Helper functions for skill lookup and filtering

Note: SkillCategory and SkillEntry are defined in skill_types.py
to avoid circular imports with dm_bot.characters.models.
"""

from dm_bot.characters.skill_types import SkillCategory, SkillEntry


def get_skill_by_name(skills: list[SkillEntry], name: str) -> SkillEntry | None:
    """Find a skill by exact name match, then fuzzy match.

    Args:
        skills: List of skill entries to search
        name: Skill name to find

    Returns:
        Matching SkillEntry or None if not found
    """
    # Exact match first
    for skill in skills:
        if skill.name == name:
            return skill
    # Fuzzy match (case-insensitive)
    name_lower = name.lower()
    for skill in skills:
        if skill.name.lower() == name_lower:
            return skill
        # Handle Chinese/English aliases
        if skill.name.lower() in name_lower or name_lower in skill.name.lower():
            return skill
    return None


def get_skills_by_category(
    skills: list[SkillEntry], category: SkillCategory
) -> list[SkillEntry]:
    """Filter skills by category.

    Args:
        skills: List of skill entries
        category: Category to filter by

    Returns:
        List of skills in the specified category
    """
    return [s for s in skills if s.category == category]


def _make_skill(
    name: str,
    category: SkillCategory,
    *,
    value: int = 15,
    specialization: str | None = None,
    is_language: bool = False,
    is_derived: bool = False,
    default_value: int | None = None,
) -> SkillEntry:
    """Helper to create a SkillEntry with defaults."""
    return SkillEntry(
        name=name,
        value=value,
        category=category,
        specialization=specialization,
        is_language=is_language,
        is_derived=is_derived,
        default_value=default_value if default_value is not None else value,
    )


# =============================================================================
# COC 7th Edition Skill Database (80+ skills)
# =============================================================================

COC_SKILLS: list[SkillEntry] = [
    # -------------------------------------------------------------------------
    # COMBAT Skills
    # -------------------------------------------------------------------------
    # Fighting with specializations (use FIGHTSPEC category for specializations)
    _make_skill(
        "Fighting (Brawl)", SkillCategory.FIGHTSPEC, value=25, specialization="Brawl"
    ),
    _make_skill(
        "Fighting (Sword)", SkillCategory.FIGHTSPEC, value=25, specialization="Sword"
    ),
    _make_skill(
        "Fighting (Axe)", SkillCategory.FIGHTSPEC, value=20, specialization="Axe"
    ),
    _make_skill(
        "Fighting (Spear)", SkillCategory.FIGHTSPEC, value=20, specialization="Spear"
    ),
    # Shooting with specializations
    _make_skill(
        "Shooting (Handgun)", SkillCategory.COMBAT, value=25, specialization="Handgun"
    ),
    _make_skill(
        "Shooting (Rifle/Shotgun)",
        SkillCategory.COMBAT,
        value=25,
        specialization="Rifle/Shotgun",
    ),
    _make_skill("Shooting (SMG)", SkillCategory.COMBAT, value=20, specialization="SMG"),
    # Other combat
    _make_skill("Brawl", SkillCategory.COMBAT, value=25),
    _make_skill("Grapple", SkillCategory.COMBAT, value=20),
    _make_skill("Dodge", SkillCategory.COMBAT, value=25),  # DEX×2
    # Firearms (alternative names)
    _make_skill(
        "Firearms (Handgun)", SkillCategory.COMBAT, value=25, specialization="Handgun"
    ),
    _make_skill(
        "Firearms (Rifle)", SkillCategory.COMBAT, value=25, specialization="Rifle"
    ),
    # -------------------------------------------------------------------------
    # PERCEPTION Skills
    # -------------------------------------------------------------------------
    _make_skill("Spot Hidden", SkillCategory.PERCEPTION, value=25),  # INT×5
    _make_skill("Listen", SkillCategory.PERCEPTION, value=25),  # POW×5
    _make_skill("Search", SkillCategory.PERCEPTION, value=25),  # INT×5
    _make_skill("Sense", SkillCategory.PERCEPTION, value=20),  # POW×5
    # Chinese names for common perception checks
    _make_skill("侦查", SkillCategory.PERCEPTION, value=25),  # Spot Hidden
    _make_skill("侦察", SkillCategory.PERCEPTION, value=25),  # Spot Hidden (alternate)
    _make_skill("聆听", SkillCategory.PERCEPTION, value=25),  # Listen
    _make_skill("感知", SkillCategory.PERCEPTION, value=20),  # Sense
    # -------------------------------------------------------------------------
    # KNOWLEDGE Skills
    # -------------------------------------------------------------------------
    _make_skill("Accounting", SkillCategory.KNOWLEDGE, value=25),  # INT×5
    _make_skill("Anthropology", SkillCategory.KNOWLEDGE, value=10),  # INT×5
    _make_skill("Archaeology", SkillCategory.KNOWLEDGE, value=10),  # INT×5
    _make_skill("Art", SkillCategory.KNOWLEDGE, value=20),  # INT×5
    _make_skill("Charm", SkillCategory.KNOWLEDGE, value=25),  # APP×5
    _make_skill("Climbing", SkillCategory.KNOWLEDGE, value=20),  # (STR+DEX)×5/2
    _make_skill("Cops And Robbers", SkillCategory.KNOWLEDGE, value=20),  # INT×5
    _make_skill("Craft", SkillCategory.CRFT, value=20),  # INT×5
    _make_skill("Disguise", SkillCategory.KNOWLEDGE, value=20),  # APP×5
    _make_skill("Diving", SkillCategory.MOTION, value=20),  # (STR+CON)×5/2
    _make_skill("Drive Auto", SkillCategory.MOTION, value=20),  # DEX×5
    _make_skill("Elec Repair", SkillCategory.CRFT, value=20),  # INT×5
    _make_skill("Electronics", SkillCategory.CRFT, value=20),  # INT×5
    _make_skill("Fast Talk", SkillCategory.COMMUNICATION, value=20),  # APP×5
    _make_skill("First Aid", SkillCategory.KNOWLEDGE, value=20),  # (DEX+INT)×5/2
    _make_skill("History", SkillCategory.KNOWLEDGE, value=25),  # INT×5
    _make_skill("Intimidate", SkillCategory.COMMUNICATION, value=20),  # (STR+APP)×5/2
    _make_skill("Jump", SkillCategory.MOTION, value=20),  # (STR+DEX)×5/2
    _make_skill("Law", SkillCategory.KNOWLEDGE, value=20),  # INT×5
    _make_skill("Library Use", SkillCategory.KNOWLEDGE, value=25),  # INT×5
    _make_skill("Locksmith", SkillCategory.CRFT, value=15),  # DEX×5
    _make_skill("Mech Repair", SkillCategory.CRFT, value=20),  # INT×5
    _make_skill("Medicine", SkillCategory.KNOWLEDGE, value=10),  # INT×5
    _make_skill("Natural World", SkillCategory.KNOWLEDGE, value=20),  # INT×5
    _make_skill("Navigate", SkillCategory.PERCEPTION, value=20),  # (POW+INT)×5/2
    _make_skill("Occult", SkillCategory.KNOWLEDGE, value=15),  # INT×5
    _make_skill("Operate Heavy Machinery", SkillCategory.MOTION, value=20),  # DEX×5
    _make_skill("Persuade", SkillCategory.COMMUNICATION, value=25),  # APP×5
    _make_skill("Pilot", SkillCategory.MOTION, value=20),  # DEX×5
    _make_skill("Psychoanalysis", SkillCategory.KNOWLEDGE, value=10),  # INT×5
    _make_skill("Psychology", SkillCategory.KNOWLEDGE, value=20),  # INT×5
    _make_skill("Ride", SkillCategory.MOTION, value=20),  # DEX×5
    _make_skill("Sleight of Hand", SkillCategory.CRFT, value=15),  # DEX×5
    _make_skill("Stealth", SkillCategory.MOTION, value=20),  # DEX×5
    _make_skill("Survival", SkillCategory.PERCEPTION, value=20),  # (POW+INT)×5/2
    _make_skill("Swim", SkillCategory.MOTION, value=20),  # (STR+CON)×5/2
    _make_skill("Throw", SkillCategory.MOTION, value=20),  # DEX×5
    _make_skill("Track", SkillCategory.PERCEPTION, value=20),  # (INT+POW)×5/2
    # -------------------------------------------------------------------------
    # LANGUAGE Skills
    # -------------------------------------------------------------------------
    _make_skill(
        "Language (Own)", SkillCategory.LANGUAGE, value=25, is_derived=True
    ),  # EDU×5
    _make_skill("Language (Other)", SkillCategory.LANGUAGE, value=1, is_language=True),
    _make_skill(
        "母语", SkillCategory.LANGUAGE, value=25, is_derived=True
    ),  # Own Language
    _make_skill("中文", SkillCategory.LANGUAGE, value=25, is_language=True),
    _make_skill("English", SkillCategory.LANGUAGE, value=20, is_language=True),
    _make_skill("Latin", SkillCategory.LANGUAGE, value=15, is_language=True),
    _make_skill("Greek", SkillCategory.LANGUAGE, value=10, is_language=True),
    _make_skill("Arabic", SkillCategory.LANGUAGE, value=10, is_language=True),
    _make_skill("Japanese", SkillCategory.LANGUAGE, value=10, is_language=True),
    _make_skill("Spanish", SkillCategory.LANGUAGE, value=10, is_language=True),
    _make_skill("French", SkillCategory.LANGUAGE, value=10, is_language=True),
    _make_skill("German", SkillCategory.LANGUAGE, value=10, is_language=True),
    # -------------------------------------------------------------------------
    # Communication Skills (additional)
    # -------------------------------------------------------------------------
    _make_skill("说服", SkillCategory.COMMUNICATION, value=25),  # Persuade
    _make_skill("魅惑", SkillCategory.COMMUNICATION, value=25),  # Charm
    _make_skill("胁迫", SkillCategory.COMMUNICATION, value=20),  # Intimidate
    _make_skill("话术", SkillCategory.COMMUNICATION, value=20),  # Fast Talk
    _make_skill("威胁", SkillCategory.COMMUNICATION, value=20),  # Intimidate
    # -------------------------------------------------------------------------
    # Craft/Trade Skills
    # -------------------------------------------------------------------------
    _make_skill("Art (Painting)", SkillCategory.CRFT, value=20),
    _make_skill("Art (Sculpture)", SkillCategory.CRFT, value=15),
    _make_skill("Art (Photography)", SkillCategory.CRFT, value=20),
    _make_skill("Craft (Carpentry)", SkillCategory.CRFT, value=20),
    _make_skill("Craft (Leatherwork)", SkillCategory.CRFT, value=15),
    _make_skill("Craft (Metalwork)", SkillCategory.CRFT, value=10),
    _make_skill("Craft (Electrical)", SkillCategory.CRFT, value=15),
    # -------------------------------------------------------------------------
    # Additional COC7 Skills
    # -------------------------------------------------------------------------
    _make_skill("Accounting", SkillCategory.KNOWLEDGE, value=25),
    _make_skill("Anthropology", SkillCategory.KNOWLEDGE, value=10),
    _make_skill("Archaeology", SkillCategory.KNOWLEDGE, value=10),
    _make_skill("Charm", SkillCategory.COMMUNICATION, value=25),
    _make_skill("Climb", SkillCategory.MOTION, value=20),
    _make_skill("Cops And Robbers", SkillCategory.KNOWLEDGE, value=20),
    _make_skill("Disguise", SkillCategory.COMMUNICATION, value=20),
    _make_skill("Dodge", SkillCategory.COMBAT, value=25),
    _make_skill("Drive Auto", SkillCategory.MOTION, value=20),
    _make_skill("Elec Repair", SkillCategory.CRFT, value=20),
    _make_skill("Fight", SkillCategory.COMBAT, value=25),
    _make_skill("Fine Manual", SkillCategory.CRFT, value=15),
    _make_skill("Firearm", SkillCategory.COMBAT, value=25),
    _make_skill("First Aid", SkillCategory.KNOWLEDGE, value=20),
    _make_skill("History", SkillCategory.KNOWLEDGE, value=25),
    _make_skill("Insight", SkillCategory.PERCEPTION, value=20),
    _make_skill("Intimidate", SkillCategory.COMMUNICATION, value=20),
    _make_skill("Jump", SkillCategory.MOTION, value=20),
    _make_skill("Language (Own)", SkillCategory.LANGUAGE, value=25, is_derived=True),
    _make_skill("Language (Other)", SkillCategory.LANGUAGE, value=1, is_language=True),
    _make_skill("Law", SkillCategory.KNOWLEDGE, value=20),
    _make_skill("Library", SkillCategory.KNOWLEDGE, value=25),
    _make_skill("Listen", SkillCategory.PERCEPTION, value=25),
    _make_skill("Locksmith", SkillCategory.CRFT, value=15),
    _make_skill("Mech Repair", SkillCategory.CRFT, value=20),
    _make_skill("Medicine", SkillCategory.KNOWLEDGE, value=10),
    _make_skill("Natural World", SkillCategory.KNOWLEDGE, value=20),
    _make_skill("Navigate", SkillCategory.PERCEPTION, value=20),
    _make_skill("Occult", SkillCategory.KNOWLEDGE, value=15),
    _make_skill("Operate Heavy Machine", SkillCategory.MOTION, value=15),
    _make_skill("Persuade", SkillCategory.COMMUNICATION, value=25),
    _make_skill("Pilot", SkillCategory.MOTION, value=20),
    _make_skill("Psychoanalysis", SkillCategory.KNOWLEDGE, value=10),
    _make_skill("Psychology", SkillCategory.PERCEPTION, value=20),
    _make_skill("Ride", SkillCategory.MOTION, value=20),
    _make_skill("Search", SkillCategory.PERCEPTION, value=25),
    _make_skill("Sense", SkillCategory.PERCEPTION, value=20),
    _make_skill("Sleight of Hand", SkillCategory.CRFT, value=15),
    _make_skill("Spot Hidden", SkillCategory.PERCEPTION, value=25),
    _make_skill("Stealth", SkillCategory.MOTION, value=20),
    _make_skill("Survival", SkillCategory.PERCEPTION, value=20),
    _make_skill("Swim", SkillCategory.MOTION, value=20),
    _make_skill("Throw", SkillCategory.MOTION, value=20),
    _make_skill("Track", SkillCategory.PERCEPTION, value=20),
]


# Export public interface
__all__ = [
    "SkillCategory",
    "SkillEntry",
    "COC_SKILLS",
    "get_skill_by_name",
    "get_skills_by_category",
]
