import json
from collections.abc import AsyncIterator

from pydantic import BaseModel, Field

from dm_bot.models.schemas import ModelRequest
from dm_bot.router.contracts import TurnPlan


class NarrationRequest(BaseModel):
    player_input: str = Field(min_length=1)
    state_snapshot: dict[str, object] = Field(default_factory=dict)
    tool_results: list[dict[str, object]] = Field(default_factory=list)
    plan: TurnPlan


class NarrationService:
    def __init__(self, client) -> None:
        self._client = client

    async def narrate(self, request: NarrationRequest) -> str:
        prompt = self._build_model_request(request)
        response = await self._client.call_narrator(prompt)
        return response.content.strip()

    async def stream_narrate(self, request: NarrationRequest) -> AsyncIterator[str]:
        prompt = self._build_model_request(request)
        async for chunk in self._client.stream_narrator(prompt):
            if chunk:
                yield chunk

    def _build_model_request(self, request: NarrationRequest) -> ModelRequest:
        prompt = ModelRequest(
            system_prompt=(
                "You are the Chinese D&D DM. Produce final Discord-ready prose only. "
                "Write like a practical tabletop DM: concise sensory framing, clear actionable details, "
                "distinct NPC speech when needed, and no repetitive filler. "
                "Do not invent state mutations."
            ),
            user_prompt=self._build_prompt(request),
        )
        return prompt

    def _build_prompt(self, request: NarrationRequest) -> str:
        compact_context = {
            "mode": request.plan.mode,
            "narration_brief": request.plan.narration_brief,
            "state_snapshot": request.state_snapshot,
            "tool_results": request.tool_results,
            "state_intents": [intent.model_dump() for intent in request.plan.state_intents],
            "player_input": request.player_input,
        }
        return json.dumps(compact_context, ensure_ascii=False)
