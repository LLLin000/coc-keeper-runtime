from dm_bot.adventures.loader import load_adventure
from dm_bot.adventures.trigger_engine import TriggerEngine


def test_trigger_engine_can_record_private_knowledge_and_move_story_node() -> None:
    package = load_adventure("fuzhe")
    state = {
        "scene_id": "car_crash_scene",
        "location_id": "car_crash_intersection",
        "story_node_id": "investigator_intro",
        "module_state": {},
        "clues_found": [],
        "knowledge_log": [],
    }
    engine = TriggerEngine()

    resolution = engine.execute(
        package=package,
        adventure_state=state,
        event={"kind": "action", "action_id": "inspect_crash", "user_id": "user-1"},
    )

    assert resolution.matched_trigger_ids
    assert state["story_node_id"] == "forum_investigation"
    assert any(item["title"] == "神秘少女目击" for item in state["knowledge_log"])


def test_fuzhe_module_contains_multiple_onboarding_tracks_and_story_nodes() -> None:
    package = load_adventure("fuzhe")

    roles = {track.role for track in package.onboarding_tracks}
    kinds = {node.kind for node in package.story_nodes}

    assert {"investigator", "magical_girl"}.issubset(roles)
    assert {"scene", "event"}.issubset(kinds)
