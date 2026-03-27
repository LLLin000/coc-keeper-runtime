import asyncio
from collections.abc import AsyncIterator
from uuid import uuid4

from pydantic import BaseModel, Field

from dm_bot.models.schemas import TurnEnvelope


class TurnDispatchResult(BaseModel):
    trace_id: str = Field(min_length=1)
    reply: str = Field(min_length=1)


class TurnRequest(BaseModel):
    campaign_id: str
    channel_id: str
    user_id: str
    content: str = Field(min_length=1)
    trace_id: str | None = None


class TurnCoordinator:
    def __init__(self, *, turn_runner, persistence_store=None) -> None:
        self._turn_runner = turn_runner
        self._persistence_store = persistence_store
        self._locks: dict[str, asyncio.Lock] = {}

    async def handle_turn(
        self,
        request: TurnRequest | None = None,
        *,
        campaign_id: str | None = None,
        channel_id: str | None = None,
        user_id: str | None = None,
        content: str | None = None,
    ) -> TurnDispatchResult:
        request = request or TurnRequest(
            campaign_id=campaign_id or "",
            channel_id=channel_id or "",
            user_id=user_id or "",
            content=content or "",
        )
        trace_id = request.trace_id or str(uuid4())
        lock = self._locks.setdefault(request.campaign_id, asyncio.Lock())
        async with lock:
            result = await self._turn_runner.run_turn(
                TurnEnvelope(
                    campaign_id=request.campaign_id,
                    channel_id=request.channel_id,
                    user_id=request.user_id,
                    trace_id=trace_id,
                    content=request.content,
                )
            )
        if self._persistence_store is not None:
            self._persistence_store.append_event(
                campaign_id=request.campaign_id,
                trace_id=trace_id,
                event_type="turn.completed",
                payload={"reply": result.reply, "channel_id": request.channel_id, "user_id": request.user_id},
            )
        return TurnDispatchResult(trace_id=trace_id, reply=result.reply)

    async def stream_turn(
        self,
        request: TurnRequest | None = None,
        *,
        campaign_id: str | None = None,
        channel_id: str | None = None,
        user_id: str | None = None,
        content: str | None = None,
    ) -> AsyncIterator[str]:
        request = request or TurnRequest(
            campaign_id=campaign_id or "",
            channel_id=channel_id or "",
            user_id=user_id or "",
            content=content or "",
        )
        trace_id = request.trace_id or str(uuid4())
        lock = self._locks.setdefault(request.campaign_id, asyncio.Lock())
        last_reply = ""
        async with lock:
            async for reply in self._turn_runner.stream_turn(
                TurnEnvelope(
                    campaign_id=request.campaign_id,
                    channel_id=request.channel_id,
                    user_id=request.user_id,
                    trace_id=trace_id,
                    content=request.content,
                )
            ):
                last_reply = reply
                yield reply
        if self._persistence_store is not None:
            self._persistence_store.append_event(
                campaign_id=request.campaign_id,
                trace_id=trace_id,
                event_type="turn.completed",
                payload={"reply": last_reply, "channel_id": request.channel_id, "user_id": request.user_id},
            )
