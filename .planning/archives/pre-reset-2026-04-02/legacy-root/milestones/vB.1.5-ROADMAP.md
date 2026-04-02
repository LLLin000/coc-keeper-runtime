# Milestone vB.1.5: Character Lifecycle And Governance Surface

**Status:** ✅ SHIPPED 2026-04-01
**Phases:** 55-61
**Total Plans:** 10

## Overview

Track B milestone completing the character lifecycle and governance surface layer. This milestone delivers the full player-facing archive lifecycle (create → activate → archive → delete → recover), instance management (select → retire → reactivate), admin visibility commands, admin governance actions with audit logging, and integration polish tying ready validation to the instance model.

## Phases

### Phase 55: Profile List And Event Logging Foundation

**Goal:** Establish profile list command and governance event log foundation
**Depends on:** Phase 54
**Plans:** 2 plans

Plans:
- [x] 55-01: GovernanceEventLog + SessionStore Integration
- [x] 55-02: Profile list command with event logging

**Details:**
- Added GovernanceEventLog class for auditable event capture
- Integrated event logging into SessionStore for member join/leave events
- Added `/profiles` command with detail_view and status icons
- Added `/my_character` command for campaign character instance overview
- Added `/admin_profiles` command for admin visibility

### Phase 56: Archive Lifecycle Operations

**Goal:** Implement archive activate and enhanced archive commands with event logging
**Depends on:** Phase 55
**Plans:** 1 plan

Plans:
- [x] 56-01: Enhanced archive/activate commands with event logging and detailed messages

**Details:**
- `activate_profile()` sets status='active' with governance event
- `/archive_profile` now shows instance warnings when archiving
- `/activate_profile` shows which campaigns have active instances

### Phase 57: Delete And Recovery Operations

**Goal:** Add soft-delete with 7-day grace period, recover, and purge
**Depends on:** Phase 56
**Plans:** 2 plans

Plans:
- [x] 57-01: TDD - Archive Repository soft-delete/recover/purge methods
- [x] 57-02: Discord Commands for delete/recover

**Details:**
- Added `deleted_at` field to InvestigatorArchiveProfile
- `delete_profile()` soft-deletes (status='deleted', deleted_at=now)
- `recover_profile()` restores deleted→active within 7-day grace
- Fixed `replace_active_with()` - sets old to 'archived' (not 'replaced')
- Added `purge_expired_deleted()` - auto-permanent delete after grace period
- Added `/delete_profile` and `/recover_profile` commands
- Updated `/profiles` to show 🔴 for deleted profiles with grace countdown

### Phase 58: Instance Management

**Goal:** Implement instance retire and select operations
**Depends on:** Phase 57
**Plans:** 1 plan

Plans:
- [x] 58-01: Instance retire and select methods

**Details:**
- Added `status: str = "active"` field to CampaignCharacterInstance
- `get_active_instances_for_user()` checks status == "active" and character_name
- `retire_instance()` sets status='retired', clears character_name and archive_profile_id
- `select_instance_profile()` validates profile status=='active', sets character_name from archive
- Added 18 passing tests for instance management

### Phase 59: Admin Visibility Surfaces

**Goal:** Implement admin commands for profile and instance visibility
**Depends on:** Phase 58
**Plans:** 1 plan

Plans:
- [x] 59-01: Admin Visibility Commands (AV-02, AV-03, AV-04)

**Details:**
- `/admin_profile_detail` - interactive profile selection + full detail view
- `/admin_ownership_chain` - traces full ownership chain per user
- `/admin_instances` - all active instances grouped by campaign
- All commands require admin/owner role

### Phase 60: Admin Governance Actions

**Goal:** Implement admin governance operations with full audit logging
**Depends on:** Phase 59
**Plans:** 2 plans

Plans:
- [x] 60-01: Admin governance methods + Discord commands
- [x] 60-02: GovernanceEventLog persistence

**Details:**
- `force_archive_instance()` - admin retire with audit reason
- `reassign_ownership()` - owner transfer with role demotion
- `force_archive()` in ArchiveRepository - admin profile archival
- `/admin_force_archive_profile`, `/admin_force_archive_instance`, `/admin_reassign_ownership`
- `/admin_governance_events` (renamed from debug_status to avoid conflict)
- GovernanceEventLog persistence wired via PersistenceStore

### Phase 61: Integration And Polish

**Goal:** End-to-end integration testing and presentation polish
**Depends on:** Phase 60
**Plans:** 1 plan

Plans:
- [x] 61-01: Integration and Polish (PV-02, PV-04)

**Details:**
- PV-04: `validate_ready()` now checks `instance.status == "active"` and `instance.character_name` instead of `member.selected_profile_id`
- PV-02: `profile_detail()` shows campaign instance context (campaign_id, status, character_name)
- Fixed 8 tests to use instance model instead of selected_profile_id/active_character_name
- Created E2E lifecycle tests in `test_e2e_lifecycle.py`

---

## Milestone Summary

**Key Accomplishments:**

1. **GovernanceEventLog** — Complete audit trail for all lifecycle operations (join, leave, activate, archive, delete, recover, select, retire, force-archive, ownership reassign)

2. **Full Profile Lifecycle** — PLC-01 through PLC-06 complete: list → activate → archive → replace → delete → recover with 7-day grace

3. **Instance Model** — CampaignCharacterInstance with status='active'/'retired', character_name, archive_profile_id; replaces selected_profile_id/active_character_name on member

4. **Admin Visibility** — Three commands for admin oversight: profile detail, ownership chain, cross-campaign instance list

5. **Admin Governance** — Three actions with audit reasons: force-archive profile, force-archive instance, reassign ownership; all logged with timestamp, admin ID, target ID, reason

6. **Persistence** — GovernanceEventLog survives bot restarts via SQLite persistence

7. **Ready Gate Fix** — validate_ready() now correctly checks instance model instead of deprecated member fields

**Technical Decisions:**
- Soft-delete uses 7-day grace period before permanent purge
- Force-archive requires owner role (not admin)
- Ownership reassignment demotes old owner to ADMIN
- Instance status is source of truth for ready validation

**Files Modified:**
- `src/dm_bot/orchestrator/session_store.py`
- `src/dm_bot/coc/archive.py`
- `src/dm_bot/discord_bot/commands.py`
- `src/dm_bot/discord_bot/client.py`
- `src/dm_bot/persistence/store.py`
- `tests/test_ready_gate.py`
- `tests/test_ready_commands.py`
- `tests/test_multi_user_session.py`
- `tests/test_lobby_flow.py`
- `tests/test_discord_commands.py`
- `tests/test_instance_management.py`
- `tests/test_e2e_lifecycle.py` (new)

**Test Coverage:**
- 513 tests passing
- `uv run python -m dm_bot.main smoke-check`: 513 passed

---

_For current project status, see .planning/workstreams/track-b/ROADMAP.md_
