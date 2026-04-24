from dm_bot.adventures.loader import load_adventure
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


def test_set_adventure_location_updates_both_ids():
    """ADV-04: set_adventure_location updates location_id AND scene_id"""
    gameplay = build_gameplay()
    gameplay.load_adventure(load_adventure("fuzhe"))

    # Initial state
    assert gameplay.adventure_state["location_id"] == "car_crash_intersection"
    assert gameplay.adventure_state["scene_id"] == "car_crash_scene"

    gameplay.set_adventure_location("wetland_gate")

    # Both should be updated
    assert gameplay.adventure_state["location_id"] == "wetland_gate"
    assert gameplay.adventure_state["scene_id"] == "wetland_scene"


def test_keyword_navigation_transitions_room():
    """ADV-04: Keyword navigation triggers room transition"""
    gameplay = build_gameplay()
    gameplay.load_adventure(load_adventure("fuzhe"))

    # Initial at car_crash_intersection
    assert gameplay.adventure_state["location_id"] == "car_crash_intersection"

    # Navigate using keyword
    result = gameplay.evaluate_scene_action("进入湿地公园")

    # Should transition
    assert gameplay.adventure_state["location_id"] == "wetland_gate"
    assert result["kind"] == "auto"


def test_public_snapshot_excludes_gm_only_fields():
    """ADV-03: public snapshot excludes gm_only visibility fields"""
    gameplay = build_gameplay()
    gameplay.load_adventure(load_adventure("fuzhe"))

    # Set some state including gm_only field
    gameplay.update_adventure_state(
        san_pressure=5,
        danger_level="high",
        module_rule_mode="fuzhe",  # This is gm_only
    )

    snapshot = gameplay.adventure_snapshot()

    # Public state should NOT contain gm_only fields
    public_state = snapshot["public"]["state"]
    assert "san_pressure" in public_state
    assert "danger_level" in public_state
    assert "module_rule_mode" not in public_state

    # GM state SHOULD contain gm_only fields
    gm_state = snapshot["gm"]["state"]
    assert "module_rule_mode" in gm_state
    assert gm_state["module_rule_mode"] == "fuzhe"


def test_reachable_locations_from_snapshot():
    """ADV-04: adventure_snapshot returns correct reachable locations"""
    gameplay = build_gameplay()
    gameplay.load_adventure(load_adventure("fuzhe"))

    snapshot = gameplay.adventure_snapshot()

    reachable = snapshot["public"]["reachable_locations"]
    assert len(reachable) >= 3  # car_crash_intersection has 4 connections

    # All reachable locations should have to_location_id
    for loc in reachable:
        assert "to_location_id" in loc


def test_scene_frame_updates_after_transition():
    """ADV-04: scene_frame_text reflects new location after transition"""
    gameplay = build_gameplay()
    gameplay.load_adventure(load_adventure("fuzhe"))

    # Initial frame at car_crash_scene
    frame1 = gameplay.scene_frame_text()
    assert "车祸路口" in frame1

    # Transition
    gameplay.set_adventure_location("wetland_gate")

    # Frame should update
    frame2 = gameplay.scene_frame_text()
    assert "湿地公园" in frame2


def test_location_connection_keywords_work():
    """ADV-04: Location connections have correct keywords for navigation"""
    adventure = load_adventure("fuzhe")

    car_crash = adventure.location_by_id("car_crash_intersection")

    # Check wetland_gate connection exists with correct keywords
    wetland_conn = None
    for conn in car_crash.connections:
        if conn.to_location_id == "wetland_gate":
            wetland_conn = conn
            break

    assert wetland_conn is not None
    assert any("湿地" in k or "公园" in k for k in wetland_conn.keywords)


def test_multiple_location_transitions_preserve_state():
    """ADV-04: Multiple location transitions don't lose previous state"""
    gameplay = build_gameplay()
    gameplay.load_adventure(load_adventure("fuzhe"))

    # Set some state
    gameplay.update_adventure_state(san_pressure=3)

    # Transition 1: car_crash -> mystery_forum
    gameplay.set_adventure_location("mystery_forum")
    assert gameplay.adventure_state["location_id"] == "mystery_forum"
    assert gameplay.adventure_state["module_state"]["san_pressure"] == 3

    # Transition 2: mystery_forum -> wetland_gate
    gameplay.set_adventure_location("wetland_gate")
    assert gameplay.adventure_state["location_id"] == "wetland_gate"
    assert gameplay.adventure_state["module_state"]["san_pressure"] == 3  # Preserved


def test_gm_snapshot_includes_all_state():
    """ADV-03: GM snapshot includes all discoverable and gm_only fields"""
    gameplay = build_gameplay()
    gameplay.load_adventure(load_adventure("fuzhe"))

    # Set various visibility levels
    gameplay.update_adventure_state(
        san_pressure=5,  # discoverable
        danger_level="critical",  # discoverable
        module_rule_mode="fuzhe",  # gm_only
    )

    snapshot = gameplay.adventure_snapshot()
    gm = snapshot["gm"]

    # GM sees everything
    assert gm["state"]["san_pressure"] == 5
    assert gm["state"]["danger_level"] == "critical"
    assert gm["state"]["module_rule_mode"] == "fuzhe"

    # Public sees only discoverable
    public = snapshot["public"]["state"]
    assert public["san_pressure"] == 5
    assert public["danger_level"] == "critical"
    assert "module_rule_mode" not in public
