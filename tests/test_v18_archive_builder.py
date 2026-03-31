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
    def __init__(
        self, user_id: str, display_name: str = "Alice", *, administrator: bool = False
    ) -> None:
        self.id = user_id
        self.display_name = display_name
        self.guild_permissions = type(
            "GuildPermissions", (), {"administrator": administrator}
        )()


class FakeInteraction:
    def __init__(
        self,
        *,
        channel_id: str,
        guild_id: str = "guild-1",
        user_id: str = "user-1",
        display_name: str = "Alice",
        administrator: bool = False,
    ) -> None:
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.user = FakeUser(user_id, display_name, administrator=administrator)
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
                return FakeQuestionChoice(
                    slot="key_past_event",
                    question="你为什么会落魄到这一步？最近究竟发生了什么？",
                )
            return FakeQuestionChoice(
                slot="key_past_event",
                question="过去究竟发生过什么，才把他推到了今天这一步？",
            )
        if "life_goal" not in session.answers:
            return FakeQuestionChoice(
                slot="life_goal",
                question="如果这一切还没把他压垮，他现在最想达成的人生目标是什么？",
            )
        if "weakness" not in session.answers:
            return FakeQuestionChoice(
                slot="weakness", question="他最致命的弱点或劣势是什么？"
            )
        if "core_belief" not in session.answers:
            return FakeQuestionChoice(
                slot="core_belief",
                question="如果别人说这一切都是他的错，他会怎么替自己辩护？",
            )
        return FakeQuestionChoice(
            slot="important_person", question="在他心里最重要的人是谁？"
        )


def test_sheet_command_redirects_from_game_hall_to_archive_channel() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
    from dm_bot.rules.compendium import FixtureCompendium
    from dm_bot.rules.engine import RulesEngine

    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp-1", channel_id="hall-1", guild_id="guild-1", owner_id="user-1"
    )
    store.bind_archive_channel(guild_id="guild-1", channel_id="archive-1")
    gameplay = GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={})
        ),
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
            "str": 50,
            "con": 55,
            "dex": 60,
            "app": 65,
            "pow": 70,
            "siz": 50,
            "int": 75,
            "edu": 80,
            "luck": 45,
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

    assert "角色档案" in interaction.response.messages[0][0]


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
    asyncio.run(
        commands.builder_reply(
            interaction, answer="我总在夜里追新闻，结果因为一篇得罪人的报道被行业封杀。"
        )
    )
    asyncio.run(
        commands.builder_reply(
            interaction, answer="我想查清那篇报道背后的真相，重新拿回自己的名字。"
        )
    )
    asyncio.run(
        commands.builder_reply(
            interaction, answer="我太执拗，也太容易因为愧疚把自己逼进死角。"
        )
    )
    asyncio.run(
        commands.builder_reply(
            interaction, answer="就算所有人都怀疑我，真相也值得追到底。"
        )
    )
    asyncio.run(commands.builder_reply(interaction, answer="我姐姐，她还愿意相信我。"))
    asyncio.run(commands.builder_reply(interaction, answer="图书馆使用,聆听,心理学"))

    profiles = repo.list_profiles("user-1")
    assert len(profiles) == 1
    assert profiles[0].name == "林秋"
    assert profiles[0].coc.occupation == "夜班记者"
    assert profiles[0].coc.attributes.int == 70
    assert profiles[0].life_goal.startswith("我想查清")
    assert "执拗" in profiles[0].weakness
    assert "低谷" in profiles[0].background or "命运" in profiles[0].background
    assert "姐姐" in profiles[0].important_person or "姐姐" in profiles[0].important_tie
    assert profiles[0].finishing.recommended_interest_skills
    assert "规则" in profiles[0].finishing.rules_note
    assert "不会静默覆盖" in interaction.response.messages[-1][0]
    assert "人物画像" in interaction.response.messages[-2][0]


