import asyncio
import json

from dm_bot.models.schemas import ModelResponse
from dm_bot.narration.service import NarrationRequest, NarrationService
from dm_bot.router.contracts import TurnPlan


class StubClient:
    def __init__(self) -> None:
        self.requests = []

    async def call_narrator(self, request):
        self.requests.append(request)
        return ModelResponse(model="test", content="回复")


def test_narration_service_uses_dm_focused_chinese_prompt() -> None:
    client = StubClient()
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

    request = client.requests[0]
    assert "Chinese D&D DM" in request.system_prompt
    payload = json.loads(request.user_prompt)
    assert payload["player_input"] == "我推开门。"
