import pytest
from datetime import datetime

from dm_bot.router.intent import (
    MessageIntent,
    IntentClassificationRequest,
    IntentClassificationResult,
    MessageIntentMetadata,
    get_intent_priority,
    should_buffer_intent,
    get_handling_decision,
    INTENT_PRIORITY_BY_PHASE,
)
from dm_bot.router.message_buffer import MessageBuffer, BufferedMessage
from dm_bot.router.intent_handler import IntentHandlerRegistry


class TestMessageIntent:
    """Tests for MessageIntent enum."""

    def test_intent_values(self):
        assert MessageIntent.OOC.value == "ooc"
        assert MessageIntent.SOCIAL_IC.value == "social_ic"
        assert MessageIntent.PLAYER_ACTION.value == "player_action"
        assert MessageIntent.RULES_QUERY.value == "rules_query"
        assert MessageIntent.ADMIN_ACTION.value == "admin_action"
        assert MessageIntent.UNKNOWN.value == "unknown"

    def test_intent_priority_by_phase(self):
        assert "onboarding" in INTENT_PRIORITY_BY_PHASE
        assert "scene_round_open" in INTENT_PRIORITY_BY_PHASE
        assert "scene_round_resolving" in INTENT_PRIORITY_BY_PHASE
        assert "combat" in INTENT_PRIORITY_BY_PHASE


class TestIntentPriority:
    """Tests for get_intent_priority function."""

    def test_player_action_high_priority_in_scene_round_open(self):
        priority = get_intent_priority(MessageIntent.PLAYER_ACTION, "scene_round_open")
        assert priority == 10

    def test_admin_action_high_priority_in_all_phases(self):
        assert get_intent_priority(MessageIntent.ADMIN_ACTION, "combat") >= 9
        assert (
            get_intent_priority(MessageIntent.ADMIN_ACTION, "scene_round_resolving")
            >= 9
        )

    def test_ooc_deferred_in_scene_round_open(self):
        priority = get_intent_priority(MessageIntent.OOC, "scene_round_open")
        assert priority < get_intent_priority(
            MessageIntent.PLAYER_ACTION, "scene_round_open"
        )

    def test_default_priority_for_unknown_phase(self):
        priority = get_intent_priority(MessageIntent.OOC, "unknown_phase")
        assert priority >= 1


class TestShouldBufferIntent:
    """Tests for should_buffer_intent function."""

    def test_no_buffering_in_lobby(self):
        assert not should_buffer_intent(MessageIntent.OOC, "lobby")
        assert not should_buffer_intent(MessageIntent.PLAYER_ACTION, "lobby")

    def test_buffering_in_scene_round_resolving(self):
        assert should_buffer_intent(MessageIntent.OOC, "scene_round_resolving")
        assert should_buffer_intent(MessageIntent.SOCIAL_IC, "scene_round_resolving")

    def test_admin_action_never_buffered(self):
        assert not should_buffer_intent(
            MessageIntent.ADMIN_ACTION, "scene_round_resolving"
        )
        assert not should_buffer_intent(MessageIntent.ADMIN_ACTION, "combat")

    def test_player_action_not_buffered_in_combat(self):
        assert not should_buffer_intent(MessageIntent.PLAYER_ACTION, "combat")

    def test_ooc_buffered_in_combat(self):
        assert should_buffer_intent(MessageIntent.OOC, "combat")


class TestGetHandlingDecision:
    """Tests for get_handling_decision function."""

    def test_buffered_decision(self):
        decision = get_handling_decision(MessageIntent.OOC, "scene_round_resolving")
        assert "buffered" in decision.lower()

    def test_immediate_processing_for_admin(self):
        decision = get_handling_decision(MessageIntent.ADMIN_ACTION, "combat")
        assert "immediately" in decision.lower()


class TestIntentClassificationModels:
    """Tests for Pydantic models."""

    def test_intent_classification_request(self):
        req = IntentClassificationRequest(
            trace_id="test-123",
            campaign_id="camp-456",
            channel_id="ch-789",
            user_id="user-001",
            content="Hello everyone!",
            session_phase="lobby",
            is_admin=False,
        )
        assert req.trace_id == "test-123"
        assert req.session_phase == "lobby"
        assert req.is_admin is False

    def test_intent_classification_result(self):
        result = IntentClassificationResult(
            intent=MessageIntent.OOC,
            confidence=0.9,
            reasoning="Player said 'hello everyone' which is meta discussion",
        )
        assert result.intent == MessageIntent.OOC
        assert result.confidence == 0.9

    def test_message_intent_metadata(self):
        metadata = MessageIntentMetadata(
            intent=MessageIntent.PLAYER_ACTION,
            classification_reasoning="Player describes character action",
            handling_decision="Will be processed immediately",
            phase_at_classification="scene_round_open",
        )
        assert metadata.intent == MessageIntent.PLAYER_ACTION
        assert not metadata.was_buffered


