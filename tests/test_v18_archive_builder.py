import asyncio
from dataclasses import dataclass

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

    def typing(self):
        class _Typing:
            async def __aenter__(self_inner):
                return None

            async def __aexit__(self_inner, exc_type, exc, tb):
                return False

        return _Typing()


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


class FakeGuild:
    def __init__(self, guild_id: str) -> None:
        self.id = guild_id


class FakeMessage:
    def __init__(
        self,
        *,
        channel_id: str,
        guild_id: str = "guild-1",
        user_id: str = "user-1",
        display_name: str = "Alice",
        content: str,
    ) -> None:
        self.channel = FakeChannel()
        self.channel.id = channel_id
        self.guild = FakeGuild(guild_id)
        self.author = FakeUser(user_id, display_name)
        self.author.bot = False
        self.content = content
        self.mentions: list[object] = []


@dataclass
class FakeQuestionChoice:
    slot: str
    question: str


class FakeInterviewPlanner:
    async def next_question(self, session):
        concept = session.answers.get("concept", "")
        if "key_past_event" not in session.answers:
            if "落魄" in concept:
                return FakeQuestionChoice(slot="key_past_event", question="你为什么会落魄到这一步？最近究竟发生了什么？")
            return FakeQuestionChoice(slot="key_past_event", question="过去究竟发生过什么，才把他推到了今天这一步？")
        if "life_goal" not in session.answers:
            return FakeQuestionChoice(slot="life_goal", question="如果这一切还没把他压垮，他现在最想达成的人生目标是什么？")
        if "weakness" not in session.answers:
            return FakeQuestionChoice(slot="weakness", question="他最致命的弱点或劣势是什么？")
        if "disposition" not in session.answers:
            return FakeQuestionChoice(slot="disposition", question="别人通常会怎么评价他的处事方式？")
        return FakeQuestionChoice(slot="favored_skills", question="列出 2-4 个他最拿手的技能，用逗号分隔。")


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
        interview_planner=FakeInterviewPlanner(),
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
    asyncio.run(commands.builder_reply(interaction, answer="26岁的夜班记者"))
    asyncio.run(commands.builder_reply(interaction, answer="我总在夜里追新闻，结果因为一篇得罪人的报道被行业封杀。"))
    asyncio.run(commands.builder_reply(interaction, answer="我想查清那篇报道背后的真相，重新拿回自己的名字。"))
    asyncio.run(commands.builder_reply(interaction, answer="我太执拗，也太容易因为愧疚把自己逼进死角。"))
    asyncio.run(commands.builder_reply(interaction, answer="冷静但固执。"))
    asyncio.run(commands.builder_reply(interaction, answer="图书馆使用,聆听,心理学"))

    profiles = repo.list_profiles("user-1")
    assert len(profiles) == 1
    assert profiles[0].name == "林秋"
    assert profiles[0].coc.occupation == "夜班记者"
    assert profiles[0].coc.attributes.int == 70
    assert profiles[0].life_goal.startswith("我想查清")
    assert "执拗" in profiles[0].weakness
    assert profiles[0].finishing.recommended_interest_skills
    assert "规则" in profiles[0].finishing.rules_note


def test_builder_uses_concept_to_ask_a_more_specific_follow_up() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.coc.builder import ConversationalCharacterBuilder

    builder = ConversationalCharacterBuilder(
        archive_repository=InvestigatorArchiveRepository(),
        roll_provider=lambda expr: {"3d6*5": 55, "2d6+6*5": 70, "luck": 60}[expr],
        interview_planner=FakeInterviewPlanner(),
    )

    assert builder.start(user_id="user-1", visibility="private") == "先给这位调查员起个名字。"
    prompt, profile = asyncio.run(builder.answer(user_id="user-1", answer="林钟轩"))
    assert profile is None
    assert "一句短话" in prompt

    prompt, profile = asyncio.run(builder.answer(user_id="user-1", answer="38岁的落魄临床医生"))

    assert profile is None
    assert "落魄" in prompt or "发生了什么" in prompt


def test_archive_channel_plain_messages_advance_builder_session() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.coc.builder import ConversationalCharacterBuilder

    repo = InvestigatorArchiveRepository()
    builder = ConversationalCharacterBuilder(
        archive_repository=repo,
        roll_provider=lambda expr: {"3d6*5": 55, "2d6+6*5": 70, "luck": 60}[expr],
        interview_planner=FakeInterviewPlanner(),
    )
    store = SessionStore()
    store.bind_archive_channel(guild_id="guild-1", channel_id="archive-1")
    commands = BotCommands(
        settings=Settings(),
        session_store=store,
        turn_coordinator=None,
        archive_repository=repo,
        character_builder=builder,
    )
    interaction = FakeInteraction(channel_id="archive-1")

    asyncio.run(commands.start_character_builder(interaction, visibility="private"))

    name_message = FakeMessage(channel_id="archive-1", content="林钟轩")
    asyncio.run(commands.handle_channel_message_stream(message=name_message))

    assert "一句短话" in name_message.channel.messages[-1]


