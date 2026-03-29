# Phase 63 Context - Adventure Runtime

## Overview
- **Phase**: 63-adventure-runtime
- **Goal**: Load fuzhe.json (fuzhe_mini.json doesn't exist yet), verify trigger chains fire correctly, room transitions update state, reveal gates enforce visibility, and consequence chains produce expected state changes.
- **Depends on**: Phase 62 (Session Orchestrator)
- **Requirements**: ADV-01, ADV-02, ADV-03, ADV-04

## What Exists

### Source Files
| File | Purpose |
|------|---------|
| `src/dm_bot/adventures/fuzhe.json` | Full fuzhe module with 14 triggers, 9 locations |
| `src/dm_bot/adventures/trigger_engine.py` | Trigger execution engine (139 lines) |
| `src/dm_bot/adventures/models.py` | AdventurePackage, AdventureScene, AdventureLocation, AdventureTrigger, TriggerCondition, TriggerEffect models |
| `src/dm_bot/adventures/loader.py` | `load_adventure(adventure_id)` function |
| `src/dm_bot/orchestrator/gameplay.py` | GameplayOrchestrator with adventure state management |

### Key Models
```python
# AdventurePackage validates:
# - start_scene_id must reference existing scene
# - start_location_id must reference existing location (if locations defined)
# - location connections must reference valid locations
# - story_node_id must reference valid node (if story_nodes defined)

# Trigger engine handles:
# - event_kind: "action", "roll", or "chain"
# - conditions: location_id, pending_roll_id, state_matches, required_clues, min_total, max_total
# - effects: set_module_state, increment_module_state, move_location, move_story_node, add_clue, record_knowledge, clear_pending_roll
```

### Existing Tests
| File | Coverage |
|------|----------|
| `tests/test_adventure_loader.py` | Load mad_mansion, starter_crypt; AdventurePackage validation |
| `tests/test_gameplay_integration.py` | GameplayOrchestrator, scene transitions, manual roll triggers |

## Critical Gap

**fuzhe_mini.json does NOT exist** in `src/dm_bot/adventures/`.

The test-module-design.md describes a 4-node vertical slice for deterministic testing:
- `car_crash_intersection` (entry)
- `mystery_forum` (investigation)
- `wetland_gate` (pivot/combat)
- `wetland_ambush` (event)

But this file was never created. For Phase 63, we will use **fuzhe.json** directly since:
1. It has 14 triggers covering all requirement patterns
2. It has 9 locations covering room transition requirements
3. It has proper state_fields and reveal policies

## Test Gap Analysis

Per test-coverage-survey.md:
> "trigger engine lightly tested"

Current test_gameplay_integration.py tests:
- `test_manual_roll_applies_trigger_consequences()` - tests mad_mansion trigger chain
- Missing: explicit trigger condition tests (roll success/fail branches, state_matches, location_id)

## Requirements Coverage

| Requirement | What to Test |
|-------------|--------------|
| ADV-01 | `load_adventure("fuzhe")` returns valid AdventurePackage, 14 triggers, 9 locations, state_fields |
| ADV-02 | Trigger chains fire on conditions: action triggers fire on action_id match; roll triggers fire on min_total/max_total; state_matches conditions |
| ADV-03 | `adventure_snapshot()["public"]["state"]` only contains "discoverable"/"public" fields; "gm_only" fields hidden |
| ADV-04 | `set_adventure_location("wetland_gate")` updates both `location_id` and `scene_id`; keyword navigation "进入湿地公园" triggers location change |

## Key Methods to Test

```python
# In GameplayOrchestrator:
load_adventure(adventure)           # ADV-01
set_adventure_location(location_id) # ADV-04 - updates location_id AND scene_id
adventure_snapshot()                # ADV-03 - public_state filtering
evaluate_scene_action(content)      # ADV-02 - trigger chain execution
resolve_manual_roll(...)            # ADV-02 - roll trigger consequences

# In TriggerEngine:
execute(package, adventure_state, event, trigger_ids)  # ADV-02

# In AdventurePackage:
public_state(module_state)  # ADV-03 - filters by visibility
gm_state(module_state)      # ADV-03 - returns all fields
```

## Approach

1. Create `tests/test_fuzhe_adventure_loader.py` - Verify fuzhe loads correctly
2. Create `tests/test_trigger_chains.py` - Test specific trigger chains fire with correct state changes
3. Create `tests/test_room_transitions_and_reveals.py` - Test ADV-03 (reveals) and ADV-04 (transitions)

All tests use existing FakeInteraction/model mock patterns from test_gameplay_integration.py.
