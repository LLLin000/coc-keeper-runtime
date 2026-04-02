---
phase: 48-Pre-Play-Onboarding
plan: 01
subsystem: session_management
tags: [onboarding, discord, ui, session_flow]

# Dependency graph
requires:
  - phase: 47-Session-Phases
    provides: SessionPhase enum with ONBOARDING phase
provides:
  - Pre-play onboarding with interactive Discord buttons
  - Per-player onboarding completion tracking
  - Default COC 7E quick-start content
  - Adventure package override mechanism
affects: [49-Scene-Round-Collection, 50-Message-Intent-Routing]

# Tech tracking
tech-stack:
  added: [discord.ui.View, discord.ui.Button]
  patterns: [persistent Discord views, phase-gated session flow]

key-files:
  created:
    - src/dm_bot/orchestrator/onboarding.py - OnboardingContent system
    - src/dm_bot/orchestrator/onboarding_controller.py - Flow controller
    - src/dm_bot/discord_bot/onboarding_views.py - Interactive Discord views
  modified:
    - src/dm_bot/orchestrator/session_store.py - Added onboarding fields
    - src/dm_bot/discord_bot/commands.py - Added /start-session and /complete-onboarding
    - src/dm_bot/discord_bot/client.py - Registered new commands

key-decisions:
  - Used persistent Discord View with timeout=None for survival across bot restarts
  - Default onboarding includes COC 7E core rules: D100, Pushing, SAN, Luck
  - Per-player completion tracking enables flexible session flow
  - Transition to SCENE_ROUND_OPEN only after all players confirm

patterns-established:
  - "Phase-gated session flow: LOBBY → AWAITING_READY → AWAITING_ADMIN_START → ONBOARDING → SCENE_ROUND_OPEN"

requirements-completed: []

# Metrics
duration: 45min
completed: 2026-03-28
---

# Phase 48 Plan 1: Pre-Play Onboarding Summary

**Interactive pre-play onboarding with Discord button-based flow, per-player completion tracking, and COC 7E quick-start content**

## Performance

- **Duration:** 45 min
- **Started:** 2026-03-28T15:52:53Z
- **Completed:** 2026-03-28T16:38:00Z
- **Tasks:** 6 tasks (Tasks 1-6 in plan)
- **Files modified:** 7 files

## Accomplishments
- Extended CampaignSession model with onboarding_completed (per-player) and onboarding_content fields
- Created default COC 7E quick-start onboarding content (D100, Pushing, SAN, Luck sections)
- Built interactive OnboardingView with Discord button flow
- Implemented OnboardingController for managing flow and phase transitions
- Modified /start-session to transition to ONBOARDING phase before gameplay
- Added /complete-onboarding command for players to confirm readiness
- Updated turn handling to block actions during onboarding until player confirms

## Task Commits

Each task was committed atomically:

1. **Task 1-6: Full implementation** - `d420a22` (feat)
   - Extended session_store.py with onboarding fields
   - Created onboarding.py with OnboardingContent system
   - Created onboarding_controller.py for flow management
   - Created onboarding_views.py for Discord UI
   - Updated commands.py and client.py for new commands
   - Updated test_commands.py for new flow

**Plan metadata:** `d420a22` (docs: complete plan)

## Files Created/Modified
- `src/dm_bot/orchestrator/session_store.py` - Added onboarding_completed, onboarding_content fields
- `src/dm_bot/orchestrator/onboarding.py` - OnboardingContent with COC 7E default content
- `src/dm_bot/orchestrator/onboarding_controller.py` - OnboardingController for flow management
- `src/dm_bot/discord_bot/onboarding_views.py` - Interactive OnboardingView with buttons
- `src/dm_bot/discord_bot/commands.py` - Added /start-session and /complete-onboarding commands
- `src/dm_bot/discord_bot/client.py` - Registered new slash commands
- `tests/test_commands.py` - Updated test for new onboarding flow

## Decisions Made
- Used persistent Discord View with timeout=None to survive bot restarts
- Default onboarding covers core COC 7E mechanics players need: D100, Pushing, SAN, Luck
- Per-player completion tracking allows flexible session where late-joining players can onboard
- All players must confirm before transitioning to SCENE_ROUND_OPEN

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Fixed AttributeError in OnboardingController when adventure package lacks onboarding_content field - added hasattr check
- Fixed test failure by updating test to call /complete-onboarding for both players before checking adventure opening message

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Onboarding system complete and tested
- Ready for Phase 49: Scene Round Collection (collecting player inputs before KP output)
- Onboarding flow properly gates gameplay until players confirm

---
*Phase: 48-Pre-Play-Onboarding*
*Completed: 2026-03-28*
