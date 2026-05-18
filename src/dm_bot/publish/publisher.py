"""Event publisher that routes events by visibility path."""

from dm_bot.publish.models import PublicationEvent, PublicationPath


class Publisher:
    """Stores and routes runtime events by visibility and type."""

    def __init__(self) -> None:
        self._events: list[PublicationEvent] = []

    @property
    def events(self) -> list[PublicationEvent]:
        return list(self._events)

    def publish(self, event: PublicationEvent) -> None:
        self._events.append(event)

    def get_events(
        self,
        visibility: PublicationPath | None = None,
        event_type: str | None = None,
    ) -> list[PublicationEvent]:
        result = self._events
        if visibility:
            result = [e for e in result if e.visibility == visibility]
        if event_type:
            result = [e for e in result if e.event_type == event_type]
        return list(result)

    def clear(self) -> None:
        self._events.clear()
