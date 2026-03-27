from enum import StrEnum

from pydantic import BaseModel, Field


class CharacterSourceLabel(StrEnum):
    SNAPSHOT = "snapshot"


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


class CharacterRecord(BaseModel):
    source: CharacterSourceInfo
    external_id: str
    name: str
    species: str
    classes: list[dict[str, object]] = Field(default_factory=list)
    proficiency_bonus: int
    armor_class: int
    speed: int
    hp: HitPoints
    abilities: AbilityScores
    skills: dict[str, int] = Field(default_factory=dict)
    attacks: list[AttackProfile] = Field(default_factory=list)
    spellcasting: SpellcastingSummary | None = None
    resources: dict[str, int] = Field(default_factory=dict)
