---
phase: E86
plan: 01
type: execute
status: complete
completed_at: 2026-03-31
---

## E86-01: Scenario Runner Assertion Fix

### Objective
Fix scenario runner's assertion logic so scenarios actually fail when assertions are not met.

### What Was Built

| File | Change |
|------|--------|
| `src/dm_bot/testing/scenario_runner.py` | Added `_evaluate_scenario_assertions()` method, fixed phase_timeline collection, replaced broken post-loop block |
| `tests/test_scenarios.py` | Added 12 unit tests for assertion evaluation |

### Tasks Completed

| Task | Status | Details |
|------|--------|---------|
| Task 1: Add `_evaluate_scenario_assertions()` | ✅ | Evaluates phase_timeline, final_phase, state_campaign_members, state_no_duplicate_members, visible_public_must_include, visible_kp_must_include, visible_player_forbidden |
| Task 2: Fix phase_timeline collection | ✅ | Captures initial phase before loop, tracks phase changes after each step |
| Task 3: Add assertion tests | ✅ | 12 tests covering mismatch detection, pass cases, visibility, state, duplicates |

### Requirements Addressed

| Requirement | Status |
|-------------|--------|
| ASSERT-01: phase_timeline properly evaluated | ✅ |
| ASSERT-02: state assertions evaluated | ✅ |
| ASSERT-03: visibility assertions evaluated | ✅ |
| ASSERT-04: scenarios fail when assertions not met | ✅ |

### Verification

- `uv run pytest tests/test_scenarios.py::TestScenarioAssertions -v` — 12 passed
- `uv run pytest -q` — 833 passed, 13 failed (scenario failures now properly detected)
- Scenario failures are now legitimate: PHASE_TRANSITION_MISMATCH, VISIBILITY_LEAK, etc.

### Key Changes

1. **`_evaluate_scenario_assertions()`** — New method that takes `(Scenario, phase_timeline, final_state, all_outputs)` and returns `Failure | None`
2. **Phase timeline fix** — Initial phase captured after `driver.start()`, changes tracked after each step
3. **Broken post-loop removed** — Lines 134-150 replaced with scenario-level assertion evaluation

### Self-Check

- [x] All tasks executed
- [x] Each task committed individually
- [x] SUMMARY.md created
- [x] STATE.md updated
- [x] No regressions in non-scenario tests
