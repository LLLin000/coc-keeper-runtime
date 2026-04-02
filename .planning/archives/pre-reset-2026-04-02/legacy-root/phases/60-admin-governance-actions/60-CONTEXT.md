# Phase 60: Admin Governance Actions - Context

**Gathered:** 2026-04-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement admin governance actions with full audit logging.
This phase delivers:
- `/admin_force_archive_profile` — Admin force-archives a player's active profile (AV-05)
- `/admin_force_archive_instance` — Admin force-retires a player's campaign instance (AV-06)
- `/admin_reassign_ownership` — Admin reassigns campaign ownership to another player (AV-07)
- All admin actions logged with timestamp, admin ID, target ID, and reason (AV-08)
- `/debug_status` — Shows recent governance events for a campaign (AUD-03)

</domain>

<decisions>
## Implementation Decisions

### D-01: Force-Archive Behavior (AV-05, AV-06)
- **Reuse existing methods**: Admin calls the same `archive_profile()` / `retire_instance()` as users
- Admin path identified by `operator_id != user_id` in governance event
- This maintains consistency with existing lifecycle patterns

### D-02: Reason Field Requirement (AV-08)
- **Reason is REQUIRED** for all admin actions
- **Minimum 10 characters** to ensure meaningful audit content
- Validation happens before operation executes

### D-03: Ownership Reassignment (AV-07)
- **Old owner becomes ADMIN** after reassignment (not MEMBER)
- New owner receives OWNER role
- Reassignment logged with full context:
  - `operation: "ownership_reassign"`
  - `user_id: new_owner_id`
  - `operator_id: admin_id`
  - `reason: <required>`
  - `before_state: {role: "OWNER"}`
  - `after_state: {role: "ADMIN"}`

### D-04: Debug Status Command (AUD-03)
- **Shows ALL events** (not filtered by type)
- **Default limit: 20** most recent events
- Uses existing `get_recent_events(campaign_id, limit=20)` method
- Accessible to ADMIN and OWNER roles in the campaign

### Agent Discretion
- Command naming: `/admin_force_archive_profile`, `/admin_force_archive_instance`, `/admin_reassign_ownership`, `/debug_status`
- Error messages follow existing patterns
- Discord interaction flow (ephemeral responses for admin feedback)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Archive & Profiles
- `src/dm_bot/coc/archive.py` — `InvestigatorArchiveProfile`, `InvestigatorArchiveRepository.archive_profile()`
- `src/dm_bot/coc/__init__.py` — Archive exports

### Campaign & Session
- `src/dm_bot/orchestrator/session_store.py` — `CampaignMember`, `CampaignCharacterInstance`, `CampaignRole`, `CampaignSession.members`, `retire_instance()`, `get_character_instance()`
- `SessionStore.append_event()` — write governance events
- `SessionStore.get_by_channel()` — get campaign session

### Governance Event Log
- `src/dm_bot/orchestrator/governance_event_log.py` — `GovernanceEvent`, `GovernanceEventLog.get_recent_events()`
- `reason` field: already in schema, marked "required for admin actions"

### Discord Commands
- `src/dm_bot/discord_bot/commands.py` — Existing admin command patterns (admin_profile_detail, admin_ownership_chain, admin_instances)
- `src/dm_bot/discord_bot/client.py` — Command registration pattern with `@tree.command`

### Requirements
- `.planning/workstreams/track-b/REQUIREMENTS.md` — AV-05, AV-06, AV-07, AV-08, AUD-03
- `.planning/workstreams/track-b/ROADMAP.md` — Phase 60 description

### Prior Context
- `.planning/phases/58-instance-management/58-CONTEXT.md` — D-02 (retire_instance behavior)
- `.planning/phases/57-delete-and-recovery-operations/57-CONTEXT.md` — D-05 to D-08 (profile lifecycle)
- `.planning/phases/59-admin-visibility-surfaces/59-CONTEXT.md` — Admin patterns, D-01 to D-04

</canonical_refs>

<codebase_context>
## Existing Code Insights

### Reusable Assets
- `InvestigatorArchiveRepository.archive_profile()` — existing user self-archive method
- `SessionStore.retire_instance()` — existing instance retire method
- `GovernanceEventLog.get_recent_events()` — returns sorted events with limit
- `CampaignRole` enum: OWNER, ADMIN, MEMBER
- Admin role check pattern: `member.role in {CampaignRole.OWNER, CampaignRole.ADMIN}`

### Established Patterns
- Admin commands check `operator_id != user_id` to distinguish admin vs self operations
- Reason field already part of GovernanceEvent schema
- Commands use `ephemeral=True` for admin feedback
- Existing admin commands in commands.py: admin_profile_detail, admin_ownership_chain, admin_instances

### Integration Points
- `/admin_force_archive_profile` → `archive_repository.archive_profile()` + governance event with reason
- `/admin_force_archive_instance` → `session_store.retire_instance()` + governance event with reason
- `/admin_reassign_ownership` → `session.members` role update + governance event
- `/debug_status` → `governance_event_log.get_recent_events()` + format output

</codebase_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 60-admin-governance-actions*
*Context gathered: 2026-04-01*
