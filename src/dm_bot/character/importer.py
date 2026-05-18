"""Character import -- parse and validate structured input."""

import json

from dm_bot.character.archive import CharacterArchive
from dm_bot.character.sheet import CharacterSheet


def import_character(data: str, player_id: str) -> CharacterArchive | None:
    """Parse JSON string into CharacterArchive. Returns None on failure."""
    try:
        parsed = json.loads(data)
    except (json.JSONDecodeError, ValueError):
        return None
    try:
        if "name" not in parsed:
            return None
        cid = parsed.pop("character_id", player_id)
        sheet = CharacterSheet(character_id=cid, **parsed)
        return CharacterArchive(character_id=cid, player_id=player_id, sheet=sheet)
    except Exception:
        return None
