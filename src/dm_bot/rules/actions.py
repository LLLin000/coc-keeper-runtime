from typing import Literal

from pydantic import BaseModel, Field


class LookupAction(BaseModel):
    kind: Literal["spell", "monster", "class", "equipment", "rule"]
    slug: str = Field(min_length=1)
    baseline: str = Field(min_length=1)


class StatBlock(BaseModel):
    name: str
    armor_class: int
    hit_points: int


AdvantageMode = Literal["none", "advantage", "disadvantage"]
COCDifficulty = Literal["regular", "hard", "extreme"]


class RuleAction(BaseModel):
    action: Literal[
        "attack_roll",
        "ability_check",
        "saving_throw",
        "damage_roll",
        "raw_roll",
        "coc_skill_check",
        "coc_sanity_check",
    ]
    actor: StatBlock
    target: StatBlock | None = None
    parameters: dict[str, object] = Field(default_factory=dict)
