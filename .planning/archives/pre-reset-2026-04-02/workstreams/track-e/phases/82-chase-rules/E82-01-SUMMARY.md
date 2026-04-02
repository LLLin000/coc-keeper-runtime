# Phase E82: Chase Rules Implementation Summary

## Phase Information

| Field | Value |
|-------|-------|
| Phase | E82-chase-rules |
| Plan | 01 |
| Status | **COMPLETE** |
| Started | 2026-03-31T12:32:00Z |
| Duration | ~30 minutes |
| Requirements | CHASE-01, CHASE-02, CHASE-03, CHASE-04, CHASE-05 |

## Objective

Implement COC 7e chase mechanics including pursuer/fleeer roles, CON rolls, and obstacle resolution for pursuit and escape scenarios.

## Deliverables

### Artifacts Created

| Artifact | Lines | Status |
|----------|-------|--------|
| `src/dm_bot/rules/coc/chase.py` | ~400 | ✅ Complete |
| `src/dm_bot/gameplay/chase.py` | ~150 | ✅ Complete |
| `tests/rules/coc/test_chase.py` | ~250 | ✅ Complete |
| `tests/scenarios/acceptance/scen_chase.yaml` | ~100 | ✅ Complete |
| `src/dm_bot/testing/runtime_driver.py` | +220 | ✅ Modified |

### Core Models

**ChaseEncounter** - Main chase state container:
- Participants (fleeers and pursuers)
- Locations (with entry/exit obstacles)
- Round resolution with CON checks
- End conditions (escape, capture)

**ChaseParticipant** - Individual in chase:
- CON-based endurance checks
- DEX-based movement order
- Exhaustion state tracking
- Movement rate (reduced when exhausted)

**ChaseObstacle** - Barrier requiring skill checks:
- Skill required (climb, jump, dodge, etc.)
- Difficulty (regular, hard, extreme)
- Failure effect (fall_back, damage, stuck, slow)

**ChaseLocation** - Chase space:
- Entry/exit obstacles
- End location marking
- Dangerous location flag

## Implementation Details

### Chase Round Resolution

1. **CON Checks**: Each participant rolls CON × 5 or less to avoid exhaustion
2. **Fleeer Movement**: Active fleeers move forward in DEX order
3. **Pursuer Movement**: Pursuers move to close distance to nearest fleeer
4. **End Conditions**: Check for escape (fleeer reaches end) or capture (pursuer catches fleeer)

### RuntimeTestDriver Integration

Added chase methods:
- `start_chase(fleeer_ids, pursuer_ids, locations)` - Start a new chase
- `resolve_chase_round()` - Resolve one round
- `get_chase_status()` - Get current state
- `end_chase()` - End and get final result

## Test Results

```
21 passed in 0.18s
- TestChaseParticipant: 5 tests
- TestChaseEncounter: 7 tests
- TestChaseObstacles: 4 tests
- TestChaseLocation: 3 tests
- TestChaseIntegration: 2 tests
```

## Deviation Notes

Fixed a typo in plan code: `dice_rolls or {}n` → `dice_rolls or {}` (line 304 of plan).

## Known Issues

Pre-existing test failures unrelated to this phase:
- `test_armor_piercing_bypasses_armor` - Pre-existing bug in original combat.py
- Archive persistence tests - Pre-existing issues

## Decisions Made

1. **Exhaustion penalty**: Exhausted participants get MOV - 1 (minimum 1)
2. **Movement resolution**: Fleeers move first (they're the active party), then pursuers
3. **Direction logic**: Pursuers move towards nearest fleeer; if tied, move forward

## Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| CHASE-01: Chase Data Models | ✅ Complete | ChaseEncounter, ChaseParticipant, ChaseLocation, ChaseObstacle |
| CHASE-02: CON Check System | ✅ Complete | CON roll each round, exhaustion on failure, MOV penalty |
| CHASE-03: Movement System | ✅ Complete | Fleeers move first (DEX order), pursuers close distance |
| CHASE-04: Obstacle Resolution | ✅ Complete | ChaseObstacle with skill/difficulty/failure_effect |
| CHASE-05: End Conditions | ✅ Complete | Escape (fleeer reaches end), capture (pursuer catches fleeer) |

## Files Modified/Created

| File | Change |
|------|--------|
| `src/dm_bot/rules/coc/chase.py` | New - Chase system models |
| `src/dm_bot/gameplay/chase.py` | New - GameplayChaseManager for session integration |
| `src/dm_bot/testing/runtime_driver.py` | Added chase methods (start_chase, resolve_chase_round, get_chase_status, end_chase) |
| `tests/rules/coc/test_chase.py` | New - 21 unit tests |
| `tests/scenarios/acceptance/scen_chase.yaml` | New - E2E chase scenario |

---

*Phase E82 execution complete - 2026-03-31*
