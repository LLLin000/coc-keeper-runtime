import asyncio

import pytest
from pydantic import ValidationError

from dm_bot.config import Settings
from dm_bot.models.schemas import ModelResponse, TurnEnvelope
from dm_bot.runtime.model_checks import build_model_snapshot
from dm_bot.router.contracts import TurnPlan
from dm_bot.router.service import RouterError, RouterService
from dm_bot.narration.service import NarrationRequest, NarrationService
from dm_bot.orchestrator.turn_runner import TurnRunner


class StubOllamaClient:
    def __init__(self, *, router_content: str = "", narrator_content: str = "") -> None:
        self.router_model = "router-test"
        self.narrator_model = "narrator-test"
        self.router_requests = []
        self.narrator_requests = []
        self._router_content = router_content
        self._narrator_content = narrator_content

    async def call_router(self, request):
        self.router_requests.append(request)
        return ModelResponse(model=self.router_model, content=self._router_content)

    async def call_narrator(self, request):
        self.narrator_requests.append(request)
        return ModelResponse(model=self.narrator_model, content=self._narrator_content)


def test_turn_plan_requires_structured_mode() -> None:
    with pytest.raises(ValidationError):
        TurnPlan.model_validate(
            {
                "mode": "freeform",
                "tool_calls": [],
                "state_intents": [],
                "narration_brief": "brief",
            }
        )


def test_router_service_returns_validated_turn_plan() -> None:
    client = StubOllamaClient(
        router_content='{"mode":"dm","tool_calls":[],"state_intents":[],"narration_brief":"keep it short"}'
    )
    service = RouterService(client)
    envelope = TurnEnvelope(
        campaign_id="camp-1",
        channel_id="chan-1",
        user_id="user-1",
        trace_id="trace-1",
        content="我想看看门后面有什么。",
    )

    plan = asyncio.run(service.route(envelope))

    assert plan.mode == "dm"
    assert plan.narration_brief == "keep it short"
    assert client.router_requests
    assert client.router_requests[0].response_format == {"type": "json_object"}


def test_router_service_rejects_invalid_json_payload() -> None:
    client = StubOllamaClient(router_content="not-json")
    service = RouterService(client)
    envelope = TurnEnvelope(
        campaign_id="camp-1",
        channel_id="chan-1",
        user_id="user-1",
        trace_id="trace-1",
        content="发起攻击",
    )

    with pytest.raises(RouterError):
        asyncio.run(service.route(envelope))


def test_router_service_normalizes_common_schema_aliases() -> None:
    client = StubOllamaClient(
        router_content=(
            '{"mode":"dm","tool_calls":[{"tool":"lookup_rule","params":{"topic":"stealth"}}],'
            '"state_intents":["exploring"],"narration_brief":"brief"}'
        )
    )
    service = RouterService(client)
    envelope = TurnEnvelope(
        campaign_id="camp-1",
        channel_id="chan-1",
        user_id="user-1",
        trace_id="trace-1",
        content="我想潜行。",
    )

    plan = asyncio.run(service.route(envelope))

    assert plan.tool_calls[0].name == "lookup_rule"
    assert plan.tool_calls[0].arguments == {"topic": "stealth"}
    assert plan.state_intents[0].kind == "exploring"


def test_router_service_normalizes_string_tool_calls() -> None:
    client = StubOllamaClient(
        router_content='{"mode":"dm","tool_calls":["use flashlights"],"state_intents":[],"narration_brief":"brief"}'
    )
    service = RouterService(client)
    envelope = TurnEnvelope(
        campaign_id="camp-1",
        channel_id="chan-1",
        user_id="user-1",
        trace_id="trace-1",
        content="我点火把。",
    )

    plan = asyncio.run(service.route(envelope))

    assert plan.tool_calls[0].name == "use flashlights"
    assert plan.tool_calls[0].arguments == {}


def test_turn_runner_passes_compact_context_to_narrator() -> None:
    client = StubOllamaClient(
        router_content=(
            '{"mode":"scene","tool_calls":[{"name":"lookup_rule","arguments":{"topic":"stealth"}}],'
            '"state_intents":[{"kind":"scene_focus","payload":{"speaker":"守卫"}}],'
            '"narration_brief":"用紧张的语气回应。"}'
        ),
        narrator_content="守卫压低声音，说门后有脚步声。",
    )
    router = RouterService(client)
    narrator = NarrationService(client)
    runner = TurnRunner(router=router, narrator=narrator)
    envelope = TurnEnvelope(
        campaign_id="camp-1",
        channel_id="chan-1",
        user_id="user-1",
        trace_id="trace-1",
        content="我贴着门偷听。",
    )

    result = asyncio.run(
        runner.run_turn(
            envelope,
            tool_results=[{"name": "lookup_rule", "result": "被动察觉 13"}],
            state_snapshot={"location": "地窖门口", "combat_round": 0},
        )
    )

    assert result.plan.mode == "scene"
    assert result.reply == "守卫压低声音，说门后有脚步声。"
    narration_request = client.narrator_requests[0]
    assert "combat_round" in narration_request.user_prompt
    assert "被动察觉 13" in narration_request.user_prompt
    assert "tool_calls" not in narration_request.user_prompt


def test_turn_runner_includes_guidance_context_from_gameplay() -> None:
    from dm_bot.adventures.models import AdventurePackage
    from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
    from dm_bot.rules.compendium import FixtureCompendium
    from dm_bot.rules.engine import RulesEngine

    gameplay = GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={})),
    )
    gameplay.load_adventure(
        AdventurePackage.model_validate(
            {
                "slug": "guided_module",
                "title": "Guided Module",
                "premise": "测试。",
                "start_scene_id": "hall",
                "scenes": [
                    {
                        "id": "hall",
                        "title": "大厅",
                        "summary": "白色大厅中央有一座石钟。",
                        "guidance": {"light_hint": "注意石钟和门。"},
                        "interactables": [
                            {
                                "id": "clock",
                                "title": "石钟",
                                "keywords": ["钟"],
                                "judgement": "auto",
                                "result_text": "钟针在倒退。"
                            }
                        ]
                    }
                ],
            }
        )
    )
    client = StubOllamaClient(
        router_content='{"mode":"dm","tool_calls":[],"state_intents":[],"narration_brief":"brief"}',
        narrator_content="你看到石钟的指针正在倒退。",
    )
    runner = TurnRunner(router=RouterService(client), narrator=NarrationService(client), gameplay=gameplay)

    result = asyncio.run(
        runner.run_turn(
            TurnEnvelope(
                campaign_id="camp-1",
                channel_id="chan-1",
                user_id="user-1",
                trace_id="trace-1",
                content="我看钟。",
            )
        )
    )

    assert "倒退" in result.reply
    assert "guidance" in client.narrator_requests[0].user_prompt


def test_model_snapshot_reports_router_and_narrator_readiness(monkeypatch) -> None:
    monkeypatch.setattr(
        "dm_bot.runtime.model_checks.list_ollama_models",
        lambda settings: ["qwen3:1.7b", "collective-v0.1-chinese-roleplay-8b"],
    )
    settings = Settings(
        router_model="qwen3:1.7b",
        narrator_model="collective-v0.1-chinese-roleplay-8b",
        ollama_base_url="http://localhost:11434/v1",
    )

    snapshot = build_model_snapshot(settings)

    assert snapshot.status == "ok"
    assert snapshot.checks["router_model"].name == "qwen3:1.7b"
    assert snapshot.checks["narrator_model"].name == "collective-v0.1-chinese-roleplay-8b"
