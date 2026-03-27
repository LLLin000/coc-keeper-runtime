from fastapi import FastAPI

from dm_bot.runtime.health import build_health_snapshot


def create_app() -> FastAPI:
    app = FastAPI(title="dm-bot-runtime")

    @app.get("/health")
    async def health() -> dict[str, object]:
        return build_health_snapshot().model_dump()

    return app
