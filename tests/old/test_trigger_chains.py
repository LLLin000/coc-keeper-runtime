import pytest
from dm_bot.adventures.loader import load_adventure
from dm_bot.adventures.trigger_engine import TriggerEngine, TriggerResolution
from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
from dm_bot.rules.engine import RulesEngine
from dm_bot.rules.compendium import FixtureCompendium


def build_gameplay():
    return GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={})
        ),
    )


def test_fuzhe_inspect_crash_trigger_chain():
    """ADV-02: fuzhe_inspect_crash fires on inspect_crash action"""
    engine = TriggerEngine()
    adventure = load_adventure("fuzhe")

    adventure_state = {
        "location_id": "car_crash_intersection",
        "story_node_id": "investigator_intro",
        "module_state": dict(adventure.state_defaults()),
        "clues_found": [],
        "knowledge_log": [],
    }

    resolution = engine.execute(
        package=adventure,
        adventure_state=adventure_state,
        event={"kind": "action", "action_id": "inspect_crash"},
        trigger_ids=["fuzhe_inspect_crash"],
    )

    module_state = adventure_state["module_state"]
    assert module_state["car_crash_witnessed"] == True
    assert module_state["san_pressure"] == 1
    assert module_state["danger_level"] == "rising"
    assert module_state["current_investigation_stage"] == "forum"
    assert adventure_state["story_node_id"] == "forum_investigation"
    assert "fuzhe_inspect_crash" in resolution.matched_trigger_ids


def test_fuzhe_roll_trigger_forum_search_success():
    """ADV-02: forum_search_success fires when roll >= 10"""
    engine = TriggerEngine()
    adventure = load_adventure("fuzhe")

    adventure_state = {
        "location_id": "mystery_forum",
        "story_node_id": "forum_investigation",
        "module_state": dict(adventure.state_defaults()),
        "clues_found": [],
        "knowledge_log": [],
    }

    # Simulate pending roll setup (normally done by set_pending_roll effect)
    adventure_state["pending_roll"] = {
        "id": "forum_library_check",
        "action": "ability_check",
        "label": "LibraryUse",
    }

    # Execute roll trigger chain with successful roll
    resolution = engine.execute(
        package=adventure,
        adventure_state=adventure_state,
        event={
            "kind": "roll",
            "pending_roll_id": "forum_library_check",
            "roll_action": "ability_check",
            "roll_total": 25,  # Success (>= 10)
            "user_id": "",
        },
    )

    module_state = adventure_state["module_state"]
    assert module_state["forum_researched"] == True
    assert module_state["current_investigation_stage"] == "wetland"
    assert "pending_roll" not in adventure_state
    assert "forum_search_success" in resolution.matched_trigger_ids


def test_fuzhe_roll_trigger_forum_search_fail():
    """ADV-02: forum_search_fail fires when roll < 10"""
    gameplay = build_gameplay()
    gameplay.load_adventure(load_adventure("fuzhe"))
    gameplay.set_adventure_location("mystery_forum")

    gameplay.evaluate_scene_action("搜索论坛调查")

    result = gameplay.resolve_manual_roll(
        actor_name="调查员",
        action="ability_check",
        label="LibraryUse",
        modifier=0,
    )

    state = gameplay.adventure_state["module_state"]
    assert state.get("forum_researched") == False
    assert "pending_roll" not in gameplay.adventure_state


def test_fuzhe_blood_angel_joins_trigger():
    """ADV-02: blood_angel_joins fires on blood_angel_encounter action"""
    engine = TriggerEngine()
    adventure = load_adventure("fuzhe")

    adventure_state = {
        "location_id": "convenience_store",
        "story_node_id": "investigator_intro",
        "module_state": dict(adventure.state_defaults()),
        "clues_found": [],
        "knowledge_log": [],
    }

    resolution = engine.execute(
        package=adventure,
        adventure_state=adventure_state,
        event={"kind": "action", "action_id": "blood_angel_encounter"},
        trigger_ids=["blood_angel_joins"],
    )

    module_state = adventure_state["module_state"]
    assert module_state["blood_angel_joined"] == True
    assert module_state["magical_girl_count"] == 1
    assert "blood_angel_joins" in resolution.matched_trigger_ids


def test_trigger_resolution_contains_matched_ids_and_events():
    """ADV-02: TriggerResolution contains correct matched_trigger_ids"""
    engine = TriggerEngine()
    adventure = load_adventure("fuzhe")

    adventure_state = {
        "location_id": "car_crash_intersection",
        "story_node_id": "investigator_intro",
        "module_state": dict(adventure.state_defaults()),
        "clues_found": [],
        "knowledge_log": [],
    }

    resolution = engine.execute(
        package=adventure,
        adventure_state=adventure_state,
        event={"kind": "action", "action_id": "inspect_crash"},
        trigger_ids=["fuzhe_inspect_crash"],
    )

    assert "fuzhe_inspect_crash" in resolution.matched_trigger_ids
    assert len(resolution.events) >= 4
    assert resolution.merged_table_summary()


def test_trigger_engine_direct_execution():
    """ADV-02: TriggerEngine.execute() works directly"""
    engine = TriggerEngine()
    adventure = load_adventure("fuzhe")

    adventure_state = {
        "location_id": "car_crash_intersection",
        "story_node_id": "investigator_intro",
        "module_state": dict(adventure.state_defaults()),
        "clues_found": [],
        "knowledge_log": [],
    }

    resolution = engine.execute(
        package=adventure,
        adventure_state=adventure_state,
        event={"kind": "action", "action_id": "inspect_crash"},
        trigger_ids=["fuzhe_inspect_crash"],
    )

    assert "fuzhe_inspect_crash" in resolution.matched_trigger_ids
    assert len(resolution.events) >= 4
    assert resolution.merged_table_summary()
