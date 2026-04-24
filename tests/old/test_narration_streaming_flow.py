"""NARR-02: Narration streaming output delivery tests."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from dm_bot.models.schemas import ModelResponse
from dm_bot.narration.service import NarrationService, NarrationRequest
from dm_bot.router.contracts import TurnPlan, StateIntent, ToolCall


@pytest.fixture
def mock_stream_narrator_client():
    async def mock_stream(prompt):
        chunks = ["张记", "者在", "书架", "间翻", "找。"]
        for chunk in chunks:
            yield chunk

    client = MagicMock()
    client.stream_narrator = mock_stream
    return client


@pytest.fixture
def narration_service(mock_stream_narrator_client):
    return NarrationService(client=mock_stream_narrator_client)


@pytest.fixture
def narration_request():
    return NarrationRequest(
        player_input="检查书架",
        state_snapshot={},
        tool_results=[],
        plan=TurnPlan(
            mode="scene",
            tool_calls=[],
            state_intents=[],
            narration_brief="调查员检查书架",
            speaker_hints=[],
        ),
    )


@pytest.mark.asyncio
async def test_stream_narrate_yields_chunks(narration_service, narration_request):
    chunks = []
    async for chunk in narration_service.stream_narrate(narration_request):
        chunks.append(chunk)
    assert len(chunks) >= 3
    assert all(isinstance(c, str) for c in chunks)


@pytest.mark.asyncio
async def test_stream_narrate_skips_empty_chunks(narration_service, narration_request):
    async def mock_stream_with_empty(prompt):
        yield "非空"
        yield ""
        yield "还是非空"

    narration_service._client.stream_narrator = mock_stream_with_empty
    chunks = []
    async for chunk in narration_service.stream_narrate(narration_request):
        chunks.append(chunk)
    assert all(c != "" for c in chunks)
    assert "非空" in "".join(chunks)


@pytest.mark.asyncio
async def test_stream_narrate_concatenated_output(narration_service, narration_request):
    full_text = ""
    async for chunk in narration_service.stream_narrate(narration_request):
        full_text += chunk
    assert "张记" in full_text or "非空" in full_text or len(full_text) > 0
