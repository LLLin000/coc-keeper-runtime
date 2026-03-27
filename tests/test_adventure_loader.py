from dm_bot.adventures.loader import load_adventure


import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from dm_bot.adventures.loader import load_adventure
from dm_bot.adventures.models import AdventurePackage


def test_load_starter_adventure() -> None:
    adventure = load_adventure("starter_crypt")

    assert adventure.slug == "starter_crypt"
    assert adventure.title
    assert len(adventure.scenes) >= 3
    assert adventure.start_scene_id == adventure.scenes[0].id
    assert "time_remaining" in adventure.state_defaults()
    assert any(scene.combat for scene in adventure.scenes)


def test_adventure_package_rejects_missing_start_scene() -> None:
    payload = {
        "slug": "broken",
        "title": "Broken",
        "premise": "Missing start scene.",
        "start_scene_id": "missing",
        "scenes": [{"id": "intro", "title": "Intro", "summary": "x"}],
    }

    with pytest.raises(ValidationError):
        AdventurePackage.model_validate(payload)


def test_load_adventure_from_path_supports_custom_package(tmp_path: Path) -> None:
    payload = {
        "slug": "custom_module",
        "title": "Custom Module",
        "premise": "Custom premise.",
        "start_scene_id": "intro",
        "state_fields": [
            {"key": "alarm_level", "default": 0, "visibility": "public"},
            {"key": "true_mastermind", "default": "少女", "visibility": "gm_only"},
        ],
        "scenes": [
            {
                "id": "intro",
                "title": "大厅",
                "summary": "冷光照亮大厅。",
                "clues": ["石钟正在走动"],
                "reveals": ["四个光幕通往不同分馆"],
            }
        ],
        "endings": [{"id": "escape", "title": "逃离", "summary": "幸存者离开了宅邸。"}],
    }
    path = tmp_path / "custom_module.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    adventure = load_adventure("custom_module", base_path=tmp_path)

    assert adventure.slug == "custom_module"
    assert adventure.state_defaults()["alarm_level"] == 0
    assert adventure.state_defaults()["true_mastermind"] == "少女"


def test_load_mad_mansion_formal_module() -> None:
    adventure = load_adventure("mad_mansion")

    assert adventure.title == "疯狂之馆"
    assert adventure.start_scene_id == "central_hall"
    assert {scene.id for scene in adventure.scenes} >= {
        "central_hall",
        "greed_hall",
        "life_hall",
        "death_hall",
        "blood_hall",
    }
    assert "time_remaining" in adventure.state_defaults()
    assert any(ending.id == "survive" for ending in adventure.endings)
