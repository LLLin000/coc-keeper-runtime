"""COC 7th Edition Experience & Skill Improvement

Complete experience and skill improvement system:
- After-session skill improvement rolls
- Improvement chance: 1d100 < skill → +1d10 improvement
- New occupational skill points each session
- Credit Rating-based occupational point allocation
- INT-based interest skill points

Reference: Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 4
"""

from pydantic import BaseModel, Field


# =============================================================================
# Skill Point Allocations
# =============================================================================

# Credit Rating determines occupational skill points
CREDIT_RATING_OCCUPATIONAL_POINTS: dict[int, int] = {
    0: 0,  # None
    9: 10,  # Poor
    19: 15,  # Average
    49: 20,  # Good
    79: 30,  # Great
    99: 40,  # Fantastic
}

# Interest skill points based on INT
INT_INTEREST_POINTS: dict[int, int] = {
    0: 0,
    49: 2,
    59: 2,
    69: 3,
    79: 4,
    89: 5,
    99: 6,
    100: 7,  # Exceptional (INT 90+)
}


def get_occupational_skill_points(credit_rating: int) -> int:
    """Get occupational skill points from Credit Rating.

    Args:
        credit_rating: Credit Rating value (0-99)

    Returns:
        Number of occupational skill points to distribute
    """
    for threshold, points in sorted(
        CREDIT_RATING_OCCUPATIONAL_POINTS.items(), reverse=True
    ):
        if credit_rating >= threshold:
            return points
    return 0


def get_interest_skill_points(int_value: int) -> int:
    """Get interest skill points from INT.

    Args:
        int_value: Intelligence value (1-100)

    Returns:
        Number of interest skill points to distribute
    """
    for threshold, points in sorted(INT_INTEREST_POINTS.items(), reverse=True):
        if int_value >= threshold:
            return points
    return 0


# =============================================================================
# Skill Improvement Result
# =============================================================================


class SkillImprovementResult(BaseModel):
    """Result of a skill improvement roll."""

    skill_key: str
    skill_name_cn: str
    current_value: int
    improvement_roll: int
    new_value: int
    improved: bool
    rendered: str = ""


# =============================================================================
# Skill Improvement Roll
# =============================================================================


def roll_skill_improvement(
    skill_key: str,
    current_value: int,
    improvement_roll: int | None = None,
) -> SkillImprovementResult:
    """Roll for skill improvement after a session.

    COC7e: After a session, if a skill was used, can attempt improvement.
    - Roll 1d100
    - If roll < current skill value, skill improves by 1d10

    Args:
        skill_key: The skill being improved
        current_value: Current skill value
        improvement_roll: Pre-rolled value (for determinism)

    Returns:
        SkillImprovementResult with outcome
    """
    import random
    from dm_bot.rules.coc.skills import COC_SKILLS

    skill = COC_SKILLS.get(skill_key)
    skill_name = skill.name_cn if skill else skill_key

    # Roll if not provided
    if improvement_roll is None:
        improvement_roll = random.randint(1, 100)

    # Check for improvement
    improved = improvement_roll < current_value

    if improved:
        improvement_amount = random.randint(1, 10)
        new_value = current_value + improvement_amount
    else:
        new_value = current_value

    rendered = f"【技能提升】{skill_name}\n"
    rendered += f"当前技能: {current_value} | 投掷: {improvement_roll:02d}\n"

    if improved:
        rendered += f"成功！技能提升 +{improvement_amount}\n"
        rendered += f"新技能值: {new_value}"
    else:
        rendered += "失败 - 技能未提升"

    return SkillImprovementResult(
        skill_key=skill_key,
        skill_name_cn=skill_name,
        current_value=current_value,
        improvement_roll=improvement_roll,
        new_value=new_value,
        improved=improved,
        rendered=rendered,
    )


def roll_all_skill_improvements(
    skills_used: list[str],
    current_skills: dict[str, int],
    improvement_rolls: dict[str, int] | None = None,
) -> list[SkillImprovementResult]:
    """Roll skill improvements for multiple skills.

    Args:
        skills_used: List of skills that were used during the session
        current_skills: Current skill values as dict
        improvement_rolls: Optional pre-rolled values for each skill

    Returns:
        List of SkillImprovementResult for each skill
    """
    results = []
    rolls = improvement_rolls or {}

    for skill_key in skills_used:
        current_value = current_skills.get(skill_key, 0)
        if current_value > 0:
            roll = rolls.get(skill_key)
            result = roll_skill_improvement(
                skill_key=skill_key,
                current_value=current_value,
                improvement_roll=roll,
            )
            results.append(result)

    return results


