from typing import Literal

from pydantic import BaseModel, Field, model_validator


Visibility = Literal["public", "discoverable", "secret", "gm_only"]
JudgementKind = Literal["auto", "roll", "clarify"]


class AdventureStateField(BaseModel):
    key: str
    default: int | bool | str | list[str] = ""
    visibility: Visibility = "discoverable"


class AdventureScene(BaseModel):
    class Guidance(BaseModel):
        ambient_focus: list[str] = Field(default_factory=list)
        light_hint: str = ""
        rescue_hint: str = ""

    class Presentation(BaseModel):
        entry_text: str = ""
        pressure_text: str = ""
        choice_prompt: str = ""

    class Interactable(BaseModel):
        id: str
        title: str
        keywords: list[str] = Field(default_factory=list)
        judgement: JudgementKind = "auto"
        result_text: str = ""
        prompt_text: str = ""
        roll_type: str = ""
        roll_label: str = ""
        discover_clue: str = ""
        transition_scene_id: str = ""
        guidance_tier: Literal["light", "rescue"] = "light"

    id: str
    title: str
    summary: str
    clues: list[str] = Field(default_factory=list)
    reveals: list[str] = Field(default_factory=list)
    combat: bool = False
    exits: list[str] = Field(default_factory=list)
    guidance: Guidance = Field(default_factory=Guidance)
    presentation: Presentation = Field(default_factory=Presentation)
    interactables: list[Interactable] = Field(default_factory=list)


class AdventureEnding(BaseModel):
    id: str
    title: str
    summary: str


class AdventureLocationConnection(BaseModel):
    to_location_id: str
    keywords: list[str] = Field(default_factory=list)
    travel_text: str = ""
    observe_text: str = ""


class AdventureLocation(BaseModel):
    id: str
    scene_id: str
    title: str
    aliases: list[str] = Field(default_factory=list)
    landmarks: list[str] = Field(default_factory=list)
    connections: list[AdventureLocationConnection] = Field(default_factory=list)


class AdventurePackage(BaseModel):
    slug: str
    title: str
    premise: str
    objectives: list[str] = Field(default_factory=list)
    start_scene_id: str
    start_location_id: str | None = None
    state_fields: list[AdventureStateField] = Field(default_factory=list)
    scenes: list[AdventureScene] = Field(default_factory=list)
    locations: list[AdventureLocation] = Field(default_factory=list)
    endings: list[AdventureEnding] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_structure(self) -> "AdventurePackage":
        scene_ids = {scene.id for scene in self.scenes}
        if self.start_scene_id not in scene_ids:
            raise ValueError("start_scene_id must reference an existing scene")
        if self.locations:
            location_ids = {location.id for location in self.locations}
            for location in self.locations:
                if location.scene_id not in scene_ids:
                    raise ValueError("location.scene_id must reference an existing scene")
                for connection in location.connections:
                    if connection.to_location_id not in location_ids:
                        raise ValueError("location connection must reference an existing location")
            if self.start_location_id is None:
                self.start_location_id = self.start_scene_id
            if self.start_location_id not in location_ids:
                raise ValueError("start_location_id must reference an existing location")
        elif self.start_location_id is None:
            self.start_location_id = self.start_scene_id
        return self

    def scene_by_id(self, scene_id: str) -> AdventureScene:
        for scene in self.scenes:
            if scene.id == scene_id:
                return scene
        raise KeyError(scene_id)

    def location_by_id(self, location_id: str) -> AdventureLocation:
        if self.locations:
            for location in self.locations:
                if location.id == location_id:
                    return location
            raise KeyError(location_id)
        scene = self.scene_by_id(location_id)
        return AdventureLocation(
            id=scene.id,
            scene_id=scene.id,
            title=scene.title,
            landmarks=list(scene.guidance.ambient_focus),
            connections=[AdventureLocationConnection(to_location_id=target, keywords=[target]) for target in scene.exits],
        )

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
