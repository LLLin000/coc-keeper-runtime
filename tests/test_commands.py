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
        self.sent_messages: list[FakeSentMessage] = []

    async def send(self, content: str, **kwargs) -> None:
        self.messages.append(content)
        sent = FakeSentMessage(content)
        self.sent_messages.append(sent)
        if kwargs.get("wait"):
            return sent
        return None


class FakeSentMessage:
    def __init__(self, content: str) -> None:
        self.content = content
        self.edits: list[str] = []

    async def edit(self, *, content: str) -> None:
        self.content = content
        self.edits.append(content)


class FakeChannel:
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.sent_messages: list[FakeSentMessage] = []

    async def send(self, content: str) -> None:
        self.messages.append(content)
        sent = FakeSentMessage(content)
        self.sent_messages.append(sent)
        return sent


class FakeInteraction:
    def __init__(self, *, channel_id: str = "chan-1", guild_id: str = "guild-1", user_id: str = "user-1") -> None:
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.user = type("User", (), {"id": user_id})()
        self.response = FakeResponse()
        self.followup = FakeFollowup()
        self.channel = FakeChannel()


class StubTurnService:
    def __init__(self) -> None:
        self.calls = []

    async def handle_turn(self, *, campaign_id: str, channel_id: str, user_id: str, content: str):
        self.calls.append((campaign_id, channel_id, user_id, content))
        return type("TurnResult", (), {"reply": "地牢里传来低语。", "trace_id": "trace-1"})()

    async def stream_turn(self, *, campaign_id: str, channel_id: str, user_id: str, content: str):
        self.calls.append((campaign_id, channel_id, user_id, content))
        yield "地牢里"
        yield "地牢里传来低语。"


def test_setup_command_reports_models() -> None:
    commands = BotCommands(
        settings=Settings(),
        session_store=SessionStore(),
        turn_coordinator=StubTurnService(),
    )
    interaction = FakeInteraction()

    asyncio.run(commands.setup_check(interaction))

    assert interaction.response.deferred is True
    assert interaction.followup.messages
    assert "router_model" in interaction.followup.messages[0]


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
    assert interaction.followup.messages == ["DM 正在回应…"]
    assert interaction.followup.sent_messages[0].edits[-1] == "地牢里传来低语。"
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


def test_load_adventure_prompts_ready_up_and_records_onboarding_state() -> None:
    from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
    from dm_bot.rules.compendium import FixtureCompendium
    from dm_bot.rules.engine import RulesEngine

    store = SessionStore()
    store.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
    commands = BotCommands(
        settings=Settings(),
        session_store=store,
        turn_coordinator=StubTurnService(),
        gameplay=GameplayOrchestrator(
            importer=None,
            registry=CharacterRegistry(),
            rules_engine=RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={})),
        ),
    )
    interaction = FakeInteraction(channel_id="chan-1", user_id="user-1")

    asyncio.run(commands.load_adventure(interaction, adventure_id="mad_mansion"))

    assert "loaded adventure" in interaction.response.messages[0][0]
    assert interaction.channel.messages
    assert "ready" in interaction.channel.messages[0].lower()
    assert commands._gameplay.adventure_state["onboarding"]["status"] == "awaiting_ready"


def test_ready_command_posts_opening_when_all_members_are_ready() -> None:
    from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
    from dm_bot.rules.compendium import FixtureCompendium
    from dm_bot.rules.engine import RulesEngine

    store = SessionStore()
    store.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
    store.join_campaign(channel_id="chan-1", user_id="user-2")
    gameplay = GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={})),
    )
    gameplay.load_adventure(__import__("dm_bot.adventures.loader", fromlist=["load_adventure"]).load_adventure("mad_mansion"))
    commands = BotCommands(
        settings=Settings(),
        session_store=store,
        turn_coordinator=StubTurnService(),
        gameplay=gameplay,
    )
    first = FakeInteraction(channel_id="chan-1", user_id="user-1")
    second = FakeInteraction(channel_id="chan-1", user_id="user-2")
    first.channel = second.channel

    asyncio.run(commands.ready_for_adventure(first, character_name="调查员A"))
    asyncio.run(commands.ready_for_adventure(second, character_name="调查员B"))

    assert any("疯狂之馆" in message for message in first.channel.messages)
    assert any("先从最显眼的事物开始" in message for message in first.channel.messages)
    assert commands._gameplay.adventure_state["onboarding"]["status"] == "in_progress"


def test_streaming_channel_message_edits_single_message() -> None:
    from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
    from dm_bot.rules.compendium import FixtureCompendium
    from dm_bot.rules.engine import RulesEngine

    store = SessionStore()
    store.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
    gameplay = GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={})),
    )
    coordinator = StubTurnService()
    commands = BotCommands(
        settings=Settings(),
        session_store=store,
        turn_coordinator=coordinator,
        gameplay=gameplay,
    )
    message = type(
        "Message",
        (),
        {
            "channel": FakeChannel(),
            "guild": type("Guild", (), {"id": "guild-1"})(),
            "author": type("Author", (), {"id": "user-1", "bot": False})(),
            "content": "我推开门。",
            "mentions": [],
        },
    )()
    message.channel.id = "chan-1"

    asyncio.run(commands.handle_channel_message_stream(message=message))

    assert message.channel.messages[0] == "DM 正在回应…"
    assert message.channel.sent_messages[0].edits[-1] == "地牢里传来低语。"
