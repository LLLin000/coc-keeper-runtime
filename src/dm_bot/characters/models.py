from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class CharacterSourceLabel(StrEnum):
    SNAPSHOT = "snapshot"
    COC_PREGEN = "coc_pregen"


class CharacterIdentity(BaseModel):
    external_id: str
    name: str
    species: str
    classes: list[dict[str, object]] = Field(default_factory=list)


class CharacterSourceInfo(BaseModel):
    provider: str
    label: CharacterSourceLabel


class HitPoints(BaseModel):
    current: int
    maximum: int
    temporary: int = 0


class AbilityScores(BaseModel):
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int


class AttackProfile(BaseModel):
    name: str
    attack_bonus: int
    damage: str


class SpellcastingSummary(BaseModel):
    ability: str
    save_dc: int
    attack_bonus: int


class COCAttributes(BaseModel):
    str: int
    con: int
    dex: int
    app: int
    pow: int
    siz: int
    int: int
    edu: int


class COCInvestigatorProfile(BaseModel):
    occupation: str = ""
    age: int = 0
    san: int = 0
    hp: int = 0
    mp: int = 0
    luck: int = 0
    build: int = 0
    damage_bonus: str = "0"
    move_rate: int = 0
    attributes: COCAttributes = Field(
        default_factory=lambda: COCAttributes(
            str=0, con=0, dex=0, app=0, pow=0, siz=0, int=0, edu=0
        )
    )
    skills: list[SkillEntry] = Field(default_factory=list)


class CharacterRecord(BaseModel):
    source: CharacterSourceInfo
    external_id: str
    name: str
    species: str = ""
    classes: list[dict[str, object]] = Field(default_factory=list)
    proficiency_bonus: int = 0
    armor_class: int = 0
    speed: int = 0
    hp: HitPoints = Field(
        default_factory=lambda: HitPoints(current=0, maximum=0, temporary=0)
    )
    abilities: AbilityScores = Field(
        default_factory=lambda: AbilityScores(
            strength=0,
            dexterity=0,
            constitution=0,
            intelligence=0,
            wisdom=0,
            charisma=0,
        )
    )
    skills: list[SkillEntry] = Field(default_factory=list)
    attacks: list[AttackProfile] = Field(default_factory=list)
    spellcasting: SpellcastingSummary | None = None
    resources: dict[str, int] = Field(default_factory=dict)
    coc: COCInvestigatorProfile | None = None

    def migrate_skills_from_dict(
        self, skills_dict: dict[str, int]
    ) -> "CharacterRecord":
        """Migrate from old dict[str, int] format to list[SkillEntry].

        Args:
            skills_dict: Old-style skill dictionary {skill_name: value}

        Returns:
            Updated CharacterRecord with skills migrated to list[SkillEntry]
        """
        from dm_bot.rules.skills import (
            SkillCategory,
            SkillEntry,
            get_skill_by_name,
            COC_SKILLS,
        )

        new_skills = []
        for name, value in skills_dict.items():
            existing = get_skill_by_name(COC_SKILLS, name)
            if existing:
                new_skills.append(
                    SkillEntry(
                        name=name,
                        value=value,
                        category=existing.category,
                        specialization=existing.specialization,
                        is_language=existing.is_language,
                        is_derived=existing.is_derived,
                        default_value=existing.value,
                    )
                )
            else:
                # Unknown skill - add as OTHER category
                new_skills.append(
                    SkillEntry(
                        name=name,
                        value=value,
                        category=SkillCategory.OTHER,
                    )
                )
        return self.model_copy(update={"skills": new_skills})
