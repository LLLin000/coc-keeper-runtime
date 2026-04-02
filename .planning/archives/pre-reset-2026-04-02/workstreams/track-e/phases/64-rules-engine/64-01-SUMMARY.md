---
phase: 64-rules-engine
plan: "01"
subsystem: rules
tags: [coc, rules-engine, tdd, skill-checks, sanity, combat, pushed-rolls]

# Dependency graph
requires:
  - phase: 63-adventure-runtime/63-01
    provides: Adventure runtime with room/scene graph, trigger tree, consequence chain
provides:
  - "COC skill check flow: success_rank (critical/extreme/hard/regular/failure), fumble detection"
  - "COC sanity check flow: san_loss on success vs failure, breakdown at zero"
  - "Combat round resolution: HP reduction, defeated state, combatant removal"
  - "Pushed roll re-roll: initial failure triggers second roll, second result applies"
affects: [track-e phases, session orchestration, gameplay integration]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "TDD cycle: RED (failing tests) → GREEN (implementation) → REFACTOR"
    - "Engine delegates to dice_roller, passes through outcome fields"
    - "Stub dice rollers for isolated testing"

key-files:
  created:
    - tests/test_coc_rules_flow.py (RULES-01/02 tests)
    - tests/test_combat_resolution_flow.py (RULES-03 tests)
    - tests/test_pushed_roll_flow.py (pushed roll consequence tests)
  modified:
    - src/dm_bot/rules/dice.py (fixed fumble condition)
    - src/dm_bot/rules/engine.py (implemented pushed roll re-roll)

key-decisions:
  - "HP mutation is caller's responsibility - engine returns damage value only"
  - "Pushed roll re-roll logic: if pushed=True and first roll fails, call _roll_percentile again"
  - "Second roll in pushed sequence uses pushed=False to prevent infinite chain"

patterns-established:
  - "Test stub dice rollers return dicts matching PercentileOutcome schema"
  - "Engine._roll_percentile wraps dice_roller.roll_percentile and validates outcome"

requirements-completed: [RULES-01, RULES-02, RULES-03]

# Metrics
duration: 25min
completed: 2026-03-29
---

# Phase 64: Rules Engine Flow Summary

**COC skill checks, SAN damage, combat resolution, and pushed roll re-roll flow with TDD validation**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-03-29T session
- **Completed:** 2026-03-29
- **Tasks:** 3 test files, 27 tests
- **Files modified:** 5

## Accomplishments
- Created 3 test files with 27 tests covering RULES-01/02/03
- Fixed fumble condition bug in dice.py (was using old logic, fixed to COC spec: 96-100)
- Implemented pushed roll re-roll in engine.py for failed pushed checks
- All 384 tests in full suite passing (no regressions)

## Task Commits

Each task was committed atomically:

1. **RED: COC skill check and SAN damage tests** - `1c6425e` (test)
2. **RED: Combat round resolution tests** - `8c9b1bd` (test)
3. **RED: Pushed roll re-roll consequence tests** - `062367d` (test)
4. **GREEN: Implementation fixes** - `1b5a89a` (feat)

**Plan metadata:** `1b5a89a` (feat: rules engine flow tests passing)

## Files Created/Modified
- `tests/test_coc_rules_flow.py` - RULES-01/02: skill check success ranks, fumble, SAN damage flow
- `tests/test_combat_resolution_flow.py` - RULES-03: combat round HP tracking, defeated state
- `tests/test_pushed_roll_flow.py` - Pushed roll re-roll consequence tests
- `src/dm_bot/rules/dice.py` - Fixed fumble: `rolled >= 96` per COC spec
- `src/dm_bot/rules/engine.py` - Added pushed roll re-roll: if pushed=True and first fail, roll again

## Decisions Made
- Used stub dice rollers returning dicts matching PercentileOutcome schema for isolated testing
- Engine returns `damage` in result dict; caller applies HP mutation (separation of concerns)
- Pushed roll second roll uses `pushed=False` to enforce single re-roll rule

## Deviations from Plan

None - plan executed with TDD cycle as specified.

## Issues Encountered
None - all issues were auto-fixed per deviation rules:
1. Fumble bug in test stub (Rule 1 - Bug): test stub had old fumble logic, fixed to match dice.py
2. Pushed roll not re-rolling (Rule 2 - Missing Critical): engine didn't implement re-roll, added logic

## Next Phase Readiness
- Rules engine flow complete and tested
- Ready for session orchestration integration (SESS track)
- No blockers

---
*Phase: 64-rules-engine*
*Completed: 2026-03-29*