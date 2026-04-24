import asyncio
import json

from dm_bot.narration.service import NarrationRequest, NarrationService
from dm_bot.router.contracts import TurnPlan
from tests.fakes.models import FastMock


def test_narration_service_uses_dm_focused_chinese_prompt() -> None:
    client = FastMock()
    service = NarrationService(client)

    asyncio.run(
        service.narrate(
            NarrationRequest(
                player_input="我推开门。",
                state_snapshot={"mode": "dm"},
                tool_results=[],
                plan=TurnPlan(
                    mode="dm",
                    tool_calls=[],
                    state_intents=[],
                    narration_brief="描述门后的场景。",
                    speaker_hints=[],
                ),
            )
        )
    )

    request = client.narrator_requests[0]
    assert "Chinese Call of Cthulhu Keeper" in request.system_prompt
    payload = json.loads(request.user_prompt)
    assert payload["player_input"] == "我推开门。"


def test_narration_service_includes_public_and_gm_adventure_context() -> None:
    client = FastMock()
    service = NarrationService(client)

    asyncio.run(
        service.narrate(
            NarrationRequest(
                player_input="我检查大厅里的钟。",
                state_snapshot={
                    "adventure": {
                        "public": {"scene": "大厅", "state": {"time_remaining": 180}},
                        "gm": {"state": {"administrator_truth": "奈亚化身"}},
                    }
                },
                tool_results=[],
                plan=TurnPlan(
                    mode="dm",
                    tool_calls=[],
                    state_intents=[],
                    narration_brief="描述当前大厅和压力。",
                    speaker_hints=[],
                ),
            )
        )
    )

    request = client.narrator_requests[0]
    payload = json.loads(request.user_prompt)
    assert (
        payload["state_snapshot"]["adventure"]["public"]["state"]["time_remaining"]
        == 180
    )
    assert (
        payload["state_snapshot"]["adventure"]["gm"]["state"]["administrator_truth"]
        == "奈亚化身"
    )


def test_narration_service_streams_chunks() -> None:
    client = FastMock(narrator_content="回复")
    service = NarrationService(client)

    async def collect() -> list[str]:
        chunks = []
        async for chunk in service.stream_narrate(
            NarrationRequest(
                player_input="我推开门。",
                state_snapshot={"mode": "dm"},
                tool_results=[],
                plan=TurnPlan(
                    mode="dm",
                    tool_calls=[],
                    state_intents=[],
                    narration_brief="描述门后的场景。",
                    speaker_hints=[],
                ),
            )
        ):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect())

    assert chunks == ["回", "复"]
    assert client.narrator_requests
