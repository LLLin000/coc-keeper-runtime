"""Tests for presentation layer: CardSection, CardRenderer, DiscordCardRenderer."""

from typing import Protocol, runtime_checkable

from dm_bot.coc.presentation import CardSection, CardRenderer, DiscordCardRenderer


def test_card_section_creation_with_all_fields() -> None:
    """CardSection can be created with all fields specified."""
    section = CardSection(
        title="Test Section",
        content="Test content",
        visibility="private",
        order=3,
    )
    assert section.title == "Test Section"
    assert section.content == "Test content"
    assert section.visibility == "private"
    assert section.order == 3


def test_card_section_defaults() -> None:
    """CardSection defaults visibility to 'public' and order to 0."""
    section = CardSection(title="Minimal", content="Content")
    assert section.visibility == "public"
    assert section.order == 0


def test_card_section_is_dataclass() -> None:
    """CardSection is a dataclass, not a Pydantic model."""
    from dataclasses import is_dataclass

    assert is_dataclass(CardSection)
    assert not hasattr(CardSection, "model_dump")


def test_discord_card_renderer_renders_sections() -> None:
    """DiscordCardRenderer formats sections as **title**\\ncontent."""
    renderer = DiscordCardRenderer()
    sections = [
        CardSection(title="Header", content="Header content", order=0),
        CardSection(title="Details", content="Detail content", order=1),
    ]
    result = renderer.render(sections)
    assert len(result) == 2
    assert result[0] == "**Header**\nHeader content"
    assert result[1] == "**Details**\nDetail content"


def test_discord_card_renderer_empty_sections() -> None:
    """DiscordCardRenderer returns empty list for no sections."""
    renderer = DiscordCardRenderer()
    result = renderer.render([])
    assert result == []


def test_card_renderer_protocol_accepts_discord_renderer() -> None:
    """DiscordCardRenderer satisfies the CardRenderer protocol."""
    renderer: CardRenderer = DiscordCardRenderer()
    sections = [CardSection(title="T", content="C")]
    result = renderer.render(sections)
    assert isinstance(result, list)
    assert len(result) == 1


def test_card_section_visibility_values() -> None:
    """CardSection visibility accepts all defined values."""
    valid_visibilities = ["public", "private", "group", "keeper"]
    for vis in valid_visibilities:
        section = CardSection(title="T", content="C", visibility=vis)  # type: ignore[arg-type]
        assert section.visibility == vis
