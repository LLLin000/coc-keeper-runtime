"""Tests for adventure file loading."""

import json
import os
import tempfile

from dm_bot.adventure.loader import AdventureLoader


class TestAdventureLoaderFile:
    def test_load_from_file(self):
        loader = AdventureLoader()
        data = {
            "adventure_id": "test_mansion",
            "name": "The Haunted Mansion",
            "scenes": {
                "hall": {
                    "scene_id": "hall",
                    "name": "Entrance Hall",
                    "description": "A dark hallway.",
                }
            },
        }
        tmp = os.path.join(tempfile.gettempdir(), "test_adventure.json")
        try:
            with open(tmp, "w") as f:
                json.dump(data, f)
            adv = loader.load_module(tmp)
            assert adv.adventure_id == "test_mansion"
            assert adv.name == "The Haunted Mansion"
            assert "hall" in adv.scenes
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
