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

    async def _call_model(self, model: str, request: ModelRequest) -> ModelResponse:
        response = await self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        return ModelResponse(model=model, content=content)

