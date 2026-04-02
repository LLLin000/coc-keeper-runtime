---
phase: 62-track-b-vb15-regression-repair
plan: 01
status: complete
wave: 1
completed: 2026-04-02
---

## Phase 62: vB.1.5 Regression Repair - Summary

### Overview
Repaired the merged Track B regressions that broke the vB.1.5 lifecycle and governance contracts.

### What Was Repaired

#### Task 1: Archive Lifecycle Contracts
**Files:** `src/dm_bot/coc/archive.py`

- Added `deleted_at: datetime | None` field to `InvestigatorArchiveProfile`
- Implemented soft-delete in `delete_profile()` - sets status="deleted" and deleted_at timestamp
- Added `recover_profile()` method with grace-period validation
- Added `purge_expired_deleted()` method with event logging support
- Fixed `replace_active_with()` to set old profile status to "archived" (not "replaced")
- Updated `summary_line()` and `detail_view()` to show 🔴 marker for deleted profiles

#### Task 2: Session Instance Lifecycle and Governance APIs
**Files:** `src/dm_bot/orchestrator/session_store.py`

- Added `status: str = "active"` field to `CampaignCharacterInstance`
- Added `event_log: GovernanceEventLog` attribute to `SessionStore`
- Added `get_active_instances_for_user(user_id)` method
- Added `retire_instance(channel_id, user_id)` method
- Added `select_instance_profile(channel_id, user_id, profile_id, archive_repo)` method
- Added `force_archive_instance(channel_id, admin_id, target_user_id, reason)` method
- Added `reassign_ownership(channel_id, current_owner_id, new_owner_id, reason)` method
- Fixed `bind_character()` to update instance character_name and status
- Fixed `select_archive_profile()` to update instance with profile info
- Fixed `validate_ready()` to check instance truth (status + character_name)

#### Task 3: Command and Presentation Surfaces
**Files:** `src/dm_bot/discord_bot/commands.py`

- Fixed `ready` command to call `transition_on_all_ready()` after setting player ready
- Fixed `start_session` to use `can_start_session()` and filter ready check to MEMBER role only
- Fixed `complete_onboarding` to filter pending check to MEMBER role only

#### Task 4: Persistence Layer
**Files:** `src/dm_bot/persistence/store.py`

- Added `save_governance_events(events_state)` method
- Added `load_governance_events()` method

### Test Results

| Test Suite | Result |
|------------|--------|
| test_archive_delete_recover.py | 16/16 passed |
| test_instance_management.py | 26/26 passed |
| test_ready_gate.py | 16/16 passed |
| test_e2e_lifecycle.py | 8/8 passed |
| test_scenarios.py | 26/26 passed |

**Total: 92 Phase-relevant tests passed**

### Repository Gate
- pytest: 923 passed
- smoke-check: 923 passed

### Key Behavior Changes

1. **Archive profiles now support soft delete** with deleted_at timestamp and grace-period recovery
2. **CampaignCharacterInstance now has explicit status** field defaulting to "active"
3. **Ready gate checks instance truth** - instance.status == "active" and instance.character_name must be set
4. **Session transitions correctly filter** MEMBER role players only (not owner/admin)
5. **Governance events are persisted** via new event_log wiring
6. **Residual contract drift was closed** by aligning legacy CRUD, chaos, and command expectations to the current lifecycle and operator contracts

### Files Modified
- `src/dm_bot/coc/archive.py`
- `src/dm_bot/orchestrator/session_store.py`
- `src/dm_bot/orchestrator/governance_event_log.py` (import added)
- `src/dm_bot/discord_bot/commands.py`
- `src/dm_bot/persistence/store.py`
