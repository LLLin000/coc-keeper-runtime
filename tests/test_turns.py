import asyncio

from dm_bot.models.schemas import TurnEnvelope
from dm_bot.orchestrator.session_store import SessionStore
from dm_bot.orchestrator.turns import TurnCoordinator, TurnRequest


class StubTurnRunner:
    def __init__(self) -> None:
        self.calls: list[TurnEnvelope] = []
        self.active = 0
        self.max_active = 0

    async def run_turn(
        self,
        envelope: TurnEnvelope,
        *,
        session_phase="lobby",
        intent=None,
        intent_reasoning="",
        **kwargs,
    ):
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        self.calls.append(envelope)
        await asyncio.sleep(0.01)
        self.active -= 1
        return type("TurnResult", (), {"reply": f"reply:{envelope.content}"})()


def test_session_store_binds_and_tracks_members() -> None:
    store = SessionStore()

    session = store.bind_campaign(
        campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1"
    )
    joined = store.join_campaign(channel_id="chan-1", user_id="user-2")

    assert session.campaign_id == "camp-1"
    assert joined is session
    assert session.member_ids == {"user-1", "user-2"}
    assert store.get_by_channel("chan-1") is session


def test_session_store_can_leave_and_bind_active_character() -> None:
    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1"
    )
    store.join_campaign(channel_id="chan-1", user_id="user-2")

    store.bind_character(channel_id="chan-1", user_id="user-2", character_name="Lia")
    session = store.leave_campaign(channel_id="chan-1", user_id="user-2")

    assert "user-2" not in session.member_ids
    assert session.active_characters == {}


def test_turn_coordinator_serializes_turns_per_campaign() -> None:
    runner = StubTurnRunner()
    coordinator = TurnCoordinator(turn_runner=runner)

    async def exercise() -> list[str]:
        results = await asyncio.gather(
            coordinator.handle_turn(
                TurnRequest(
                    campaign_id="camp-1",
                    channel_id="chan-1",
                    user_id="user-1",
                    content="先攻",
                ),
            ),
            coordinator.handle_turn(
                TurnRequest(
                    campaign_id="camp-1",
                    channel_id="chan-1",
                    user_id="user-2",
                    content="攻击",
                ),
            ),
        )
        return [result.reply for result in results]

    replies = asyncio.run(exercise())

    assert replies == ["reply:先攻", "reply:攻击"]
    assert runner.max_active == 1
    assert all(call.trace_id for call in runner.calls)