class TestMessageBuffer:
    """Tests for MessageBuffer."""

    def test_buffer_message(self):
        buffer = MessageBuffer()
        metadata = MessageIntentMetadata(
            intent=MessageIntent.OOC,
            classification_reasoning="test",
            handling_decision="test",
            phase_at_classification="scene_round_resolving",
        )

        result = buffer.buffer_message(
            channel_id="ch-123",
            user_id="user-001",
            content="Hello!",
            intent=MessageIntent.OOC,
            metadata=metadata,
        )
        assert result is True

    def test_get_buffered_messages(self):
        buffer = MessageBuffer()
        metadata = MessageIntentMetadata(
            intent=MessageIntent.OOC,
            classification_reasoning="test",
            handling_decision="test",
            phase_at_classification="scene_round_resolving",
        )

        buffer.buffer_message(
            "ch-123", "user-001", "Hello!", MessageIntent.OOC, metadata
        )
        messages = buffer.get_buffered_messages("ch-123")
        assert len(messages) == 1

    def test_release_buffered_messages(self):
        buffer = MessageBuffer()
        metadata = MessageIntentMetadata(
            intent=MessageIntent.OOC,
            classification_reasoning="test",
            handling_decision="test",
            phase_at_classification="scene_round_resolving",
        )

        buffer.buffer_message(
            "ch-123", "user-001", "Hello!", MessageIntent.OOC, metadata
        )
        messages = buffer.release_buffered_messages("ch-123")
        assert len(messages) == 1
        assert buffer.get_buffered_messages("ch-123") == []

    def test_clear_buffer(self):
        buffer = MessageBuffer()
        metadata = MessageIntentMetadata(
            intent=MessageIntent.OOC,
            classification_reasoning="test",
            handling_decision="test",
            phase_at_classification="scene_round_resolving",
        )

        buffer.buffer_message(
            "ch-123", "user-001", "Hello!", MessageIntent.OOC, metadata
        )
        buffer.clear_buffer("ch-123")
        assert not buffer.has_buffered_messages("ch-123")

    def test_buffer_summary(self):
        buffer = MessageBuffer()
        metadata = MessageIntentMetadata(
            intent=MessageIntent.OOC,
            classification_reasoning="test",
            handling_decision="test",
            phase_at_classification="scene_round_resolving",
        )

        buffer.buffer_message(
            "ch-123", "user-001", "Hello!", MessageIntent.OOC, metadata
        )
        buffer.buffer_message("ch-123", "user-002", "Hi!", MessageIntent.OOC, metadata)

        summary = buffer.get_buffer_summary("ch-123")
        assert summary["total"] == 2
        assert summary["by_intent"]["ooc"] == 2


class TestIntentHandlerRegistry:
    """Tests for IntentHandlerRegistry."""

    @pytest.fixture
    def buffer(self):
        return MessageBuffer()

    @pytest.fixture
    def registry(self, buffer):
        return IntentHandlerRegistry(buffer)

    @pytest.mark.asyncio
    async def test_handle_player_action_in_scene_round_open(self, registry):
        classification = IntentClassificationResult(
            intent=MessageIntent.PLAYER_ACTION,
            confidence=0.9,
            reasoning="Player describes action",
        )

        result = await registry.handle_message(
            user_id="user-001",
            content="I try to open the door",
            classification=classification,
            session_phase="scene_round_open",
        )

        assert result.should_process is True
        assert result.should_buffer is False

    @pytest.mark.asyncio
    async def test_buffer_ooc_in_combat(self, registry):
        classification = IntentClassificationResult(
            intent=MessageIntent.OOC,
            confidence=0.9,
            reasoning="Meta discussion",
        )

        result = await registry.handle_message(
            user_id="user-001",
            content="Hey guys, what's happening?",
            classification=classification,
            session_phase="combat",
        )

        assert result.should_process is False
        assert result.should_buffer is True

    @pytest.mark.asyncio
    async def test_admin_action_always_processed(self, registry):
        classification = IntentClassificationResult(
            intent=MessageIntent.ADMIN_ACTION,
            confidence=0.95,
            reasoning="Admin command",
        )

        result = await registry.handle_message(
            user_id="admin-001",
            content="/pause",
            classification=classification,
            session_phase="combat",
            is_admin=True,
        )

        assert result.should_process is True
        assert result.should_buffer is False


