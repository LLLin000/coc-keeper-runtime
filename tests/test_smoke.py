"""Smoke tests for the new architecture."""

import subprocess


class TestSmoke:
    def test_import_scene(self):
        from dm_bot.scene.state import SceneState
        from dm_bot.scene.action import Action, ActionResult
        from dm_bot.scene.round import Round
        assert SceneState.WAITING is not None

    def test_import_character(self):
        from dm_bot.character.sheet import CharacterSheet
        assert CharacterSheet is not None

    def test_import_adventure(self):
        from dm_bot.adventure.models import Scene, NPC, Adventure
        from dm_bot.adventure.loader import AdventureLoader
        assert Scene is not None

    def test_import_narrator(self):
        from dm_bot.narrator.client import SimpleNarrator
        from dm_bot.narrator.prompts import scene_opening, scene_resolution
        assert SimpleNarrator is not None

    def test_import_store(self):
        from dm_bot.store.db import Store
        assert Store is not None

    def test_import_rules(self):
        from dm_bot.rules.dice import SeededDiceRoller
        from dm_bot.rules.coc import resolve_skill_check
        assert SeededDiceRoller is not None

    def test_import_discord_bot(self):
        from dm_bot.discord_bot.commands import BotCommands
        assert BotCommands is not None

    def test_main_smoke_check(self):
        result = subprocess.run(
            ["uv", "run", "python", "-m", "dm_bot.main", "smoke-check"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "import successfully" in result.stdout
