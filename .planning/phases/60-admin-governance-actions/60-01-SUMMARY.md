# Phase 60-01 Summary: Admin Governance Actions

## Completed

Wave 1: Core implementation of admin governance commands.

## Files Modified

### `tests/test_instance_management.py`
Added 8 new tests:
- `TestForceArchiveInstanceAdmin` (3 tests): logs_event_with_reason, admin_must_be_owner, target_not_member_raises
- `TestReassignOwnership` (5 tests): owner_to_member, logs_event, admin_forbidden, target_not_member_raises, to_self_forbidden

### `src/dm_bot/orchestrator/session_store.py`
Added 2 methods:
- `force_archive_instance(channel_id, admin_id, target_user_id, reason)` - Admin force-retires a user's instance. Only owner can do this. Logs `instance_force_archive` event.
- `reassign_ownership(channel_id, current_owner_id, new_owner_id, reason)` - Transfer ownership. Old owner becomes ADMIN. Logs `ownership_reassign` event.

### `src/dm_bot/discord_bot/commands.py`
Added 4 handlers:
- `admin_force_archive_profile(interaction, profile_id, reason)` - AV-05. Reason min 10 chars.
- `admin_force_archive_instance(interaction, user_id, reason)` - AV-06. Only owner can do this.
- `admin_reassign_ownership(interaction, user_id, reason)` - AV-07. Only current owner can reassign.
- `admin_governance_events(interaction)` - AUD-03. Shows 20 most recent governance events.

### `src/dm_bot/discord_bot/client.py`
Registered 4 new commands:
- `/admin_force_archive_profile profile_id:<id> reason:<text>`
- `/admin_force_archive_instance user_id:<@mention> reason:<text>`
- `/admin_reassign_ownership user_id:<@mention> reason:<text>`
- `/admin_governance_events`

## Verification

```
uv run pytest -q: 500 passed
uv run python -m dm_bot.main smoke-check: 500 passed
```

## Requirements Covered

| Requirement | Implementation |
|-------------|----------------|
| AV-05: Admin force-archive profile | admin_force_archive_profile |
| AV-06: Admin force-archive instance | admin_force_archive_instance (owner only) |
| AV-07: Reassign ownership | admin_reassign_ownership |
| AV-08: All admin actions logged | GovernanceEvent with reason field |
| AUD-03: debug_status | admin_governance_events |
