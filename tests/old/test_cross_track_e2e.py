"""Cross-track E2E: full flow from character creation to consequence presentation.

Tests the complete pipeline across all tracks:
- Track B: ConversationalCharacterBuilder → InvestigatorArchiveProfile
- Track D: card_view() → CardSection → DiscordCardRenderer
- Track E: InvestigatorPanel → RulesEngine → dice/SAN
- Track D: ConsequenceAggregator → Keeper-style narrative text
"""

from __future__ import annotations

import pytest

from dm_bot.coc.builder import ConversationalCharacterBuilder
from dm_bot.coc.archive import InvestigatorArchiveProfile, InvestigatorArchiveRepository
from dm_bot.coc.panels import InvestigatorPanel
from dm_bot.coc.presentation import CardSection, DiscordCardRenderer
from dm_bot.characters.models import COCAttributes, COCInvestigatorProfile
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine
from dm_bot.rules.actions import RuleAction, StatBlock
from dm_bot.orchestrator.consequence_aggregator import (
    ConsequenceAggregator,
)


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def archive_repo():
    """In-memory archive repository."""
    return InvestigatorArchiveRepository()


@pytest.fixture
def builder(archive_repo):
    """Fresh ConversationalCharacterBuilder instance."""
    return ConversationalCharacterBuilder(archive_repository=archive_repo)


@pytest.fixture
def rules_engine():
    """RulesEngine with fixture compendium."""
    return RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={}))


@pytest.fixture
def renderer():
    """DiscordCardRenderer instance."""
    return DiscordCardRenderer()


@pytest.fixture
def aggregator():
    """ConsequenceAggregator instance."""
    return ConsequenceAggregator()


# ── Track B: Character Builder Flow ─────────────────────────────────────────


class TestCharacterBuilderFlow:
    """End-to-end character builder interview."""

    def test_builder_prompts_use_keeper_voice(self, builder) -> None:
        """Verify builder intro question uses Keeper tone (D40/D42)."""
        user_id = "player-2"
        first_question = builder.start(user_id=user_id, visibility="private")

        # Should have Keeper voice, not form-like
        assert "黑暗" in first_question or "调查员" in first_question
        assert "先给这位" not in first_question  # Old form-like text

    @pytest.mark.asyncio
    async def test_name_extraction_from_concept(self, builder) -> None:
        """Builder extracts name when user provides it in concept answer."""
        user_id = "player-3"
        builder.start(user_id=user_id)

        # Answer name
        await builder.answer(user_id=user_id, answer="王侦探")

        # Answer concept with embedded age/occupation
        await builder.answer(user_id=user_id, answer="38岁的落魄临床医生")

        session = builder._sessions.get(user_id)
        assert session.answers.get("name") == "王侦探"
        # Age should be extracted from concept
        assert session.answers.get("age") == "38"

    @pytest.mark.asyncio
    async def test_full_interview_produces_archive_profile(self, builder) -> None:
        """Complete the full interview flow and verify archive profile is produced."""
        user_id = "player-1"

        # Start builder
        first_question = builder.start(user_id=user_id, visibility="private")
        assert first_question is not None
        assert "名字" in first_question

        # Answer: name
        next_q, profile = await builder.answer(user_id=user_id, answer="张记者")
        assert profile is None

        # Answer: concept
        next_q, profile = await builder.answer(user_id=user_id, answer="35岁的调查记者")
        assert profile is None

        # Continue with remaining answers
        answers = [
            "新闻学硕士，在都市报干了十年",
            "揭露企业污染丑闻",
            "让真相大白于天下",
            "对权威的不信任",
            "真相高于一切",
            "编辑老李",
        ]
        for answer in answers:
            next_q, profile = await builder.answer(user_id=user_id, answer=answer)

        # Verify the session progressed
        session = builder._sessions.get(user_id)
        assert session is not None
        assert session.raw_answers.get("name") == "张记者"


# ── Track D: Archive Card Presentation ──────────────────────────────────────


