import asyncio

from dm_bot.config import Settings
from dm_bot.discord_bot.commands import BotCommands
from dm_bot.orchestrator.session_store import SessionStore
from dm_bot.persistence.store import PersistenceStore


class FakeResponse:
    def __init__(self) -> None:
        self.deferred = False
        self.messages: list[tuple[str, bool]] = []

    async def send_message(self, content: str, ephemeral: bool = False) -> None:
        self.messages.append((content, ephemeral))

    async def defer(self, *, thinking: bool = False, ephemeral: bool = False) -> None:
        self.deferred = True


class FakeFollowup:
    def __init__(self) -> None:
        self.messages: list[str] = []

    async def send(self, content: str) -> None:
        self.messages.append(content)


class FakeInteraction:
    def __init__(self, *, channel_id: str = "chan-1", guild_id: str = "guild-1", user_id: str = "user-1") -> None:
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.user = type("User", (), {"id": user_id})()
        self.response = FakeResponse()
        self.followup = FakeFollowup()


class StubTurnService:
    def __init__(self) -> None:
        self.calls = []

    async def handle_turn(self, *, campaign_id: str, channel_id: str, user_id: str, content: str):
        self.calls.append((campaign_id, channel_id, user_id, content))
        return type("TurnResult", (), {"reply": "地牢里传来低语。", "trace_id": "trace-1"})()


def test_setup_command_reports_models() -> None:
    commands = BotCommands(
        settings=Settings(),
        session_store=SessionStore(),
        turn_coordinator=StubTurnService(),
    )
    interaction = FakeInteraction()

    asyncio.run(commands.setup_check(interaction))

    assert interaction.response.messages
    assert "router_model" in interaction.response.messages[0][0]


def test_bind_and_join_commands_manage_campaign_session() -> None:
    store = SessionStore()
    commands = BotCommands(
        settings=Settings(),
        session_store=store,
        turn_coordinator=StubTurnService(),
    )
    owner_interaction = FakeInteraction(channel_id="chan-1", user_id="owner")
    joiner_interaction = FakeInteraction(channel_id="chan-1", user_id="guest")

    asyncio.run(commands.bind_campaign(owner_interaction, campaign_id="camp-1"))
    asyncio.run(commands.join_campaign(joiner_interaction))

    session = store.get_by_channel("chan-1")
    assert session is not None
    assert session.member_ids == {"owner", "guest"}


def test_turn_command_defers_and_sends_followup_reply() -> None:
    turn_service = StubTurnService()
    store = SessionStore()
    store.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
    commands = BotCommands(
        settings=Settings(),
        session_store=store,
        turn_coordinator=turn_service,
    )
    interaction = FakeInteraction(channel_id="chan-1", user_id="user-1")

    asyncio.run(commands.take_turn(interaction, content="我推开门。"))

    assert interaction.response.deferred is True
    assert interaction.followup.messages == ["地牢里传来低语。"]
    assert turn_service.calls == [("camp-1", "chan-1", "user-1", "我推开门。")]


def test_bind_command_persists_session_binding(tmp_path) -> None:
    store = SessionStore()
    persistence = PersistenceStore(tmp_path / "commands.sqlite3")
    commands = BotCommands(
        settings=Settings(),
        session_store=store,
        turn_coordinator=StubTurnService(),
        persistence_store=persistence,
    )
    interaction = FakeInteraction(channel_id="chan-1", guild_id="guild-1", user_id="owner")

    asyncio.run(commands.bind_campaign(interaction, campaign_id="camp-1"))

    restored = persistence.load_sessions()
    assert restored["chan-1"]["campaign_id"] == "camp-1"
