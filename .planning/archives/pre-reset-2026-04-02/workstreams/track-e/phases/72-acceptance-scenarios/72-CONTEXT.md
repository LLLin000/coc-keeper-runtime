# Phase 72 Context

**Phase:** E72
**Milestone:** vE.2.2 — 统一 Scenario-Driven E2E 验证框架
**Created:** 2026-03-30

---

## What This Phase Does

Writes the acceptance-level scenarios (happy path, fuzhe_15turn, crash recovery, chaos lobby) and configures CI.

---

## Depends On

- **E71** must be complete: FailureCode, contract scenarios, VCR cassettes (if any)

---

## Key Files to Read (from E71 output)

- `tests/scenarios/contract/` — reference for scenario structure
- `src/dm_bot/testing/runtime_driver.py` — all driver methods including `simulate_crash()`, `simulate_stream_interrupt()`
- `src/dm_bot/adventures/fuzhe_mini.json` — adventure fixture

---

## Constraints

1. **All scenarios must pass in headless CI** — no live Discord, no live AI
2. **Deterministic by default** — use `dice_seed` for reproducible runs
3. **fuzhe_mini must be ready** — if E69 fuzhe_mini is delayed, use fuzhe.json with explicit 4-node scope
4. **Timeout: 60s per scenario** — long enough for 15-turn, not so long CI hangs
5. **Artifacts gitignored** — don't commit test artifacts

---

## Out of Scope

None — this is the final phase.

---

## Final Delivery Gate

When E72 is complete, the following must ALL be true:
- `uv run pytest tests/scenarios/ -v` → all pass
- `uv run python -m dm_bot.main run-scenario --all` → all pass
- `uv run python -m dm_bot.main smoke-check` → pass
- `uv run pytest -q` → 408+ pass (existing tests + new scenarios)
