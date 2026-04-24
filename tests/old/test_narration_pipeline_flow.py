"""NARR-01: Narration pipeline prompt construction tests."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from dm_bot.models.schemas import ModelResponse
from dm_bot.narration.service import NarrationService, NarrationRequest
from dm_bot.router.contracts import TurnPlan, StateIntent, ToolCall


@pytest.fixture
def mock_narrator_client():
    client = MagicMock()
    client.call_narrator = AsyncMock(
        return_value=ModelResponse(
            content="张记者在书架间翻找，突然发现一本日记。",
            finish_reason="stop",
            model="test",
        )
    )
    return client


@pytest.fixture
def narration_service(mock_narrator_client):
    return NarrationService(client=mock_narrator_client)


@pytest.fixture
def narration_request():
    return NarrationRequest(
        player_input="我检查一下书架",
        state_snapshot={"location": "书房", "time": "深夜"},
        tool_results=[{"name": "coc_skill_check", "result": "hard success"}],
        plan=TurnPlan(
            mode="scene",
            tool_calls=[ToolCall(name="coc_skill_check", arguments={})],
            state_intents=[StateIntent(kind="san_check", payload={})],
            narration_brief="调查员在书架间翻找线索",
            speaker_hints=["张记者"],
        ),
    )


@pytest.mark.asyncio
async def test_build_prompt_includes_mode_and_narration_brief(
    narration_service, narration_request
):
    prompt = narration_service._build_prompt(narration_request)
    data = json.loads(prompt)
    assert data["mode"] == "scene"
    assert "书架" in data["narration_brief"]


@pytest.mark.asyncio
async def test_build_prompt_includes_state_snapshot(
    narration_service, narration_request
):
    prompt = narration_service._build_prompt(narration_request)
    data = json.loads(prompt)
    assert "state_snapshot" in data
    assert data["state_snapshot"]["location"] == "书房"


@pytest.mark.asyncio
async def test_build_prompt_includes_tool_results(narration_service, narration_request):
    prompt = narration_service._build_prompt(narration_request)
    data = json.loads(prompt)
    assert "tool_results" in data
    assert len(data["tool_results"]) == 1


@pytest.mark.asyncio
async def test_build_prompt_includes_player_input(narration_service, narration_request):
    prompt = narration_service._build_prompt(narration_request)
    data = json.loads(prompt)
    assert "player_input" in data
    assert "书架" in data["player_input"]


@pytest.mark.asyncio
async def test_build_prompt_state_intents_as_dicts(
    narration_service, narration_request
):
    prompt = narration_service._build_prompt(narration_request)
    data = json.loads(prompt)
    assert "state_intents" in data
    assert len(data["state_intents"]) == 1
    assert data["state_intents"][0]["kind"] == "san_check"


@pytest.mark.asyncio
async def test_system_prompt_contains_chinese_keeper_tone(
    narration_service, narration_request
):
    model_request = narration_service._build_model_request(narration_request)
    assert (
        "Chinese" in model_request.system_prompt
        or "中文" in model_request.system_prompt
    )
    assert (
        "Keeper" in model_request.system_prompt
        or "Keeper" in model_request.system_prompt
    )


@pytest.mark.asyncio
async def test_narrate_returns_string_content(narration_service, narration_request):
    result = await narration_service.narrate(narration_request)
    assert isinstance(result, str)
    assert len(result) > 0
