# Phase 55: Profile List And Event Logging Foundation - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the foundation for profile lifecycle visibility and event logging. This phase delivers:
- `/profiles` command showing all user profiles with status
- `/admin_profiles` showing campaign member profiles to admins
- Governance event log schema for lifecycle operations
- Enforcement of one-active-instance per user per campaign

</domain>

<decisions>
## Implementation Decisions

### Event Log Schema
- **D-01:** Full governance event schema with:
  - `timestamp`: ISO datetime
  - `operation`: Operation type (e.g., `profile_activate`, `profile_archive`, `instance_retire`)
  - `user_id`: Target user
  - `profile_id`: Target profile
  - `campaign_id`: Campaign context (if applicable)
  - `operator_id`: Who performed the action (may differ from user_id for admin actions)
  - `before_state`: Profile/instance state before operation
  - `after_state`: Profile/instance state after operation
  - `reason`: Optional reason/notes (required for admin actions per AV-08)

### Admin Profile Listing Scope
- **D-02:** `/admin_profiles` lists profiles for current campaign members only
  - Shows: Discord user → archive profile → campaign member → campaign instance chain
  - Requires campaign to be bound to channel
  - Displays all members' profile status (active, archived, has instance, etc.)

### Profile Listing Display Format
- **D-03:** `/profiles` shows full card format for each profile
  - Reuse existing `detail_view()` from `InvestigatorArchiveProfile` 
  - Sort by: active first, then by name
  - Include status prominently in header

### One-Instance Enforcement
- **D-04:** `character_instances[user_id]` dict already ensures single instance per user per campaign
- No additional enforcement needed at Phase 55 — vB.1.4 established the single-key pattern

### Instance Listing
- **D-05:** Users can view their active campaign character instance via `/my_character` or similar
  - Shows: character name, archive profile reference, campaign name
  - Display in campaign context when channel is bound

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Archive & Profiles
- `src/dm_bot/coc/archive.py` — `InvestigatorArchiveProfile`, `InvestigatorArchiveRepository`, `detail_view()`, `list_profiles()`, `list_all_profiles()`, status field ("active", "archived", "replaced")
- `src/dm_bot/coc/__init__.py` — Archive exports

### Campaign & Session
- `src/dm_bot/orchestrator/session_store.py` — `CampaignMember`, `CampaignCharacterInstance`, `CampaignSession.members`, `CampaignSession.character_instances`, `SessionStore.list_members()`

### Discord Commands
- `src/dm_bot/discord_bot/commands.py` — Existing slash command patterns

### Requirements
- `.planning/workstreams/track-b/REQUIREMENTS.md` — PLC-01, PV-01 (profile listing), AV-01 (admin listing), AUD-01 (event log), ILC-01/ILC-04 (instance visibility/enforcement)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `InvestigatorArchiveProfile.detail_view()` — Full card display method already exists
- `InvestigatorArchiveRepository.list_profiles(user_id)` — Already returns sorted list (active first)
- `InvestigatorArchiveRepository.list_all_profiles()` — For admin listing
- `SessionStore.list_members(channel_id)` — Returns campaign members
- `CampaignSession.character_instances[user_id]` — Single instance per user already

### Established Patterns
- Status field on profiles: `"active"`, `"archived"`, `"replaced"` — existing in `InvestigatorArchiveProfile.status`
- Slash commands in `commands.py` use `@tree.command` decorator
- Error handling with `ValidationResult` and error enums
- Profile summary lines use `summary_line()` method

### Integration Points
- `/profiles` command → `InvestigatorArchiveRepository.list_profiles(user_id)` → render with `detail_view()`
- `/admin_profiles` command → `SessionStore.list_members()` + `InvestigatorArchiveRepository.list_all_profiles()` → filter by campaign
- Event log → new `GovernanceEventLog` class → append-only storage
- Instance viewing → `SessionStore.get_character_instance()` → display

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 55-profile-list-and-event-logging-foundation*
*Context gathered: 2026-03-31*
