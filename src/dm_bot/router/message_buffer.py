from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from dm_bot.router.intent import (
    MessageIntent,
    MessageIntentMetadata,
    should_buffer_intent,
)


@dataclass
class BufferedMessage:
    """A message waiting to be delivered after phase ends."""

    user_id: str
    content: str
    intent: MessageIntent
    metadata: MessageIntentMetadata
    received_at: datetime = field(default_factory=datetime.now)


class MessageBuffer:
    """Buffers messages during high-intensity session phases.

    Messages are buffered during phases like SCENE_ROUND_RESOLVING and COMBAT,
    then delivered when the phase transitions to a less intensive phase.
    """

    def __init__(self) -> None:
        self._buffers: dict[str, list[BufferedMessage]] = {}

    def buffer_message(
        self,
        channel_id: str,
        user_id: str,
        content: str,
        intent: MessageIntent,
        metadata: MessageIntentMetadata,
    ) -> bool:
        """Add a message to the buffer.

        Returns True if message was buffered, False otherwise.
        """
        if channel_id not in self._buffers:
            self._buffers[channel_id] = []

        buffered = BufferedMessage(
            user_id=user_id,
            content=content,
            intent=intent,
            metadata=metadata,
        )
        self._buffers[channel_id].append(buffered)
        return True

    def get_buffered_messages(self, channel_id: str) -> list[BufferedMessage]:
        """Get all buffered messages for a channel."""
        return self._buffers.get(channel_id, [])

    def has_buffered_messages(self, channel_id: str) -> bool:
        """Check if a channel has buffered messages."""
        return len(self._buffers.get(channel_id, [])) > 0

    def release_buffered_messages(
        self,
        channel_id: str,
    ) -> list[BufferedMessage]:
        """Release all buffered messages for a channel.

        Returns the buffered messages and clears the buffer.
        """
        messages = self._buffers.pop(channel_id, [])
        return messages

    def clear_buffer(self, channel_id: str) -> None:
        """Clear the buffer for a channel without returning messages."""
        self._buffers.pop(channel_id, None)

    def get_buffer_summary(self, channel_id: str) -> dict:
        """Get a summary of buffered messages for a channel."""
        messages = self._buffers.get(channel_id, [])
        by_intent: dict[str, int] = {}
        for msg in messages:
            key = msg.intent.value
            by_intent[key] = by_intent.get(key, 0) + 1

        return {
            "total": len(messages),
            "by_intent": by_intent,
            "oldest": messages[0].received_at.isoformat() if messages else None,
            "newest": messages[-1].received_at.isoformat() if messages else None,
        }

    def format_buffered_message_summary(self, channel_id: str) -> str | None:
        """Format buffered messages as a user-facing summary."""
        messages = self._buffers.get(channel_id, [])
        if not messages:
            return None

        lines = ["**Buffered Messages:**"]
        by_user: dict[str, list[str]] = {}

        for msg in messages:
            if msg.user_id not in by_user:
                by_user[msg.user_id] = []
            by_user[msg.user_id].append(msg.content[:50])

        for user_id, contents in by_user.items():
            lines.append(f"• <@{user_id}>: {'; '.join(contents[:3])}")

        return "\n".join(lines)
