import pytest

from dm_bot.router.intent import MessageIntent, IntentClassificationResult
from dm_bot.router.message_buffer import MessageBuffer
from dm_bot.router.intent_handler import IntentHandlerRegistry


class TestFeedbackDelivery:
    """Tests for feedback message delivery in intent handling."""

    @pytest.fixture
    def message_buffer(self):
        return MessageBuffer()

    @pytest.fixture
    def intent_handler(self, message_buffer):
        return IntentHandlerRegistry(message_buffer=message_buffer)

    @pytest.mark.asyncio
    async def test_buffered_message_feedback(self, intent_handler):
        result = await intent_handler.handle_message(
            user_id="user1",
            content="我攻击史莱姆",
            classification=IntentClassificationResult(
                intent=MessageIntent.PLAYER_ACTION,
                confidence=0.9,
                reasoning="Player action during resolving phase",
            ),
            session_phase="scene_round_resolving",
        )
        assert result.should_buffer is True
        assert result.feedback_message is not None
        assert len(result.feedback_message) <= 50

    @pytest.mark.asyncio
    async def test_ignored_message_feedback(self, intent_handler):
        result = await intent_handler.handle_message(
            user_id="user1",
            content="random gibberish",
            classification=IntentClassificationResult(
                intent=MessageIntent.UNKNOWN,
                confidence=0.5,
                reasoning="Unable to determine intent",
            ),
            session_phase="scene_round_open",
        )
        assert result.feedback_message is not None
        assert "⏸️" in result.feedback_message

    @pytest.mark.asyncio
    async def test_ignored_message_feedback_combat(self, intent_handler):
        result = await intent_handler.handle_message(
            user_id="user1",
            content="hello world",
            classification=IntentClassificationResult(
                intent=MessageIntent.UNKNOWN,
                confidence=0.3,
                reasoning="Unknown message",
            ),
            session_phase="combat",
        )
        assert result.feedback_message is not None
        assert "⏸️" in result.feedback_message
        assert len(result.feedback_message) <= 50

    @pytest.mark.asyncio
    async def test_deferred_rules_query_feedback(self, intent_handler):
        result = await intent_handler.handle_message(
            user_id="user1",
            content="力量检定怎么算？",
            classification=IntentClassificationResult(
                intent=MessageIntent.RULES_QUERY,
                confidence=0.95,
                reasoning="Player is asking about rules",
            ),
            session_phase="combat",
        )
        assert result.feedback_message is not None
        assert "📋" in result.feedback_message
        assert len(result.feedback_message) <= 50

    @pytest.mark.asyncio
    async def test_deferred_rules_query_feedback_resolving(self, intent_handler):
        result = await intent_handler.handle_message(
            user_id="user1",
            content="什么是敏捷检定？",
            classification=IntentClassificationResult(
                intent=MessageIntent.RULES_QUERY,
                confidence=0.95,
                reasoning="Rules question",
            ),
            session_phase="scene_round_resolving",
        )
        assert result.feedback_message is not None
        assert "📋" in result.feedback_message

    @pytest.mark.asyncio
    async def test_no_feedback_for_processed(self, intent_handler):
        result = await intent_handler.handle_message(
            user_id="user1",
            content="我调查尸体",
            classification=IntentClassificationResult(
                intent=MessageIntent.PLAYER_ACTION,
                confidence=0.9,
                reasoning="Player action during open phase",
            ),
            session_phase="scene_round_open",
        )
        assert result.should_process is True
        assert result.should_buffer is False

    @pytest.mark.asyncio
    async def test_feedback_character_limit(self, intent_handler):
        phases_to_test = [
            "scene_round_open",
            "scene_round_resolving",
            "combat",
            "awaiting_ready",
        ]
        for phase in phases_to_test:
            result = await intent_handler.handle_message(
                user_id="user1",
                content="test",
                classification=IntentClassificationResult(
                    intent=MessageIntent.UNKNOWN,
                    confidence=0.5,
                    reasoning="test",
                ),
                session_phase=phase,
            )
            if result.feedback_message:
                assert len(result.feedback_message) <= 50, (
                    f"Feedback for phase {phase} exceeds 50 chars: {result.feedback_message}"
                )
