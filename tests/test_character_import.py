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


class TestImportPipeline:
    def test_import_validate_save(self):
        from dm_bot.character.importer import import_character
        from dm_bot.character.validation import validate_character
        from dm_bot.store.db import Store
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_import_pipe.db")
        if os.path.exists(db_path): os.remove(db_path)
        store = Store(db_path)
        try:
            data = '{"name": "Alice", "age": 30, "strength": 60, "constitution": 50}'
            archive = import_character(data, player_id="u1")
            assert archive is not None
            errors = validate_character(archive.sheet)
            assert len(errors) == 0
            store.save_character(archive)
            loaded = store.load_character(archive.character_id)
            assert loaded is not None
            assert loaded.sheet.name == "Alice"
        finally:
            del store; gc.collect()
            if os.path.exists(db_path): os.remove(db_path)
