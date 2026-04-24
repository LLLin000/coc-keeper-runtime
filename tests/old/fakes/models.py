"""Shared model mock fixtures for tests — FastMock, SlowMock, ErrorMock, ApiMock."""

from __future__ import annotations
import asyncio
import os
from collections.abc import AsyncIterator
from openai import AsyncOpenAI
from dm_bot.models.schemas import ModelRequest, ModelResponse


class StubModelClient:
    def __init__(
        self,
        *,
        router_content: str = '{"mode":"dm","tool_calls":[],"state_intents":[],"narration_brief":"test"}',
        narrator_content: str = "测试回复",
        router_error: Exception | None = None,
        narrator_error: Exception | None = None,
    ) -> None:
        self.router_model = "stub-router"
        self.narrator_model = "stub-narrator"
        self.router_requests: list = []
        self.narrator_requests: list = []
        self._router_content = router_content
        self._narrator_content = narrator_content
        self._router_error = router_error
        self._narrator_error = narrator_error

    async def call_router(self, request):
        self.router_requests.append(request)
        if self._router_error:
            raise self._router_error
        return ModelResponse(model=self.router_model, content=self._router_content)

    async def call_narrator(self, request):
        self.narrator_requests.append(request)
        if self._narrator_error:
            raise self._narrator_error
        return ModelResponse(model=self.narrator_model, content=self._narrator_content)

    async def stream_narrator(self, request):
        self.narrator_requests.append(request)
        if self._narrator_error:
            raise self._narrator_error
        for char in self._narrator_content:
            yield char


class FastMock(StubModelClient):
    """Instant successful response."""

    pass


class SlowMock(StubModelClient):
    """Delayed response for timeout/race-window coverage."""

    def __init__(self, *, delay_seconds: float = 0.1, **kwargs) -> None:
        super().__init__(**kwargs)
        self._delay = delay_seconds

    async def call_router(self, request):
        await asyncio.sleep(self._delay)
        return await super().call_router(request)

    async def call_narrator(self, request):
        await asyncio.sleep(self._delay)
        return await super().call_narrator(request)


class ErrorMock(StubModelClient):
    """API failure / upstream exception path."""

    def __init__(
        self,
        *,
        router_error: Exception | None = None,
        narrator_error: Exception | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            router_error=router_error or RuntimeError("stub router error"),
            narrator_error=narrator_error or RuntimeError("stub narrator error"),
            **kwargs,
        )


class ApiModelClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        router_model: str = "router",
        narrator_model: str = "narrator",
    ) -> None:
        self.router_model = router_model
        self.narrator_model = narrator_model
        self.router_requests: list = []
        self.narrator_requests: list = []
        self._base_url = base_url or os.environ.get(
            "DM_BOT_API_BASE_URL", "http://localhost:11434/v1"
        )
        self._api_key = api_key or os.environ.get("DM_BOT_API_KEY", "ollama")
        self._client = AsyncOpenAI(base_url=self._base_url, api_key=self._api_key)

    async def call_router(self, request: ModelRequest) -> ModelResponse:
        self.router_requests.append(request)
        response = await self._client.chat.completions.create(
            model=self.router_model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        return ModelResponse(model=self.router_model, content=content)

    async def call_narrator(self, request: ModelRequest) -> ModelResponse:
        self.narrator_requests.append(request)
        response = await self._client.chat.completions.create(
            model=self.narrator_model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        return ModelResponse(model=self.narrator_model, content=content)

    async def stream_narrator(self, request: ModelRequest) -> AsyncIterator[str]:
        self.narrator_requests.append(request)
        stream = await self._client.chat.completions.create(
            model=self.narrator_model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            stream=True,
        )
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            content = getattr(delta, "content", None)
            if content:
                yield content
