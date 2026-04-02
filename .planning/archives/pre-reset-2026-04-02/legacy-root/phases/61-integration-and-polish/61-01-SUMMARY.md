# Phase 61-01 Summary: Integration And Polish

## Completed

Phase 61 complete - Integration and Polish for vB.1.5.

## Files Modified

### `src/dm_bot/orchestrator/session_store.py`
- Updated `validate_ready()` (lines 407-428) to use instance model instead of `member.selected_profile_id` and `member.active_character_name`
- New logic: checks `instance.status == "active"` and `instance.character_name` is set

### `src/dm_bot/discord_bot/commands.py`
- Updated `profile_detail()` (lines 497-526) to show campaign instance context when profile is linked to an active instance
- Shows: campaign_id, instance status (🟢 活跃 / ⚪ 已退役), character_name

### `tests/test_ready_gate.py`
- Updated existing tests to use instance model: `test_ready_succeeds_with_selected_profile`, `test_ready_succeeds_with_active_character_name`
- Added new tests: `test_ready_with_active_instance_via_select_profile`, `test_ready_with_retired_instance_fails`, `test_ready_with_active_instance_but_empty_character_name`, `test_ready_still_rejects_non_member`, `test_ready_still_rejects_no_session`

### `tests/test_ready_commands.py`
- Updated `test_ready_success` to use `CampaignCharacterInstance` with `character_name` set

### `tests/test_multi_user_session.py`
- Updated fixture `three_player_session` to create instance for owner manually
- Updated `test_three_player_select_profile_and_ready` and `test_all_players_can_have_active_character_name` to use instance model

### `tests/test_lobby_flow.py`
- Updated `test_full_lobby_flow_bind_join_select_ready` and `test_lobby_flow_state_persistence` to use instance model

### `tests/test_discord_commands.py`
- Updated `test_ready_sets_player_ready_on_success` to use `CampaignCharacterInstance`

### `tests/test_e2e_lifecycle.py` (NEW FILE)
- Created E2E lifecycle tests covering:
  - Full lifecycle: select profile → ready → retire → reactivate
  - Cannot ready without active instance
  - Cannot ready with retired instance
  - profile_detail shows active/retired instance context

## Requirements Covered

| Requirement | Implementation |
|-------------|----------------|
| PV-02: /profile_detail shows instance context | Enhanced `profile_detail()` shows campaign_id, status, character_name |
| PV-04: User cannot ready without valid active instance | Updated `validate_ready()` checks `instance.status == "active"` and `instance.character_name` |

## Verification

```
uv run pytest -q: 513 passed
uv run python -m dm_bot.main smoke-check: 513 passed
```

## Key Design Change (D-01)

The ready gate now validates using the `CampaignCharacterInstance` model:
- OLD: `member.selected_profile_id and member.active_character_name`
- NEW: `instance.status == "active" and instance.character_name`

This ensures ready validation works correctly with the instance lifecycle (select → active → retire).

## Notes

- 8 tests in `test_e2e_lifecycle.py` all pass
- All 513 tests pass including updated tests in `test_ready_gate.py`, `test_ready_commands.py`, `test_multi_user_session.py`, `test_lobby_flow.py`, `test_discord_commands.py`
- Pre-existing LSP errors in `session_store.py` `load_sessions` method remain (not related to Phase 61 changes)
