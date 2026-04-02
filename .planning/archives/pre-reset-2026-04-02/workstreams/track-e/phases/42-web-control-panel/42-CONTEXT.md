# Phase 42: Web Control Panel - Context

**Completed:** 2026-03-28
**Status:** Implemented

## Outcome

This phase added the first local polling-based operations panel so the operator can see bot/API/model/smoke-check state and trigger lifecycle actions from one local page.

## Delivered

- `GET /control-panel` local web UI
- `GET /control-panel/state`
- `POST /control-panel/actions/{action}`
- action coverage for bot/api/system restart, stop/start, sync, and smoke-check

## Notes

- The panel is intentionally operational, not a GM gameplay panel.
- The page uses polling instead of SSE/WebSocket in this milestone.
