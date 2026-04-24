---
phase: 01-scene-lifecycle
plan: "01"
subsystem: runtime
tags: [scene-lifecycle, player-focus, session-state, batch-resolution]

# Dependency graph
requires: []
provides:
  - Explicit SceneLifecycle enum (COLLECTING, LOCKED, RESOLVING, PUBLISHED)
  - Explicit PlayerFocusScope enum (SINGLE, SHARED, KEEPER_ONLY)
  - Lifecycle-aware session state in CampaignSession
  - Gameplay-mode lifecycle/focus tracking in GameModeState
  - Structured lifecycle context via get_lifecycle_context()
affects: [01-scene-lifecycle/02, 01-scene-lifecycle/03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Canonical runtime models over implicit conventions
    - Lifecycle state machine with valid transitions
    - Separation of scene lifecycle and player focus as distinct concepts

key-files:
  created: []
  modified:
    - src/dm_bot/orchestrator/session_store.py
    - src/dm_bot/gameplay/modes.py
    - tests/test_multi_user_session.py

key-decisions:
  - "SceneLifecycle and PlayerFocusScope are separate enums, not collapsed into one field"
  - "Valid lifecycle transitions follow COLLECTING -> LOCKED -> RESOLVING -> PUBLISHED state machine"
  - "GameModeState defaults preserve single-scene backward compatibility"

patterns-established:
  - "Scene lifecycle is a first-class runtime model, not inferred from message timing"
  - "Player focus scope is tracked independently from scene lifecycle"
  - "Lifecycle state is serialized/deserialized with session state for persistence"

requirements-completed: [RTR-01, RTR-02]

# Metrics
duration: 7 min
completed: 2026-04-11
---

# Phase 1 Plan 1: Scene Lifecycle Models Summary

**Explicit scene lifecycle and player focus models as canonical runtime state, with structured state machine transitions and backward-compatible defaults**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-11T02:56:28Z
- **Completed:** 2026-04-11T03:03:52Z
- **Tasks:** 3 completed
- **Files modified:** 3

## Accomplishments

- Introduced explicit `SceneLifecycle` enum with states: COLLECTING, LOCKED, RESOLVING, PUBLISHED
- Introduced explicit `PlayerFocusScope` enum with scopes: SINGLE, SHARED, KEEPER_ONLY
- Added lifecycle-aware state to `CampaignSession` with transition methods
- Enhanced `GameModeState` with lifecycle/focus fields and `sync_from_session()` method
- Ensured proper serialization/deserialization in `dump_sessions()`/`load_sessions()`
- Added 7 regression tests covering lifecycle transitions and distinctness invariant
- All 29 tests pass (22 existing + 7 new)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add explicit scene lifecycle and focus models** - `eba7a8b` (feat)
2. **Task 2: Integrate lifecycle state into gameplay runtime** - (integrated via Task 1 changes)
3. **Task 3: Lock the behavior with regression tests** - `f5da336` (test)

**Plan metadata:** (included in final commit)

## Files Created/Modified

- `src/dm_bot/orchestrator/session_store.py` - Added SceneLifecycle enum, PlayerFocusScope enum, lifecycle fields and methods to CampaignSession
- `src/dm_bot/gameplay/modes.py` - Enhanced GameModeState with scene_lifecycle and player_focus fields, sync method, and helper predicates
- `tests/test_multi_user_session.py` - Added 7 regression tests for lifecycle model

## Decisions Made

- Used separate enums for scene lifecycle and player focus rather than a single combined field, ensuring RTR-01 requirement that they remain distinct
- Implemented valid transition state machine (COLLECTING -> LOCKED -> RESOLVING -> PUBLISHED) rather than allowing arbitrary transitions
- Default lifecycle is COLLECTING (open for action submission) and default focus is SINGLE (one actor at a time), preserving existing single-scene behavior

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Scene lifecycle and player focus models are in place and tested
- Phase 2 (Fork And Switch Focus) can build on these canonical models
- No blockers identified

---
*Phase: 01-scene-lifecycle*
*Completed: 2026-04-11*
