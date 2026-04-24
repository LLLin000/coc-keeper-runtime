import asyncio

from dm_bot.adventures.extraction import extract_room_graph_draft
from dm_bot.models.schemas import ModelResponse
from dm_bot.router.service import RouterService


class StubLLM:
    async def extract_json(self, prompt: str) -> str:
        self.prompt = prompt
        return (
            '{"source_name":"剧本","topology_summary":"一栋宅邸","locations":[],'
            '"trigger_trees":[],"trigger_drafts":[]}'
        )


class StubRouterClient:
    def __init__(self) -> None:
        self.requests = []

    async def call_router(self, request):
        self.requests.append(request)
        return ModelResponse(
            model="test",
            content='{"mode":"dm","tool_calls":[],"state_intents":[],"narration_brief":"描述现场","speaker_hints":[]}',
        )


def test_router_prompt_is_keeper_focused() -> None:
    from dm_bot.models.schemas import TurnEnvelope

    client = StubRouterClient()
    service = RouterService(client)
    asyncio.run(
        service.route(
            TurnEnvelope(
                trace_id="t1",
                campaign_id="c1",
                channel_id="ch1",
                user_id="u1",
                content="我调查墙上的血字。",
            )
        )
    )

    request = client.requests[0]
    assert "Call of Cthulhu Keeper" in request.system_prompt


def test_extraction_prompt_mentions_room_graph_and_keeper_logic() -> None:
    llm = StubLLM()
    asyncio.run(extract_room_graph_draft("大厅里有一座钟。", source_name="剧本", llm=llm))
    assert "Keeper" in llm.prompt
    assert "room graph" in llm.prompt
