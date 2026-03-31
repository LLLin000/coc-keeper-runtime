# Phase 57: Delete And Recovery Operations - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement permanent delete and grace-period recovery for profiles, plus clarify replace behavior.

This phase delivers:
- User can permanently delete an archived profile (not an active one)
- Deleted profiles enter a 7-day grace period before permanent erasure
- Deleted profiles visible in /profiles with "deleted" status during grace period
- User can recover a recently deleted profile within the grace period
- Replacing an active profile moves the old one to archived state
- All lifecycle operations write governance events

**Requirements:** PLC-04, PLC-05, PLC-06

</domain>

<decisions>
## Implementation Decisions

### D-05: Replace → Archived State
- When replacing an active profile, the old profile moves to "archived" state
- NOT "replaced" status — aligns with manual archive operation
- This is a change from current code behavior in `replace_active_with()`

### D-06: Grace Period Duration
- Deleted profiles remain in grace period for **7 days** before permanent erasure
- After 7 days, profile is automatically hard-deleted from storage

### D-07: Deleted Profile Visibility
- Deleted profiles show in `/profiles` with status "deleted" during grace period
- Users can see their deletable profiles and recovery option
- After grace period expires, profile is permanently removed (not visible anywhere)

### D-08: Permanent Delete Trigger
- **Auto-execution**: Grace period expiration triggers automatic permanent deletion
- No admin action required — self-service model
- Governance event logged at time of permanent deletion

### Carried Forward from Phase 56
- **D-01**: Detailed transition messages for all lifecycle operations
- **D-02**: Warn on archive if user has active campaign instances
- **D-03**: All lifecycle operations write governance events
- **D-04**: Block activate if user has active campaign instances

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Archive & Profiles
- `src/dm_bot/coc/archive.py` — `InvestigatorArchiveProfile`, `InvestigatorArchiveRepository`, `delete_profile()` (currently hard-delete), `replace_active_with()` (needs update to set archived instead of replaced)
- `src/dm_bot/coc/__init__.py` — Archive exports

### Campaign & Session
- `src/dm_bot/orchestrator/session_store.py` — `CampaignMember`, `CampaignCharacterInstance`, `SessionStore.append_event()`, `get_active_instances_for_user()` (added in Phase 56)

### Governance Event Log
- `src/dm_bot/orchestrator/governance_event_log.py` — `GovernanceEvent`, `GovernanceEventLog`

### Discord Commands
- `src/dm_bot/discord_bot/commands.py` — Existing lifecycle commands to enhance with delete/recover operations

### Requirements
- `.planning/workstreams/track-b/REQUIREMENTS.md` — PLC-04, PLC-05, PLC-06

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `InvestigatorArchiveRepository.delete_profile(user_id, profile_id)` — currently hard-deletes, needs modification for soft-delete with grace period
- `InvestigatorArchiveRepository.replace_active_with(user_id, profile_id)` — sets old to "replaced", needs to change to "archived"
- `SessionStore.append_event(...)` — governance event logging already exists
- `InvestigatorArchiveProfile.status` field — needs new "deleted" status value

### Established Patterns
- Status values: "active", "archived", "replaced" — need to add "deleted"
- Slash command responses use `ephemeral=True` for private feedback
- `Interaction.user.id` is user_id
- Profile lookup: `archive_repository.get_profile(user_id, profile_id)`

### What Needs Building
1. **New status**: Add "deleted" to profile status enum/values
2. **Soft delete**: Modify `delete_profile()` to set status="deleted" with timestamp instead of hard-deleting
3. **Grace period tracking**: Store `deleted_at` timestamp on profile
4. **Recovery command**: New `/recover_profile` command to restore deleted→active
5. **Permanent delete logic**: Background or on-access check to hard-delete after 7 days
6. **Update replace**: Change `replace_active_with()` to set old status="archived" not "replaced"
7. **Enhanced list**: `/profiles` shows deleted profiles during grace period with "deleted" status
8. **Governance events**: Log `profile_delete`, `profile_recover`, `profile_purge` operations

### Integration Points
- `/profiles` → show deleted profiles during grace period
- `/delete_profile <id>` → soft delete with grace period
- `/recover_profile <id>` → restore from deleted to active
- Auto-purge → hard delete after grace period expires

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 57-delete-and-recovery-operations*
*Context gathered: 2026-03-31*