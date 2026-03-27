from dm_bot.config import Settings, get_settings
from dm_bot.models.schemas import HealthSnapshot, ModelTarget


def build_health_snapshot(settings: Settings | None = None) -> HealthSnapshot:
    settings = settings or get_settings()

    router_reachable = bool(settings.router_model and settings.ollama_base_url)
    narrator_reachable = bool(settings.narrator_model and settings.ollama_base_url)
    status = "ok" if router_reachable and narrator_reachable else "degraded"

    return HealthSnapshot(
        status=status,
        checks={
            "router_model": ModelTarget(
                name=settings.router_model,
                reachable=router_reachable,
                detail="configured" if router_reachable else "missing configuration",
            ),
            "narrator_model": ModelTarget(
                name=settings.narrator_model,
                reachable=narrator_reachable,
                detail="configured" if narrator_reachable else "missing configuration",
            ),
        },
    )

