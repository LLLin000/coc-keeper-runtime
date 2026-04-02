# Phase 70 Context

**Phase:** E70
**Milestone:** vE.2.2 — 统一 Scenario-Driven E2E 验证框架
**Created:** 2026-03-30

---

## What This Phase Does

Formalizes the Scenario DSL, implements full artifact output, adds the CLI entry point, and defines model_mode and initial state strategy.

---

## Depends On

- **E69** must be complete: `RuntimeTestDriver`, `ScenarioRunner`, `StepResult` contract, `SeededDiceRoller`, `fuzhe_mini.json`

---

## Key Files to Read (from E69 output)

After E69 completes, read:
- `src/dm_bot/testing/runtime_driver.py` — RuntimeTestDriver interface
- `src/dm_bot/testing/scenario_runner.py` — basic ScenarioRunner
- `src/dm_bot/testing/step_result.py` — StepResult dataclass
- `tests/scenarios/acceptance/scen_smoke.yaml` — minimal scenario example

---

## Constraints

1. **Don't re-implement RuntimeTestDriver** — import from E69's `testing/` module
2. **Scenario DSL must be parseable by Pydantic/dataclass** — not raw dict
3. **Artifacts go to `artifacts/scenarios/<id>/<timestamp>/`** — gitignored
4. **`fake_contract` is the default** — live Ollama only for `model_mode: live`
5. **CLI must work headlessly** — no Discord, no GUI, no browser

---

## Out of Scope

- New scenarios (E71/E72)
- VCR cassette recording (E71)
- CI full configuration (E72 — final polish)
