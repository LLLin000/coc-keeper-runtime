---
phase: D42
plan: 01
subsystem: presentation
tags: [keeper-voice, system-prompts, chinese-localization, narrative-formatting]

# Dependency graph
requires:
  - phase: D40
    provides: Keeper voice established in builder prompts
provides:
  - Model-guided system prompts use consistent Keeper voice
  - Consequence formatting uses narrative Keeper-style text
  - All player-facing system messages use consistent Chinese
affects: [D41, D43, D44, D45]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Keeper voice: '你是克苏鲁的呼唤的 Keeper' instead of '你是XX器'"
    - "Narrative formatting for rule outcomes"
    - "Chinese-first player-facing messages"

key-files:
  created: []
  modified:
    - src/dm_bot/coc/builder.py
    - src/dm_bot/orchestrator/consequence_aggregator.py
    - src/dm_bot/discord_bot/commands.py
    - tests/test_discord_commands.py
    - tests/test_commands.py
    - tests/test_scenario_runner.py

key-decisions:
  - "Narration service prompt left unchanged — already uses 'Chinese Call of Cthulhu Keeper'"
  - "Internal/debug strings left in English (e.g., log messages, variable names)"
  - "Test assertions updated to match new Chinese messages"

patterns-established:
  - "Model-guided prompts: '你是克苏鲁的呼唤的 Keeper，正在...' pattern for all builder system prompts"
  - "Consequence formatting: narrative framing with em-dash separators"
  - "Player-facing messages: consistent Chinese with subtle Keeper tone"

requirements-completed: [KEEPER-01, KEEPER-02, KEEPER-03, KEEPER-04]

# Metrics
duration: 15min
completed: 2026-03-31
---

# Phase D42 Plan 01: Keeper Prompt Polish Summary

**Polished all remaining Keeper voice across the system — model-guided system prompts, consequence formatting, and player-facing system messages**

## Performance

- **Duration:** 15 min
- **Started:** 2026-03-31T00:00:00Z
- **Completed:** 2026-03-31T00:15:00Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- All three model-guided system prompts in builder.py now use "你是克苏鲁的呼唤的 Keeper" instead of generic "XX器" framing
- Consequence aggregator formats outcomes with narrative Keeper-style text (e.g., "检定通过——你勉强做到了" instead of "成功")
- All player-facing system messages in commands.py translated to consistent Chinese
- Narration service prompt confirmed solid — already uses "Chinese Call of Cthulhu Keeper"

## Task Commits

Each task was committed atomically:

1. **Task 1: Polish model-guided system prompts with Keeper voice** - `6540733` (feat)
2. **Task 2: Polish consequence formatting with narrative framing** - `2664cf1` (feat)
3. **Task 3: Polish system messages to consistent Chinese** - `fd20707` (feat)
4. **Test fix: Update test assertions for Chinese messages** - `42a77c6` (fix)

## Files Created/Modified

- `src/dm_bot/coc/builder.py` - Three model-guided system prompts rewritten with Keeper voice
- `src/dm_bot/orchestrator/consequence_aggregator.py` - _format_outcome and _format_trigger_effect use narrative framing
- `src/dm_bot/discord_bot/commands.py` - All player-facing messages translated to Chinese
- `tests/test_discord_commands.py` - Updated assertion for Chinese adventure loaded message
- `tests/test_commands.py` - Updated assertion for Chinese adventure loaded message
- `tests/test_scenario_runner.py` - Updated assertion for Chinese binding message

## Decisions Made

- Narration service prompt left unchanged — already solid with "Chinese Call of Cthulhu Keeper" framing
- Internal/debug strings left in English (log messages, variable names) — only player-facing messages translated
- Trigger format changed from `[触发器]` to `【事件触发】` for visual consistency with other Keeper-style brackets

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test assertions checking for old English strings**
- **Found during:** Task 3 (command message translation)
- **Issue:** Three test files had assertions checking for English strings that were intentionally changed to Chinese
- **Fix:** Updated test assertions to match new Chinese messages
- **Files modified:** tests/test_discord_commands.py, tests/test_commands.py, tests/test_scenario_runner.py
- **Verification:** All 813 tests pass, smoke check passes
- **Committed in:** `42a77c6` (test fix commit)

---

**Total deviations:** 1 auto-fixed (1 bug - test assertions)
**Impact on plan:** Test updates necessary for correctness after intentional message changes. No scope creep.

## Issues Encountered

- None — plan executed as specified

## Known Stubs

- `_llm_summarize_groups` in consequence_aggregator.py has a TODO for Ollama integration — pre-existing, not introduced by this plan. This is a placeholder for future LLM summarization of consequence groups.

## Verification Results

- `uv run pytest tests/coc/test_builder.py -x -q` — 7 passed
- `uv run pytest tests/test_discord_commands.py -x -q` — 10 passed
- `uv run pytest tests/ -k "consequence" -x -q` — 3 passed
- `uv run python -m dm_bot.main smoke-check` — 813 passed
- `uv run pytest -q` — 813 passed

## Next Phase Readiness

- Keeper voice is now consistent across builder, narration, consequences, and system messages
- Ready for D43 (Activity-Ready Presentation Contracts) and D41 (Archive Card Redesign)
- No blockers or concerns

---
*Phase: D42*
*Completed: 2026-03-31*