class TestPhaseDependentHandling:
    def test_rules_query_deferred_in_combat(self):
        assert should_buffer_intent(MessageIntent.RULES_QUERY, "combat")

    def test_social_ic_buffered_in_combat(self):
        assert should_buffer_intent(MessageIntent.SOCIAL_IC, "combat")

    def test_social_ic_not_buffered_in_lobby(self):
        assert not should_buffer_intent(MessageIntent.SOCIAL_IC, "lobby")

    def test_ooc_not_buffered_in_scene_round_open(self):
        assert not should_buffer_intent(MessageIntent.OOC, "scene_round_open")

    def test_ooc_buffered_in_scene_round_resolving(self):
        assert should_buffer_intent(MessageIntent.OOC, "scene_round_resolving")

    def test_player_action_buffered_in_scene_round_resolving(self):
        assert should_buffer_intent(
            MessageIntent.PLAYER_ACTION, "scene_round_resolving"
        )

    def test_all_intents_buffered_in_resolving_except_admin(self):
        for intent in MessageIntent:
            if intent == MessageIntent.ADMIN_ACTION:
                assert not should_buffer_intent(intent, "scene_round_resolving")
            else:
                assert should_buffer_intent(intent, "scene_round_resolving")


class TestSceneRoundIntegration:
    @pytest.fixture
    def buffer(self):
        return MessageBuffer()

    @pytest.fixture
    def registry(self, buffer):
        return IntentHandlerRegistry(buffer)

    @pytest.mark.asyncio
    async def test_ooc_during_open_deferred_not_buffered(self, registry):
        classification = IntentClassificationResult(
            intent=MessageIntent.OOC,
            confidence=0.85,
            reasoning="Meta discussion about scheduling",
        )

        result = await registry.handle_message(
            user_id="user-001",
            content="Hey, when are we playing next week?",
            classification=classification,
            session_phase="scene_round_open",
        )

        assert result.should_process is True
        assert result.should_buffer is False

    @pytest.mark.asyncio
    async def test_player_action_during_open_prioritized(self, registry):
        classification = IntentClassificationResult(
            intent=MessageIntent.PLAYER_ACTION,
            confidence=0.95,
            reasoning="Player describes character action",
        )

        result = await registry.handle_message(
            user_id="user-001",
            content="I search the room for clues",
            classification=classification,
            session_phase="scene_round_open",
        )

        assert result.should_process is True
        assert result.should_buffer is False

    @pytest.mark.asyncio
    async def test_all_messages_buffered_during_resolving(self, registry):
        for intent in [
            MessageIntent.OOC,
            MessageIntent.SOCIAL_IC,
            MessageIntent.PLAYER_ACTION,
            MessageIntent.RULES_QUERY,
        ]:
            classification = IntentClassificationResult(
                intent=intent,
                confidence=0.9,
                reasoning="test",
            )

            result = await registry.handle_message(
                user_id="user-001",
                content="test message",
                classification=classification,
                session_phase="scene_round_resolving",
            )

            assert result.should_buffer is True, (
                f"{intent.value} should buffer during resolving"
            )
            assert result.should_process is False


class TestMessageBufferDelivery:
    def test_buffer_and_release(self):
        buffer = MessageBuffer()
        metadata = MessageIntentMetadata(
            intent=MessageIntent.OOC,
            classification_reasoning="test",
            handling_decision="buffered",
            phase_at_classification="scene_round_resolving",
        )

        buffer.buffer_message("ch-1", "user-1", "Hello!", MessageIntent.OOC, metadata)
        buffer.buffer_message(
            "ch-1", "user-2", "Hi there!", MessageIntent.SOCIAL_IC, metadata
        )

        assert buffer.has_buffered_messages("ch-1")

        messages = buffer.release_buffered_messages("ch-1")
        assert len(messages) == 2
        assert not buffer.has_buffered_messages("ch-1")

    def test_buffer_summary_by_intent(self):
        buffer = MessageBuffer()
        ooc_meta = MessageIntentMetadata(
            intent=MessageIntent.OOC,
            classification_reasoning="test",
            handling_decision="buffered",
            phase_at_classification="scene_round_resolving",
        )
        action_meta = MessageIntentMetadata(
            intent=MessageIntent.PLAYER_ACTION,
            classification_reasoning="test",
            handling_decision="buffered",
            phase_at_classification="scene_round_resolving",
        )

        buffer.buffer_message("ch-1", "u1", "hey", MessageIntent.OOC, ooc_meta)
        buffer.buffer_message(
            "ch-1", "u2", "action", MessageIntent.PLAYER_ACTION, action_meta
        )
        buffer.buffer_message("ch-1", "u3", "hi", MessageIntent.OOC, ooc_meta)

        summary = buffer.get_buffer_summary("ch-1")
        assert summary["total"] == 3
        assert summary["by_intent"]["ooc"] == 2
        assert summary["by_intent"]["player_action"] == 1

    def test_formatted_summary(self):
        buffer = MessageBuffer()
        metadata = MessageIntentMetadata(
            intent=MessageIntent.OOC,
            classification_reasoning="test",
            handling_decision="buffered",
            phase_at_classification="scene_round_resolving",
        )
        buffer.buffer_message(
            "ch-1", "12345", "Hello world", MessageIntent.OOC, metadata
        )

        formatted = buffer.format_buffered_message_summary("ch-1")
        assert formatted is not None
        assert "Buffered Messages" in formatted
        assert "12345" in formatted