def test_builder_uses_concept_to_ask_a_more_specific_follow_up() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.coc.builder import AnswerNormalizer, ConversationalCharacterBuilder

    builder = ConversationalCharacterBuilder(
        archive_repository=InvestigatorArchiveRepository(),
        roll_provider=lambda expr: {"3d6*5": 55, "2d6+6*5": 70, "luck": 60}[expr],
        interview_planner=FakeInterviewPlanner(),
    )

    assert "让我先了解一下这位即将踏入黑暗的调查员" in builder.start(
        user_id="user-1", visibility="private"
    )
    prompt, profile = asyncio.run(builder.answer(user_id="user-1", answer="林钟轩"))
    assert profile is None
    assert "一句话勾勒" in prompt

    prompt, profile = asyncio.run(
        builder.answer(user_id="user-1", answer="38岁的落魄临床医生")
    )

    assert profile is None
    assert "落魄" in prompt or "发生了什么" in prompt

    normalizer = AnswerNormalizer()
    normalized = normalizer.normalized_contract(builder._sessions["user-1"].answers)
    assert normalized.age == "38"
    assert normalized.occupation == "临床医生"


def test_answer_normalizer_canonicalizes_age_occupation_and_skills() -> None:
    from dm_bot.coc.builder import AnswerNormalizer

    normalizer = AnswerNormalizer()

    assert normalizer.normalize_slot(
        slot="age", raw=" 38 岁左右 ", current_answers={}
    ) == {"age": "38"}
    assert normalizer.normalize_slot(
        slot="occupation", raw="我是一个 临床医生 ", current_answers={}
    ) == {"occupation": "临床医生"}
    assert normalizer.normalize_slot(
        slot="favored_skills",
        raw="医学， 急救、心理学/聆听",
        current_answers={},
    ) == {"favored_skills": "医学, 急救, 心理学, 聆听"}


def test_section_normalizer_preserves_explicit_answers_over_ai_synthesis() -> None:
    from dm_bot.coc.builder import (
        AnswerNormalizer,
        CharacterSheetSynthesis,
        SectionNormalizer,
    )

    answers = {
        "name": "林钟轩",
        "concept": "38岁的落魄临床医生",
        "age": "38",
        "occupation": "临床医生",
        "key_past_event": "一次手术纠纷毁掉了他的声誉。",
        "life_goal": "赚很多钱然后隐居。",
        "weakness": "过度自信且酗酒。",
        "disposition": "嘴硬，控制欲强。",
        "favored_skills": "医学, 急救, 心理学",
    }
    synthesis = CharacterSheetSynthesis(
        key_past_event="AI 改写的过去",
        life_goal="AI 改写的目标",
        weakness="AI 改写的弱点",
        disposition="AI 改写的性格",
        favored_skills=["图书馆使用", "聆听"],
        background="AI 背景摘要",
    )

    payload = SectionNormalizer().to_writeback(
        answers=answers,
        synthesis=synthesis,
        answer_normalizer=AnswerNormalizer(),
    )

    assert payload.key_past_event == "一次手术纠纷毁掉了他的声誉。"
    assert payload.life_goal == "赚很多钱然后隐居。"
    assert payload.weakness == "过度自信且酗酒。"
    assert payload.disposition == "嘴硬，控制欲强。"
    assert payload.favored_skills == ["医学", "急救", "心理学"]


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

    assert "一句话勾勒" in name_message.channel.messages[-1]


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

    emitted_messages: list[str] = []
    for answer in [
        "林钟轩",
        "38岁的落魄临床医生",
        "三年前的一场手术纠纷把我从医院里赶了出来。",
        "我想证明那次事故里真正犯错的人不是我。",
        "我太骄傲，也太容易在压力下酗酒。",
        "我不是在犯错，我是在救人。",
        "我的导师，他教我怎么拿起手术刀。",
        "医学,急救,心理学",
    ]:
        message = FakeMessage(channel_id="archive-1", content=answer)
        asyncio.run(commands.handle_channel_message_stream(message=message))
        emitted_messages.extend(message.channel.messages)

    profiles = repo.list_profiles("user-1")
    assert len(profiles) == 1
    assert profiles[0].name == "林钟轩"
    assert profiles[0].coc.occupation == "临床医生"
    assert "证明" in profiles[0].life_goal
    assert profiles[0].specialty
    assert "导师" in profiles[0].important_person
    assert any("人物画像" in item for item in emitted_messages)


