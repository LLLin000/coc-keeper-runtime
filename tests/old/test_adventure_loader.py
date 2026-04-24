import asyncio
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from dm_bot.adventures.loader import load_adventure
from dm_bot.adventures.models import AdventurePackage
from dm_bot.adventures.extraction import extract_room_graph_draft


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
    assert adventure.scene_by_id("central_hall").guidance.light_hint
    assert adventure.scene_by_id("central_hall").interactables
    assert adventure.start_location_id == "central_hall"
    assert adventure.location_by_id("central_hall").connections


def test_adventure_package_supports_room_graph_locations() -> None:
    adventure = AdventurePackage.model_validate(
        {
            "slug": "graph_module",
            "title": "Graph Module",
            "premise": "Test graph.",
            "start_scene_id": "hall",
            "start_location_id": "hall",
            "scenes": [
                {"id": "hall", "title": "大厅", "summary": "白色大厅。"},
                {"id": "library", "title": "图书馆", "summary": "旧书散落一地。"},
            ],
            "locations": [
                {
                    "id": "hall",
                    "scene_id": "hall",
                    "title": "大厅",
                    "aliases": ["中央大厅"],
                    "landmarks": ["石钟", "门"],
                    "connections": [
                        {
                            "to_location_id": "library",
                            "keywords": ["图书馆", "门"],
                            "travel_text": "你穿过木门，进入图书馆。",
                            "observe_text": "门后隐约传来纸张摩擦声。",
                        }
                    ],
                },
                {"id": "library", "scene_id": "library", "title": "图书馆"},
            ],
        }
    )

    hall = adventure.location_by_id("hall")
    assert hall.connections[0].to_location_id == "library"
    assert hall.landmarks == ["石钟", "门"]


def test_adventure_package_supports_guidance_tiers_and_interactables() -> None:
    adventure = AdventurePackage.model_validate(
        {
            "slug": "guided_module",
            "title": "Guided Module",
            "premise": "Test premise.",
            "start_scene_id": "intro",
            "scenes": [
                {
                    "id": "intro",
                    "title": "大厅",
                    "summary": "一个可测试的大厅。",
                    "guidance": {
                        "ambient_focus": ["石钟", "四道门"],
                        "light_hint": "先看看最显眼的装置。",
                        "rescue_hint": "如果没头绪，就去调查石钟或门。"
                    },
                    "interactables": [
                        {
                            "id": "clock",
                            "title": "石钟",
                            "keywords": ["钟", "clock"],
                            "judgement": "auto",
                            "result_text": "你看见钟针正在倒退。"
                        }
                    ]
                }
            ],
        }
    )

    scene = adventure.scene_by_id("intro")
    assert scene.guidance.light_hint == "先看看最显眼的装置。"
    assert scene.interactables[0].judgement == "auto"


class StubExtractionLLM:
    def __init__(self, payload: str) -> None:
        self.payload = payload
        self.prompts: list[str] = []

    async def extract_json(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.payload


def test_extract_room_graph_draft_returns_reviewable_structure() -> None:
    llm = StubExtractionLLM(
        json.dumps(
            {
                "source_name": "疯狂之馆",
                "topology_summary": "中央大厅连接四个分馆。",
                "locations": [
                    {"id": "central_hall", "title": "中央大厅", "summary": "倒计时大厅。", "neighbors": ["greed_hall"]},
                    {"id": "greed_hall", "title": "贪欲之馆", "summary": "管理员在等交易。", "neighbors": ["central_hall"]},
                ],
                "trigger_trees": [
                    {
                        "location_id": "central_hall",
                        "root_trigger": "调查数字钟",
                        "outcomes": ["揭露倒计时", "引导进入分馆"],
                    }
                ],
                "trigger_drafts": [
                    {
                        "id": "clock_inspection",
                        "event_kind": "action",
                        "action_id": "clock",
                        "summary": "调查数字钟时揭露倒计时压力。"
                    }
                ],
            },
            ensure_ascii=False,
        )
    )

    draft = asyncio.run(extract_room_graph_draft("source text", source_name="疯狂之馆", llm=llm))

    assert draft.source_name == "疯狂之馆"
    assert draft.locations[0].id == "central_hall"
    assert draft.trigger_trees[0].location_id == "central_hall"
    assert draft.trigger_drafts[0].id == "clock_inspection"
    assert "room graph" in llm.prompts[0].lower()
