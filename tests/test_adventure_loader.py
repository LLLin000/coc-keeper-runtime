from dm_bot.adventures.loader import load_adventure


def test_load_starter_adventure() -> None:
    adventure = load_adventure("starter_crypt")

    assert adventure.slug == "starter_crypt"
    assert adventure.title
    assert len(adventure.scenes) >= 3
    assert any(scene.combat for scene in adventure.scenes)
