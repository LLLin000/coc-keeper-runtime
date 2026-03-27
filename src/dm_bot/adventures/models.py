from typing import Literal

from pydantic import BaseModel, Field, model_validator


Visibility = Literal["public", "discoverable", "secret", "gm_only"]


class AdventureStateField(BaseModel):
    key: str
    default: int | bool | str | list[str] = ""
    visibility: Visibility = "discoverable"


class AdventureScene(BaseModel):
    id: str
    title: str
    summary: str
    clues: list[str] = Field(default_factory=list)
    reveals: list[str] = Field(default_factory=list)
    combat: bool = False
    exits: list[str] = Field(default_factory=list)


class AdventureEnding(BaseModel):
    id: str
    title: str
    summary: str


class AdventurePackage(BaseModel):
    slug: str
    title: str
    premise: str
    objectives: list[str] = Field(default_factory=list)
    start_scene_id: str
    state_fields: list[AdventureStateField] = Field(default_factory=list)
    scenes: list[AdventureScene] = Field(default_factory=list)
    endings: list[AdventureEnding] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_structure(self) -> "AdventurePackage":
        scene_ids = {scene.id for scene in self.scenes}
        if self.start_scene_id not in scene_ids:
            raise ValueError("start_scene_id must reference an existing scene")
        return self

    def scene_by_id(self, scene_id: str) -> AdventureScene:
        for scene in self.scenes:
            if scene.id == scene_id:
                return scene
        raise KeyError(scene_id)

    def state_defaults(self) -> dict[str, int | bool | str | list[str]]:
        return {field.key: field.default for field in self.state_fields}

    def public_state(self, module_state: dict[str, object]) -> dict[str, object]:
        visible: dict[str, object] = {}
        for field in self.state_fields:
            if field.visibility in {"public", "discoverable"} and field.key in module_state:
                visible[field.key] = module_state[field.key]
        return visible

    def gm_state(self, module_state: dict[str, object]) -> dict[str, object]:
        return {field.key: module_state.get(field.key, field.default) for field in self.state_fields}
