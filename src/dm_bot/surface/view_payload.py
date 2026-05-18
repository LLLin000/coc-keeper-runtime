"""Structured view payload — separates what to display from how to format."""

from pydantic import BaseModel, Field


class FieldEntry(BaseModel):
    """A named key-value pair for compact display."""

    name: str
    value: str
    inline: bool = False


class ViewSection(BaseModel):
    """A titled content block within a view."""

    heading: str
    body: str
    fields: list[FieldEntry] = Field(default_factory=list)


class ViewPayload(BaseModel):
    """Structured display data independent of formatting target."""

    title: str
    description: str = ""
    sections: list[ViewSection] = Field(default_factory=list)
    fields: list[FieldEntry] = Field(default_factory=list)
    footer: str = ""
