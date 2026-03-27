from collections.abc import AsyncIterator

from dm_bot.gameplay.scene_formatter import format_scene_output
from pydantic import BaseModel, Field

from dm_bot.models.schemas import TurnEnvelope
from dm_bot.narration.service import NarrationRequest
from dm_bot.router.contracts import TurnPlan


class TurnResult(BaseModel):
    plan: TurnPlan
    reply: str = Field(min_length=1)


class TurnRunner:
    def __init__(self, *, router, narrator, gameplay=None) -> None:
        self._router = router
        self._narrator = narrator
        self._gameplay = gameplay

    async def run_turn(
        self,
        envelope: TurnEnvelope,
        *,
        tool_results: list[dict[str, object]] | None = None,
        state_snapshot: dict[str, object] | None = None,
    ) -> TurnResult:
        plan, narration_request = await self._prepare_turn(
            envelope,
            tool_results=tool_results,
            state_snapshot=state_snapshot,
        )
        reply = await self._narrator.narrate(narration_request)
        reply = format_scene_output(plan=plan, raw_output=reply)
        return TurnResult(plan=plan, reply=reply)

    async def stream_turn(
        self,
        envelope: TurnEnvelope,
        *,
        tool_results: list[dict[str, object]] | None = None,
        state_snapshot: dict[str, object] | None = None,
    ) -> AsyncIterator[str]:
        plan, narration_request = await self._prepare_turn(
            envelope,
            tool_results=tool_results,
            state_snapshot=state_snapshot,
        )
        collected = ""
        try:
            async for chunk in self._narrator.stream_narrate(narration_request):
                collected += chunk
                yield format_scene_output(plan=plan, raw_output=collected)
            if not collected:
                reply = await self._narrator.narrate(narration_request)
                yield format_scene_output(plan=plan, raw_output=reply)
        except Exception:
            reply = await self._narrator.narrate(narration_request)
            yield format_scene_output(plan=plan, raw_output=reply)

    async def _prepare_turn(
        self,
        envelope: TurnEnvelope,
        *,
        tool_results: list[dict[str, object]] | None = None,
        state_snapshot: dict[str, object] | None = None,
    ) -> tuple[TurnPlan, NarrationRequest]:
        plan = await self._router.route(envelope)
        computed_tool_results = tool_results or []
        if self._gameplay is not None:
            computed_tool_results = [*computed_tool_results, *self._gameplay.resolve_plan(plan)]
        request = NarrationRequest(
            player_input=envelope.content,
            state_snapshot=state_snapshot or {},
            tool_results=computed_tool_results,
            plan=plan,
        )
        return plan, request
