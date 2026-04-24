from dm_bot.adventures.loader import load_adventure
from dm_bot.adventures.models import AdventurePackage


def test_load_fuzhe_adventure():
    """ADV-01: fuzhe.json loads and returns valid AdventurePackage"""
    adventure = load_adventure("fuzhe")

    # Basic validation
    assert adventure.slug == "fuzhe"
    assert adventure.title == "覆辙"
    assert adventure.start_scene_id == "car_crash_scene"

    # Structural counts
    assert len(adventure.triggers) == 14
    assert len(adventure.locations) == 9
    assert len(adventure.state_fields) >= 12
    assert len(adventure.story_nodes) >= 7


def test_fuzhe_scene_and_location_access():
    """ADV-01: Scenes and locations are accessible by ID"""
    adventure = load_adventure("fuzhe")

    # Scene access
    scene = adventure.scene_by_id("car_crash_scene")
    assert scene.title == "车祸路口"
    assert scene.combat == False

    wetland = adventure.scene_by_id("wetland_scene")
    assert wetland.combat == True  # First combat scene

    # Location access
    loc = adventure.location_by_id("wetland_gate")
    assert loc.title == "湿地公园入口"
    assert (
        len(loc.connections) >= 4
    )  # Connections to store, restaurant, cultural_street, school

    # Connection validation - all to_location_ids exist
    for location in adventure.locations:
        for conn in location.connections:
            adventure.location_by_id(conn.to_location_id)  # Must not raise


def test_fuzhe_trigger_access():
    """ADV-01: Triggers are accessible and have correct structure"""
    adventure = load_adventure("fuzhe")

    # Action trigger
    inspect = adventure.trigger_by_id("fuzhe_inspect_crash")
    assert inspect.event_kind == "action"
    assert inspect.action_id == "inspect_crash"
    assert (
        len(inspect.effects) >= 4
    )  # record_knowledge, move_story_node, increments, sets

    # Roll trigger with conditions
    forum_success = adventure.trigger_by_id("forum_search_success")
    assert forum_success.event_kind == "roll"
    assert forum_success.roll_label == "LibraryUse"
    assert forum_success.conditions.min_total == 10

    forum_fail = adventure.trigger_by_id("forum_search_fail")
    assert forum_fail.conditions.max_total == 9


def test_fuzhe_state_field_visibility():
    """ADV-01 + ADV-03: State fields have correct visibility levels"""
    adventure = load_adventure("fuzhe")

    defaults = adventure.state_defaults()
    assert defaults.get("san_pressure") == 0
    assert defaults.get("car_crash_witnessed") == False

    # Test visibility filtering
    module_state = {
        "san_pressure": 5,
        "module_rule_mode": "fuzhe",  # gm_only visibility
        "danger_level": "high",  # discoverable visibility
    }

    public = adventure.public_state(module_state)
    assert "san_pressure" in public
    assert "danger_level" in public
    assert "module_rule_mode" not in public  # gm_only filtered out

    gm = adventure.gm_state(module_state)
    assert "module_rule_mode" in gm  # gm_only included for GM


def test_fuzhe_validator_passes():
    """ADV-01: AdventurePackage validator accepts fuzhe structure"""
    adventure = load_adventure("fuzhe")
    # If we get here without exception, validator passed
    assert adventure.slug == "fuzhe"
