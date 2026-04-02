# Phase 58: Instance Management - Execution Summary

**Completed:** 2026-03-31
**Wave:** 1
**Status:** ✅ Complete

## What Was Built

Phase 58 implements instance management operations for campaign character instances:
- `ILC-02`: User can retire their active campaign character instance
- `ILC-03`: User can select a different archive profile to project as a new campaign instance

## Changes Made

### `src/dm_bot/orchestrator/session_store.py`

1. **Added `status` field to `CampaignCharacterInstance`** (line 71)
   - Field: `status: str = "active"` with comment `# "active" or "retired"`
   - Valid values: `"active"`, `"retired"`

2. **Updated `get_active_instances_for_user()`** (line 515)
   - Changed condition from `if instance.character_name` to `if instance.status == "active" and instance.character_name`
   - Now correctly filters out retired instances

3. **Added `retire_instance()` method** (lines 519-554)
   - Sets `status = "retired"`, clears `character_name` and `archive_profile_id`
   - Logs `instance_retire` governance event
   - Raises `ValueError` if no campaign bound or user has no instance
   - Already-retired instances return without error (no-op)

4. **Added `select_instance_profile()` method** (lines 556-604)
   - Validates profile exists and `status == "active"` (raises `ValueError` if not)
   - Sets `character_name` from `archive_profile.name`
   - Sets `archive_profile_id` and `status = "active"`
   - Logs `instance_select` governance event
   - Can operate without validation (`archive_repo=None`) for testing/external callers

5. **Added TYPE_CHECKING import** for `InvestigatorArchiveRepository` (line 6)
   - Used as forward reference in type annotation to avoid circular imports

### `tests/test_instance_management.py` (NEW FILE)

18 tests across 4 test classes:
- `TestCampaignCharacterInstanceStatus` (3 tests)
- `TestGetActiveInstancesForUser` (3 tests)
- `TestRetireInstance` (5 tests)
- `TestSelectInstanceProfile` (7 tests)

## Verification

| Check | Result |
|-------|--------|
| `uv run pytest -q tests/test_instance_management.py` | ✅ 18 passed |
| `uv run pytest -q` | ✅ 492 passed |
| `uv run python -m dm_bot.main smoke-check` | ✅ Passed |

## Decisions Made

| ID | Decision | Choice |
|----|----------|--------|
| G-01 | Retire 行为 | C: 标记 status='retired'，保留审计记录 |
| G-02 | Name 来源 | A: archive_profile.name |
| G-03 | Profile 验证 | A: 必须是 active |
| G-04 | 操作作用域 | A: 当前 campaign |
| G-05 | Event 操作名 | A: instance_retire / instance_select |

## Requirements Satisfied

| Requirement | Status |
|------------|--------|
| ILC-02: User can retire their active campaign character instance | ✅ |
| ILC-03: User can select a different archive profile to project as new instance | ✅ |

## Notes

- The `GovernanceEventLog` class already supported `instance_retire` and `instance_select` as valid operation names (discovered in governance_event_log.py line 12)
- Pre-existing LSP errors in session_store.py (lines 666+) are related to JSON persistence and unrelated to these changes
