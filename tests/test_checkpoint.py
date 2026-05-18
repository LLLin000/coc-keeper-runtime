"""Tests for post-session checkpoint."""


class TestSessionCheckpoint:
    def test_improve_skills(self):
        from dm_bot.character.checkpoint import SessionCheckpoint
        from dm_bot.character.sheet import CharacterSheet

        sheet = CharacterSheet(character_id="c1", name="Alice", skills={"spot_hidden": 40, "library_use": 30})
        cp = SessionCheckpoint()
        result = cp.process(sheet, skills_used=["spot_hidden", "library_use"],
                            improvement_rolls={"spot_hidden": 30, "library_use": 99})
        assert result.skills_tried == 2
        assert result.skills_improved >= 1
        assert result.updated_sheet.skills["spot_hidden"] > 40

    def test_no_skills_no_change(self):
        from dm_bot.character.checkpoint import SessionCheckpoint
        from dm_bot.character.sheet import CharacterSheet

        sheet = CharacterSheet(character_id="c1", name="Alice")
        cp = SessionCheckpoint()
        result = cp.process(sheet, skills_used=[])
        assert result.skills_tried == 0
        assert result.skills_improved == 0


class TestCheckpointPersistence:
    def test_save_checkpoint(self):
        from dm_bot.store.db import Store
        from dm_bot.character.checkpoint import SessionCheckpoint
        from dm_bot.character.sheet import CharacterSheet
        from dm_bot.character.archive import CharacterArchive
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_chkpt2.db")
        if os.path.exists(db_path): os.remove(db_path)
        store = Store(db_path)
        try:
            sheet = CharacterSheet(character_id="c1", name="Alice", skills={"spot_hidden": 40})
            archive = CharacterArchive(character_id="c1", player_id="u1", sheet=sheet)
            store.save_character(archive)

            cp = SessionCheckpoint()
            result = cp.process(sheet, skills_used=["spot_hidden"], improvement_rolls={"spot_hidden": 30})
            assert result.skills_improved == 1

            updated = CharacterArchive(character_id="c1", player_id="u1", sheet=result.updated_sheet)
            store.save_character(updated)
            loaded = store.load_character("c1")
            assert loaded.sheet.skills["spot_hidden"] > 40
        finally:
            del store; gc.collect()
            if os.path.exists(db_path): os.remove(db_path)
