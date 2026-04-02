---
phase: 54-character-selection-and-ready-validation
plan: 02
subsystem: discord-commands
tags: [discord, slash-commands, validation, session-store, archive-profile]

# Dependency graph
requires:
  - phase: 54-character-selection-and-ready-validation
    plan: 01
    provides: "SelectProfileError, ReadyGateError, validate_ready(), select_archive_profile() returning ValidationResult"
provides:
  - "/select_profile Discord slash command wired to session_store.select_archive_profile()"
  - "/ready Discord slash command wired to session_store.validate_ready()"
  - "Unit tests for both command handlers"
affects:
  - track-c Discord interaction layer
  - track-b character profile lifecycle

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "ValidationResult return type for command handlers"
    - "Ephemeral error messages for validation failures"
    - "Profile projection sync after successful validation"

key-files:
  created:
    - tests/test_ready_commands.py
  modified:
    - src/dm_bot/discord_bot/commands.py
    - src/dm_bot/discord_bot/client.py

key-decisions:
  - "select_profile() builds profiles dict for ownership validation, then re-fetches profile object for projection sync"
  - "/ready command wired to new ready() method, not ready_for_adventure()"

patterns-established:
  - "Pattern: Command handler validates first via session_store method, then performs side effects on success"
  - "Pattern: Ephemeral error messages for validation failures; success messages also ephemeral for consistency"

requirements-completed: []

# Metrics
duration: 40min
completed: 2026-03-29
---

# Phase 54 Plan 02: Discord Command Wiring Summary

**`/select_profile` and `/ready` Discord slash commands wired to SessionStore validation methods with ephemeral error responses**

## Performance

- **Duration:** ~40 min
- **Started:** 2026-03-29T
- **Completed:** 2026-03-29T
- **Tasks:** 4 (command wiring x2, unit tests, full regression)
- **Files modified:** 3 (commands.py, client.py, test_ready_commands.py)

## Accomplishments
- `/select_profile` slash command re-implemented to call `session_store.select_archive_profile()` with ValidationResult return type
- `/ready` slash command re-implemented to call `session_store.validate_ready()` via new `ready()` method
- Both commands use ephemeral error messages for validation failures
- Profile projection sync (`_sync_profile_projection_for_channel`) restored after validation success
- Full test suite passes (246 tests)

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire /select_profile command** - `38a7fd2` (feat)
2. **Task 2: Wire /ready command** - `38a7fd2` (feat)
3. **Task 3: Unit tests for ready gate** - `e183f15` (test)
4. **Task 4: Full regression verification** - `smoke-check: 246 passed`

**Plan metadata:** `5d1d9ed` (docs: create phase plan)

## Files Created/Modified
- `src/dm_bot/discord_bot/commands.py` - `select_profile()` rewired to validation, new `ready()` method added
- `src/dm_bot/discord_bot/client.py` - `/ready` command now calls `ready()` instead of `ready_for_adventure()`
- `tests/test_ready_commands.py` - 4 unit tests covering select_profile and ready command handlers

## Decisions Made

- Re-fetch profile object from archive after `select_archive_profile()` validation succeeds — the `profiles` dict was only used for ownership validation, not for the projection sync
- Error messages are ephemeral for both failure and success cases (success message also ephemeral for DM consistency)

## Deviations from Plan

None - plan executed exactly as written, with one auto-fix during execution.

### Auto-fixed Issues

**1. [Rule 1 - Bug] Missing `_sync_profile_projection_for_channel()` call after validation refactor**
- **Found during:** Task 4 (full regression)
- **Issue:** New `select_profile()` called `session_store.select_archive_profile()` but skipped the `_sync_profile_projection_for_channel()` call that the old implementation had. This broke `test_select_profile_immediately_syncs_projection_panel`.
- **Fix:** Added re-fetch of profile object from archive repository after validation success, then called `_sync_profile_projection_for_channel(channel_id, user_id, profile)`
- **Files modified:** `src/dm_bot/discord_bot/commands.py`
- **Verification:** `test_select_profile_immediately_syncs_projection_panel` passes, full suite 246/246
- **Committed in:** `38a7fd2` (part of feat commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Bug fix restored missing projection sync that is required for correct UI behavior. No scope change.

## Issues Encountered
- `turn_coordinator=MagicMock()` missing from test instantiations — added to all test cases
- `_make_interaction` helper was calling `int()` on string IDs like "user-2" causing ValueError — fixed to store string IDs directly matching `FakeInteraction` pattern

## Next Phase Readiness
- Command wiring complete, validation integrated with SessionStore
- Both `/select_profile` and `/ready` commands are functional with proper gate validation
- No blockers for continuation

---
*Phase: 54-character-selection-and-ready-validation / 02*
*Completed: 2026-03-29*
