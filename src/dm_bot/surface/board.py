"""Base board abstraction for surface views."""

from abc import ABC, abstractmethod
from typing import Any


class Board(ABC):
    """A view that renders runtime state into Discord-formatted output."""

    @abstractmethod
    def render(self, state: dict[str, Any]) -> str:
        """Render board state as Discord-formatted string."""
