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


class TestCharacterArchive:
    def test_create_archive(self):
        from dm_bot.character.archive import CharacterArchive

        sheet = CharacterSheet(character_id="c1", name="Alice", occupation="Detective")
        archive = CharacterArchive(character_id="c1", player_id="user_1", sheet=sheet)
        assert archive.schema_version == 1
        assert archive.sheet.name == "Alice"
        assert archive.player_id == "user_1"

    def test_archive_default_version(self):
        from dm_bot.character.archive import CharacterArchive

        sheet = CharacterSheet(character_id="c2", name="Bob")
        archive = CharacterArchive(character_id="c2", player_id="user_2", sheet=sheet)
        assert archive.schema_version == 1

    def test_archive_versioned_serialization(self):
        from dm_bot.character.archive import CharacterArchive

        sheet = CharacterSheet(character_id="c3", name="Charlie", strength=60)
        archive = CharacterArchive(character_id="c3", player_id="user_3", sheet=sheet)
        data = archive.model_dump()
        assert data["schema_version"] == 1
        assert data["sheet"]["name"] == "Charlie"


class TestFullPathBuilder:
    def test_full_path_creates_character(self):
        from dm_bot.character.builder import FullPathBuilder

        builder = FullPathBuilder()
        result = builder.build_fast()
        assert result.name is not None
        assert result.strength >= 30

    def test_full_path_heuristic_fallback(self):
        from dm_bot.character.builder import FullPathBuilder

        builder = FullPathBuilder(use_model=False)
        result = builder.build()
        assert isinstance(result.name, str)
        assert len(result.name) > 0


class TestCharacterStore:
    def test_save_and_load_character(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_crud_save.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        try:
            sheet = CharacterSheet(character_id="c1", name="Alice", occupation="Writer")
            archive = CharacterArchive(character_id="c1", player_id="u1", sheet=sheet)
            store.save_character(archive)
            loaded = store.load_character("c1")
            assert loaded is not None
            assert loaded.sheet.name == "Alice"
            assert loaded.player_id == "u1"
        finally:
            del store
            gc.collect()
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_list_characters_by_player(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_crud_list.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        try:
            alice = CharacterArchive(character_id="c1", player_id="u1", sheet=CharacterSheet(character_id="c1", name="Alice"))
            bob = CharacterArchive(character_id="c2", player_id="u1", sheet=CharacterSheet(character_id="c2", name="Bob"))
            charlie = CharacterArchive(character_id="c3", player_id="u2", sheet=CharacterSheet(character_id="c3", name="Charlie"))
            for a in [alice, bob, charlie]:
                store.save_character(a)
            u1_list = store.list_characters("u1")
            assert len(u1_list) == 2
            u2_list = store.list_characters("u2")
            assert len(u2_list) == 1
            assert u2_list[0].sheet.name == "Charlie"
        finally:
            del store
            gc.collect()
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_delete_character(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_crud_del.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        try:
            sheet = CharacterSheet(character_id="c1", name="ToDelete")
            archive = CharacterArchive(character_id="c1", player_id="u1", sheet=sheet)
            store.save_character(archive)
            store.delete_character("c1")
            assert store.load_character("c1") is None
        finally:
            del store
            gc.collect()
            if os.path.exists(db_path):
                os.remove(db_path)


class TestBuilderPersistence:
    def test_builder_persists_to_store(self):
        from dm_bot.character.builder import CharacterBuilder
        from dm_bot.store.db import Store
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_build_persist.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        try:
            builder = CharacterBuilder(store=store)
            builder.begin_creation("user_1")
            builder.handle_response("user_1", "Alice")
            builder.handle_response("user_1", "30")
            result = builder.handle_response("user_1", "Detective")
            assert "角色创建完成" in result
            loaded = store.load_character("user_1")
            assert loaded is not None
            assert loaded.sheet.name == "Alice"
            assert loaded.sheet.age == 30
        finally:
            del store
            gc.collect()
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_builder_without_store_no_persist(self):
        from dm_bot.character.builder import CharacterBuilder

        builder = CharacterBuilder()
        builder.begin_creation("user_2")
        builder.handle_response("user_2", "Bob")
        builder.handle_response("user_2", "25")
        result = builder.handle_response("user_2", "Doctor")
        assert "角色创建完成" in result
        sheet = builder.get_sheet("user_2")
        assert sheet is not None
        assert sheet.name == "Bob"
