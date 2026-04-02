# Phase 55: Plan 55-02 - /profiles Upgrade + /my_character + /admin_profiles

**Phase:** Profile List And Event Logging Foundation
**Plan:** 55-02
**Date:** 2026-03-31
**Status:** Complete

## Summary

Implemented three Discord commands for Phase 55 profile visibility.

## What Was Built

### 1. `/profiles` Upgrade (PLC-01, PV-01)

Modified `list_profiles` in BotCommands to:
- Use `detail_view()` instead of `summary_line()` for full investigator card display
- Add status emoji header: 🟢 for active, ⚪ for archived
- Show profile name and status in header line
- Each profile displayed with blank line separator

### 2. `/my_character` Command (ILC-01)

New command showing user's active campaign character instance:
- Requires bound campaign session
- Requires user to be a campaign member
- Shows: character name, campaign ID, creation time, source
- Shows linked archive profile name and occupation if available

### 3. `/admin_profiles` Command (AV-01)

New admin command listing all player profiles in the campaign:
- Requires admin or owner role (CampaignRole.OWNER or CampaignRole.ADMIN)
- Shows ownership chain: Discord user → campaign member → selected profile → character instance
- Displays for each member:
  - Role icon (👑 owner, ⚔️ admin, 🎭 member)
  - Active character instance (or "无活跃角色")
  - Selected profile name, occupation, and status
  - Ready status (✓/✗)
- Public message (not ephemeral) so all campaign members can see

## Key Decisions

- Status emoji: 🟢 for active, ⚪ for archived (vs. text "active"/"archived")
- `/admin_profiles` output is public (not ephemeral) so campaign observers can see structure
- `/my_character` output is ephemeral (private to user)

## Files Changed

- `src/dm_bot/discord_bot/commands.py` (+155 lines, -1 line)

## Verification

- `uv run python -c "from dm_bot.discord_bot.commands import BotCommands"` → imports ok
- `uv run pytest -q` → 458 passed
- LSP errors are pre-existing (not introduced by this change)

## Commits

- `feat(55): upgrade /profiles to detail_view and add /my_character /admin_profiles commands`
