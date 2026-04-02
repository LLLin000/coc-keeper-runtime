---
phase: 66-model-router
plan: "01"
subsystem: router
tags: [router, intent-classification, message-buffer, turn-plan, track-e]
dependency_graph:
  requires: ["60-test-infrastructure/60-01"]
  provides: ["router-flow-ROUTER-01", "router-flow-ROUTER-02", "router-flow-ROUTER-03"]
  affects: ["orchestrator", "discord-bot", "session-management"]
tech_stack:
  added: [pytest-asyncio]
  patterns: [TDD, RED-GREEN cycle, async mock patterns]
key_files:
  created:
    - tests/test_router_service_flow.py
    - tests/test_message_buffer_flow.py
    - tests/test_intent_classification_flow.py
  modified: []
decisions:
  - "RouterService.route() uses AsyncMock for client.call_router to isolate from model"
  - "MessageBuffer tested directly without async or model dependencies"
  - "Intent functions (should_buffer_intent, get_intent_priority) tested as pure functions"
metrics:
  duration: "~15 minutes"
  completed_date: "2026-03-29"
---

# Phase 66-01 Plan Summary: Model / Router Flow

**One-liner:** Router flow tests covering TurnPlan generation, message buffering, and intent classification - all 33 tests passing.

## Overview

Phase E66 validates the intent classification, turn plan generation, and message buffering flows for the COC Keeper runtime router layer. Tests cover ROUTER-01 (RouterService TurnPlan), ROUTER-02 (MessageBuffer), and ROUTER-03 (intent classification).

## What Was Done

### ROUTER-01: RouterService TurnPlan Generation

Created `tests/test_router_service_flow.py` with 6 tests validating:
- `RouterService.route()` returns valid TurnPlan with mode, tool_calls, narration_brief
- Invalid JSON response raises `RouterError`
- Missing required fields raise `RouterError`
- String tool_calls are normalized to dict format
- speaker_hints populated from model response
- Envelope fields passed correctly to model

### ROUTER-02: MessageBuffer Flow

Created `tests/test_message_buffer_flow.py` with 10 tests validating:
- `buffer_message()` returns True on success
- `get_buffered_messages()` retrieves all buffered messages for channel
- `release_buffered_messages()` clears buffer atomically
- `clear_buffer()` removes without returning
- `has_buffered_messages()` correct boolean state
- `format_buffered_message_summary()` returns formatted string
- `get_buffer_summary()` returns dict with counts and timestamps
- Channel isolation - different channels don't share buffers

### ROUTER-03: Intent Classification

Created `tests/test_intent_classification_flow.py` with 17 tests validating:
- `should_buffer_intent()` correctly buffers PLAYER_ACTION during scene_round_resolving
- `should_buffer_intent()` does NOT buffer ADMIN_ACTION during scene_round_resolving
- `should_buffer_intent()` correctly handles combat phase (PLAYER_ACTION not buffered, OOC buffered)
- `should_buffer_intent()` returns False for other phases (scene_round_open, lobby)
- `get_intent_priority()` returns correct priorities by phase (10 for highest priority intents)
- `get_handling_decision()` returns appropriate decision strings
- `MessageIntentMetadata` structure with all required fields
- All `MessageIntent` enum values correctly defined

## Test Results

```
tests/test_router_service_flow.py     6 passed
tests/test_message_buffer_flow.py    10 passed
tests/test_intent_classification_flow.py 17 passed
Total: 33 passed in 0.26s
```

## Commits

| Hash   | Message |
|--------|---------|
| a27811f | test(router-66): add router service TurnPlan generation tests (ROUTER-01) |
| 1757c7e | test(router-66): add message buffering flow tests (ROUTER-02) |
| 31b4412 | test(router-66): add intent classification flow tests (ROUTER-03) |

## Deviations from Plan

**None** - plan executed exactly as written.

**Note:** Implementation was already in place (router/service.py, router/intent.py, router/message_buffer.py). Tests passed on first run, indicating GREEN phase directly. This is expected when implementing tests for existing functionality.

## Verification Commands

```bash
# Run router flow tests
uv run pytest tests/test_router_service_flow.py tests/test_message_buffer_flow.py tests/test_intent_classification_flow.py -v

# Full test suite
uv run pytest -q
```

## Self-Check

- [x] All 3 test files created with minimum required lines (159, 130, 127 lines)
- [x] All 33 router flow tests passing
- [x] All commits made with correct format
- [x] No regressions in existing tests (323 passed, 2 pre-existing failures unrelated to this phase)
