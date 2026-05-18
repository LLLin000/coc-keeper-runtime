"""Tests for character import."""


class TestCharacterImport:
    def test_import_valid_json(self):
        from dm_bot.character.importer import import_character

        data = '{"name": "Alice", "age": 30, "strength": 60, "constitution": 50}'
        result = import_character(data, player_id="u1")
        assert result is not None
        assert result.sheet.name == "Alice"
        assert result.sheet.strength == 60

    def test_import_invalid_json(self):
        from dm_bot.character.importer import import_character

        result = import_character("not json", player_id="u1")
        assert result is None

    def test_import_missing_required(self):
        from dm_bot.character.importer import import_character

        result = import_character('{"age": 30}', player_id="u1")
        assert result is None
