"""COC 7th Edition Skill System

Complete skill definitions, categories, and skill check resolution.
Reference: Call of Cthulhu 7th Edition Keeper's Rulebook
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


# =============================================================================
# Skill Categories
# =============================================================================


class SkillCategory(StrEnum):
    """COC 7th Edition skill categories."""

    COMBAT = "combat"  # Fighting, Shooting, Brawl, Dodge, Throw, Grapple
    LANGUAGE = "language"  # Own Language, other languages
    KNOWLEDGE = "knowledge"  # Academic and professional knowledge
    INTERPERSONAL = "interpersonal"  # Charm, Fast Talk, Intimidate, Persuade
    OBSERVATION = "observation"  # Listen, Spot Hidden, etc.
    PRACTICAL = "practical"  # Climb, Jump, Repair skills, etc.
    CRAFT = "craft"  # Art/Craft specialized skills
    MAGIC = "magic"  # Spellcast, Cthulhu Mythos
    COMBAT_SPECIALTY = "combat_specialty"  # Specialized fighting/shooting types


# =============================================================================
# Complete Skill Definitions (COC 7th Edition - 80+ skills)
# =============================================================================


class SkillDefinition(BaseModel):
    """Definition of a single COC skill."""

    name: str  # English name
    name_cn: str  # Chinese name
    category: SkillCategory
    base_points: int = 0  # Base starting points (usually 0 for most skills)
    occupational: bool = True  # Can be improved with occupational points
    interest: bool = True  # Can be improved with interest points
    specialized: bool = False  # Has subtypes (e.g., Fighting: Brawling, Sword)
    subtypes: list[str] = Field(default_factory=list)  # Available specializations


# Complete skill dictionary - COC 7th Edition standard skills
COC_SKILLS: dict[str, SkillDefinition] = {
    # -------------------------------------------------------------------------
    # COMBAT SKILLS
    # -------------------------------------------------------------------------
    "fighting": SkillDefinition(
        name="Fighting",
        name_cn="格斗",
        category=SkillCategory.COMBAT,
        base_points=25,
        subtypes=["Brawling", "Sword", "Axe", "Spear", "Other"],
    ),
    "shooting": SkillDefinition(
        name="Shooting",
        name_cn="射击",
        category=SkillCategory.COMBAT,
        base_points=20,
        subtypes=["Handgun", "Rifle/Shotgun", "SMG", "Bow", "Other"],
    ),
    "brawl": SkillDefinition(
        name="Brawl",
        name_cn="斗殴",
        category=SkillCategory.COMBAT,
        base_points=25,
        occupational=False,
    ),
    "dodge": SkillDefinition(
        name="Dodge",
        name_cn="闪避",
        category=SkillCategory.COMBAT,
        base_points=25,
        occupational=False,
    ),
    "throw": SkillDefinition(
        name="Throw",
        name_cn="投掷",
        category=SkillCategory.COMBAT,
        base_points=20,
        occupational=False,
    ),
    "grapple": SkillDefinition(
        name="Grapple",
        name_cn="摔跤",
        category=SkillCategory.COMBAT,
        base_points=15,
        occupational=False,
    ),
    # -------------------------------------------------------------------------
    # LANGUAGE SKILLS
    # -------------------------------------------------------------------------
    "language_own": SkillDefinition(
        name="Own Language",
        name_cn="母语",
        category=SkillCategory.LANGUAGE,
        base_points=25,
        occupational=False,
        subtypes=[],  # Native language has no subtypes
    ),
    "language_english": SkillDefinition(
        name="English",
        name_cn="英语",
        category=SkillCategory.LANGUAGE,
        base_points=20,
    ),
    "language_arabic": SkillDefinition(
        name="Arabic",
        name_cn="阿拉伯语",
        category=SkillCategory.LANGUAGE,
        base_points=10,
    ),
    "language_chinese": SkillDefinition(
        name="Chinese",
        name_cn="汉语",
        category=SkillCategory.LANGUAGE,
        base_points=20,
    ),
    "language_french": SkillDefinition(
        name="French",
        name_cn="法语",
        category=SkillCategory.LANGUAGE,
        base_points=15,
    ),
    "language_german": SkillDefinition(
        name="German",
        name_cn="德语",
        category=SkillCategory.LANGUAGE,
        base_points=15,
    ),
    "language_greek": SkillDefinition(
        name="Greek",
        name_cn="希腊语",
        category=SkillCategory.LANGUAGE,
        base_points=10,
    ),
    "language_hebrew": SkillDefinition(
        name="Hebrew",
        name_cn="希伯来语",
        category=SkillCategory.LANGUAGE,
        base_points=10,
    ),
    "language_hindi": SkillDefinition(
        name="Hindi",
        name_cn="印地语",
        category=SkillCategory.LANGUAGE,
        base_points=10,
    ),
    "language_italian": SkillDefinition(
        name="Italian",
        name_cn="意大利语",
        category=SkillCategory.LANGUAGE,
        base_points=10,
    ),
    "language_japanese": SkillDefinition(
        name="Japanese",
        name_cn="日语",
        category=SkillCategory.LANGUAGE,
        base_points=10,
    ),
    "language_korean": SkillDefinition(
        name="Korean",
        name_cn="韩语",
        category=SkillCategory.LANGUAGE,
        base_points=10,
    ),
    "language_latin": SkillDefinition(
        name="Latin",
        name_cn="拉丁语",
        category=SkillCategory.LANGUAGE,
        base_points=10,
    ),
    "language_portuguese": SkillDefinition(
        name="Portuguese",
        name_cn="葡萄牙语",
        category=SkillCategory.LANGUAGE,
        base_points=10,
    ),
    "language_russian": SkillDefinition(
        name="Russian",
        name_cn="俄语",
        category=SkillCategory.LANGUAGE,
        base_points=10,
    ),
    "language_spanish": SkillDefinition(
        name="Spanish",
        name_cn="西班牙语",
        category=SkillCategory.LANGUAGE,
        base_points=15,
    ),
    "language_other": SkillDefinition(
        name="Other Language",
        name_cn="其他语言",
        category=SkillCategory.LANGUAGE,
        base_points=1,
        subtypes=["Any specific language"],
    ),
    # -------------------------------------------------------------------------
    # KNOWLEDGE SKILLS
    # -------------------------------------------------------------------------
    "accounting": SkillDefinition(
        name="Accounting",
        name_cn="会计",
        category=SkillCategory.KNOWLEDGE,
        base_points=10,
    ),
    "anthropology": SkillDefinition(
        name="Anthropology",
        name_cn="人类学",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
    ),
    "archaeology": SkillDefinition(
        name="Archaeology",
        name_cn="考古学",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
    ),
    "cthulhu_mythos": SkillDefinition(
        name="Cthulhu Mythos",
        name_cn="克苏鲁神话",
        category=SkillCategory.KNOWLEDGE,
        base_points=0,
        occupational=False,
        interest=False,
    ),
    "history": SkillDefinition(
        name="History",
        name_cn="历史",
        category=SkillCategory.KNOWLEDGE,
        base_points=10,
    ),
    "law": SkillDefinition(
        name="Law",
        name_cn="法律",
        category=SkillCategory.KNOWLEDGE,
        base_points=5,
    ),
    "medicine": SkillDefinition(
        name="Medicine",
        name_cn="医学",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
    ),
    "occult": SkillDefinition(
        name="Occult",
        name_cn="神秘学",
        category=SkillCategory.KNOWLEDGE,
        base_points=5,
    ),
    "politics": SkillDefinition(
        name="Politics",
        name_cn="政治",
        category=SkillCategory.KNOWLEDGE,
        base_points=5,
    ),
    "psychoanalysis": SkillDefinition(
        name="Psychoanalysis",
        name_cn="心理分析",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
    ),
    "psychology": SkillDefinition(
        name="Psychology",
        name_cn="心理学",
        category=SkillCategory.KNOWLEDGE,
        base_points=10,
    ),
    "science": SkillDefinition(
        name="Science",
        name_cn="科学",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
        subtypes=[
            "Biology",
            "Chemistry",
            "Physics",
            "Astronomy",
            "Geology",
            "Mathematics",
        ],
    ),
    # -------------------------------------------------------------------------
    # INTERPERSONAL SKILLS
    # -------------------------------------------------------------------------
    "charm": SkillDefinition(
        name="Charm",
        name_cn="魅惑",
        category=SkillCategory.INTERPERSONAL,
        base_points=15,
        occupational=False,
    ),
    "fast_talk": SkillDefinition(
        name="Fast Talk",
        name_cn="快速交谈",
        category=SkillCategory.INTERPERSONAL,
        base_points=5,
        occupational=False,
    ),
    "intimidate": SkillDefinition(
        name="Intimidate",
        name_cn="恐吓",
        category=SkillCategory.INTERPERSONAL,
        base_points=15,
        occupational=False,
    ),
    "persuade": SkillDefinition(
        name="Persuade",
        name_cn="说服",
        category=SkillCategory.INTERPERSONAL,
        base_points=10,
        occupational=False,
    ),
    "leadership": SkillDefinition(
        name="Leadership",
        name_cn="领导力",
        category=SkillCategory.INTERPERSONAL,
        base_points=10,
        occupational=False,
    ),
    "appraise": SkillDefinition(
        name="Appraise",
        name_cn="鉴定",
        category=SkillCategory.INTERPERSONAL,
        base_points=10,
        occupational=False,
    ),
    # -------------------------------------------------------------------------
    # OBSERVATION SKILLS
    # -------------------------------------------------------------------------
    "listen": SkillDefinition(
        name="Listen",
        name_cn="聆听",
        category=SkillCategory.OBSERVATION,
        base_points=20,
        occupational=False,
    ),
    "spot_hidden": SkillDefinition(
        name="Spot Hidden",
        name_cn="侦查",
        category=SkillCategory.OBSERVATION,
        base_points=25,
        occupational=False,
    ),
    "search": SkillDefinition(
        name="Search",
        name_cn="搜查",
        category=SkillCategory.OBSERVATION,
        base_points=20,
        occupational=False,
    ),
    "track": SkillDefinition(
        name="Track",
        name_cn="追踪",
        category=SkillCategory.OBSERVATION,
        base_points=10,
    ),
    # -------------------------------------------------------------------------
    # PRACTICAL SKILLS
    # -------------------------------------------------------------------------
    "climb": SkillDefinition(
        name="Climb",
        name_cn="攀爬",
        category=SkillCategory.PRACTICAL,
        base_points=20,
        occupational=False,
    ),
    "jump": SkillDefinition(
        name="Jump",
        name_cn="跳跃",
        category=SkillCategory.PRACTICAL,
        base_points=20,
        occupational=False,
    ),
    "swim": SkillDefinition(
        name="Swim",
        name_cn="游泳",
        category=SkillCategory.PRACTICAL,
        base_points=20,
        occupational=False,
    ),
    "drive_auto": SkillDefinition(
        name="Drive Auto",
        name_cn="驾驶汽车",
        category=SkillCategory.PRACTICAL,
        base_points=20,
        occupational=False,
    ),
    "pilot": SkillDefinition(
        name="Pilot",
        name_cn="驾驶",
        category=SkillCategory.PRACTICAL,
        base_points=1,
        subtypes=["Boat", "Aircraft", "Hovercraft", "Other"],
    ),
    "navigate": SkillDefinition(
        name="Navigate",
        name_cn="导航",
        category=SkillCategory.PRACTICAL,
        base_points=10,
    ),
    "survival": SkillDefinition(
        name="Survival",
        name_cn="生存",
        category=SkillCategory.PRACTICAL,
        base_points=10,
        subtypes=[
            "Arctic",
            "Desert",
            "Forest",
            "Island",
            "Jungle",
            "Mountain",
            "Plains",
            "Urban",
        ],
    ),
    "ride": SkillDefinition(
        name="Ride",
        name_cn="骑乘",
        category=SkillCategory.PRACTICAL,
        base_points=10,
        subtypes=["Horse", "Camel", "Elephant", "Other"],
    ),
    "sleight_of_hand": SkillDefinition(
        name="Sleight of Hand",
        name_cn="巧手",
        category=SkillCategory.PRACTICAL,
        base_points=10,
        occupational=False,
    ),
    "stealth": SkillDefinition(
        name="Stealth",
        name_cn="潜行",
        category=SkillCategory.PRACTICAL,
        base_points=20,
        occupational=False,
    ),
    "disguise": SkillDefinition(
        name="Disguise",
        name_cn="伪装",
        category=SkillCategory.PRACTICAL,
        base_points=1,
        occupational=False,
    ),
    "lockpick": SkillDefinition(
        name="Lockpick",
        name_cn="开锁",
        category=SkillCategory.PRACTICAL,
        base_points=1,
        occupational=False,
    ),
    "拆解": SkillDefinition(
        name="拆解",
        name_cn="Disassemble",
        category=SkillCategory.PRACTICAL,
        base_points=1,
        occupational=False,
    ),
    # -------------------------------------------------------------------------
    # REPAIR & TECHNICAL SKILLS
    # -------------------------------------------------------------------------
    "elec_repair": SkillDefinition(
        name="Elec. Repair",
        name_cn="电气维修",
        category=SkillCategory.PRACTICAL,
        base_points=10,
    ),
    "mech_repair": SkillDefinition(
        name="Mech. Repair",
        name_cn="机械维修",
        category=SkillCategory.PRACTICAL,
        base_points=10,
    ),
    "operate_hv_machine": SkillDefinition(
        name="Operate Heavy Machine",
        name_cn="操作重型机械",
        category=SkillCategory.PRACTICAL,
        base_points=1,
    ),
    "computer_use": SkillDefinition(
        name="Computer Use",
        name_cn="计算机使用",
        category=SkillCategory.PRACTICAL,
        base_points=10,
        occupational=False,
    ),
    "hacking": SkillDefinition(
        name="Hacking",
        name_cn="黑客",
        category=SkillCategory.PRACTICAL,
        base_points=1,
        occupational=False,
    ),
    "craft_chemical": SkillDefinition(
        name="Craft (Chemical)",
        name_cn="化学工艺",
        category=SkillCategory.CRAFT,
        base_points=1,
    ),
    "craft_electronic": SkillDefinition(
        name="Craft (Electronic)",
        name_cn="电子工艺",
        category=SkillCategory.CRAFT,
        base_points=1,
    ),
    "craft_mechanical": SkillDefinition(
        name="Craft (Mechanical)",
        name_cn="机械工艺",
        category=SkillCategory.CRAFT,
        base_points=1,
    ),
    "craft_structural": SkillDefinition(
        name="Craft (Structural)",
        name_cn="结构工艺",
        category=SkillCategory.CRAFT,
        base_points=1,
    ),
    # -------------------------------------------------------------------------
    # MEDICAL & FIRST AID
    # -------------------------------------------------------------------------
    "first_aid": SkillDefinition(
        name="First Aid",
        name_cn="急救",
        category=SkillCategory.PRACTICAL,
        base_points=30,
        occupational=False,
    ),
    "pharmacy": SkillDefinition(
        name="Pharmacy",
        name_cn="药学",
        category=SkillCategory.PRACTICAL,
        base_points=1,
    ),
    # -------------------------------------------------------------------------
    # SCIENCE & KNOWLEDGE
    # -------------------------------------------------------------------------
    "biology": SkillDefinition(
        name="Biology",
        name_cn="生物学",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
    ),
    "chemistry": SkillDefinition(
        name="Chemistry",
        name_cn="化学",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
    ),
    "physics": SkillDefinition(
        name="Physics",
        name_cn="物理学",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
    ),
    "astronomy": SkillDefinition(
        name="Astronomy",
        name_cn="天文学",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
    ),
    "geology": SkillDefinition(
        name="Geology",
        name_cn="地质学",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
    ),
    "mathematics": SkillDefinition(
        name="Mathematics",
        name_cn="数学",
        category=SkillCategory.KNOWLEDGE,
        base_points=10,
    ),
    "forensics": SkillDefinition(
        name="Forensics",
        name_cn="法医学",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
    ),
    # -------------------------------------------------------------------------
    # LIBRARY & RESEARCH
    # -------------------------------------------------------------------------
    "library_use": SkillDefinition(
        name="Library Use",
        name_cn="图书馆使用",
        category=SkillCategory.PRACTICAL,
        base_points=20,
        occupational=False,
    ),
    " occult_knowledge": SkillDefinition(
        name="Occult Knowledge",
        name_cn="神秘知识",
        category=SkillCategory.KNOWLEDGE,
        base_points=5,
        occupational=False,
    ),
    # -------------------------------------------------------------------------
    # ART & CRAFT (Creative skills)
    # -------------------------------------------------------------------------
    "art_craft": SkillDefinition(
        name="Art/Craft",
        name_cn="艺术/手艺",
        category=SkillCategory.CRAFT,
        base_points=5,
        subtypes=[
            "Acting",
            "Coding",
            "Cooking",
            "Dancing",
            "Drawing",
            "ETCetera",
            "Marquetry",
            "Modeling",
            "Painting",
            "Photography",
            "Sculpting",
            "Singing",
            "Storytelling",
            "Writing",
            "Other",
        ],
    ),
    "hypnosis": SkillDefinition(
        name="Hypnosis",
        name_cn="催眠",
        category=SkillCategory.PRACTICAL,
        base_points=1,
    ),
    "mesmerism": SkillDefinition(
        name="Mesmerism",
        name_cn="催眠术",
        category=SkillCategory.PRACTICAL,
        base_points=1,
    ),
    # -------------------------------------------------------------------------
    # MAGIC RELATED
    # -------------------------------------------------------------------------
    "spellcast": SkillDefinition(
        name="Spellcast",
        name_cn="法术施放",
        category=SkillCategory.MAGIC,
        base_points=0,
        occupational=False,
    ),
    # -------------------------------------------------------------------------
    # OTHER SKILLS
    # -------------------------------------------------------------------------
    "animal_handling": SkillDefinition(
        name="Animal Handling",
        name_cn="动物驱使",
        category=SkillCategory.PRACTICAL,
        base_points=10,
    ),
    "natural_world": SkillDefinition(
        name="Natural World",
        name_cn="自然世界",
        category=SkillCategory.KNOWLEDGE,
        base_points=10,
    ),
    "plant_lore": SkillDefinition(
        name="Plant Lore",
        name_cn="植物知识",
        category=SkillCategory.KNOWLEDGE,
        base_points=5,
    ),
    "animal_lore": SkillDefinition(
        name="Animal Lore",
        name_cn="动物知识",
        category=SkillCategory.KNOWLEDGE,
        base_points=5,
    ),
    "othe": SkillDefinition(
        name="othe",
        name_cn="oth",
        category=SkillCategory.KNOWLEDGE,
        base_points=1,
    ),
}


# =============================================================================
# Skill Check Result
# =============================================================================


class SuccessRank(StrEnum):
    """COC 7th Edition success ranks."""

    CRITICAL = "critical"  # Roll 01 - exceptional success
    EXTREME = "extreme"  # ≤ 1/5 of skill value
    HARD = "hard"  # ≤ 1/2 of skill value
    REGULAR = "regular"  # ≤ skill value
    FAILURE = "failure"  # > skill value
    FUMBLE = "fumble"  # 96+ when skill ≥50, or 100


class SkillCheckResult(BaseModel):
    """Result of a COC skill check."""

    skill_key: str
    skill_name_cn: str
    skill_value: int
    rolled: int
    success: bool
    success_rank: SuccessRank
    critical: bool = False  # Roll of 01
    fumble: bool = False  # 96+ when value≥50, or 100
    bonus_dice: int = 0
    penalty_dice: int = 0
    pushed: bool = False
    difficulty: Literal["regular", "hard", "extreme"] = "regular"
    rendered: str = ""


# =============================================================================
# Skill Check Resolver
# =============================================================================


def resolve_skill_check(
    skill_key: str,
    skill_value: int,
    rolled: int,
    bonus_dice: int = 0,
    penalty_dice: int = 0,
    difficulty: Literal["regular", "hard", "extreme"] = "regular",
    pushed: bool = False,
) -> SkillCheckResult:
    """Resolve a COC skill check.

    Args:
        skill_key: The skill identifier (e.g., "fighting", "shooting")
        skill_value: The investigator's skill value (0-100+)
        rolled: The dice roll result (1-100)
        bonus_dice: Number of bonus dice (keep lowest)
        penalty_dice: Number of penalty dice (keep highest)
        difficulty: Check difficulty
        pushed: Whether this was a pushed roll

    Returns:
        SkillCheckResult with full outcome details
    """
    skill_def = COC_SKILLS.get(skill_key)
    skill_name_cn = skill_def.name_cn if skill_def else skill_key

    # Calculate thresholds
    if difficulty == "extreme":
        threshold = max(1, skill_value // 5)
    elif difficulty == "hard":
        threshold = max(1, skill_value // 2)
    else:  # regular
        threshold = skill_value

    # Determine success and rank
    critical = rolled == 1
    fumble = rolled == 100 or (skill_value >= 50 and rolled >= 96)

    # Critical (01) always succeeds
    if critical:
        success = True
        rank = SuccessRank.CRITICAL
    # Fumble always fails
    elif fumble:
        success = False
        rank = SuccessRank.FUMBLE
    else:
        success = rolled <= threshold
        if success:
            if rolled <= max(1, skill_value // 5):
                rank = SuccessRank.EXTREME
            elif rolled <= max(1, skill_value // 2):
                rank = SuccessRank.HARD
            else:
                rank = SuccessRank.REGULAR
        else:
            rank = SuccessRank.FAILURE

    # Build rendered description
    rank_text = {
        SuccessRank.CRITICAL: "大成功",
        SuccessRank.EXTREME: "成功",
        SuccessRank.HARD: "困难成功",
        SuccessRank.REGULAR: "成功",
        SuccessRank.FAILURE: "失败",
        SuccessRank.FUMBLE: "大失败",
    }[rank]

    bonus_text = ""
    if bonus_dice > 0:
        bonus_text = f" (奖励骰:{bonus_dice})"
    elif penalty_dice > 0:
        bonus_text = f" (惩罚骰:{penalty_dice})"

    if pushed:
        bonus_text += " [强制]"

    rendered = f"{rolled:02d} ≤ {threshold} ({skill_name_cn}{bonus_text}) → {rank_text}"

    return SkillCheckResult(
        skill_key=skill_key,
        skill_name_cn=skill_name_cn,
        skill_value=skill_value,
        rolled=rolled,
        success=success,
        success_rank=rank,
        critical=critical,
        fumble=fumble,
        bonus_dice=bonus_dice,
        penalty_dice=penalty_dice,
        pushed=pushed,
        difficulty=difficulty,
        rendered=rendered,
    )


def get_skills_by_category(category: SkillCategory) -> dict[str, SkillDefinition]:
    """Get all skills in a specific category."""
    return {
        key: skill for key, skill in COC_SKILLS.items() if skill.category == category
    }


def get_skill_categories() -> list[SkillCategory]:
    """Get list of all skill categories."""
    return list(SkillCategory)


# =============================================================================
# Standard Occupation Skill Point Distributions (COC 7th Edition)
# =============================================================================

# Credit Rating determines occupational skill points
OCCUPATIONAL_SKILL_POINTS: dict[int, int] = {
    0: 0,  # None
    9: 10,  # Poor
    19: 15,  # Average
    49: 20,  # Good
    79: 30,  # Great
    99: 40,  # Fantastic
}

# Interest skill points based on INT
INTEREST_SKILL_POINTS: dict[int, int] = {
    0: 0,
    49: 2,
    59: 2,
    69: 3,
    79: 4,
    89: 5,
    99: 6,
    100: 7,  # Exceptional (INT 90+)
}

# EDU-based skill point gains for improvement
IMPROVEMENT_SKILL_POINTS: dict[int, int] = {
    0: 0,
    89: 1,  # INT 90+
    100: 2,  # INT 100+
}


# =============================================================================
# Specialized Skill Handling
# =============================================================================


def is_specialized_skill(skill_key: str) -> bool:
    """Check if a skill has specializations (e.g., Fighting: Sword)."""
    skill = COC_SKILLS.get(skill_key)
    return skill is not None and skill.specialized


def expand_specialized_skill(skill_key: str, specialization: str | None = None) -> str:
    """Expand a specialized skill with its specialization.

    Examples:
        "fighting" + "Sword" -> "fighting_sword"
        "science" + "Biology" -> "science_biology"
    """
    if specialization is None:
        return skill_key

    # Normalize the specialization name
    spec_normalized = specialization.lower().replace(" ", "_")
    return f"{skill_key}_{spec_normalized}"


def get_skill_display_name(skill_key: str, specialization: str | None = None) -> str:
    """Get the full display name of a skill with its specialization."""
    skill = COC_SKILLS.get(skill_key)
    if skill is None:
        return skill_key

    if specialization:
        return f"{skill.name_cn}({specialization})"
    return skill.name_cn