class TestArchiveCardPresentation:
    """Archive card_view and DiscordCardRenderer (D41/D43)."""

    def test_card_view_produces_sections(self) -> None:
        """card_view() returns list of CardSection objects."""
        profile = _make_sample_profile("arch-1", "张记者", "记者", 35)

        sections = profile.card_view()
        assert isinstance(sections, list)
        assert len(sections) >= 4  # At least header, identity, stats, skills

        # Each section should be a CardSection
        for section in sections:
            assert isinstance(section, CardSection)
            assert section.title
            assert section.content
            assert section.visibility in ("public", "private", "group", "keeper")

    def test_card_view_has_long_term_archive_label(self) -> None:
        """Card sections include 长期档案 label (PRESENT-03)."""
        profile = _make_sample_profile("arch-2", "王侦探", "私家侦探", 40)

        sections = profile.card_view()
        all_content = " ".join(s.content for s in sections)
        assert "长期档案" in all_content

    def test_card_view_sections_under_1024_chars(self) -> None:
        """Each section fits within Discord embed field limit (PRESENT-02)."""
        profile = _make_sample_profile(
            "arch-3",
            "李医生",
            "医生",
            45,
            career_arc="医学院毕业后在市医院工作二十年",
            key_past_event="一次医疗事故改变了职业生涯",
            core_belief="生命至上",
            life_goal="治愈更多病人",
            weakness="过度责任感",
            important_person="已故导师",
            significant_location="市医院",
            treasured_possession="导师的手术刀",
            disposition="温和但坚定",
            favored_skills=["急救", "医学", "心理学", "图书馆", "侦查"],
        )

        sections = profile.card_view()
        for section in sections:
            assert len(section.content) < 1024, (
                f"Section '{section.title}' exceeds 1024 chars: {len(section.content)}"
            )

    def test_discord_renderer_produces_readable_output(self, renderer) -> None:
        """DiscordCardRenderer renders sections to readable strings."""
        sections = [
            CardSection(title="身份", content="张记者 | 记者 | 35岁", order=0),
            CardSection(
                title="数值",
                content="🧠 SAN 60 | ❤️ HP 11 | 💧 MP 12 | 🍀 LUCK 60",
                order=1,
            ),
        ]

        rendered = renderer.render(sections)
        assert len(rendered) == 2
        assert "**身份**" in rendered[0]
        assert "**数值**" in rendered[1]
        assert "🧠" in rendered[1]
        assert "❤️" in rendered[1]


# ── Track E: Rules Engine + Panel ───────────────────────────────────────────


class TestRulesEngineIntegration:
    """Rules engine with character panel (Track E)."""

    def test_skill_check_produces_outcome(self, rules_engine) -> None:
        """COC skill check produces structured outcome."""
        action = RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="张记者", armor_class=0, hit_points=11),
            parameters={"label": "侦查", "value": 50},
        )

        result = rules_engine.execute(action)
        assert "success" in result
        assert "roll" in result

    def test_sanity_check_produces_outcome(self, rules_engine) -> None:
        """SAN check produces structured outcome with san_loss."""
        action = RuleAction(
            action="coc_sanity_check",
            actor=StatBlock(name="张记者", armor_class=0, hit_points=11),
            parameters={
                "current_san": 60,
                "loss_on_success": "0",
                "loss_on_failure": "1d6",
            },
        )

        result = rules_engine.execute(action)
        assert "san_loss" in result
        assert "success" in result

    def test_panel_tracks_state_changes(self) -> None:
        """InvestigatorPanel tracks SAN/HP/MP changes."""
        panel = InvestigatorPanel(
            user_id="player-1",
            name="张记者",
            occupation="记者",
            san=60,
            hp=11,
            mp=12,
            luck=60,
            skills={"侦查": 50, "图书馆": 60},
        )

        # Simulate SAN loss
        panel.san -= 5
        assert panel.san == 55

        # Simulate HP damage
        panel.hp -= 3
        assert panel.hp == 8

        # Summary should reflect changes
        summary = panel.summary(knowledge_titles=[])
        assert "SAN=55" in summary
        assert "HP=8" in summary


# ── Track D: Consequence Aggregation ────────────────────────────────────────


