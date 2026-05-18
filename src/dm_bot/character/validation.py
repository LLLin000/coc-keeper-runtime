"""COC character validation rules."""

from dm_bot.character.sheet import CharacterSheet


STAT_MIN = 3
STAT_MAX = 99
AGE_MIN = 15
AGE_MAX = 120

STAT_NAMES = ["strength", "constitution", "size", "dexterity",
              "appearance", "intelligence", "power", "education"]


def validate_character(sheet: CharacterSheet) -> list[str]:
    errors: list[str] = []
    if not sheet.name:
        errors.append("Name is required")
    if sheet.age < AGE_MIN:
        errors.append(f"Age {sheet.age} is below minimum {AGE_MIN}")
    if sheet.age > AGE_MAX:
        errors.append(f"Age {sheet.age} exceeds maximum {AGE_MAX}")
    for stat_name in STAT_NAMES:
        val = getattr(sheet, stat_name, 0)
        if val < STAT_MIN or val > STAT_MAX:
            errors.append(f"{stat_name.title()} {val} out of range [{STAT_MIN}-{STAT_MAX}]")
    return errors
