---
phase: "01"
plan: "03"
subsystem: "dual-model-control"
tags:
  - router
  - narrator
  - orchestration
  - ollama
duration: "active session"
completed: "2026-03-27"
requirements-completed:
  - ORCH-01
  - ORCH-02
  - ORCH-03
  - ORCH-04
  - OPS-03
key-files:
  created:
    - src/dm_bot/router/contracts.py
    - src/dm_bot/router/service.py
    - src/dm_bot/narration/service.py
    - src/dm_bot/orchestrator/turn_runner.py
    - src/dm_bot/runtime/model_checks.py
    - tests/test_dual_model_orchestration.py
  modified:
    - src/dm_bot/runtime/health.py
---

# Phase 01 Plan 03: Dual-Model Control Summary

Implemented the local router-plus-narrator pipeline on top of the shared Ollama transport. The runtime now validates structured router output before orchestration, keeps narration generation separate from canonical state intent, and exposes model-slot readiness through the health workflow.

## What Changed

- Added strict router contracts in `src/dm_bot/router/contracts.py` for mode, tool calls, state intents, and narration brief.
- Added `RouterService` in `src/dm_bot/router/service.py` to call the router model and fail hard on malformed JSON or schema violations.
- Added `NarrationService` in `src/dm_bot/narration/service.py` to build a compact narration payload from player input, validated plan, state snapshot, and deterministic tool results.
- Added `TurnRunner` in `src/dm_bot/orchestrator/turn_runner.py` to join router and narrator without letting prose mutate canonical state.
- Added `src/dm_bot/runtime/model_checks.py` and wired `runtime/health.py` through it so router and narrator readiness are surfaced as distinct health slots.
- Added `tests/test_dual_model_orchestration.py` covering router contract validation, malformed router failure handling, compact narration payload boundaries, and model readiness reporting.

## Verification

- `uv run pytest tests/test_dual_model_orchestration.py -k "router or contract" -q`
- Result: `3 passed`
- `uv run pytest tests/test_dual_model_orchestration.py -q`
- Result: `5 passed`

## Deviations from Plan

None. The implementation stayed inside the planned module boundaries and reused the Plan `01-01` transport layer without introducing additional services or dependencies.

## Next Phase Readiness

Plan `01-02` can now bind Discord commands and deferred interactions to a stable `TurnRunner` instead of calling model clients directly. That keeps Discord integration as an adapter over a tested orchestration core.
