# Phase 71 Context

**Phase:** E71
**Milestone:** vE.2.2 — 统一 Scenario-Driven E2E 验证框架
**Created:** 2026-03-30

---

## What This Phase Does

Builds the failure classification system and contract-level scenario suites.

---

## Depends On

- **E70** must be complete: DSL parser, ArtifactWriter, ScenarioRunner wired

---

## Key Files to Read (from E70 output)

- `src/dm_bot/testing/scenario_runner.py` — updated with DSL + ArtifactWriter
- `src/dm_bot/testing/failure_taxonomy.py` — new (Task 1)
- `tests/scenarios/contract/` — directory for new scenarios
- `tests/orchestrator/test_visibility.py` — audit for redundancy

---

## Constraints

1. **All scenarios use `model_mode: fake_contract`** — no live AI, FastMock captures everything
2. **FailureCode must be imported by ScenarioRunner** — wire early
3. **Visibility tests: check test_visibility.py first** — don't duplicate
4. **AI contract: inspect captured router_requests / narrator_requests** — FastMock captures these
5. **VCR cassettes: optional** — only if Ollama is live; document if skipped

---

## Out of Scope

- Acceptance scenarios (E72)
- CI configuration (E72)
