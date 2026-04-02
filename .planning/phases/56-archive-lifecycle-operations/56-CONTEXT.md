# Phase 56: Archive Lifecycle Operations - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement profile lifecycle operations (activate, archive) with full governance event logging and clear user-facing transition messages.

This phase delivers:
- User can activate an archived profile, making it available for campaign selection
- User can archive their active profile (soft-delete), moving it to archived state
- User sees detailed transition messages confirming each operation
- All lifecycle operations are logged with full context (not just admin actions)

**Requirements:** PLC-02, PLC-03, PV-03, AUD-02

</domain>

<decisions>
## Implementation Decisions

### D-01: Detailed Transition Messages (PV-03)
- When archiving or activating a profile, show detailed message with:
  - Profile name
  - Operation performed
  - Before state → After state
  - If profile has active campaign instances, include warning listing affected campaigns
- Format example for archive:
  ```
  ✓ 已归档「调查员名」
  状态：active → archived
  该档案已从可用列表移除。
  ⚠️ 注意：你在战役 [campaign_id] 中有活跃角色 [角色名]，如需退役请在游戏大厅手动处理。
  ```
- Format example for activate:
  ```
  ✓ 已激活「调查员名」
  状态：archived → active
  该档案现已可用于战役选择。
  ```

### D-02: Campaign Instance Cleanup on Archive (PLC-03)
- When archiving an active profile, DO NOT auto-retire campaign character instances
- Instead, check all campaigns where user has a `character_instance` with `character_name` set
- If any found, include warning in transition message listing affected campaigns and instance names
- User must manually retire/leave campaign instances (Phase 58 scope)

### D-03: Event Logging Scope (AUD-02)
- ALL lifecycle operations write governance events, not just admin actions
- Operations to log: `profile_archive`, `profile_activate`
- Each event includes full context: `timestamp`, `operation`, `user_id`, `profile_id`, `campaign_id` (if applicable), `operator_id` (=user_id for self-actions), `before_state`, `after_state`, `reason` (optional for player actions)

### D-04: Activate Conflict Detection
- Before activating a profile, check ALL campaigns in SessionStore for any active `character_instance` belonging to this user
- If user has any active instance (character_name set), BLOCK activation with error message:
  ```
  无法激活档案「X」，因为你在战役 [campaign_id] 中有活跃角色 [角色名]。
  请先在游戏大厅使用 /retire 或 /leave 退役后再激活。
  ```
- Prevents state corruption from orphaned instances

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Archive & Profiles
- `src/dm_bot/coc/archive.py` — `InvestigatorArchiveProfile`, `InvestigatorArchiveRepository`, `detail_view()`, `archive_profile()`, `replace_active_with()`, status field ("active", "archived", "replaced")
- `src/dm_bot/coc/__init__.py` — Archive exports

### Campaign & Session
- `src/dm_bot/orchestrator/session_store.py` — `CampaignMember`, `CampaignCharacterInstance`, `SessionStore.character_instances`, `SessionStore.append_event()`, `SessionStore.get_character_instance()`, `channels_selecting_profile()`

### Governance Event Log
- `src/dm_bot/orchestrator/governance_event_log.py` — `GovernanceEvent`, `GovernanceEventLog`, schema with `timestamp`, `operation`, `user_id`, `profile_id`, `campaign_id`, `operator_id`, `before_state`, `after_state`, `reason`

### Discord Commands
- `src/dm_bot/discord_bot/commands.py` — Existing `archive_profile()` (line 694), `activate_profile()` (line 711) — these need enhancement with event logging and detailed messages
- Channel enforcement via `check_channel()`

### Persistence
- `_persist_archives()` — saves archive state after operations
- `_persist_sessions()` — saves session state after operations

### Requirements
- `.planning/workstreams/track-b/REQUIREMENTS.md` — PLC-02, PLC-03, PV-03, AUD-02

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `InvestigatorArchiveRepository.archive_profile(user_id, profile_id)` — already sets status to "archived"
- `InvestigatorArchiveRepository.replace_active_with(user_id, profile_id)` — already handles old active → "replaced" and new → "active"
- `CampaignSession.character_instances[user_id]` — dict keyed by user_id with `CampaignCharacterInstance` values
- `SessionStore.append_event(...)` — already exists for governance event logging
- `SessionStore.channels_selecting_profile(user_id, profile_id)` — returns list of channel_ids where profile is selected

### Established Patterns
- Status field on profiles: `"active"`, `"archived"`, `"replaced"` — existing in `InvestigatorArchiveProfile.status`
- Slash command responses use `ephemeral=True` for private feedback
- `Interaction.user.id` is the user_id for Discord users
- Profile lookup: `archive_repository.get_profile(user_id, profile_id)`

### What Needs Building
1. **Conflict detection** — new method to check all campaigns for active instances before activate
2. **Instance warning builder** — new helper to build campaign instance warning text
3. **Enhanced archive command** — add governance event + detailed message + instance warning
4. **Enhanced activate command** — add conflict check + governance event + detailed message
5. **Governance events** — call `session_store.append_event()` in both operations

</code_context>

<deferred>
## Deferred Ideas

- Auto-retire campaign instances on archive — deferred to Phase 58 (Instance Management)
- Permanent delete with grace period recovery — Phase 57
- Admin force-archive with reason — Phase 60

</deferred>

---
*Phase: 56-archive-lifecycle-operations*
*Context gathered: 2026-03-31*
