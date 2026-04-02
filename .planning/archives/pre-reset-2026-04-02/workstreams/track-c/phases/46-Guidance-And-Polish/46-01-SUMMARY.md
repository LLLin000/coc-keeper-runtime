# Phase 46: Guidance & Polish - Summary

**Completed:** 2026-03-28
**Status:** Complete

## Objective
Add user guidance and reduce command clutter in game halls.

## Tasks Completed

### Task 1: Welcome/Setup Message with Channel Structure ✅
**Modified:** `src/dm_bot/discord_bot/commands.py`

Enhanced the `/setup` command to include comprehensive channel structure guidance:
- Four channel types explained: 角色档案, 游戏大厅, KP-trace, 管理员
- Current bindings displayed when available
- Binding commands listed for each channel type
- Falls back to default guidance when session store unavailable

### Task 2: Long Outputs Use Ephemeral Mode ✅
**Status:** Already implemented in existing code

Verified the following commands use `ephemeral=True`:
- `list_profiles` (line 198)
- `profile_detail` (line 213)
- Most private/confidential commands

### Task 3: Diagnostic Commands Prefer Ephemeral ✅
**Status:** Already implemented in existing code

Verified the following commands use `ephemeral=True`:
- `setup_check` (line 47)
- `debug_status` (line 700)
- `coc_assets_summary` (line 723)

### Task 4: Gameplay Narration Stays in Game Halls ✅
**Status:** Already implemented in existing code

Verified via `ChannelEnforcer` integration:
- `take_turn` command uses `check_channel("take_turn", interaction)` 
- Enforces channel binding before allowing gameplay

## Success Criteria

| Criteria | Status |
|----------|--------|
| GUIDE-03: New users see welcome message with channel structure | ✅ |
| CLUTTER-01: Long command outputs use ephemeral mode | ✅ |
| CLUTTER-02: Diagnostic commands prefer trace/admin channels | ✅ |
| CLUTTER-03: Gameplay narration stays focused in game halls | ✅ |

## Files Modified

- `src/dm_bot/discord_bot/commands.py` - Enhanced setup_check with channel guidance

## Tests

All 130 tests pass.

```bash
uv run pytest -q
# 130 passed, 3 warnings
```
