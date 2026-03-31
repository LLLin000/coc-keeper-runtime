---
phase: E80-visibility-dispatcher
plan: "01"
subsystem: discord_bot
tags:
  - visibility
  - discord
  - dm
  - channel
  - test
dependency_graph:
  requires:
    - E79-skill-usage-tracking
  provides:
    - visibility-dispatcher
    - discord-integration
  affects:
    - discord_bot
    - orchestrator
tech_stack:
  added:
    - discord.Embed for structured messages
    - FakeDiscordClient test infrastructure
  patterns:
    - visibility-based routing
    - embed-based message formatting
key_files:
  created:
    - src/dm_bot/discord_bot/visibility_dispatcher.py
    - tests/discord_bot/test_visibility_dispatcher.py
    - tests/scenarios/contract/visibility/test_visibility_leak.yaml
  modified:
    - tests/fakes/discord.py
decisions:
  - "Use discord.Embed for structured output with title, description, fields"
  - "FakeTextChannel inherits from discord.TextChannel for isinstance checks"
  - "FakeUser implements minimal discord.User interface for DM sending"
  - "Keeper/gm_only content logged only, never sent to Discord"
metrics:
  duration: "~30 minutes"
  completed: "2026-03-31"
  tasks_completed: 6
  tests_added: 17
---

# Phase E80 Plan 01: Visibility Dispatcher Completion Summary

## One-liner
Complete visibility dispatcher with actual Discord channel/DM sending and comprehensive tests.

## Completed Tasks

| Task | Name | Files | Status |
|------|------|-------|--------|
| 1 | Update _send_public | visibility_dispatcher.py | ✅ |
| 2 | Update _send_private | visibility_dispatcher.py | ✅ |
| 3 | Update _send_group | visibility_dispatcher.py | ✅ |
| 4 | Create FakeDiscordClient | tests/fakes/discord.py | ✅ |
| 5 | Create unit tests | tests/discord_bot/test_visibility_dispatcher.py | ✅ |
| 6 | Create contract test | tests/scenarios/contract/visibility/test_visibility_leak.yaml | ✅ |

## What Was Built

### 1. VisibilityDispatcher Implementation (src/dm_bot/discord_bot/visibility_dispatcher.py)

**Resolved 3 TODOs:**

- **TODO line 89 (now resolved)**: `_send_public` now sends embeds to Discord campaign channel
  - Formats consequences as structured Discord Embeds
  - Groups consequences by character
  - Handles errors gracefully

- **TODO line 133 (now resolved)**: `_send_private` now sends DMs to individual players
  - Fetches Discord user by ID
  - Sends embed with private consequences
  - Handles "DMs disabled" case

- **TODO line 168 (now resolved)**: `_send_group` now sends DMs to group members
  - Collects all target users from character_to_user mapping
  - Sends same embed to all group members

### 2. FakeDiscordClient Test Infrastructure (tests/fakes/discord.py)

Added:
- `FakeDMChannel`: Tracks sent messages and embeds
- `FakeUser`: Inherits from discord.User, implements `dm_channel` property and `send()` method
- `FakeTextChannel`: Inherits from discord.TextChannel for proper isinstance checks
- `FakeDiscordClient`: Manages users/channels, provides `fetch_user`, `fetch_channel` methods

### 3. Unit Tests (tests/discord_bot/test_visibility_dispatcher.py)

17 tests covering:
- Public channel sending
- Private DM sending  
- Group DM sending
- Empty consequences handling
- Unknown character handling
- Keeper visibility isolation (gm_only never reaches Discord)
- Edge cases (no client, no channel configured, user not found)

### 4. Contract Test (tests/scenarios/contract/visibility/test_visibility_leak.yaml)

Verifies:
- Public output excludes gm_only content
- Private output excludes gm_only content
- Group output excludes gm_only content
- Keeper log contains gm_only content
- Player visible output never contains gm_only

## Key Implementation Details

### Message Format
All Discord messages use `discord.Embed` with:
- Title: "场景回合结果" (public), "私有信息" (private), "团体信息" (group)
- Description: Consequence count
- Fields: Individual consequences grouped by character
- Color: Blue (public), Purple (private), Gold (group)
- Timestamp

### Visibility Routing
```
PUBLIC → _send_public (channel)
PRIVATE → _send_private (DM to player)  
GROUP → _send_group (DM to group members)
KEEPER → _log_keeper_only (internal log only)
```

### Error Handling
- `discord.Forbidden`: Logged as warning (can't send to channel/user)
- `discord.HTTPException`: Logged as error
- `ValueError`/`discord.NotFound`: User ID format issues, logged as error
- Missing client or channel: Returns early with warning log

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing] FakeUser/FakeTextChannel proper inheritance**
- **Found during:** Task 4 (Create FakeDiscordClient)
- **Issue:** Initial FakeUser didn't inherit from discord.User, causing isinstance checks to fail
- **Fix:** Made FakeUser and FakeTextChannel properly inherit from discord.User and discord.TextChannel
- **Files modified:** tests/fakes/discord.py

**2. [Rule 1 - Bug] Test assertions checked wrong methods**
- **Found during:** Task 5 (Create unit tests)
- **Issue:** Tests checked `get_user_dm_messages` but visibility dispatcher sends embeds, not content strings
- **Fix:** Updated tests to check `get_user_dm_embeds` and verify embed attributes
- **Files modified:** tests/discord_bot/test_visibility_dispatcher.py

**3. [Rule 1 - Bug] gm_only not valid Visibility enum**
- **Found during:** Task 5 (Create unit tests)
- **Issue:** Tests used "gm_only" as visibility value but enum only has "keeper"
- **Fix:** Changed tests to use "keeper" which is the correct enum value for gm_only equivalent
- **Files modified:** tests/discord_bot/test_visibility_dispatcher.py

## Known Stubs

None - all visibility dispatcher stubs have been replaced with actual implementation.

## Verification

### Test Results
```
17 passed in tests/discord_bot/test_visibility_dispatcher.py
```

### Pre-existing Failures (Not Related to This Phase)
6 tests in COC rules fail due to pre-existing issues:
- Missing `siz` field in COCAttributes
- Missing `random` import in derived.py
- Missing `mp_cost` field in SpellCastResult
- Armor piercing logic issue

These are unrelated to visibility dispatcher and existed before this phase.

### Smoke Check
```bash
uv run python -m dm_bot.main smoke-check
# Same results: 6 pre-existing failures, 750 passed
```

## Commits

- `f43dc7d`: feat(track-e): Complete visibility dispatcher with Discord integration

## Next Steps

Phase E80 is complete. The visibility dispatcher is now fully functional with:
- Actual Discord channel sending for public messages
- DM sending for private messages
- DM sending for group messages
- Proper keeper-only content isolation
- Comprehensive test coverage

Ready for integration with the session orchestrator and campaign binding system.
