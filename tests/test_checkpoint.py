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
