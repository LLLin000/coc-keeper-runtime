"""Presentation layer: decouple archive data from Discord-specific formatting.

This module defines the abstraction boundary between data (Track B) and
presentation (Track D). It does NOT define any canonical state or data
ownership — purely formatting contracts per ACTIVITY-02.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol


Visibility = Literal["public", "private", "group", "keeper"]


@dataclass
class CardSection:
    """A single section of an investigator card.

    Lightweight dataclass (not Pydantic) — this is a presentation contract,
    not a data model per ACTIVITY-02.
    """

    title: str
    content: str
    visibility: Visibility = "public"
    order: int = 0


class CardRenderer(Protocol):
    """Protocol for rendering card sections into display strings.

    Uses structural subtyping — any class with a render() method matching
    this signature satisfies the protocol. Enables future ActivityCardRenderer
    without changing archive.py.
    """

    def render(self, sections: list[CardSection]) -> list[str]: ...


class DiscordCardRenderer:
    """Renders CardSections as Discord-formatted messages.

    Matches current behavior: bold title + newline + content.
    Does NOT modify or own any canonical state — purely formatting.
    """

    def render(self, sections: list[CardSection]) -> list[str]:
        return [f"**{s.title}**\n{s.content}" for s in sections]
