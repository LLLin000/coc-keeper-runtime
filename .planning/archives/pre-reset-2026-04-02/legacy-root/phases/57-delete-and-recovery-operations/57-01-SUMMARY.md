# Phase 57-01 Summary: Archive Repository TDD

**Plan:** 57-01
**Wave:** 1
**Date:** 2026-03-31
**Status:** ✓ Complete

## Changes Made

### archive.py
1. **Added `deleted_at: datetime | None` field** to `InvestigatorArchiveProfile`
2. **Updated `summary_line()`** to show 🔴 for deleted status
3. **Updated `detail_view()`** to show 🔴 for deleted status
4. **Fixed `replace_active_with()`** to set old profile status="archived" (not "replaced") per D-05
5. **Changed `delete_profile()`** to soft-delete (status="deleted", deleted_at=now)
6. **Added `recover_profile()`** to restore deleted→active within 7-day grace
7. **Added `purge_expired_deleted()`** for auto-permanent delete after grace period

### Tests
Created `tests/test_archive_delete_recover.py` with 16 tests covering:
- Deleted status and deleted_at field
- Soft-delete behavior
- Recover within grace period
- Replace→archived (not replaced)
- Purge expired deleted profiles

## Decisions Implemented
- D-05: replace → archived
- D-06: 7-day grace period
- D-08: Auto-purge after grace period

## Verification
- `uv run pytest -q tests/test_archive_delete_recover.py`: 16 passed
- `uv run pytest -q`: 474 passed
- `uv run python -m dm_bot.main smoke-check`: 474 passed

## Commit
`b056c44` feat(57): add soft-delete with grace period, recover, purge, and replace→archived
