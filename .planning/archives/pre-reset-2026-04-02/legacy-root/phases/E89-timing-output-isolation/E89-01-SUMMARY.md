---
phase: E89
plan: 01
status: complete
completed_at: "2026-04-01T00:21:00Z"
---

# Phase E89 Plan 01 Summary: Timing + Output Isolation

## What Was Done

Fixed two critical issues in the scenario runner that made debugging impossible:

### 1. Duration Measurement (Duration always 0ms)

**Problem:** `StepResult.duration_ms` field existed but was never set — all step executions defaulted to 0.0.

**Fix:** Added `time.monotonic()` timing around step execution in `scenario_runner.py`:
- Imported `time` module
- Wrapped `await self._run_command_step()` and `await self._run_message_step()` with timing
- Set `result.duration_ms = (time.monotonic() - step_start) * 1000` after each step
- Assert-only steps get `duration_ms=0.0` (they don't execute anything)

**File:** `src/dm_bot/testing/scenario_runner.py`

### 2. Output Isolation (Cumulative outputs across steps)

**Problem:** `emitted_outputs` captured the entire `_output_records` list, so step 10 contained outputs from steps 0-9.

**Fix:** Added `output_start` index capture before each step and sliced after:
- `runtime_driver.py run_command()`: Added `output_start = len(self._output_records)` and changed all `list(self._output_records)` to `list(self._output_records[output_start:])`
- `scenario_runner.py _run_command_step()`: Same pattern for driver method branch
- `send_message()` already did this correctly — used as the pattern

**Files:** `src/dm_bot/testing/runtime_driver.py`, `src/dm_bot/testing/scenario_runner.py`

### 3. New Tests

Added 4 new tests to verify the fixes:
- `test_step_duration_is_measured` — verifies duration_ms >= 0 for all steps
- `test_assert_step_has_zero_duration` — verifies assert-only steps report 0.0
- `test_step_outputs_are_isolated` — verifies no cross-step output contamination
- `test_driver_output_isolation_standalone` — verifies driver-level isolation

**File:** `tests/test_scenario_runner.py`

## Test Results

- **14/14** `test_scenario_runner.py` tests pass (10 existing + 4 new)
- **842/855** total tests pass (13 pre-existing failures from E86/E87/E88 scope)
- No regressions introduced

## Key Decisions

- Used `time.monotonic()` instead of `time.time()` — immune to system clock changes, standard for elapsed time
- Duration test asserts `>= 0` not `> 0` — sub-millisecond operations on Windows may register as 0
- Output isolation uses index slicing pattern already established in `send_message()`
