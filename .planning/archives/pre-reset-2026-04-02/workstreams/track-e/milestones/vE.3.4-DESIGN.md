# vE.3.4: Runtime Phase Transition Wiring

## Goal

修复 RuntimeTestDriver 场景中的 phase 转换断裂问题。13 个场景正确检测到 PHASE_TRANSITION_MISMATCH，说明命令执行后 session phase 仍停留在 `lobby`。

## Root Cause Analysis

### Problem 1: `join_campaign` doesn't transition phase
- `SessionStore.join_campaign()` only adds member, doesn't change phase
- Expected: `lobby → awaiting_ready` after first join
- Actual: stays at `lobby`

### Problem 2: `ready` command requires preconditions
- `BotCommands.ready()` needs character + profile bound
- Scenarios call `ready` without `set_role` or `select_profile` first
- Ready silently fails or throws, phase never advances

### Problem 3: Missing phase transition triggers
- No command transitions `lobby → awaiting_ready`
- No command transitions `awaiting_ready → awaiting_admin_start`
- No command transitions `awaiting_admin_start → onboarding`
- These transitions should happen automatically when conditions are met

## Design Principle

**Phase transitions should be automatic, not manual.** When the last player joins, phase should auto-advance to `awaiting_ready`. When all players ready, auto-advance to `awaiting_admin_start`.

## Phases

### E90: Auto-Advance Lobby → Awaiting Ready

**Problem:** Phase stays at `lobby` after players join. Should auto-advance when first non-owner joins.

**Fix:** Add phase transition logic to `join_campaign()` — when member count > 1 (owner + at least one player), transition to `awaiting_ready`.

**Files:** `src/dm_bot/orchestrator/session_store.py`

**Tests:** 
- `test_join_campaign_transitions_to_awaiting_ready()`
- `test_owner_only_stays_in_lobby()`
- `test_multiple_joins_stay_in_awaiting_ready()`

### E91: Ready Command Phase Transitions

**Problem:** `ready` command doesn't properly transition phase when all players are ready.

**Fix:** 
1. `ready()` should transition session phase to `awaiting_admin_start` when all members are ready
2. Add `all_ready()` check to session store
3. Wire phase transition in BotCommands.ready()

**Files:** `src/dm_bot/orchestrator/session_store.py`, `src/dm_bot/discord_bot/commands.py`

**Tests:**
- `test_ready_transitions_when_all_ready()`
- `test_ready_waits_for_last_player()`

### E92: Admin Start → Onboarding → Scene Round

**Problem:** No command or flow transitions from `awaiting_admin_start` to `onboarding` to `scene_round_open`.

**Fix:**
1. `start_session()` command should transition `awaiting_admin_start → onboarding`
2. Onboarding completion should transition `onboarding → scene_round_open`
3. Wire these transitions in the existing command handlers

**Files:** `src/dm_bot/orchestrator/session_store.py`, `src/dm_bot/discord_bot/commands.py`

**Tests:**
- `test_start_session_transitions_to_onboarding()`
- `test_onboarding_complete_transitions_to_scene_round()`

### E93: Scenario Precondition Alignment

**Problem:** Some scenarios expect phase transitions but don't set up required preconditions (roles, profiles).

**Fix:**
1. Update scenario YAML files to include required `set_role` steps before `ready`
2. Add `select_profile` steps where needed
3. Ensure chaos scenarios properly test duplicate member detection

**Files:** `tests/scenarios/**/*.yaml`

**Tests:** All 13 failing scenarios should now pass

## Success Criteria

1. All 13 previously failing scenarios now pass
2. Phase transitions are automatic and deterministic
3. No regressions in existing 842 tests
4. `uv run python -m dm_bot.main run-scenario --all` shows all scenarios PASS

## Estimated Effort

3-4 phases, each is small targeted fix (10-20 lines of code + tests)