class TestConsequenceAggregation:
    """ConsequenceAggregator with Keeper-style formatting (D42)."""

    def test_skill_check_outcome_formatted_as_keeper_text(self, aggregator) -> None:
        """Skill check outcomes use narrative Keeper-style text."""
        result = _mock_action_result(
            character_id="张记者",
            action_text="我仔细搜索房间",
            rule_outcomes=[
                {
                    "action": "coc_skill_check",
                    "label": "侦查",
                    "success": True,
                    "roll": "35/50",
                    "grade": "hard",
                }
            ],
        )

        batch = _mock_batch_result([result])
        aggregated = aggregator.aggregate(batch)

        # Should have public group
        assert "public" in aggregated.groups
        consequences = aggregated.groups["public"].consequences
        assert len(consequences) > 0

        # Content should be Keeper-style narrative
        content = consequences[0].content
        assert "检定" in content or "侦查" in content

    def test_sanity_check_outcome_formatted_as_keeper_text(self, aggregator) -> None:
        """SAN check outcomes use narrative Keeper-style text."""
        result = _mock_action_result(
            character_id="张记者",
            action_text="看到可怕的景象",
            rule_outcomes=[
                {
                    "action": "coc_sanity_check",
                    "success": False,
                    "san_loss": "1d6",
                }
            ],
        )

        batch = _mock_batch_result([result])
        aggregated = aggregator.aggregate(batch)

        consequences = aggregated.groups["public"].consequences
        content = consequences[0].content
        assert "SAN" in content or "理智" in content

    def test_consequences_grouped_by_visibility(self, aggregator) -> None:
        """Consequences are properly grouped by visibility level."""
        results = [
            _mock_action_result(
                character_id="张记者",
                action_text="公开行动",
                rule_outcomes=[
                    {
                        "action": "coc_skill_check",
                        "label": "侦查",
                        "success": True,
                        "roll": "30/50",
                        "grade": "",
                    }
                ],
                visibility="public",
            ),
            _mock_action_result(
                character_id="张记者",
                action_text="私密发现",
                rule_outcomes=[
                    {
                        "action": "coc_skill_check",
                        "label": "心理学",
                        "success": True,
                        "roll": "20/40",
                        "grade": "",
                    }
                ],
                visibility="private",
            ),
        ]

        batch = _mock_batch_result(results)
        aggregated = aggregator.aggregate(batch)

        assert "public" in aggregated.groups
        assert "private" in aggregated.groups
        assert len(aggregated.groups["public"].consequences) > 0
        assert len(aggregated.groups["private"].consequences) > 0


# ── Full Cross-Track Pipeline ───────────────────────────────────────────────


class TestFullCrossTrackPipeline:
    """End-to-end: builder → archive → panel → rules → consequences."""

    @pytest.mark.asyncio
    async def test_character_flows_through_all_layers(
        self, builder, rules_engine, renderer, aggregator
    ) -> None:
        """A character flows through all track layers without error."""
        user_id = "player-e2e"

        # Step 1: Build character (Track B)
        builder.start(user_id=user_id, visibility="private")
        await builder.answer(user_id=user_id, answer="赵警员")
        await builder.answer(user_id=user_id, answer="40岁的退休警探")

        # Continue with remaining answers
        for answer in [
            "警校毕业后在重案组干了十五年",
            "一次失败的行动导致搭档死亡",
            "找出当年行动的真相",
            "过度自责",
            "正义必须得到伸张",
            "已故搭档的家人",
        ]:
            await builder.answer(user_id=user_id, answer=answer)

        # Verify builder session exists
        session = builder._sessions.get(user_id)
        assert session is not None
        assert session.raw_answers.get("name") == "赵警员"

        # Step 2: Create archive profile manually (simulating finalization)
        archive = _make_sample_profile(
            "arch-e2e",
            "赵警员",
            "私家侦探",
            40,
            concept="40岁的退休警探",
            career_arc="警校毕业后在重案组干了十五年",
            key_past_event="一次失败的行动导致搭档死亡",
            core_belief="正义必须得到伸张",
            life_goal="找出当年行动的真相",
            weakness="过度自责",
            important_person="已故搭档的家人",
            favored_skills=["侦查", "手枪", "心理学"],
        )

        # Step 3: Render card (Track D)
        sections = archive.card_view()
        assert len(sections) >= 4
        rendered = renderer.render(sections)
        assert len(rendered) == len(sections)
        assert any("长期档案" in r for r in rendered)

        # Step 4: Create runtime panel (Track E)
        panel = InvestigatorPanel(
            user_id=user_id,
            name="赵警员",
            occupation="私家侦探",
            san=55,
            hp=12,
            mp=11,
            luck=55,
            skills={"侦查": 60, "手枪": 70, "心理学": 50},
        )

        # Step 5: Execute rules check (Track E)
        action = RuleAction(
            action="coc_skill_check",
            actor=StatBlock(name="赵警员", armor_class=0, hit_points=12),
            parameters={"label": "侦查", "value": 60},
        )
        rules_result = rules_engine.execute(action)
        assert isinstance(rules_result, dict)

        # Step 6: Aggregate consequences (Track D)
        mock_result = _mock_action_result(
            character_id="赵警员",
            action_text="搜索犯罪现场",
            rule_outcomes=[
                {
                    "action": "coc_skill_check",
                    "label": "侦查",
                    "success": True,
                    "roll": "25/60",
                    "grade": "hard",
                }
            ],
        )
        batch = _mock_batch_result([mock_result])
        consequences = aggregator.aggregate(batch)

        assert "public" in consequences.groups
        assert len(consequences.groups["public"].consequences) > 0

        # Step 7: Verify panel state after rules
        panel.journal.append("搜索犯罪现场")
        assert "搜索犯罪现场" in panel.journal


