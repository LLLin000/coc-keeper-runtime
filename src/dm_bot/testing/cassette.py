from __future__ import annotations
import json
from pathlib import Path
from typing import Any

import yaml


def record_cassette(
    cassette_dir: Path,
    scenario_id: str,
    cassette_type: str,
    request: Any,
    response: Any,
) -> None:
    cassette_dir.mkdir(parents=True, exist_ok=True)
    path = cassette_dir / f"{scenario_id}.yaml"

    entry = {
        "request": _serialize_request(request),
        "response": _serialize_response(response),
    }

    existing: list[dict[str, Any]] = []
    if path.exists():
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        existing = data if isinstance(data, list) else []

    existing.append(entry)

    with path.open("w", encoding="utf-8") as f:
        yaml.dump(existing, f, allow_unicode=True, default_flow_style=False)


def load_cassette(
    cassette_dir: Path,
    scenario_id: str,
    index: int = 0,
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    path = cassette_dir / f"{scenario_id}.yaml"
    if not path.exists():
        return None

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or index >= len(data):
        return None

    entry = data[index]
    return entry["request"], entry["response"]


def _serialize_request(request: Any) -> dict[str, Any]:
    return {
        "system_prompt": getattr(request, "system_prompt", ""),
        "user_prompt": getattr(request, "user_prompt", ""),
    }


def _serialize_response(response: Any) -> dict[str, Any]:
    return {
        "model": getattr(response, "model", ""),
        "content": getattr(response, "content", ""),
    }
