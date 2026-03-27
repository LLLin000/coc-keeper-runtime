from pydantic import BaseModel, Field


class AdventureScene(BaseModel):
    id: str
    title: str
    summary: str
    clues: list[str] = Field(default_factory=list)
    combat: bool = False


class AdventurePackage(BaseModel):
    slug: str
    title: str
    premise: str
    objectives: list[str] = Field(default_factory=list)
    scenes: list[AdventureScene] = Field(default_factory=list)
