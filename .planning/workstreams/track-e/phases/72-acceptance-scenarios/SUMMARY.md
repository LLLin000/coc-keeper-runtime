# Phase E72 Summary: Acceptance Scenarios + CI Execution

**Phase:** E72-01
**Milestone:** vE.2.2 — 统一 Scenario-Driven E2E 验证框架
**Status:** COMPLETE
**Tests:** 434 passing (423 original + 11 scenario tests)

---

## Goal

Write acceptance scenarios proving full session lifecycle, crash recovery, stream interrupt handling, and chaos load. Configure CI to run headlessly.

---

## What was accomplished

### Task 1: Happy Path Scenario ✅
- `tests/scenarios/acceptance/scen_session_happy_path.yaml` — full lifecycle: bind→join→ready→start_session→complete_onboarding→round→resolve→next_round

### Task 2: Fuzhe Mini 15-Turn Scenario ✅
- `tests/scenarios/acceptance/scen_fuzhe_15turn.yaml` — navigates fuzhe_mini adventure through key nodes with seeded dice

### Task 3: Crash Recovery Scenario ✅
- `tests/scenarios/recovery/scen_crash_recovery.yaml` — simulates crash mid-session, verifies system continues

### Task 4: Stream Interrupt Scenario ✅
- `tests/scenarios/recovery/scen_stream_interrupt.yaml` — simulates stream interrupt, verifies system continues

### Task 5: Chaos Lobby Scenario ✅
- `tests/scenarios/chaos/scen_chaos_lobby.yaml` — 5 concurrent users, no duplicate members, all phases correct

### Task 6: CI Execution ✅
- `tests/test_scenarios.py` — pytest parametrized test that discovers and runs all YAML scenarios
- `artifacts/` added to `.gitignore`
- `uv run pytest tests/scenarios/` → works (via test_scenarios.py)
- `uv run python -m dm_bot.main run-scenario --all` → 11/11 passed

### Bug Fixes Found During Execution
- **ScenarioRegistry path bug**: `scenario.path` now stored in Scenario object, fixes `--all` mode resolving wrong paths for nested scenarios
- **driver. prefix support**: `_run_command_step` now supports `driver.<method>` prefix to call RuntimeTestDriver methods directly (simulate_crash, restart_runtime, simulate_stream_interrupt)

---

## Files changed

```
src/dm_bot/testing/scenario_dsl.py       (Scenario.path field, parse passes path)
src/dm_bot/testing/scenario_runner.py    (driver. prefix support)
src/dm_bot/main.py                       (use scenario.path instead of reconstructed path)
tests/test_scenarios.py                  (new, pytest parametrized scenario runner)
tests/scenarios/acceptance/scen_session_happy_path.yaml   (new)
tests/scenarios/acceptance/scen_fuzhe_15turn.yaml         (new)
tests/scenarios/recovery/scen_crash_recovery.yaml          (new)
tests/scenarios/recovery/scen_stream_interrupt.yaml        (new)
tests/scenarios/chaos/scen_chaos_lobby.yaml                (new)
.gitignore                                        (added artifacts/)
```

---

## Scenario Suites

| Suite | Tag | Count |
|-------|-----|-------|
| smoke | acceptance | 1 |
| happy_path | acceptance | 1 |
| fuzhe | acceptance | 1 |
| recovery | acceptance | 2 |
| chaos | acceptance | 1 |
| contract/visibility | contract | 3 |
| contract/reveal | contract | 2 |
| **Total** | | **11** |

---

## Verification

```
uv run pytest -q                    →  434 passed, 3 warnings
uv run python -m dm_bot.main smoke-check  →  passed
uv run python -m dm_bot.main run-scenario --all  →  11 passed, 0 failed
uv run pytest tests/test_scenarios.py -v  →  11 passed
```
