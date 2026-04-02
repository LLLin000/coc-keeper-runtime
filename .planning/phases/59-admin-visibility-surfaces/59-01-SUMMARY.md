# Phase 59-01 Summary: Admin Visibility Surfaces

## Completed

All three admin visibility commands implemented and verified.

## Files Modified

### `src/dm_bot/discord_bot/commands.py`
Added three handler methods:

1. **`admin_profile_detail(interaction, profile_id=None)`** (lines 659-732)
   - Lists all profiles (up to 25) if no profile_id provided
   - Shows status icon (🟢/⚪), profile_id, name, occupation, status
   - With profile_id: displays full `detail_view()` output
   - Admin role check (OWNER or ADMIN only)

2. **`admin_ownership_chain(interaction, user_id=None)`** (lines 734-814)
   - Traces full chain: Discord user → archive profiles → campaign memberships → character instances
   - Shows profile status and role for each level
   - Compact single-line format per level
   - Admin role check

3. **`admin_instances(interaction)`** (lines 816-889)
   - Lists all active character instances across ALL campaigns
   - Groups by campaign_id
   - Shows role icon (👑/⚔️/🎭), Discord user mention, character name, profile ref
   - Shows total count
   - Only shows instances with status=="active" (Phase 58 filter)
   - Admin role check

### `src/dm_bot/discord_bot/client.py`
Added three command registrations (after line 225):

- `admin_profile_detail` - optional `profile_id` parameter
- `admin_ownership_chain` - optional `user_id` parameter  
- `admin_instances` - no parameters

## Verification

```
uv run pytest -q: 492 passed
uv run python -m dm_bot.main smoke-check: 492 passed
```

## Requirements Covered

| Requirement | Implementation |
|-------------|----------------|
| AV-02: View any player's archive profile in detail | `admin_profile_detail` - interactive selection |
| AV-03: View full ownership chain | `admin_ownership_chain` - traces complete chain |
| AV-04: View all active instances across campaigns | `admin_instances` - grouped by campaign |

## Key Decisions Applied

| G-01 | Profile detail interaction | Interactive selection from list |
| G-02 | Ownership chain format | Compact single-line per level |
| G-03 | Cross-campaign instances | Grouped by campaign |
| G-04 | Output visibility | Mixed - lists ephemeral, chain/instances public |

## Notes

- All commands require admin/owner role in the current channel's campaign
- `admin_ownership_chain` accepts Discord mention format (`<@user_id>`) and strips to clean ID
- `admin_instances` correctly filters by `status == "active"` (Phase 58 field)
- All handlers include proper error messages for unconfigured dependencies
