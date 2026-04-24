---
phase: 02-fork-and-switch-focus
plan: "01"
subsystem: runtime
tags: [fork, switch-focus, cross-cut, scene-lifecycle, multi-scene]

# Dependency graph
requires:
  - phase: 01-scene-lifecycle
    provides: SceneLifecycle enum, PlayerFocusScope enum, CampaignSession base model
provides:
  - fork() runtime operation with max-2-open-scenes validation
  - switch_focus() with cross-cut signal detection for narrator
  - OpenScene lightweight scene tracking model
  - ForkResult and SwitchFocusResult models
affects:
  - Phase 3 batch-and-merge (builds on fork/switch infrastructure)
  - Narration system (consumes cross_cut_signal)

# Tech tracking
tech-stack:
  added: [OpenScene, ForkResult, SwitchFocusResult, ForkError]
  patterns:
    - fork() creates scene WITHOUT changing focus (decoupled operation)
    - cross-cut signal on PUBLISHED->COLLECTING transition
    - max-2-open-scenes policy enforced at fork() time

key-files:
  created: []
  modified:
    - src/dm_bot/orchestrator/session_store.py
    - src/dm_bot/gameplay/modes.py
    - tests/test_multi_user_session.py

key-decisions:
  - "fork() is decoupled from focus change - does NOT auto-switch any player's focus"
  - "cross-cut signal triggers on PUBLISHED->COLLECTING transition (resolved scene to open scene)"
  - "Runtime enforces max-2-open-scenes via fork() validation"

patterns-established:
  - "Lightweight scene tracking via open_scenes dict[str, OpenScene]"
  - "Player focus tracking via focused_scene dict[str, str]"

requirements-completed: [RTR-01, RTR-02, RTR-03]

# Metrics
duration: 5 min
completed: 2026-04-11
---

# Phase 2 Plan 1: Fork and Switch Focus Summary

**fork() and switch_focus() runtime operations with cross-cut signaling and max-2-open-scenes policy enforcement**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-11T07:13:23Z
- **Completed:** 2026-04-11T07:18:41Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- fork() creates new scenes without changing any player's focus (decoupled operation)
- Runtime enforces max-2-open-scenes policy at fork() time
- Runtime enforces player-can-only-be-in-one-open-scene policy
- switch_focus() emits cross_cut signal when switching from PUBLISHED to COLLECTING
- GameModeState exposes cross_cut_* fields for narrator consumption

## Task Commits

Each task was committed atomically:

1. **Task 1: Add open scene tracking and fork() method** - `32a85c4` (feat)
2. **Task 2: Implement switch_focus() with cross-cut signaling** - `48fc9c9` (feat)
3. **Task 3: Lock behavior with regression tests** - `194a515` (test)

**Plan metadata:** (docs: complete plan) - to be committed after SUMMARY

## Files Created/Modified
- `src/dm_bot/orchestrator/session_store.py` - OpenScene, ForkResult, SwitchFocusResult, ForkError models; fork() and switch_focus() methods
- `src/dm_bot/gameplay/modes.py` - cross_cut_signal, cross_cut_from_scene, cross_cut_to_scene fields on GameModeState
- `tests/test_multi_user_session.py` - 8 new tests for fork/switch behavior

## Decisions Made

- Used PUBLISHED (not RESOLVED) for resolved scene state - matches existing SceneLifecycle enum
- fork() does NOT auto-switch player focus - focus change requires explicit switch_focus() call
- cross-cut signal only on PUBLISHED->COLLECTING (resolved->open) transition

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## Next Phase Readiness

Phase 3 (Batch and Merge) can now build on fork/switch infrastructure:
- fork() creates scenes for batch collection
- switch_focus() handles player attention switching
- cross_cut_signal available for narrator cutaway narration

---
*Phase: 02-fork-and-switch-focus*
*Completed: 2026-04-11*
