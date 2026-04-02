---
phase: 53-handling-reason-surfaces
plan: 53
subsystem: discord-interaction
tags: [discord, feedback, intent-handling, ephemeral-messages]

# Dependency graph
requires:
  - phase: 52-player-status-surfaces
    provides: VisibilitySnapshot with campaign/adventure/session state
provides:
  - DiscordFeedbackService for sending ephemeral routing feedback
  - IntentHandlerRegistry wired into runtime
  - Feedback injection in message pipeline
  - Tests for BUFFERED/IGNORED/DEFERRED feedback
affects: [track-c-phases-related-to-discord-messaging]

# Tech tracking
tech-stack:
  added: [DiscordFeedbackService with callback interface]
  patterns: [ephemeral-feedback, intent-based-routing-feedback]

key-files:
  created:
    - src/dm_bot/discord_bot/feedback.py - Feedback delivery service
    - tests/test_feedback_delivery.py - TDD tests for feedback
  modified:
    - src/dm_bot/router/intent_handler.py - Added IGNORED/DEFERRED cases
    - src/dm_bot/main.py - Wired IntentHandlerRegistry
    - src/dm_bot/discord_bot/commands.py - Added feedback injection

key-decisions:
  - "D-01: Send routing feedback as ephemeral Discord messages (DM to user)"
  - "D-02: Feedback delivered immediately when buffered/ignored/deferred"
  - "D-03: Feedback must be ≤50 characters"
  - "D-04: Different feedback content per routing outcome"

requirements-completed: [PLAY-03, PLAY-04]

# Metrics
duration: 12min
completed: 2026-03-29
---

# Phase 53: Handling Reason Surfaces Summary

**Concise player-facing explanations for why messages were ignored, buffered, deferred, or routed differently - using ephemeral Discord DMs with phase-aware feedback ≤50 characters**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-29T07:46:15Z
- **Completed:** 2026-03-29T07:58:00Z
- **Tasks:** 5
- **Files modified:** 5

## Accomplishments
- Added IGNORED (MessageIntent.UNKNOWN) and DEFERRED (MessageIntent.RULES_QUERY) feedback cases to _get_feedback()
- Created DiscordFeedbackService with callback-based interface for sending ephemeral feedback
- Wired IntentHandlerRegistry into main.py runtime
- Injected feedback delivery into message pipeline after intent handling
- Created TDD tests verifying BUFFERED/IGNORED/DEFERRED scenarios and ≤50 char limit

## Task Commits

Each task was committed atomically:

1. **Task 1: Add IGNORED/DEFERRED feedback cases** - `c2b32e3` (feat)
2. **Task 2: Create feedback delivery service** - `91cf223` (feat)
3. **Task 3: Wire IntentHandlerRegistry into runtime** - `9df9c0f` (feat)
4. **Task 4: Inject feedback into message pipeline** - `f845487` (feat)
5. **Task 5: Write TDD tests** - `4166c33` (test)

**Plan metadata:** `e3f7a1b` (docs: complete plan)

## Files Created/Modified
- `src/dm_bot/discord_bot/feedback.py` - DiscordFeedbackService with send_feedback method
- `tests/test_feedback_delivery.py` - 7 tests for feedback scenarios
- `src/dm_bot/router/intent_handler.py` - Added UNKNOWN and RULES_QUERY feedback maps
- `src/dm_bot/main.py` - Instantiated IntentHandlerRegistry, passed to BotCommands
- `src/dm_bot/discord_bot/commands.py` - Added feedback service, integrated with intent handling

## Decisions Made
- Used DM-based ephemeral feedback instead of channel ephemeral messages (simpler integration)
- FeedbackService uses callback pattern to avoid circular dependency with bot client
- Fixed PLAYER_ACTION feedback to meet ≤50 char requirement

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] PLAYER_ACTION feedback exceeded 50 char limit**
- **Found during:** Task 5 (Running tests)
- **Issue:** Original feedback "Your action has been recorded and will be resolved shortly." was 59 characters
- **Fix:** Changed to Chinese "⏳ 行动已记录，将在结算后执行" (26 characters)
- **Files modified:** src/dm_bot/router/intent_handler.py
- **Verification:** Test passes with ≤50 char assertion
- **Committed in:** `4166c33` (part of test commit)

**2. [Rule 3 - Blocking] Duplicate code block in main.py**
- **Found during:** Task 3 (Wiring IntentHandlerRegistry)
- **Issue:** Lines 117-156 were duplicated in build_runtime function
- **Fix:** Removed duplicate block
- **Files modified:** src/dm_bot/main.py
- **Verification:** Code compiles, no duplicate RuntimeBundle returns
- **Committed in:** `9df9c0f` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (1 missing critical, 1 blocking)
**Impact on plan:** Both auto-fixes necessary for correctness. No scope creep.

## Issues Encountered
- None - plan executed with expected deviations handled

## Next Phase Readiness
- IntentHandlerRegistry is wired and functional
- Feedback delivery pipeline is in place
- Tests verify behavior meets requirements
- Ready for next Discord interaction phase

---
*Phase: 53-handling-reason-surfaces*
*Completed: 2026-03-29*
