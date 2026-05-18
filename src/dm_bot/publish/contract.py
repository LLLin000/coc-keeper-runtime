"""Renderer contract that surface layer must implement."""

from abc import ABC, abstractmethod

from dm_bot.publish.models import PublicationEvent


class RendererContract(ABC):
    """Interface that Discord (or any surface) must implement."""

    @abstractmethod
    def render(self, event: PublicationEvent) -> str:
        """Render a publication event into a display string."""
        ...
