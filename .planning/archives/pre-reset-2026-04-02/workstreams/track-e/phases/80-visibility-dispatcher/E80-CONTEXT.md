# Phase E80 Context: Visibility Dispatcher Completion

## Goal
Complete the visibility dispatcher to actually send messages to Discord channels and DMs, resolving the 3 TODOs in visibility_dispatcher.py.

## Background

### Current State
The `VisibilityDispatcher` class exists but has 3 unresolved TODOs:
1. Line 89: Send to actual Discord channel
2. Line 133: Fetch user and send DM
3. Line 168: Identify group members and send DMs

### Current Implementation
```python
class VisibilityDispatcher:
    async def dispatch(self, aggregated, character_to_user: dict[str, str]) -> None:
        # Routes to _send_public, _send_private, _send_group, _log_keeper_only
        
    async def _send_public(self, consequences: list) -> None:
        # TODO: Send to actual Discord channel
        
    async def _send_private(self, consequences: list, character_to_user: dict) -> None:
        # TODO: Fetch user and send DM
        
    async def _send_group(self, consequences: list, character_to_user: dict) -> None:
        # TODO: Identify group members and send DMs
```

## Design Decisions

### 1. Discord Client Integration

**Decision**: Use existing discord.Client from discord_bot module

**Rationale**:
- Bot already has Discord client instance
- Should inject via constructor or use singleton pattern
- Need channel_id mapping for campaigns

### 2. Message Formatting

**Decision**: Use Discord embeds for structured output

**Rationale**:
- Better readability than plain text
- Supports titles, fields, colors
- Consistent with modern Discord bots

### 3. Error Handling

**Decision**: Log errors, don't crash on send failures

**Rationale**:
- Network issues shouldn't break game flow
- Messages can be retried or logged for manual delivery
- Keep game state consistent

### 4. Testing Strategy

**Decision**: Create FakeDiscordClient for testing

**Rationale**:
- Can't rely on real Discord in tests
- Need to verify messages sent to correct recipients
- Track message content for assertions

## Implementation Requirements

### VIS-DISP-01: Public Channel Messages
- Send to campaign's bound channel
- Format as embed with consequence summary
- Handle empty consequence lists gracefully

### VIS-DISP-02: Private DMs
- Fetch Discord user by ID
- Send DM with private consequences
- Handle users with DMs disabled

### VIS-DISP-03: Group Messages
- Identify all group members
- Send same message to each member via DM
- Handle members who have left server

### VIS-DISP-04: Keeper-Only Logging
- Already implemented - just verify
- Log to diagnostics service
- No Discord output

### VIS-DISP-05: Visibility Leak Prevention
- Unit tests verify gm_only never reaches players
- Integration tests verify full flow
- Audit logging for security

## Files to Modify

- `src/dm_bot/discord_bot/visibility_dispatcher.py` - Implement TODOs
- `src/dm_bot/discord_bot/client.py` - Add helper methods if needed
- `tests/discord_bot/test_visibility_dispatcher.py` - Unit tests
- `tests/fakes/discord.py` - Add FakeDiscordClient
- `tests/scenarios/contract/test_visibility_leak.yaml` - Contract test

## Success Criteria

- [ ] Messages sent to Discord channels appear in correct channels
- [ ] Private messages reach individual players
- [ ] Group DMs work for KP-to-party communications
- [ ] gm_only content never leaks to player channels
- [ ] All 3 TODOs resolved and tested
- [ ] Error handling for network issues
- [ ] Contract tests verify visibility isolation
