import asyncio

from dm_bot.config import Settings
from dm_bot.discord_bot.commands import BotCommands
from dm_bot.orchestrator.session_store import SessionStore


class FakeResponse:
    def __init__(self) -> None:
        self.messages: list[tuple[str, bool]] = []

    async def send_message(self, content: str, ephemeral: bool = False) -> None:
        self.messages.append((content, ephemeral))

    async def defer(self, *, thinking: bool = False, ephemeral: bool = False) -> None:
        return None


class FakeFollowup:
    def __init__(self) -> None:
        self.messages: list[tuple[str, bool]] = []

    async def send(self, content: str, ephemeral: bool = False, **kwargs):
        self.messages.append((content, ephemeral))
        return None


class FakeChannel:
    def __init__(self) -> None:
        self.messages: list[str] = []

    async def send(self, content: str):
        self.messages.append(content)
        return None


class FakeUser:
    def __init__(self, user_id: str, display_name: str = "Alice") -> None:
        self.id = user_id
        self.display_name = display_name


class FakeInteraction:
    def __init__(self, *, channel_id: str, guild_id: str = "guild-1", user_id: str = "user-1", display_name: str = "Alice") -> None:
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.user = FakeUser(user_id, display_name)
        self.response = FakeResponse()
        self.followup = FakeFollowup()
        self.channel = FakeChannel()


def test_sheet_command_redirects_from_game_hall_to_archive_channel() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
    from dm_bot.rules.compendium import FixtureCompendium
    from dm_bot.rules.engine import RulesEngine

    store = SessionStore()
    store.bind_campaign(campaign_id="camp-1", channel_id="hall-1", guild_id="guild-1", owner_id="user-1")
    store.bind_archive_channel(guild_id="guild-1", channel_id="archive-1")
    gameplay = GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={})),
    )
    repo = InvestigatorArchiveRepository()
    repo.create_profile(
        user_id="user-1",
        name="Alice Carter",
        occupation="记者",
        age=27,
        background="夜班记者",
        disposition="冷静",
        favored_skills=["图书馆使用", "聆听"],
        generation={
            "str": 50, "con": 55, "dex": 60, "app": 65, "pow": 70, "siz": 50, "int": 75, "edu": 80, "luck": 45
        },
    )
    commands = BotCommands(
        settings=Settings(),
        session_store=store,
        turn_coordinator=None,
        gameplay=gameplay,
        archive_repository=repo,
    )

    interaction = FakeInteraction(channel_id="hall-1")
    asyncio.run(commands.show_sheet(interaction))

    assert "archive-1" in interaction.response.messages[0][0]


def test_conversational_builder_creates_archive_profile() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.coc.builder import ConversationalCharacterBuilder

    repo = InvestigatorArchiveRepository()
    builder = ConversationalCharacterBuilder(
        archive_repository=repo,
        roll_provider=lambda expr: {"3d6*5": 55, "2d6+6*5": 70, "luck": 60}[expr],
    )
    commands = BotCommands(
        settings=Settings(),
        session_store=SessionStore(),
        turn_coordinator=None,
        archive_repository=repo,
        character_builder=builder,
    )
    interaction = FakeInteraction(channel_id="archive-1")

    asyncio.run(commands.start_character_builder(interaction, visibility="private"))
    asyncio.run(commands.builder_reply(interaction, answer="林秋"))
    asyncio.run(commands.builder_reply(interaction, answer="记者"))
    asyncio.run(commands.builder_reply(interaction, answer="26"))
    asyncio.run(commands.builder_reply(interaction, answer="我总在夜里追新闻。"))
    asyncio.run(commands.builder_reply(interaction, answer="冷静但固执。"))
    asyncio.run(commands.builder_reply(interaction, answer="图书馆使用,聆听,心理学"))

    profiles = repo.list_profiles("user-1")
    assert len(profiles) == 1
    assert profiles[0].name == "林秋"
    assert profiles[0].coc.occupation == "记者"
    assert profiles[0].coc.attributes.int == 70


def test_ready_projects_selected_archive_profile_without_mutating_archive() -> None:
    from dm_bot.adventures.loader import load_adventure
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
    from dm_bot.rules.compendium import FixtureCompendium
    from dm_bot.rules.engine import RulesEngine

    store = SessionStore()
    store.bind_campaign(campaign_id="camp-1", channel_id="hall-1", guild_id="guild-1", owner_id="user-1")
    store.bind_archive_channel(guild_id="guild-1", channel_id="archive-1")
    gameplay = GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={})),
    )
    gameplay.load_adventure(load_adventure("mad_mansion"))
    repo = InvestigatorArchiveRepository()
    profile = repo.create_profile(
        user_id="user-1",
        name="林秋",
        occupation="记者",
        age=26,
        background="夜班记者",
        disposition="冷静但固执",
        favored_skills=["图书馆使用", "聆听", "心理学"],
        generation={
            "str": 50, "con": 55, "dex": 60, "app": 65, "pow": 70, "siz": 50, "int": 75, "edu": 80, "luck": 45
        },
    )
    store.select_archive_profile(channel_id="hall-1", user_id="user-1", profile_id=profile.profile_id)
    commands = BotCommands(
        settings=Settings(),
        session_store=store,
        turn_coordinator=None,
        gameplay=gameplay,
        archive_repository=repo,
    )
    interaction = FakeInteraction(channel_id="hall-1")

    asyncio.run(commands.ready_for_adventure(interaction))
    gameplay.apply_panel_update(user_id="user-1", san=-5, note="在模组里受到了惊吓")

    panel = gameplay.investigator_panel_snapshot("user-1")
    archive_profile = repo.get_profile("user-1", profile.profile_id)

    assert panel["name"] == "林秋"
    assert panel["san"] == archive_profile.coc.san - 5
    assert archive_profile.coc.san == 70
