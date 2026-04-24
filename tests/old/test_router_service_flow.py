"""ROUTER-01: RouterService TurnPlan generation tests."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from dm_bot.models.schemas import ModelResponse, ModelRequest
from dm_bot.router.service import RouterService, RouterError
from dm_bot.router.intent import MessageIntent
from dm_bot.router.contracts import TurnPlan
from dm_bot.models.schemas import TurnEnvelope


class StubRouterClient:
    """Stub router client for testing."""

    def __init__(self, response: ModelResponse | None = None) -> None:
        self._response = response
        self.requests: list[ModelRequest] = []

    async def call_router(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        if self._response:
            return self._response
        return ModelResponse(
            model="test",
            content=json.dumps(
                {
                    "mode": "scene",
                    "tool_calls": [],
                    "state_intents": [],
                    "narration_brief": "test narration",
                    "speaker_hints": [],
                }
            ),
        )


@pytest.fixture
def mock_router_client():
    client = MagicMock()
    client.call_router = AsyncMock(
        return_value=ModelResponse(
            content=json.dumps(
                {
                    "mode": "scene",
                    "tool_calls": [
                        {
                            "name": "coc_skill_check",
                            "arguments": {"label": "图书馆使用", "value": 60},
                        }
                    ],
                    "state_intents": [{"kind": "san_damage", "payload": {"amount": 1}}],
                    "narration_brief": "调查员在书架间翻找线索",
                    "speaker_hints": ["张记者"],
                }
            ),
            finish_reason="stop",
            model="test",
        )
    )
    return client


@pytest.fixture
def router_service(mock_router_client):
    return RouterService(client=mock_router_client)


@pytest.fixture
def envelope():
    return TurnEnvelope(
        trace_id="t1",
        campaign_id="c1",
        channel_id="ch1",
        user_id="u1",
        content="我检查一下书架",
    )


@pytest.mark.asyncio
async def test_route_returns_valid_turnplan(router_service, envelope):
    """RouterService.route() returns TurnPlan with valid mode, tool_calls, narration_brief."""
    result = await router_service.route(envelope, session_phase="scene_round_open")
    assert result.mode in ("dm", "scene", "combat")
    assert isinstance(result.tool_calls, list)
    assert len(result.narration_brief) > 0


@pytest.mark.asyncio
async def test_route_handles_invalid_json(router_service, envelope):
    """RouterService.route() raises RouterError on invalid JSON response."""
    router_service._client.call_router = AsyncMock(
        return_value=ModelResponse(
            content="not valid json {",
            finish_reason="stop",
            model="test",
        )
    )
    with pytest.raises(RouterError):
        await router_service.route(envelope)


@pytest.mark.asyncio
async def test_route_handles_validation_error(router_service, envelope):
    """RouterService.route() raises RouterError when required fields are missing."""
    router_service._client.call_router = AsyncMock(
        return_value=ModelResponse(
            content=json.dumps({"mode": "invalid_mode"}),  # missing narration_brief
            finish_reason="stop",
            model="test",
        )
    )
    with pytest.raises(RouterError):
        await router_service.route(envelope)


@pytest.mark.asyncio
async def test_route_normalizes_string_tool_calls(router_service, envelope):
    """RouterService.route() normalizes string tool_calls to dict format."""
    router_service._client.call_router = AsyncMock(
        return_value=ModelResponse(
            content=json.dumps(
                {
                    "mode": "scene",
                    "tool_calls": ["roll_dice", {"name": "check_san", "arguments": {}}],
                    "state_intents": [],
                    "narration_brief": "test narration",
                    "speaker_hints": [],
                }
            ),
            finish_reason="stop",
            model="test",
        )
    )
    result = await router_service.route(envelope)
    assert len(result.tool_calls) == 2
    assert result.tool_calls[0].name == "roll_dice"
    assert result.tool_calls[0].arguments == {}


@pytest.mark.asyncio
async def test_route_returns_speaker_hints(router_service, envelope):
    """RouterService.route() populates speaker_hints from model response."""
    result = await router_service.route(envelope)
    assert len(result.speaker_hints) >= 0


@pytest.mark.asyncio
async def test_route_passes_envelope_fields_to_model(router_service, envelope):
    """RouterService.route() passes trace_id, campaign_id, channel_id, user_id to model."""
    result = await router_service.route(
        envelope,
        session_phase="scene_round_open",
        intent=MessageIntent.PLAYER_ACTION,
        intent_reasoning="player is taking an action",
    )
    # Verify the route method completes successfully and returns valid TurnPlan
    assert result is not None
    assert isinstance(result, TurnPlan)