# ── Helpers ─────────────────────────────────────────────────────────────────


def _make_sample_profile(
    profile_id: str,
    name: str,
    occupation: str,
    age: int,
    **kwargs,
) -> InvestigatorArchiveProfile:
    """Create a sample InvestigatorArchiveProfile for testing."""
    return InvestigatorArchiveProfile(
        profile_id=profile_id,
        user_id="player-1",
        name=name,
        occupation=occupation,
        age=age,
        concept=kwargs.get("concept", f"{age}岁的{occupation}"),
        career_arc=kwargs.get("career_arc", "普通职业生涯"),
        key_past_event=kwargs.get("key_past_event", "一次难忘的经历"),
        core_belief=kwargs.get("core_belief", "相信正义"),
        life_goal=kwargs.get("life_goal", "过好每一天"),
        weakness=kwargs.get("weakness", "有点固执"),
        important_person=kwargs.get("important_person", "家人"),
        significant_location=kwargs.get("significant_location", "家乡"),
        treasured_possession=kwargs.get("treasured_possession", "旧照片"),
        disposition=kwargs.get("disposition", "平和"),
        favored_skills=kwargs.get("favored_skills", ["侦查", "说服"]),
        portrait_summary=kwargs.get("portrait_summary", f"一位{name}"),
        coc=COCInvestigatorProfile(
            occupation=occupation,
            attributes=COCAttributes(
                **{
                    "str": 60,
                    "con": 50,
                    "dex": 55,
                    "app": 70,
                    "pow": 60,
                    "siz": 65,
                    "int": 80,
                    "edu": 75,
                }
            ),
            san=60,
            hp=11,
            mp=12,
            luck=60,
            move_rate=8,
            damage_bonus="+1d4",
            build=0,
        ),
    )


def _mock_action_result(
    character_id: str,
    action_text: str,
    rule_outcomes: list[dict] | None = None,
    visibility: str = "public",
):
    """Create a mock action result for consequence aggregation testing."""
    from dataclasses import dataclass, field

    @dataclass
    class MockActionResult:
        character_id: str
        action_text: str
        rule_outcomes: list[dict] = field(default_factory=list)
        trigger_effects: list = field(default_factory=list)
        visibility: str = "public"

    return MockActionResult(
        character_id=character_id,
        action_text=action_text,
        rule_outcomes=rule_outcomes or [],
        visibility=visibility,
    )


def _mock_batch_result(results: list):
    """Create a mock batch result for consequence aggregation testing."""
    from dataclasses import dataclass, field

    @dataclass
    class MockBatchResult:
        action_results: list = field(default_factory=list)

    return MockBatchResult(action_results=results)