def test_archive_channel_plain_messages_can_finish_builder_session() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.coc.builder import ConversationalCharacterBuilder

    repo = InvestigatorArchiveRepository()
    builder = ConversationalCharacterBuilder(
        archive_repository=repo,
        roll_provider=lambda expr: {"3d6*5": 55, "2d6+6*5": 70, "luck": 60}[expr],
        interview_planner=FakeInterviewPlanner(),
    )
    store = SessionStore()
    store.bind_archive_channel(guild_id="guild-1", channel_id="archive-1")
    commands = BotCommands(
        settings=Settings(),
        session_store=store,
        turn_coordinator=None,
        archive_repository=repo,
        character_builder=builder,
    )
    interaction = FakeInteraction(channel_id="archive-1")
    asyncio.run(commands.start_character_builder(interaction, visibility="private"))

    for answer in [
        "林钟轩",
        "38岁的落魄临床医生",
        "三年前的一场手术纠纷把我从医院里赶了出来。",
        "我想证明那次事故里真正犯错的人不是我。",
        "我太骄傲，也太容易在压力下酗酒。",
        "外冷内热，但防备心很重。",
        "医学,急救,心理学",
    ]:
        message = FakeMessage(channel_id="archive-1", content=answer)
        asyncio.run(commands.handle_channel_message_stream(message=message))

    profiles = repo.list_profiles("user-1")
    assert len(profiles) == 1
    assert profiles[0].name == "林钟轩"
    assert profiles[0].coc.occupation == "临床医生"
    assert "证明" in profiles[0].life_goal
    assert profiles[0].specialty


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


def test_profiles_command_shows_richer_summary_line() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository

    repo = InvestigatorArchiveRepository()
    repo.create_profile(
        user_id="user-1",
        name="林钟轩",
        occupation="临床医生",
        age=38,
        concept="38岁的落魄临床医生",
        background="被手术纠纷拖下神坛的临床医生。",
        key_past_event="一次违规手术让他被迫离开三甲医院。",
        life_goal="赚很多钱然后逃到山里隐居。",
        weakness="过度自信且酗酒。",
        disposition="嘴硬，控制欲强。",
        specialty="神经外科",
        career_arc="三甲医院神经外科名医，后被贬至县城医院。",
        core_belief="我不是在犯错，我是在救人。",
        portrait_summary="落魄但不肯认输的临床医生。",
        favored_skills=["医学", "急救", "心理学"],
        generation={"str": 50, "con": 55, "dex": 60, "app": 65, "pow": 70, "siz": 50, "int": 75, "edu": 80, "luck": 45},
    )
    commands = BotCommands(
        settings=Settings(),
        session_store=SessionStore(),
        turn_coordinator=None,
        archive_repository=repo,
    )
    interaction = FakeInteraction(channel_id="archive-1")

    asyncio.run(commands.list_profiles(interaction))

    content = interaction.response.messages[0][0]
    assert "临床医生" in content
    assert "目标" in content


def test_profile_detail_command_renders_investigator_card_sections() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository

    repo = InvestigatorArchiveRepository()
    profile = repo.create_profile(
        user_id="user-1",
        name="林钟轩",
        occupation="临床医生",
        age=38,
        concept="38岁的落魄临床医生",
        background="被手术纠纷拖下神坛的临床医生。",
        key_past_event="一次违规手术让他被迫离开三甲医院。",
        life_goal="赚很多钱然后逃到山里隐居。",
        weakness="过度自信且酗酒。",
        disposition="嘴硬，控制欲强。",
        specialty="神经外科",
        career_arc="三甲医院神经外科名医，后被贬至县城医院。",
        core_belief="我不是在犯错，我是在救人。",
        portrait_summary="落魄但不肯认输的临床医生。",
        favored_skills=["医学", "急救", "心理学"],
        generation={"str": 50, "con": 55, "dex": 60, "app": 65, "pow": 70, "siz": 50, "int": 75, "edu": 80, "luck": 45},
    )
    commands = BotCommands(
        settings=Settings(),
        session_store=SessionStore(),
        turn_coordinator=None,
        archive_repository=repo,
    )
    interaction = FakeInteraction(channel_id="archive-1")

    asyncio.run(commands.profile_detail(interaction, profile_id=profile.profile_id))

    content = interaction.response.messages[0][0]
    assert "【调查员档案】" in content
    assert "【人物】" in content
    assert "【数值】" in content
    assert "【塑造】" in content
    assert "神经外科" in content
