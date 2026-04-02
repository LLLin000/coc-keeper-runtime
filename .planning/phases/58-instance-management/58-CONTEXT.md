# Phase 58: Instance Management - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

## Domain

## Phase Boundary

Manage campaign character instances including archival and re-selection.
This phase delivers:
- `retire_instance` operation (ILC-02)
- `select_instance_profile` operation (ILC-03)
- Instance transitions logged to governance event trail

## Decisions

### D-01: CampaignCharacterInstance Model Update
- Add `status: str = "active"` field to `CampaignCharacterInstance`
- Valid values: `"active"`, `"retired"`
- Default: `"active"` (existing instances remain compatible)

### D-02: Retire Instance Behavior (G-01)
- Set `status = "retired"` instead of deleting
- Clear `character_name` and `archive_profile_id` (null)
- Instance record is **retained** for audit trail
- User can re-select a profile after retiring

### D-03: Archive Profile as Name Source (G-02)
- When selecting archive profile for instance, use `archive_profile.name` as `character_name`
- `character_name` field is derived from archive profile's name
- No separate name input step required

### D-04: Profile Status Validation (G-03)
- When selecting archive profile for instance, validate `status == "active"`
- Only active profiles can be projected as campaign instances
- Error: `"档案 {id} 已归档，无法选用为战役投影。"`

### D-05: Operation Scope (G-04)
- Instance operations operate on **current campaign** (channel-bound)
- Same pattern as ILC-01 `get_active_instances_for_user()`

### D-06: Governance Event Names (G-05)
- `instance_retire` - when user retires their active campaign character instance
- `instance_select` - when user selects archive profile to project as instance

## Requirements

### ILC-02: Retire Campaign Character Instance
- User can archive their active campaign character instance (retire from campaign)
- Sets `status = "retired"`, clears `character_name`, `archive_profile_id`
- Logs `instance_retire` event

### ILC-03: Select Different Archive Profile for Instance
- User can select a different archive profile to project as a new campaign instance
- Validates profile `status == "active"`
- Updates `character_name` from archive profile
- Logs `instance_select` event

## Canonical References

### Archive & Profiles
- `src/dm_bot/coc/archive.py` — `InvestigatorArchiveProfile`, `InvestigatorArchiveRepository`
- `InvestigatorArchiveProfile.name` — character name source
- `InvestigatorArchiveRepository.list_profiles()` — returns active profiles

### Campaign & Session
- `src/dm_bot/orchestrator/session_store.py` — `CampaignCharacterInstance`, `CampaignSession.character_instances`
- `SessionStore.get_character_instance()` — get single instance
- `SessionStore.get_active_instances_for_user()` — get active instances
- `SessionStore.append_event()` — write governance events

### Discord Commands
- `src/dm_bot/discord_bot/commands.py` — Existing slash command patterns

## Existing Code Insights

### Reusable Assets
- `CampaignCharacterInstance` model exists (needs status field added)
- `get_active_instances_for_user()` returns all campaigns' active instances
- `GovernanceEventLog.append_event()` for audit trail
- Error enum pattern: `SelectProfileError`

### Integration Points
- `/my_character` or instance view → `SessionStore.get_character_instance()`
- Instance retire → `SessionStore` new method
- Instance select → `SessionStore` new method + validation against `InvestigatorArchiveRepository`

## Deferred Ideas

None — discussion stayed within phase scope
