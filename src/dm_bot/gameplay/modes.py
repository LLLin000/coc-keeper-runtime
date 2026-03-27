from pydantic import BaseModel, Field


class GameModeState(BaseModel):
    mode: str = "dm"
    scene_speakers: list[str] = Field(default_factory=list)

    def enter_scene(self, *, speakers: list[str]) -> None:
        self.mode = "scene"
        self.scene_speakers = speakers

    def enter_dm(self) -> None:
        self.mode = "dm"
        self.scene_speakers = []