# =============================================================================
# New Session Skill Points
# =============================================================================


class NewSessionSkillPoints(BaseModel):
    """Skill points awarded at the start of a new session."""

    occupational_points: int
    interest_points: int
    credit_rating: int
    int_value: int
    total_points: int


def calculate_new_session_skill_points(
    credit_rating: int,
    int_value: int,
) -> NewSessionSkillPoints:
    """Calculate skill points for a new session.

    COC7e: At the start of each session, gain:
    - Occupational points based on Credit Rating
    - Interest points based on INT

    Args:
        credit_rating: Character's Credit Rating
        int_value: Character's INT

    Returns:
        NewSessionSkillPoints with all point allocations
    """
    occ_points = get_occupational_skill_points(credit_rating)
    int_points = get_interest_skill_points(int_value)

    return NewSessionSkillPoints(
        occupational_points=occ_points,
        interest_points=int_points,
        credit_rating=credit_rating,
        int_value=int_value,
        total_points=occ_points + int_points,
    )


# =============================================================================
# Experience Points & Character Advancement
# =============================================================================


class CharacterAdvancement(BaseModel):
    """Record of character advancement over time."""

    sessions_completed: int = 0
    total_improvement_rolls: int = 0
    successful_improvements: int = 0
    skills_improved: list[str] = Field(default_factory=list)
    occupational_points_spent: int = 0
    interest_points_spent: int = 0
    luck_recovered: int = 0
    sanity_recovered: int = 0


def spend_occupational_point(
    current_skills: dict[str, int],
    skill_key: str,
    points: int,
) -> tuple[dict[str, int], bool]:
    """Spend occupational points to increase a skill.

    Occupational points can only increase skills listed in the character's
    occupation skill list.

    Args:
        current_skills: Current skill values
        skill_key: Skill to improve
        points: Points to spend (usually 1 point = +1 skill)

    Returns:
        Tuple of (new_skills_dict, success)
    """
    if points <= 0:
        return current_skills, False

    new_skills = dict(current_skills)
    current = new_skills.get(skill_key, 0)
    new_skills[skill_key] = current + points

    return new_skills, True


def spend_interest_point(
    current_skills: dict[str, int],
    skill_key: str,
    points: int,
) -> tuple[dict[str, int], bool]:
    """Spend interest points to increase a skill.

    Interest points can increase ANY skill (not just occupational).

    Args:
        current_skills: Current skill values
        skill_key: Skill to improve
        points: Points to spend (usually 1 point = +1 skill)

    Returns:
        Tuple of (new_skills_dict, success)
    """
    if points <= 0:
        return current_skills, False

    new_skills = dict(current_skills)
    current = new_skills.get(skill_key, 0)
    new_skills[skill_key] = current + points

    return new_skills, True


# =============================================================================
# Build Points and Character Creation
# =============================================================================

# Standard build point allocation
STANDARD_BUILD_POINTS = 480  # Total points for characteristics

# Characteristic ranges
CHARACTERISTIC_RANGE = (1, 100)  # Min and max for any characteristic


def calculate_build_points_spent(characteristics: dict[str, int]) -> int:
    """Calculate build points spent on characteristics.

    COC7e: 480 points distributed across 7 characteristics.
    Each point above 50 costs double.

    Args:
        characteristics: Dict of characteristic values

    Returns:
        Total build points spent
    """
    total = 0
    for key in ["str", "con", "dex", "app", "pow", "int", "edu"]:
        value = characteristics.get(key, 50)
        if value <= 50:
            total += value
        else:
            # Above 50 costs double
            total += 50 + (value - 50) * 2

    # SIZ is special: 2d6+6 = 8-18, costs 1 point per value
    siz = characteristics.get("siz", 10)
    total += siz

    return total


