from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from dm_bot.config import Settings
from dm_bot.models.schemas import ModelRequest, ModelResponse


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = AsyncOpenAI(
            base_url=settings.ollama_base_url,
            api_key="ollama",
        )

    @property
    def router_model(self) -> str:
        return self._settings.router_model

    @property
    def narrator_model(self) -> str:
        return self._settings.narrator_model

    async def call_router(self, request: ModelRequest) -> ModelResponse:
        return await self._call_model(self.router_model, request)

    async def call_narrator(self, request: ModelRequest) -> ModelResponse:
        return await self._call_model(self.narrator_model, request)

    async def stream_narrator(self, request: ModelRequest) -> AsyncIterator[str]:
        async for chunk in self._stream_model(self.narrator_model, request):
            yield chunk

    async def _call_model(self, model: str, request: ModelRequest) -> ModelResponse:
        payload = self._build_payload(model, request)
        response = await self._client.chat.completions.create(**payload)
        content = response.choices[0].message.content or ""
        return ModelResponse(model=model, content=content)

    def _build_payload(self, model: str, request: ModelRequest) -> dict[str, object]:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
        }
        if request.response_format is not None:
            payload["response_format"] = request.response_format
        return payload

    async def _stream_model(self, model: str, request: ModelRequest) -> AsyncIterator[str]:
        payload = self._build_payload(model, request)
        stream = await self._client.chat.completions.create(**payload, stream=True)
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            content = getattr(delta, "content", None)
            if content:
                yield content
