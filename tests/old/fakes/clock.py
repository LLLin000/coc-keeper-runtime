import datetime
import time


class FakeClock:
    def __init__(
        self, *, frozen: bool = False, start_time: float | None = None
    ) -> None:
        self._frozen = frozen
        self._offset = 0.0
        self._start = start_time if start_time is not None else time.time()

    def advance(self, seconds: float) -> None:
        if not self._frozen:
            self._offset += seconds

    def freeze(self) -> None:
        self._frozen = True

    def unfreeze(self) -> None:
        self._frozen = False

    def utcnow(self) -> datetime.datetime:
        if self._frozen:
            return datetime.datetime.fromtimestamp(
                self._start, tz=datetime.timezone.utc
            )
        return datetime.datetime.fromtimestamp(
            self._start + self._offset, tz=datetime.timezone.utc
        )

    def time(self) -> float:
        if self._frozen:
            return self._start
        return self._start + self._offset