def generate_standard_characteristics() -> dict[str, int]:
    """Generate standard characteristics with 480 build points.

    Returns:
        Dict of characteristic values that sum to ~480 points
    """
    import random

    # Start with average characteristics
    chars = {
        "str": 50,
        "con": 50,
        "dex": 50,
        "app": 50,
        "pow": 50,
        "int": 50,
        "edu": 50,
        "siz": 10,
    }

    # Simple distribution: ensure total is close to 480
    # Each char starts at 50 (except SIZ at 10), spending 350 points
    # Remaining 130 points to distribute

    points_to_spend = STANDARD_BUILD_POINTS - calculate_build_points_spent(chars)

    while points_to_spend > 0:
        # Pick a random characteristic (except SIZ)
        keys = ["str", "con", "dex", "app", "pow", "int", "edu"]
        key = random.choice(keys)

        if chars[key] < 85:  # Cap at 85 for balance
            chars[key] += 1
            points_to_spend -= 1

    return chars


# =============================================================================
# Occupation-Based Skill Distributions
# =============================================================================

# Sample occupation skill distributions
OCCUPATION_SKILL_SUGGESTIONS: dict[str, list[str]] = {
    "Antiquarian": [
        "appraisal",
        "archaeology",
        "history",
        "library_use",
        "navigate",
        "spot_hidden",
    ],
    "Artisan": [
        "art_craft",
        "craft_mechanical",
        "disguise",
        "elec_repair",
        "mech_repair",
    ],
    "Author": ["art_craft", "history", "library_use", "occult", "psychology", "write"],
    "Clergy": ["history", "law", "medicine", "occult", "persuade", "psychology"],
    "Criminal": [
        "disguise",
        "fast_talk",
        "intimidate",
        "locksmith",
        "sleight_of_hand",
        "stealth",
    ],
    "Doctor": ["first_aid", "medicine", "pharmacy", "psychology", "science_biology"],
    "Dilettante": ["appraise", "art_craft", "charm", "credit_rating", "ride", "shoot"],
    "Entertainer": [
        "art_craft",
        "charm",
        "disguise",
        "fast_talk",
        "listen",
        "persuade",
    ],
    "Hunter": [
        "climb",
        "firearms",
        "first_aid",
        "listen",
        "navigate",
        "survival",
        "track",
    ],
    "Journalist": ["art_craft", "library_use", "persuade", "psychology", "spot_hidden"],
    "Law Enforcement": [
        "drive_auto",
        "firearms",
        "intimidate",
        "law",
        "psychology",
        "spot_hidden",
    ],
    "Librarian": ["library_use", "occult", "appraise", "history", "computer_use"],
    "Military Officer": ["firearms", "first_aid", "leadership", "navigate", "tactics"],
    "Musician": ["art_craft", "charm", "fast_talk", "listen", "occult", "perform"],
    "Parapsychologist": [
        "anthropology",
        "chemistry",
        "occult",
        "physics",
        "psychology",
    ],
    "Physician": ["first_aid", "medicine", "pharmacy", "psychoanalysis", "psychology"],
    "Pilot": ["drive_auto", "mech_repair", "navigate", "pilot", "science", "survival"],
    "Police Detective": ["law", "listen", "psychology", "search", "spot_hidden"],
    "Professor": [
        "anthropology",
        "archaeology",
        "foreign_language",
        "library_use",
        "science",
    ],
    "Private Investigator": [
        "disguise",
        "drive_auto",
        "law",
        "locksmith",
        "photography",
        "spot_hidden",
    ],
    "Scientist": [
        "chemistry",
        "computer_use",
        "library_use",
        "medicine",
        "science",
        "track",
    ],
    "Secretary": [
        "accounting",
        "art_craft",
        "charm",
        "computer_use",
        "fast_talk",
        "library_use",
    ],
    "Soldier": [
        "climb",
        "firearms",
        "first_aid",
        "heavy_weapons",
        "military_science",
        "survival",
    ],
    "Travel Agent": [
        "charm",
        "credit_rating",
        "drive_auto",
        "foreign_language",
        "navigate",
    ],
}


def get_occupation_skills(occupation: str) -> list[str]:
    """Get suggested skills for an occupation.

    Args:
        occupation: The character's occupation

    Returns:
        List of suggested skill keys for that occupation
    """
    return OCCUPATION_SKILL_SUGGESTIONS.get(occupation, [])
