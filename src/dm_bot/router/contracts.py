from typing import Literal

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str = Field(min_length=1)
    arguments: dict[str, object] = Field(default_factory=dict)


class StateIntent(BaseModel):
    kind: str = Field(min_length=1)
    payload: dict[str, object] = Field(default_factory=dict)


class TurnPlan(BaseModel):
    mode: Literal["dm", "scene", "combat"]
    tool_calls: list[ToolCall] = Field(default_factory=list)
    state_intents: list[StateIntent] = Field(default_factory=list)
    narration_brief: str = Field(min_length=1)
    speaker_hints: list[str] = Field(default_factory=list)
