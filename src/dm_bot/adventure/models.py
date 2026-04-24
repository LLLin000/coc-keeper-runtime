from pydantic import BaseModel, Field


class Clue(BaseModel):
    clue_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    required_skill: str = ""
    difficulty: str = "regular"


class NPC(BaseModel):
    npc_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = ""
    stats: dict[str, int] = Field(default_factory=dict)


class Scene(BaseModel):
    scene_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    exits: list[str] = Field(default_factory=list)  # 可前往的场景ID
    clues: list[Clue] = Field(default_factory=list)
    npcs: list[NPC] = Field(default_factory=list)


class Adventure(BaseModel):
    adventure_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    scenes: dict[str, Scene] = Field(default_factory=dict)
    opening_scene_id: str = ""
