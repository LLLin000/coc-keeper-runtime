from typing import Protocol
import logging

log = logging.getLogger(__name__)


class FeedbackSender(Protocol):
    async def send_feedback(
        self,
        channel_id: str,
        user_id: str,
        message: str,
    ) -> bool: ...


class DiscordFeedbackService:
    def __init__(self, bot_client) -> None:
        self._bot = bot_client

    async def send_feedback(
        self,
        channel_id: str,
        user_id: str,
        message: str,
    ) -> bool:
        try:
            channel = self._bot.get_channel(int(channel_id))
            if channel is None:
                log.warning(f"Channel not found: {channel_id}")
                return False
            user = self._bot.get_user(int(user_id))
            if user is None:
                log.warning(f"User not found: {user_id}")
                return False
            dm_channel = user.dm_channel
            if dm_channel is None:
                dm_channel = await user.create_dm()
            await dm_channel.send(content=message)
            log.info(f"Feedback sent to user {user_id}: {message[:50]}...")
            return True
        except Exception as e:
            log.warning(f"Failed to send feedback: {e}")
            return False