def test_builder_generates_portrait_before_finalizing_profile() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.coc.builder import ConversationalCharacterBuilder

    repo = InvestigatorArchiveRepository()
    builder = ConversationalCharacterBuilder(
        archive_repository=repo,
        roll_provider=lambda expr: {"3d6*5": 55, "2d6+6*5": 70, "luck": 60}[expr],
        interview_planner=FakeInterviewPlanner(),
    )

    assert "让我先了解一下这位即将踏入黑暗的调查员" in builder.start(
        user_id="user-1", visibility="private"
    )
    asyncio.run(builder.answer(user_id="user-1", answer="林钟轩"))
    asyncio.run(builder.answer(user_id="user-1", answer="38岁的落魄临床医生"))
    asyncio.run(
        builder.answer(user_id="user-1", answer="一场手术事故让他被赶出了三甲医院。")
    )
    asyncio.run(
        builder.answer(user_id="user-1", answer="他想证明自己依然是最好的医生。")
    )
    asyncio.run(builder.answer(user_id="user-1", answer="过度自信，而且拒绝认错。"))
    prompt, profile = asyncio.run(
        builder.answer(user_id="user-1", answer="我不是在犯错，我是在救人。")
    )

    assert profile is None
    assert "人物画像" in prompt
    assert "定卡" in prompt
    assert repo.list_profiles("user-1") == []

    prompt, profile = asyncio.run(builder.answer(user_id="user-1", answer="按人物来"))

    assert profile is not None
    assert "建卡完成" in prompt


def test_ready_projects_selected_archive_profile_without_mutating_archive() -> None:
    from dm_bot.adventures.loader import load_adventure
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
    from dm_bot.rules.compendium import FixtureCompendium
    from dm_bot.rules.engine import RulesEngine

    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp-1", channel_id="hall-1", guild_id="guild-1", owner_id="user-1"
    )
    store.bind_archive_channel(guild_id="guild-1", channel_id="archive-1")
    gameplay = GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={})
        ),
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
            "str": 50,
            "con": 55,
            "dex": 60,
            "app": 65,
            "pow": 70,
            "siz": 50,
            "int": 75,
            "edu": 80,
            "luck": 45,
        },
    )
    store.select_archive_profile(
        channel_id="hall-1", user_id="user-1", profile_id=profile.profile_id
    )
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
    assert archive_profile.important_person == ""


def test_archive_detail_view_surfaces_richer_card_sections() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository

    repo = InvestigatorArchiveRepository()
    profile = repo.create_profile(
        user_id="user-1",
        name="林秋",
        occupation="记者",
        age=26,
        background="夜班记者",
        concept="26岁的夜班记者",
        important_person="姐姐",
        significant_location="旧报社顶楼",
        treasured_possession="录音笔",
        trait_notes="冷静、偏执、抗压",
        scars_and_injuries="左手虎口有一道旧伤",
        phobias_and_manias="面对失控现场时会过度清醒",
        disposition="冷静但固执",
        favored_skills=["图书馆使用", "聆听", "心理学"],
        generation={
            "str": 50,
            "con": 55,
            "dex": 60,
            "app": 65,
            "pow": 70,
            "siz": 50,
            "int": 75,
            "edu": 80,
            "luck": 45,
        },
    )

    detail = profile.detail_view()

    assert "以下内容属于长期档案" in detail
    assert "重要之人：姐姐" in detail
    assert "重要场所：旧报社顶楼" in detail
    assert "珍贵之物：录音笔" in detail
    assert "伤口与疤痕：左手虎口有一道旧伤" in detail


