"""Tests for adventure loader."""

import pytest

from dm_bot.adventure.models import Scene, NPC, Clue, Adventure
from dm_bot.adventure.loader import AdventureLoader


class TestAdventureModels:
    def test_scene_creation(self):
        scene = Scene(
            scene_id="scene-1",
            name="The Library",
            description="A dusty old library.",
        )
        assert scene.scene_id == "scene-1"
        assert scene.name == "The Library"

    def test_npc_creation(self):
        npc = NPC(
            npc_id="librarian",
            name="Old Librarian",
        )
        assert npc.name == "Old Librarian"

    def test_clue_creation(self):
        clue = Clue(
            clue_id="clue-1",
            description="A hidden note.",
        )
        assert clue.clue_id == "clue-1"

    def test_adventure_creation(self):
        scene = Scene(scene_id="s1", name="Scene 1", description="Desc")
        adventure = Adventure(
            adventure_id="adv-1",
            name="Test Adventure",
            scenes={"s1": scene},
            opening_scene_id="s1",
        )
        assert adventure.name == "Test Adventure"
        assert adventure.opening_scene_id == "s1"


class TestAdventureLoader:
    def test_load_module(self):
        loader = AdventureLoader()
        adventure = loader.load_module("starter_crypt")
        assert adventure is not None
        assert adventure.adventure_id == "starter_crypt"

    def test_get_scene(self):
        loader = AdventureLoader()
        scene = Scene(scene_id="s1", name="S1", description="D")
        adventure = Adventure(adventure_id="a1", name="A1", scenes={"s1": scene})
        result = loader.get_scene(adventure, "s1")
        assert result is not None
        assert result.scene_id == "s1"

    def test_get_scene_missing(self):
        loader = AdventureLoader()
        adventure = Adventure(adventure_id="a1", name="A1")
        result = loader.get_scene(adventure, "missing")
        assert result is None
