"""COC 7th Edition Skill Types.

Shared type definitions for the skill system.
Must not import from dm_bot.characters.models to avoid circular imports.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class SkillCategory(StrEnum):
    """Skill categories for COC 7th Edition skills."""

    COMBAT = "combat"  # Fighting, Shooting, Brawl, etc.
    PERCEPTION = "perception"  # Spot, Listen, Search, etc.
    KNOWLEDGE = "knowledge"  # History, Occult, Science, etc.
    LANGUAGE = "language"  # Own Language, Other Language
    MOTION = "motion"  # Climb, Jump, Swim, etc.
    COMMUNICATION = "communication"  # Charm, Persuade, Intimidate, etc.
    CRFT = "craft"  # Art, Craft, etc.
    FIGHTSPEC = "fightspec"  # Fighting specializations (Brawl, Sword, etc.)
    OTHER = "other"  # Uncategorized/legacy skills


class SkillEntry(BaseModel):
    """A single skill entry for a character.

    Attributes:
        name: Skill display name (e.g., "侦查", "Fighting")
        value: Current skill value (0-100)
        category: Skill category enum
        specialization: Sub-type for Fighting specializations (e.g., "Brawl", "Sword")
        is_language: True for language skills
        is_derived: True if computed from formula (e.g., Own Language = EDU×5)
        default_value: Original/default value for reset
    """

    name: str = Field(description="Skill display name (e.g., '侦查', 'Fighting')")
    value: int = Field(ge=0, le=100, description="Current skill value 0-100")
    category: SkillCategory = Field(description="Skill category enum")
    specialization: str | None = Field(
        default=None, description="Sub-type for Fighting specializations"
    )
    is_language: bool = Field(default=False, description="True for language skills")
    is_derived: bool = Field(default=False, description="True if computed from formula")
    default_value: int | None = Field(
        default=None, description="Original/default value for reset"
    )
