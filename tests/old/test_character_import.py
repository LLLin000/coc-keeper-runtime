from dm_bot.characters.importer import CharacterImporter
from dm_bot.characters.models import CharacterSourceLabel
from dm_bot.characters.sources import DicecloudSnapshotSource


def test_importer_normalizes_dicecloud_snapshot_character() -> None:
    source = DicecloudSnapshotSource(
        fixtures={
            "char-1": {
                "id": "char-1",
                "name": "林地游侠",
                "species": "Wood Elf",
                "classes": [{"name": "Ranger", "level": 3}],
                "proficiency_bonus": 2,
                "armor_class": 15,
                "speed": 35,
                "hp": {"current": 24, "maximum": 24, "temporary": 0},
                "abilities": {
                    "strength": 10,
                    "dexterity": 16,
                    "constitution": 14,
                    "intelligence": 12,
                    "wisdom": 15,
                    "charisma": 8,
                },
                "skills": {"stealth": 5, "perception": 4, "survival": 4},
                "attacks": [
                    {"name": "Longbow", "attack_bonus": 5, "damage": "1d8+3 piercing"}
                ],
                "spellcasting": {"ability": "wisdom", "save_dc": 12, "attack_bonus": 4},
                "resources": {"spell_slots_1": 3, "hit_dice_d10": 3},
            }
        }
    )
    importer = CharacterImporter(sources={"dicecloud_snapshot": source})

    character = importer.import_character("dicecloud_snapshot", "char-1")

    assert character.name == "林地游侠"
    assert character.source.label == CharacterSourceLabel.SNAPSHOT
    assert character.source.provider == "dicecloud_snapshot"
    assert character.hp.current == 24
    assert character.abilities.dexterity == 16
    assert character.skills["stealth"] == 5
    assert character.attacks[0].name == "Longbow"
    assert character.spellcasting is not None
    assert character.resources["spell_slots_1"] == 3


def test_importer_rejects_unknown_source_provider() -> None:
    importer = CharacterImporter(sources={})

    try:
        importer.import_character("unknown", "char-1")
    except KeyError as exc:
        assert "unknown" in str(exc)
    else:
        raise AssertionError("expected missing source provider to fail")
