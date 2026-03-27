import httpx

from dm_bot.config import Settings, get_settings
from dm_bot.models.schemas import HealthSnapshot, ModelTarget


def list_ollama_models(settings: Settings) -> list[str]:
    response = httpx.get(
        f"{settings.ollama_base_url.rstrip('/')}/models",
        headers={"Authorization": "Bearer ollama"},
        timeout=5.0,
    )
    response.raise_for_status()
    payload = response.json()
    return [item["id"] for item in payload.get("data", [])]


def build_model_snapshot(settings: Settings | None = None) -> HealthSnapshot:
    settings = settings or get_settings()
    try:
        available_models = list_ollama_models(settings)
    except Exception:
        available_models = []

    router_ready = settings.router_model in available_models
    narrator_ready = settings.narrator_model in available_models

    return HealthSnapshot(
        status="ok" if router_ready and narrator_ready else "degraded",
        checks={
            "router_model": ModelTarget(
                name=settings.router_model,
                reachable=router_ready,
                detail="available locally" if router_ready else "model not available locally",
            ),
            "narrator_model": ModelTarget(
                name=settings.narrator_model,
                reachable=narrator_ready,
                detail="available locally" if narrator_ready else "model not available locally",
            ),
        },
    )
