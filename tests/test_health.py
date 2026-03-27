from fastapi.testclient import TestClient

from dm_bot.runtime.app import create_app
from dm_bot.runtime.health import build_health_snapshot


def test_create_app_exposes_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "checks" in body


def test_health_snapshot_reports_model_configuration() -> None:
    snapshot = build_health_snapshot()

    assert snapshot.status in {"ok", "degraded"}
    assert "router_model" in snapshot.checks
    assert "narrator_model" in snapshot.checks

