from typing import Protocol, Callable, Awaitable
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
    def __init__(
        self,
        send_dm_callback: Callable[[str, str], Awaitable[bool]] | None = None,
    ) -> None:
        self._send_dm = send_dm_callback

    def set_send_dm_callback(
        self, callback: Callable[[str, str], Awaitable[bool]]
    ) -> None:
        self._send_dm = callback

    async def send_feedback(
        self,
        channel_id: str,
        user_id: str,
        message: str,
    ) -> bool:
        if self._send_dm is None:
            log.warning("No send_dm callback configured for feedback service")
            return False
        try:
            success = await self._send_dm(user_id, message)
            if success:
                log.info(f"Feedback sent to user {user_id}: {message[:50]}...")
            return success
        except Exception as e:
            log.warning(f"Failed to send feedback: {e}")
            return False
