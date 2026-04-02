# Phase 41: CLI Control Surface - Context

**Completed:** 2026-03-28
**Status:** Implemented

## Outcome

This phase exposed the shared runtime control service through CLI entry points so operators can inspect state and run restart/bootstrap workflows from one place.

## Delivered

- `uv run python -m dm_bot.main control-status`
- `uv run python -m dm_bot.main run-control-panel`
- retained `smoke-check` and `restart-system` as the canonical operator actions

## Notes

- The CLI layer stays thin and delegates lifecycle behavior to `RuntimeControlService`.
- This phase does not own gameplay or Discord command semantics.