def test_select_profile_immediately_syncs_projection_panel() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
    from dm_bot.rules.compendium import FixtureCompendium
    from dm_bot.rules.engine import RulesEngine

    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp-1", channel_id="hall-1", guild_id="guild-1", owner_id="user-1"
    )
    gameplay = GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={})
        ),
    )
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
            "str": 50,
            "con": 55,
            "dex": 60,
            "app": 65,
            "pow": 70,
            "siz": 50,
            "int": 75,
            "edu": 80,
            "luck": 45,
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

    asyncio.run(commands.select_profile(interaction, profile_id=profile.profile_id))

    snapshot = gameplay.investigator_panel_snapshot("user-1")
    assert snapshot["name"] == "林秋"
    assert snapshot["occupation"] == "记者"
    assert snapshot["san"] == profile.coc.san
    assert snapshot["module_flags"]["archive_profile_id"] == profile.profile_id


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
        generation={
            "str": 50,
            "con": 55,
            "dex": 60,
            "app": 65,
            "pow": 70,
            "siz": 50,
            "int": 75,
            "edu": 80,
            "luck": 45,
        },
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
        generation={
            "str": 50,
            "con": 55,
            "dex": 60,
            "app": 65,
            "pow": 70,
            "siz": 50,
            "int": 75,
            "edu": 80,
            "luck": 45,
        },
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


def test_builder_does_not_create_second_active_profile_without_explicit_replace() -> (
    None
):
    from dm_bot.coc.archive import InvestigatorArchiveRepository
    from dm_bot.coc.builder import ConversationalCharacterBuilder

    repo = InvestigatorArchiveRepository()
    repo.create_profile(
        user_id="user-1",
        name="旧角色",
        occupation="记者",
        age=30,
        background="老档案",
        disposition="冷静",
        favored_skills=["图书馆使用"],
        generation={
            "str": 50,
            "con": 55,
            "dex": 60,
            "app": 65,
            "pow": 70,
            "siz": 50,
            "int": 75,
            "edu": 80,
            "luck": 45,
        },
    )
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

    assert "已有激活档案" in interaction.response.messages[0][0]


def test_admin_can_list_all_profiles_from_admin_channel() -> None:
    from dm_bot.coc.archive import InvestigatorArchiveRepository

    repo = InvestigatorArchiveRepository()
    repo.create_profile(
        user_id="user-1",
        name="林钟轩",
        occupation="临床医生",
        age=38,
        background="医生",
        disposition="冷静",
        favored_skills=["医学"],
        generation={
            "str": 50,
            "con": 55,
            "dex": 60,
            "app": 65,
            "pow": 70,
            "siz": 50,
            "int": 75,
            "edu": 80,
            "luck": 45,
        },
    )
    repo.create_profile(
        user_id="user-2",
        name="林秋",
        occupation="记者",
        age=26,
        background="记者",
        disposition="固执",
        favored_skills=["图书馆使用"],
        generation={
            "str": 50,
            "con": 55,
            "dex": 60,
            "app": 65,
            "pow": 70,
            "siz": 50,
            "int": 75,
            "edu": 80,
            "luck": 45,
        },
    )
    store = SessionStore()
    store.bind_trace_channel(guild_id="guild-1", channel_id="admin-1")
    commands = BotCommands(
        settings=Settings(),
        session_store=store,
        turn_coordinator=None,
        archive_repository=repo,
    )
    interaction = FakeInteraction(channel_id="admin-1", administrator=True)

    asyncio.run(commands.admin_profiles(interaction))

    content = interaction.response.messages[0][0]
    assert "user-1" in content
    assert "林秋" in content


def test_doctor_profile_finishing_recommendations_stay_within_expected_skill_family() -> (
    None
):
    from dm_bot.coc.archive import InvestigatorArchiveRepository

    repo = InvestigatorArchiveRepository()
    profile = repo.create_profile(
        user_id="user-1",
        name="林钟轩",
        occupation="临床医生",
        age=38,
        concept="38岁的落魄临床医生",
        specialty="神经外科",
        background="医生",
        disposition="冷静",
        favored_skills=["医学", "急救", "心理学"],
        generation={
            "str": 50,
            "con": 55,
            "dex": 60,
            "app": 65,
            "pow": 70,
            "siz": 50,
            "int": 75,
            "edu": 80,
            "luck": 45,
        },
    )

    assert profile.finishing.recommended_occupation_skills == [
        "医学",
        "急救",
        "科学(生物学)",
        "心理学",
    ]
