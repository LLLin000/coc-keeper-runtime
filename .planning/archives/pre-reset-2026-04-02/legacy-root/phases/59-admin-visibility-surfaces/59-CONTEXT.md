# Phase 59: Admin Visibility Surfaces - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Build admin-facing visibility into all player profiles and ownership chains. This phase delivers:
- `/admin_profile_detail` — View any player's archive profile in detail (interactive selection)
- `/admin ownership_chain` — View full ownership chain for a player
- `/admin instances` — View all active campaign character instances across all campaigns (grouped by campaign)

</domain>

<decisions>
## Implementation Decisions

### D-01: Admin Profile Detail View (AV-02)
- **G-01:** Interactive selection from admin profile list
- Admin uses `/admin_profiles` to see the list, then selects a player to view their full archive profile detail
- Detail uses existing `InvestigatorArchiveProfile.detail_view()` method

### D-02: Ownership Chain Display Format (AV-03)
- **G-02:** Compact single-line format for ownership chain
- Format: `Discord_user → ArchiveProfile_name [status] → Member_role → Instance_character`
- Example: `User123 → 张三 [active] → Member → 调查员李四`

### D-03: Cross-Campaign Instance List (AV-04)
- **G-03:** Grouped by campaign
- Format: For each campaign, list all members and their active instances
- Shows: campaign_id, user_id, character_name, archive_profile_id, status

### D-04: Admin Command Output Visibility
- **G-04:** Mixed visibility
- List commands (`/admin_profiles`, `/admin instances`) default to ephemeral (admin-only)
- Detail views can have visibility set per-command (ephemeral or public)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Archive & Profiles
- `src/dm_bot/coc/archive.py` — `InvestigatorArchiveProfile`, `InvestigatorArchiveRepository`, `detail_view()`, `list_profiles()`, `list_all_profiles()`
- `src/dm_bot/coc/__init__.py` — Archive exports

### Campaign & Session
- `src/dm_bot/orchestrator/session_store.py` — `CampaignMember`, `CampaignCharacterInstance`, `CampaignSession.members`, `CampaignSession.character_instances`
- `SessionStore.list_members(channel_id)` — Returns campaign members
- `SessionStore.get_active_instances_for_user(user_id)` — Returns active instances (now checks `status == "active"`)
- `SessionStore.get_character_instance(channel_id, user_id)` — Get single instance

### Discord Commands
- `src/dm_bot/discord_bot/commands.py` — Existing slash command patterns with `@tree.command` decorator

### Requirements
- `.planning/workstreams/track-b/REQUIREMENTS.md` — AV-02, AV-03, AV-04
- `.planning/workstreams/track-b/ROADMAP.md` — Phase 59 description

### Prior Context
- `.planning/phases/55-profile-list-and-event-logging-foundation/55-CONTEXT.md` — D-02 (admin listing scope)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `InvestigatorArchiveProfile.detail_view()` — Full card display method already exists
- `InvestigatorArchiveRepository.list_all_profiles()` — Returns all profiles for admin listing
- `SessionStore.list_members(channel_id)` — Returns campaign members
- `SessionStore.get_active_instances_for_user()` — Returns user's active instances
- `CampaignCharacterInstance.status` field — Added in Phase 58

### Established Patterns
- Slash commands use `@tree.command` decorator
- Error handling with `ValidationResult` and error enums
- Profile listing uses `summary_line()` for compact display
- Instance status field: `"active"` or `"retired"` (Phase 58)

### Integration Points
- `/admin_profiles` → list members + list_all_profiles → filter by campaign → render
- `/admin instances` → iterate sessions → get active instances → group by campaign → render
- Detail view → `detail_view()` method on profile

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>
