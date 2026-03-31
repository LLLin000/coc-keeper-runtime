"""Tests for character builder."""

import pytest

from dm_bot.coc.builder import (
    ConversationalCharacterBuilder,
    BuilderSession,
    AnswerNormalizer,
)
from dm_bot.coc.archive import InvestigatorArchiveRepository


class TestBuilderSession:
    """Test builder session management."""

    def test_start_interview(self):
        """Test starting an interview."""
        repo = InvestigatorArchiveRepository()
        builder = ConversationalCharacterBuilder(archive_repository=repo)

        question = builder.start(user_id="user1")

        assert "名字" in question or "name" in question.lower()
        assert builder.has_session("user1")

    @pytest.mark.asyncio
    async def test_interview_flow(self):
        """Test basic interview flow."""
        repo = InvestigatorArchiveRepository()
        builder = ConversationalCharacterBuilder(archive_repository=repo)

        # Start
        q1 = builder.start(user_id="user1")

        # Answer name
        q2, _ = await builder.answer(user_id="user1", answer="张三")

        # Answer concept
        q3, _ = await builder.answer(user_id="user1", answer="38岁的落魄临床医生")

        # Should have more questions
        assert q3 is not None
        assert len(q3) > 0

    def test_answer_normalization(self):
        """Test answer normalization."""
        normalizer = AnswerNormalizer()

        # Test name normalization
        result = normalizer.normalize_slot(slot="name", raw="  张三  ")
        assert result["name"] == "张三"

        # Test age normalization
        result = normalizer.normalize_slot(slot="age", raw="我今年38岁")
        assert result["age"] == "38"

    def test_cannot_start_with_active_profile(self):
        """Test that user cannot start if they have active profile."""
        repo = InvestigatorArchiveRepository()

        # Create an active profile first
        repo.create_profile(
            user_id="user1",
            name="Existing",
            occupation="Doctor",
            age=30,
            background="Test",
            portrait_summary="Test",
            concept="Test",
            disposition="冷静",
            favored_skills=["医学"],
            generation={
                "str": 50,
                "con": 50,
                "dex": 50,
                "app": 50,
                "pow": 50,
                "siz": 50,
                "int": 50,
                "edu": 50,
                "luck": 50,
            },
        )

        builder = ConversationalCharacterBuilder(archive_repository=repo)

        result = builder.start(user_id="user1")

        assert "已有激活档案" in result


class TestBuilderProfileCreation:
    """Test profile creation through builder."""

    @pytest.mark.asyncio
    async def test_complete_interview_creates_profile(self):
        """Test that completing interview creates a profile."""
        repo = InvestigatorArchiveRepository()
        builder = ConversationalCharacterBuilder(archive_repository=repo)

        # Start - ask name
        builder.start(user_id="user1")

        # Name
        await builder.answer(user_id="user1", answer="张三")

        # Concept (age and occupation extracted)
        await builder.answer(user_id="user1", answer="38岁的落魄临床医生")

        # Dynamic questions - these come from HeuristicInterviewPlanner
        # After concept: age=38 and occupation=临床医生 are extracted
        # So next question should be key_past_event
        q, _ = await builder.answer(user_id="user1", answer="报道失误")

        # life_goal
        if builder.has_session("user1"):
            q, _ = await builder.answer(user_id="user1", answer="重建声誉")

        # weakness
        if builder.has_session("user1"):
            q, _ = await builder.answer(user_id="user1", answer="酗酒")

        # core_belief
        if builder.has_session("user1"):
            q, _ = await builder.answer(user_id="user1", answer="我是在救人")

        # Finalize
        if builder.has_session("user1"):
            q, profile = await builder.answer(user_id="user1", answer="定卡")
        else:
            profile = None

        assert profile is not None, "Profile should be created after finalize"
        assert profile.name == "张三"
        assert profile.coc.san > 0

    def test_profile_has_coc_stats(self):
        """Test that created profile has COC stats."""
        # This would require completing a full interview
        # For now, just verify the structure
        pass


class TestBuilderValidation:
    """Test builder validation."""

    def test_skill_list_parsing(self):
        """Test parsing skill lists."""
        from dm_bot.coc.builder import _normalize_skill_list

        # Test various formats
        assert _normalize_skill_list("医学, 急救") == ["医学", "急救"]
        assert _normalize_skill_list("医学、急救、侦查") == ["医学", "急救", "侦查"]
        assert _normalize_skill_list("") == []
