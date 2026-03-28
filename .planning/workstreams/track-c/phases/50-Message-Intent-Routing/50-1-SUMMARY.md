---
phase: 50
plan: Message-Intent-Routing
subsystem: discord-interaction
tags: [intent-classification, message-routing, phase-dependent, buffering]
dependency_graph:
  requires: [Phase-47-Session-Phases, Phase-49-Scene-Round-Collection]
  provides: [intent-classification, phase-dependent-handling, message-buffering]
  affects: [turn-pipeline, message-flow, scene-round-integration]
tech_stack:
  added: [IntentClassifier, IntentHandlerRegistry, MessageBuffer]
  patterns: [strategy-pattern, phase-dependent-routing]
key_files:
  created:
    - src/dm_bot/router/intent.py
    - src/dm_bot/router/intent_classifier.py
    - src/dm_bot/router/intent_handler.py
    - src/dm_bot/router/message_buffer.py
    - tests/test_intent_routing.py
  modified:
    - src/dm_bot/router/contracts.py
    - src/dm_bot/router/service.py
    - src/dm_bot/router/__init__.py
    - src/dm_bot/orchestrator/turn_runner.py
    - src/dm_bot/orchestrator/turns.py
    - src/dm_bot/discord_bot/commands.py
    - src/dm_bot/main.py
    - pyproject.toml
    - tests/test_commands.py
    - tests/test_gameplay_integration.py
    - tests/test_natural_message_runtime.py
    - tests/test_phase2_integration.py
    - tests/test_turns.py
decisions:
  - combat player_action not buffered: Player actions process immediately during combat (priority 10), only OOC/social/rules are buffered
  - scene_round_resolving buffers all except admin: During resolution, all non-admin intents buffer until phase ends
  - intent classification uses router model: Reuses existing qwen3:1.7b router for classification to avoid additional model overhead
  - buffered messages released on next_round: Phase transition from resolving to open triggers buffer release with summary
metrics:
  duration: ~3 hours
  completed: 2026-03-29
---

# Phase 50: Message Intent Routing Summary

AI-powered message intent classification with phase-dependent handling and buffering during high-intensity session phases.

## What Was Built

### Intent Classification System
- **MessageIntent enum**: OOC, SOCIAL_IC, PLAYER_ACTION, RULES_QUERY, ADMIN_ACTION, UNKNOWN
- **IntentClassifier**: Uses router model (qwen3:1.7b) to classify each message's intent in real-time
- **Pydantic models**: IntentClassificationRequest, IntentClassificationResult, MessageIntentMetadata for typed contracts
- **Priority tables**: Phase-dependent intent priority maps (7 session phases x 6 intent types)

### Phase-Dependent Handling
- **SCENE_ROUND_OPEN**: Player actions prioritized (10), OOC deferred (4)
- **SCENE_ROUND_RESOLVING**: All non-admin intents buffered
- **COMBAT**: Player actions process immediately (10), OOC/social/rules buffered
- **ONBOARDING**: Rules queries prioritized (10), actions deferred (3)
- **User feedback**: Each handling decision generates a user-facing explanation

### Message Buffering
- **MessageBuffer**: Per-channel message queue with intent metadata
- **Buffer on high-intensity phases**: SCENE_ROUND_RESOLVING and COMBAT buffer non-critical intents
- **Release on phase transition**: `next_round` releases buffered messages with summary
- **Buffer summary**: Formatted output grouped by user for readability

### Pipeline Integration
- **TurnRunner**: Now accepts `session_phase` and `intent` parameters
- **TurnCoordinator**: Passes intent context through handle_turn/stream_turn
- **RouterService**: Includes classified intent in router model prompt
- **BotCommands**: Classifies every message, buffers when appropriate, passes intent to narration
- **main.py**: IntentClassifier and MessageBuffer wired into runtime

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed combat player_action buffering**
- **Found during:** Task 3 (phase-dependent handling)
- **Issue:** Original `should_buffer_intent` buffered ALL non-admin intents during combat, including player actions. This contradicted the plan which states "Player action: Primary focus during COMBAT"
- **Fix:** Combat now only buffers OOC, SOCIAL_IC, and RULES_QUERY. PLAYER_ACTION and ADMIN_ACTION process immediately.
- **Files modified:** `src/dm_bot/router/intent.py`
- **Commit:** aa480df

**2. [Rule 3 - Blocking] Added pytest-asyncio dependency**
- **Found during:** Task 6 (tests)
- **Issue:** Async tests failed because pytest-asyncio was not installed and asyncio_mode was not configured
- **Fix:** Added pytest-asyncio to dev dependencies, set asyncio_mode=auto in pyproject.toml
- **Files modified:** `pyproject.toml`
- **Commit:** 2651133

**3. [Rule 3 - Blocking] Updated test stubs for new parameters**
- **Found during:** Task 6 (regression tests)
- **Issue:** 7 existing tests failed because stub classes didn't accept new keyword arguments (session_phase, intent, intent_reasoning)
- **Fix:** Updated StubTurnService, StubTurnCoordinator, StubRouter, StubTurnRunner to accept **kwargs
- **Files modified:** `tests/test_commands.py`, `tests/test_gameplay_integration.py`, `tests/test_natural_message_runtime.py`, `tests/test_phase2_integration.py`, `tests/test_turns.py`
- **Commit:** 2651133

## Test Results

```
192 passed, 0 failed
```

All 37 new intent routing tests pass. All 155 existing tests pass with no regressions.

## Success Criteria

- [x] Messages classified by intent (OOC, IC, action, rules, admin)
- [x] Phase-dependent handling works correctly
- [x] User sees feedback explaining handling rationale
- [x] Buffered messages delivered after phase transitions
- [x] Integrates with Scene Round Collection
- [x] Tests pass (192/192)
- [x] No regressions in existing functionality

## Cross-Track Impact

- **Primary Track:** Track C (Discord Interaction Layer)
- **Secondary Impact:** Track A (turn pipeline receives intent context)
- **Contracts Changed:** TurnRunner.run_turn(), TurnCoordinator.handle_turn(), RouterService.route() — all accept new optional parameters with backward-compatible defaults
- **Migration Notes:** No breaking changes. New parameters default to UNKNOWN/lobby. Existing callers work unchanged.
