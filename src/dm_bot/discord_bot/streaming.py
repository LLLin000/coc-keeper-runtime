import time
from collections.abc import AsyncIterator, Awaitable, Callable


class StreamingMessageTransport:
    def __init__(
        self,
        *,
        send_initial: Callable[[str], Awaitable[object]],
        edit_message: Callable[[object, str], Awaitable[None]],
        min_interval_seconds: float = 0.6,
        min_chars_delta: int = 48,
    ) -> None:
        self._send_initial = send_initial
        self._edit_message = edit_message
        self._min_interval_seconds = min_interval_seconds
        self._min_chars_delta = min_chars_delta

    async def stream(self, snapshots: AsyncIterator[str], *, placeholder: str = "DM 正在回应…") -> str:
        message = await self._send_initial(placeholder)
        last_sent = placeholder
        latest = placeholder
        last_emit_at = time.monotonic()

        async for snapshot in snapshots:
            latest = self._clip(snapshot)
            if self._should_emit(now=time.monotonic(), last_emit_at=last_emit_at, latest=latest, last_sent=last_sent):
                await self._edit_message(message, latest)
                last_sent = latest
                last_emit_at = time.monotonic()

        if latest != last_sent:
            await self._edit_message(message, latest)
            last_sent = latest
        return last_sent

    def _should_emit(self, *, now: float, last_emit_at: float, latest: str, last_sent: str) -> bool:
        return (
            latest != last_sent
            and (
                len(latest) - len(last_sent) >= self._min_chars_delta
                or now - last_emit_at >= self._min_interval_seconds
            )
        )

    def _clip(self, content: str) -> str:
        if len(content) <= 1900:
            return content
        return content[:1896] + " ..."
