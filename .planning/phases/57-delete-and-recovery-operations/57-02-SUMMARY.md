# Phase 57-02 Summary: Discord Commands

**Plan:** 57-02
**Wave:** 2
**Date:** 2026-03-31
**Status:** ✓ Complete

## Changes Made

### commands.py
1. **Updated `list_profiles()`** to show 🔴 for deleted profiles with grace countdown
2. **Added `delete_profile()`** command - soft-delete archived profiles
3. **Added `recover_profile()`** command - restore deleted profiles within grace period

### client.py
4. **Registered `/delete_profile`** command with Discord tree
5. **Registered `/recover_profile`** command with Discord tree

## Decisions Implemented
- D-07: Deleted profiles visible in /profiles with 🔴 status during grace period
- Cannot delete active profiles (must archive first)
- Cannot recover if grace period expired

## Verification
- `uv run pytest -q`: 474 passed
- `uv run python -m dm_bot.main smoke-check`: 474 passed

## Commit
`672c705` feat(57): add /delete_profile and /recover_profile commands, update /profiles for deleted visibility
