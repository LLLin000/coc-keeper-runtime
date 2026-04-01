# Requirements Archive: vB.1.5

**Milestone:** Character Lifecycle And Governance Surface
**Archived:** 2026-04-01
**Total Requirements:** 24

## Player-Facing Profile Lifecycle

- [x] **PLC-01**: User can view list of all their archive profiles (active and archived) via `/profiles`
- [x] **PLC-02**: User can activate an archived profile to make it available for campaign selection
- [x] **PLC-03**: User can archive their active profile (soft-delete) without deleting it permanently
- [x] **PLC-04**: User can replace an active profile with a new one, moving the old to archived state
- [x] **PLC-05**: User can permanently delete an archived profile (not an active one)
- [x] **PLC-06**: User can recover a recently deleted profile within a grace period

## Player-Facing Instance Lifecycle

- [x] **ILC-01**: User can view their active campaign character instance(s) for joined campaigns
- [x] **ILC-02**: User can archive their active campaign character instance (retire from campaign)
- [x] **ILC-03**: User can select a different archive profile to project as a new campaign instance
- [x] **ILC-04**: User cannot have more than one active campaign instance per campaign (enforced)

## Player-Facing Visibility

- [x] **PV-01**: `/profiles` command shows each profile's status: active, archived, deleted, or active-instance
- [x] **PV-02**: `/profile_detail` shows the selected profile's full archive card with instance context
- [x] **PV-03**: User sees clear transition messages when activating, archiving, or replacing profiles
- [x] **PV-04**: User cannot ready into a campaign without a valid active character instance (enforced via instance model)

## Admin-Facing Visibility

- [x] **AV-01**: Admin can list all player archive profiles in the campaign via `/admin_profiles`
- [x] **AV-02**: Admin can view any player's archive profile in detail (interactive selection)
- [x] **AV-03**: Admin can view ownership chain: Discord user → archive profile → campaign member → campaign instance
- [x] **AV-04**: Admin can view all active campaign character instances across all players (grouped by campaign)

## Admin Governance Actions

- [x] **AV-05**: Admin can force-archive a player's active profile (with audit reason)
- [x] **AV-06**: Admin can force-archive a player's campaign character instance (with audit reason)
- [x] **AV-07**: Admin can reassign campaign ownership to a different player
- [x] **AV-08**: All admin governance actions are logged with timestamp, admin ID, target ID, and reason

## Audit Trail

- [x] **AUD-01**: All lifecycle operations (activate, archive, replace, delete, recover) are recorded in event log
- [x] **AUD-02**: All admin governance actions are recorded with full context
- [x] **AUD-03**: `/debug_status` (now `/admin_governance_events`) shows recent governance events for a campaign

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PLC-01 | Phase 55 | Complete |
| PLC-02 | Phase 56 | Complete |
| PLC-03 | Phase 56 | Complete |
| PLC-04 | Phase 57 | Complete |
| PLC-05 | Phase 57 | Complete |
| PLC-06 | Phase 57 | Complete |
| ILC-01 | Phase 55 | Complete |
| ILC-02 | Phase 58 | Complete |
| ILC-03 | Phase 58 | Complete |
| ILC-04 | Phase 55 | Complete |
| PV-01 | Phase 55 | Complete |
| PV-02 | Phase 61 | Complete |
| PV-03 | Phase 56 | Complete |
| PV-04 | Phase 61 | Complete |
| AV-01 | Phase 59 | Complete |
| AV-02 | Phase 59 | Complete |
| AV-03 | Phase 59 | Complete |
| AV-04 | Phase 59 | Complete |
| AV-05 | Phase 60 | Complete |
| AV-06 | Phase 60 | Complete |
| AV-07 | Phase 60 | Complete |
| AV-08 | Phase 60 | Complete |
| AUD-01 | Phase 55 | Complete |
| AUD-02 | Phase 56 | Complete |
| AUD-03 | Phase 60 | Complete |

**Coverage:**
- vB.1.5 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0 ✓

---

_For current requirements, see .planning/workstreams/track-b/REQUIREMENTS.md_
