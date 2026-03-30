from dataclasses import dataclass
from typing import Protocol, Callable

from dm_bot.router.intent import (
    MessageIntent,
    IntentClassificationResult,
    MessageIntentMetadata,
    get_handling_decision,
    should_buffer_intent,
    get_intent_priority,
)
from dm_bot.router.message_buffer import MessageBuffer, BufferedMessage


class IntentHandler(Protocol):
    """Protocol for intent handlers."""

    async def handle(
        self,
        user_id: str,
        content: str,
        classification: IntentClassificationResult,
        metadata: MessageIntentMetadata,
    ) -> "IntentHandlingResult":
        """Handle a message with the given intent."""
        ...


@dataclass
class IntentHandlingResult:
    """Result of intent handling."""

    should_process: bool
    should_buffer: bool
    feedback_message: str | None
    deferred_content: str | None = None


class IntentHandlerRegistry:
    """Registry for handling different message intents based on session phase.

    This implements the phase-dependent intent handling rules:
    - OOC: Always responded, may buffer in high-intensity phases
    - Social IC: Normal in exploration, brief in combat
    - Player action: Primary focus during SCENE_ROUND_OPEN, COMBAT
    - Rules query: Respond when asked, may defer in combat
    - Admin action: Always processed
    """

    def __init__(self, message_buffer: MessageBuffer) -> None:
        self._buffer = message_buffer
        self._handlers: dict[MessageIntent, Callable] = {}

    async def handle_message(
        self,
        user_id: str,
        content: str,
        classification: IntentClassificationResult,
        session_phase: str,
        is_admin: bool = False,
    ) -> IntentHandlingResult:
        """Main entry point for handling a message with classified intent.

        Args:
            user_id: The user who sent the message
            content: The message content
            classification: The intent classification result
            session_phase: The current session phase
            is_admin: Whether the user has admin role

        Returns:
            IntentHandlingResult with processing decision
        """
        metadata = MessageIntentMetadata(
            intent=classification.intent,
            classification_reasoning=classification.reasoning,
            handling_decision="",
            phase_at_classification=session_phase,
        )

        handling_decision = get_handling_decision(classification.intent, session_phase)
        metadata.handling_decision = handling_decision

        buffered = should_buffer_intent(classification.intent, session_phase)

        if buffered:
            metadata.was_buffered = True
            self._buffer.buffer_message(
                channel_id="",  # Will be set by caller
                user_id=user_id,
                content=content,
                intent=classification.intent,
                metadata=metadata,
            )
            return IntentHandlingResult(
                should_process=False,
                should_buffer=True,
                feedback_message=self._get_feedback(
                    classification.intent, session_phase
                ),
            )

        priority = get_intent_priority(classification.intent, session_phase)

        return IntentHandlingResult(
            should_process=True,
            should_buffer=False,
            feedback_message=self._get_feedback(classification.intent, session_phase),
        )

    def _get_feedback(self, intent: MessageIntent, session_phase: str) -> str | None:
        """Get user feedback message explaining handling decision."""
        feedback_map = {
            MessageIntent.OOC: {
                "scene_round_open": "Your OOC message has been noted. During action collection, please focus on game actions.",
                "scene_round_resolving": "Your OOC message has been buffered and will appear after scene resolution.",
                "combat": "OOC messages are not appropriate during combat. Your message has been buffered.",
            },
            MessageIntent.SOCIAL_IC: {
                "scene_round_resolving": "Social messages are buffered during scene resolution.",
                "combat": "Social IC is limited during combat. Your message has been buffered.",
            },
            MessageIntent.PLAYER_ACTION: {
                "scene_round_resolving": "Your action has been noted and will be resolved.",
            },
            MessageIntent.RULES_QUERY: {
                "scene_round_resolving": "📋 Rules questions deferred until scene resolves.",
                "combat": "📋 Rules deferred until combat ends.",
            },
            MessageIntent.UNKNOWN: {
                "scene_round_open": "⏸️ 消息在当前阶段不适用",
                "scene_round_resolving": "⏸️ 行动已结束，请等待下一轮",
                "combat": "⏸️ 战斗中无法使用此指令",
                "awaiting_ready": "⏸️ 请先完成就位",
            },
        }

        return feedback_map.get(intent, {}).get(session_phase)

    async def release_buffered_messages(
        self,
        channel_id: str,
        process_callback: Callable[[BufferedMessage], bool],
    ) -> dict:
        """Release and process buffered messages for a channel.

        Args:
            channel_id: The channel to release messages for
            process_callback: Function to call for each buffered message

        Returns:
            Summary of processed messages
        """
        messages = self._buffer.release_buffered_messages(channel_id)
        processed = 0
        failed = 0

        for msg in messages:
            try:
                if await process_callback(msg):
                    processed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1

        return {
            "released": len(messages),
            "processed": processed,
            "failed": failed,
        }

    def get_buffer_status(self, channel_id: str) -> dict | None:
        """Get buffer status for a channel."""
        if not self._buffer.has_buffered_messages(channel_id):
            return None
        return self._buffer.get_buffer_summary(channel_id)
