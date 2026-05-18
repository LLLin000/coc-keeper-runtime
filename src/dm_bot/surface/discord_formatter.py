"""Discord markdown formatter for ViewPayload."""

from dm_bot.surface.view_payload import ViewPayload


class DiscordFormatter:
    """Converts ViewPayload to Discord-formatted markdown string."""

    @staticmethod
    def format(payload: ViewPayload) -> str:
        lines: list[str] = []
        lines.append(f"**{payload.title}**")
        if payload.description:
            lines.append(payload.description)
            lines.append("")
        for field in payload.fields:
            lines.append(f"**{field.name}:** {field.value}")
        if payload.fields:
            lines.append("")
        for section in payload.sections:
            lines.append(f"**{section.heading}**")
            if section.body:
                lines.append(section.body)
            for field in section.fields:
                lines.append(f"  {field.name}: {field.value}")
            lines.append("")
        if payload.footer:
            lines.append(f"_{payload.footer}_")
        return "\n".join(lines).strip()
