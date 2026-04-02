---
phase: 70-scenario-dsl-artifact-writer
plan: "01"
subsystem: testing
tags: [scenario, dsl, artifact, cli, testing]

# Dependency graph
requires:
  - phase: 69-scenario-runner
    provides: RuntimeTestDriver, ScenarioRunner, StepResult contract
provides:
  - Scenario DSL (YAML format) with parser and validator
  - ArtifactWriter for run artifacts (json + md)
  - run-scenario CLI command
  - model_mode strategy (fake_contract/recorded/live)
  - Initial state setup mechanism
  - Scenario registry for tests/scenarios/
affects: [71-failure-taxonomy, 72-acceptance-scenarios]

# Tech tracking
tech-stack:
  added: [orjson]
  patterns: [scenario-driven testing, artifact output, CLI subcommands]

key-files:
  created:
    - src/dm_bot/testing/scenario_dsl.py
    - src/dm_bot/testing/artifact_writer.py
    - tests/scenarios/acceptance/scen_smoke.yaml
  modified:
    - src/dm_bot/main.py
    - src/dm_bot/testing/scenario_runner.py
    - src/dm_bot/testing/runtime_driver.py

key-decisions:
  - "Used orjson for fast JSON serialization in ArtifactWriter"
  - "Made DSL parser backward compatible with E69 format for existing tests"
  - "model_mode: fake_contract as default for CI/fast runs"

patterns-established:
  - "Scenario DSL: structured YAML format for test scenarios"
  - "Artifact output: machine-readable + human-readable run records"
  - "CLI entry point: unified run-scenario command"

requirements-completed: []

# Metrics
duration: 35min
completed: 2026-03-30
---

# Phase 70 Plan 01: Scenario DSL + ArtifactWriter Summary

**YAML-based scenario DSL with ArtifactWriter and run-scenario CLI command for unified test execution**

## Performance

- **Duration:** 35 min
- **Started:** 2026-03-30T05:36:50Z
- **Completed:** 2026-03-30T06:11:00Z
- **Tasks:** 7
- **Files modified:** 6 files (3 created, 3 modified)

## Accomplishments
- Created Scenario DSL with Scenario dataclass, ScenarioParser, ScenarioValidator, and ScenarioRegistry
- Implemented ArtifactWriter that writes run.json, summary.md, timeline.json, outputs by audience, state files, and failure.json
- Added run-scenario CLI subcommand supporting --scenario, --suite, --all, --fail-fast, --model-mode, --seed
- Implemented model_mode strategy: fake_contract (default), recorded, live
- Documented initial state setup: in-memory SQLite by default, seeded dice support
- Updated ScenarioRunner to use DSL parser and ArtifactWriter
- Created smoke test scenario at tests/scenarios/acceptance/scen_smoke.yaml

## Task Commits

Each task was committed atomically:

1. **Task 1: Define and Implement Scenario DSL** - `4c10e53` (feat)
2. **Task 2: Implement ArtifactWriter** - `c4464f6` (feat)
3. **Task 3: Add run-scenario CLI Command** - `918b271` (feat)
4. **Task 4: Implement model_mode Strategy** - `9a3f97d` (feat)
5. **Task 5: Implement Initial State Setup Mechanism** - `9751552` (feat)
6. **Task 6: Wire ScenarioRunner to use DSL + ArtifactWriter + CLI** - `fd329d3` (feat)
7. **Task 7: Create Minimal Acceptance Scenario** - `602ad87` (feat)

**Plan metadata:** `1e6f0dd` (fix: backward compatibility)

## Files Created/Modified
- `src/dm_bot/testing/scenario_dsl.py` - Scenario DSL parser, validator, registry
- `src/dm_bot/testing/artifact_writer.py` - ArtifactWriter for run artifacts
- `src/dm_bot/main.py` - Added run-scenario CLI subcommand
- `src/dm_bot/testing/scenario_runner.py` - Wired to use DSL and ArtifactWriter
- `src/dm_bot/testing/runtime_driver.py` - Added model_mode support
- `tests/scenarios/acceptance/scen_smoke.yaml` - Smoke test scenario

## Decisions Made
- Used orjson for fast JSON serialization (already in dependencies)
- Made DSL parser backward compatible with E69 format (command key, assert without actor)
- model_mode defaults to fake_contract for CI compatibility

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed DSL parser to handle old test format**
- **Found during:** Task 7 (Smoke test run)
- **Issue:** Tests using old YAML format (command as key instead of action+name) were failing
- **Fix:** Made ScenarioParser and ScenarioValidator backward compatible with old format
- **Files modified:** src/dm_bot/testing/scenario_dsl.py
- **Verification:** All 418 tests pass
- **Committed in:** `1e6f0dd`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Backward compatibility fix was necessary to not break existing tests from E69.

## Issues Encountered
- None - all issues resolved during execution

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 70 complete, ready for E71 (Failure Taxonomy + Contract Scenarios)
- Scenario DSL and ArtifactWriter are in place
- CLI command working with --scenario, --suite, --all options
- Smoke test passes with 1 passed, 0 failed

---
*Phase: 70-scenario-dsl-artifact-writer*
*Completed: 2026-03-30*
