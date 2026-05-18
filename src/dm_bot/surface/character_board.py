"""Character sheet display board."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, ViewSection, FieldEntry
from dm_bot.surface.discord_formatter import DiscordFormatter


class CharacterCardBoard(Board):
    """Renders a character archive as a Discord-readable card."""

    STAT_KEYS = ["strength", "constitution", "size", "dexterity",
                  "appearance", "intelligence", "power", "education", "luck"]

    def render(self, state: dict) -> str:
        name = state.get("name", "?")
        occupation = state.get("occupation", "")
        fields = [
            FieldEntry(name="Age", value=str(state.get("age", "?"))),
            FieldEntry(name="Occupation", value=occupation or "?"),
        ]
        stat_fields = [
            FieldEntry(name=k.split("_")[0].upper()[:3], value=str(state.get(k, 0)), inline=True)
            for k in self.STAT_KEYS
        ]
        stats = ViewSection(heading="Attributes", body="", fields=stat_fields)
        hp_fields = [
            FieldEntry(name="HP", value=str(state.get("hit_points", "?")), inline=True),
            FieldEntry(name="MP", value=str(state.get("magic_points", "?")), inline=True),
            FieldEntry(name="SAN", value=f"{state.get('sanity', '?')}/{state.get('sanity_max', 99)}", inline=True),
        ]
        vitals = ViewSection(heading="Vitals", body="", fields=hp_fields)
        sections = [stats, vitals]

        skills = state.get("skills", {})
        if skills:
            sections.append(ViewSection(
                heading="Skills",
                body=", ".join(f"{k}:{v}%" for k, v in sorted(skills.items())),
            ))

        payload = ViewPayload(
            title=f"{name} ({occupation})" if occupation else name,
            fields=fields,
            sections=sections,
        )
        return DiscordFormatter.format(payload)
