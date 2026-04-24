"""Tests for character sheet and builder."""

import pytest

from dm_bot.character.sheet import CharacterSheet


class TestCharacterSheet:
    def test_sheet_creation(self):
        sheet = CharacterSheet(
            character_id="c1",
            name="John Doe",
        )
        assert sheet.name == "John Doe"
        assert sheet.character_id == "c1"

    def test_default_attributes(self):
        sheet = CharacterSheet(character_id="c1", name="Test")
        assert sheet.strength == 50
        assert sheet.dexterity == 50
        assert sheet.constitution == 50
        assert sheet.intelligence == 50
        assert sheet.power == 50
        assert sheet.appearance == 50
        assert sheet.education == 50
        assert sheet.size == 50

    def test_custom_attributes(self):
        sheet = CharacterSheet(
            character_id="c1",
            name="Strong",
            strength=80,
            dexterity=60,
        )
        assert sheet.strength == 80
        assert sheet.dexterity == 60

    def test_skills_dict(self):
        sheet = CharacterSheet(character_id="c1", name="Test")
        sheet.skills["Library Use"] = 60
        assert sheet.skills["Library Use"] == 60

    def test_sanity_range(self):
        sheet = CharacterSheet(character_id="c1", name="Test", power=70)
        assert sheet.sanity == 50  # sanity is independent default

    def test_get_skill_value(self):
        sheet = CharacterSheet(character_id="c1", name="Test")
        assert sheet.get_skill_value("Unknown") == 0
        sheet.skills["Spot Hidden"] = 45
        assert sheet.get_skill_value("Spot Hidden") == 45
