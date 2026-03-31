---
phase: D40
plan: 01
subsystem: presentation
tags: [discord, dm-routing, keeper-voice, character-builder, archive-channel]

# Dependency graph
requires:
  - phase: Track B builder foundation
    provides: ConversationalCharacterBuilder, InvestigatorArchiveProfile, InvestigatorArchiveRepository
provides:
  - DM-first character builder interview flow
  - Archive channel "建卡中..." indicator
  - Archive channel guidance explaining builder vs profile viewing
  - All builder prompts rewritten with Keeper voice
  - _consume_archive_builder_message extended with is_dm parameter
affects: [D41, D42, D43]

# Tech tracking
tech-stack:
  added: []
  patterns: [DM-first routing with fallback, Keeper-voiced prompts, is_dm parameter for message handlers]

key-files:
  created: []
  modified:
    - src/dm_bot/coc/builder.py
    - src/dm_bot/discord_bot/commands.py
    - tests/test_v18_archive_builder.py

key-decisions:
  - "DM routing uses try/except on create_dm() with ephemeral in-channel fallback"
  - "Archive indicator is non-ephemeral so other users can see someone is building"
  - "DM message includes reply instructions (direct DM reply or /builder_reply slash command)"
  - "_consume_archive_builder_message extended with is_dm parameter (default False) for backward compatibility"

patterns-established:
  - "DM-first: send to DM, post brief indicator in channel"
  - "Keeper voice: prompts read like a Keeper shaping a person, not a form"
  - "Graceful fallback: DM failure → ephemeral in-channel with explanatory message"

requirements-completed:
  - PRIVATE-01
  - PRIVATE-02
  - PRIVATE-03

# Metrics
duration: ~15min
completed: 2026-03-31
---

# Phase D40 Plan 01: Private-First Builder Experience Summary

**Route character builder to DM by default, add archive channel guidance, and rewrite all builder prompts with Keeper voice**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-31T14:34:53Z
- **Completed:** 2026-03-31T14:50:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- `/start_builder` now sends first question to user's DM instead of in-channel
- Archive channel shows "🕯️ 建卡访谈已在私信中开始。完成建卡后档案将出现在这里。" indicator
- Archive channel guidance updated to explain builder flow vs profile viewing
- All builder prompts rewritten with Keeper voice (INTRO, CONCEPT, age, occupation, finalization)
- `_consume_archive_builder_message` extended with `is_dm` parameter for future DM message handling
- Test assertions updated to match new Keeper-voiced text

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite builder prompts with Keeper voice** - `9975dd2` (feat)
2. **Task 2: Route builder to DM, add archive channel guidance** - `8e37175` (feat)
3. **Task 3: Update builder message handler for DM context** - `9b647bf` (feat)
4. **Test assertion fixes for new Keeper-voiced prompts** - `371383c` (fix)

**Plan metadata:** `8977396` (docs: create phase plan)

## Files Created/Modified

- `src/dm_bot/coc/builder.py` - Rewrote INTRO_QUESTION, CONCEPT_QUESTION, age/occupation questions, and finalization prompt with Keeper voice
- `src/dm_bot/discord_bot/commands.py` - DM routing for start_character_builder, archive channel indicator, updated guidance text, is_dm parameter on _consume_archive_builder_message
- `tests/test_v18_archive_builder.py` - Updated 3 test assertions to match new Keeper-voiced text

## Decisions Made

- DM routing uses try/except on `create_dm()` — if DM creation fails (user disabled server DMs), falls back to ephemeral in-channel with explanatory message
- Archive channel indicator is non-ephemeral so other users can see someone is building a character
- DM message includes reply instructions: "回答时直接在私信中回复即可，或在档案频道使用 `/builder_reply answer:你的回答`"
- `_consume_archive_builder_message` extended with `is_dm` parameter (default False) for backward compatibility — existing archive channel flow unchanged

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated test assertions for changed prompt text**
- **Found during:** Smoke check (uv run python -m dm_bot.main smoke-check)
- **Issue:** 3 tests in test_v18_archive_builder.py asserted on exact old text strings ("先给这位调查员起个名字。", "一句短话") which were intentionally changed to Keeper voice
- **Fix:** Updated assertions to check for new Keeper-voiced text using `in` operator instead of exact equality
- **Files modified:** tests/test_v18_archive_builder.py
- **Verification:** All 808 tests pass after fix
- **Committed in:** `371383c`

---

**Total deviations:** 1 auto-fixed (1 bug fix for test assertions)
**Impact on plan:** Test assertions needed updating to match intentional text changes. No scope creep.

## Issues Encountered

- String matching issues during initial edit due to Chinese quote characters (`""` vs `""`) — resolved by using a Python replacement script
- Smoke check caught 3 test failures from the text changes — fixed immediately as Rule 1 deviation

## Verification Results

- `uv run pytest tests/coc/test_builder.py -x -q` — 7 passed
- `uv run pytest tests/test_discord_commands.py -x -q` — 10 passed
- `uv run python -m dm_bot.main smoke-check` — 808 passed
- `uv run pytest -q` — 808 passed

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- DM-first builder flow complete and tested
- Archive channel guidance updated
- Keeper voice established across all builder prompts
- Ready for D41 (Archive Card Redesign) and D42 (Keeper Prompt Polish — note: D42's goals are largely already achieved by this plan's Keeper voice work)

---
*Phase: D40*
*Completed: 2026-03-31*
