"""COC 7th Edition Skill Point Allocation.

Handles occupational and interest point calculation and allocation
during character creation per COC7 rules.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class PointAllocationResult:
    """Result of a skill point allocation.

    Attributes:
        skill_name: Name of the skill allocated to
        previous_value: Skill value before allocation
        new_value: Skill value after allocation
        points_spent: Number of points spent
    """

    skill_name: str
    previous_value: int
    new_value: int
    points_spent: int


@dataclass
class CharacterPointPool:
    """Point pool tracking for character creation.

    Attributes:
        occupational_points: Total occupational points available
        occupational_spent: Occupational points already spent
        interest_points: Total interest points available
        interest_spent: Interest points already spent
    """

    occupational_points: int = 0
    occupational_spent: int = 0
    interest_points: int = 0
    interest_spent: int = 0

    def remaining_occupational(self) -> int:
        """Remaining occupational points."""
        return self.occupational_points - self.occupational_spent

    def remaining_interest(self) -> int:
        """Remaining interest points."""
        return self.interest_points - self.interest_spent


def calculate_occupational_points(coc) -> int:
    """Calculate Occupational skill points per COC7: (INT × 2) + (POW × 2).

    These points are spent on job-related skills during character creation.

    Args:
        coc: COCInvestigatorProfile with attributes

    Returns:
        Total occupational points available
    """
    return (coc.attributes.int * 2) + (coc.attributes.pow * 2)


def calculate_interest_points(coc) -> int:
    """Calculate Interest skill points per COC7: (IPA × 2).

    IPA (Interest Points Allocation) = POW × 2
    These points are spent on any skills during character creation.

    Args:
        coc: COCInvestigatorProfile with attributes

    Returns:
        Total interest points available
    """
    ipa = coc.attributes.pow * 2
    return ipa * 2


def get_point_pool(character) -> CharacterPointPool:
    """Get current point pool for a character.

    Args:
        character: CharacterRecord with coc profile and skills

    Returns:
        CharacterPointPool with current totals and spent amounts
    """
    if character.coc is None:
        return CharacterPointPool()

    occ_pts = calculate_occupational_points(character.coc)
    int_pts = calculate_interest_points(character.coc)

    occ_spent = character.resources.get("coc_occupational_spent", 0)
    int_spent = character.resources.get("coc_interest_spent", 0)

    return CharacterPointPool(
        occupational_points=occ_pts,
        occupational_spent=occ_spent,
        interest_points=int_pts,
        interest_spent=int_spent,
    )


def allocate_skill_points(
    character,
    skill_name: str,
    new_value: int,
    pool_type: Literal["occupational", "interest"],
) -> PointAllocationResult:
    """Allocate points to a skill from occupational or interest pool.

    Args:
        character: CharacterRecord to modify
        skill_name: Name of skill to allocate points to
        new_value: New skill value (must be > current value)
        pool_type: Which point pool to use ("occupational" or "interest")

    Returns:
        PointAllocationResult with before/after values and points spent

    Raises:
        ValueError: If not enough points in pool or skill not found
    """
    # Find skill on character
    skill_entry = None
    for s in character.skills:
        if s.name == skill_name:
            skill_entry = s
            break
    if not skill_entry:
        raise ValueError(f"Skill '{skill_name}' not found on character")

    if new_value <= skill_entry.value:
        raise ValueError(
            f"new_value ({new_value}) must be greater than current value ({skill_entry.value})"
        )

    # Calculate pool and spent key
    if character.coc is None:
        raise ValueError("Character has no COC profile")

    if pool_type == "occupational":
        total_pool = calculate_occupational_points(character.coc)
        spent_key = "coc_occupational_spent"
    else:
        total_pool = calculate_interest_points(character.coc)
        spent_key = "coc_interest_spent"

    # Track spent in resources
    current_spent = character.resources.get(spent_key, 0)
    points_to_spend = new_value - skill_entry.value
    remaining = total_pool - current_spent

    if points_to_spend > remaining:
        raise ValueError(
            f"Not enough {pool_type} points. Have: {remaining}, need: {points_to_spend}"
        )

    # Update skill value
    previous_value = skill_entry.value
    skill_entry.value = new_value

    # Update spent tracking
    character.resources[spent_key] = current_spent + points_to_spend

    return PointAllocationResult(
        skill_name=skill_name,
        previous_value=previous_value,
        new_value=new_value,
        points_spent=points_to_spend,
    )


def initialize_character_skills(
    character,
    use_occupational_defaults: bool = True,
):
    """Initialize character skills from COC_SKILLS database.

    For each skill in COC_SKILLS, add a SkillEntry to character.skills
    with the default value from the database.

    Args:
        character: CharacterRecord to initialize
        use_occupational_defaults: If True, use EDU×2 for Fighting, etc.

    Returns:
        Updated character with skills list populated
    """
    from dm_bot.rules.skills import COC_SKILLS, SkillEntry

    existing_names = {s.name for s in character.skills}
    new_skills = list(character.skills)

    for db_skill in COC_SKILLS:
        if db_skill.name in existing_names:
            continue  # Don't override character-specific values

        new_skills.append(
            SkillEntry(
                name=db_skill.name,
                value=db_skill.value,
                category=db_skill.category,
                specialization=db_skill.specialization,
                is_language=db_skill.is_language,
                is_derived=db_skill.is_derived,
                default_value=db_skill.value,
            )
        )

    return character.model_copy(update={"skills": new_skills})


# Export public interface
__all__ = [
    "PointAllocationResult",
    "CharacterPointPool",
    "calculate_occupational_points",
    "calculate_interest_points",
    "get_point_pool",
    "allocate_skill_points",
    "initialize_character_skills",
]
