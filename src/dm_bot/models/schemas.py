from typing import Literal

from pydantic import BaseModel, Field


class ModelTarget(BaseModel):
    name: str
    reachable: bool = False
    detail: str | None = None


class HealthSnapshot(BaseModel):
    status: Literal["ok", "degraded"]
    checks: dict[str, ModelTarget]


class TurnEnvelope(BaseModel):
    campaign_id: str
    channel_id: str
    user_id: str
    trace_id: str
    content: str = Field(min_length=1)


class ModelRequest(BaseModel):
    system_prompt: str
    user_prompt: str


class ModelResponse(BaseModel):
    model: str
    content: str

