# Phase E77: Combat + SAN E2E Scenario Summary

**Plan:** E77-01  
**Phase:** E77  
**Subsystem:** Track E - Runtime Control  
**Tags:** [acceptance, combat, san, character_lifecycle]  

## Objective

Write E2E scenario validating combat → SAN → insanity chain.

## Critical Deliverables

| Deliverable | Status | Evidence |
|-------------|--------|----------|
| `tests/scenarios/acceptance/scen_combat_san.yaml` | ✅ PASSED | `run-scenario` passed |

## Verification

```
uv run python -m dm_bot.main run-scenario --scenario tests/scenarios/acceptance/scen_combat_san.yaml

Results: 1 passed, 0 failed
```

## One-Liner

Combat + SAN E2E scenario (scen_combat_san.yaml) validated — combat encounter → SAN loss → insanity triggers chain verified.

## Tech Stack

- **Pattern:** Acceptance test via scenario YAML
- **Test Runner:** `dm_bot.main run-scenario`
- **Fixtures:** fake_contract model, temp_sqlite DB, dice_seed=77

## Decisions

None — scenario implementation phase, no architectural decisions made.

## Deviations from Plan

None — plan executed exactly as written.

## Dependencies

- **Required:** E76 (completed)
- **Provides:** E78 depends on E77

## Completion

- **Completed:** 2026-03-31
- **Duration:** ~1 minute (test execution)
- **Status:** ✅ Complete

---

## Self-Check

- [x] `tests/scenarios/acceptance/scen_combat_san.yaml` exists
- [x] `run-scenario` returns PASSED
- [x] Phase directory created at `.planning/phases/77-combat-san-e2e/`
- [x] All critical deliverables listed above
