# Requirements: vB.1.4 Identity Projection And Character Ownership

**Milestone:** vB.1.4
**Track:** Track B - 人物构建与管理层
**Primary Track:** Track B
**Secondary Impact:** Track C - Discord 交互层

## REQ-001: Explicit CampaignMember Model

**Category:** Architecture
**Priority:** MUST

Replace the implicit `member_ids: set[str]` with a dedicated `CampaignMember` model that carries:
- `user_id`: Discord user ID
- `campaign_id`: Campaign reference
- `joined_at`: Timestamp
- `ready: bool` (currently in `player_ready` dict)
- `selected_profile_id: str | None` (currently in `selected_profiles` dict)
- `active_character_name: str | None` (currently in `active_characters` dict)

**Acceptance Criteria:**
- [ ] `CampaignMember` dataclass exists in `session_store.py` or new file
- [ ] `CampaignSession.member_ids` replaced with `members: dict[str, CampaignMember]`
- [ ] All existing read paths updated
- [ ] All existing write paths updated

**Rationale:** The current dict-of-dicts structure makes ownership validation implicit and error-prone. A dedicated model makes membership state explicit.

---

## REQ-002: Ready Gate Validation

**Category:** Security
**Priority:** MUST

Before marking a user ready, the system MUST verify:
1. User is in `session.members`
2. User has a valid `selected_profile_id` (or explicit character name)

**Acceptance Criteria:**
- [ ] `/ready` command validates membership before proceeding
- [ ] `/ready` requires either `selected_profile_id` OR explicit `character_name` parameter
- [ ] Error message clearly states which gate failed
- [ ] Test coverage for "ready without membership" rejection

**Rationale:** Currently `/ready` does not verify membership, allowing non-members to mark ready.

---

## REQ-003: Select Profile Membership Validation

**Category:** Security
**Priority:** MUST

Before selecting a profile for a campaign, the system MUST verify:
1. User is in `session.members`
2. Profile belongs to the selecting user (`archive_profile.user_id == interaction.user.id`)

**Acceptance Criteria:**
- [ ] `/select_profile` validates membership before proceeding
- [ ] `/select_profile` validates profile ownership
- [ ] Error messages clearly state which gate failed
- [ ] Test coverage for both rejection cases

**Rationale:** Currently `/select_profile` has no membership or ownership verification.

---

## REQ-004: Admin/Owner Identity Separation

**Category:** Security
**Priority:** SHOULD

The system MUST distinguish between:
- **Campaign Owner**: The user who created/bound the campaign (`session.owner_id`)
- **Campaign Admin**: A user with guild admin privileges
- **Campaign Member**: A regular player in the campaign

**Acceptance Criteria:**
- [ ] `CampaignMember` includes a `role` field (owner, admin, member)
- [ ] Owner can be identified without checking `session.owner_id` separately
- [ ] Admin commands clearly show who issued them
- [ ] Player-facing identity never leaks admin status unless intentional

**Rationale:** Currently owner/admin identity bleeds into player identity paths. The owner is the one who bound the campaign, but there's no clear separation in membership records.

---

## REQ-005: One Active Instance Per Player Per Campaign

**Category:** Data Integrity
**Priority:** MUST

Each player can have at most ONE active `campaign_character_instance` per campaign. Attempting to create a second must either:
- Reject with clear error, OR
- Replace the existing instance (with audit trail)

**Acceptance Criteria:**
- [ ] `CampaignSession` enforces one active instance per user per campaign
- [ ] `/ready` rejects if user already has an active instance and no `character_name` override
- [ ] Projection creation logs when an instance is created or replaced
- [ ] Test coverage for duplicate instance prevention

**Rationale:** Currently there's no uniqueness enforcement beyond the in-memory map.

---

## REQ-006: Explicit Projection Contract

**Category:** Architecture
**Priority:** SHOULD

Create an explicit `CampaignCharacterInstance` concept that links:
- `campaign_id`: Which campaign
- `user_id`: Which player
- `archive_profile_id`: Which long-lived profile (or null for ad-hoc)
- `character_name`: Display name in campaign
- `panel_id`: Reference to `InvestigatorPanel`
- `created_at`: When projection was created
- `source`: "archive" | "ad_hoc" | "import"

**Acceptance Criteria:**
- [ ] Projection creation is centralized in one function
- [ ] All projection reads go through a consistent accessor
- [ ] Projection can be queried by campaign, user, or archive_profile
- [ ] `InvestigatorPanel.module_flags["archive_profile_id"]` replaced with proper linkage

**Rationale:** Currently the projection is implicit (InvestigatorPanel + session maps). Making it explicit enables lifecycle management in vB.1.5.

---

## REQ-007: Campaign Binding Guard

**Category:** Robustness
**Priority:** SHOULD

`join_campaign` and `leave_campaign` MUST guard against:
- Calling in an unbound channel (no campaign for this channel)
- Calling when session is in a phase that doesn't allow membership changes

**Acceptance Criteria:**
- [ ] `join_campaign` checks `get_by_channel()` returns non-None
- [ ] `leave_campaign` checks `get_by_channel()` returns non-None
- [ ] Both check `session.phase` allows membership changes
- [ ] Error messages are user-friendly, not stack traces

**Rationale:** Currently these can KeyError if called in an unbound channel.

---

## REQ-008: Archive-Campaign Ownership Chain

**Category:** Data Integrity
**Priority:** SHOULD

When selecting a profile for a campaign, verify:
1. Profile exists and is active
2. Profile belongs to the selecting user
3. Profile is not already selected in another campaign by the same user (or document the multi-select policy)

**Acceptance Criteria:**
- [ ] `/select_profile` validates profile existence and status
- [ ] `/select_profile` validates profile ownership
- [ ] Multi-campaign selection policy is explicit (allowed or rejected)
- [ ] Test coverage for each validation step

**Rationale:** Currently only `archive_repository.get_profile(user_id, profile_id)` provides ownership validation, and multi-campaign policy is implicit.

---

## REQ-009: Join Flow Membership Check

**Category:** Robustness
**Priority:** SHOULD

`/join_campaign` should verify:
1. User is not already a member (no duplicates)
2. Campaign allows joining in current phase

**Acceptance Criteria:**
- [ ] `/join_campaign` checks if user is already in `session.members`
- [ ] `/join_campaign` checks `session.phase` allows joining
- [ ] Duplicate join is idempotent (success or clear "already a member" message)
- [ ] Test coverage for duplicate join behavior

**Rationale:** Currently no duplicate check or phase validation.

---

## REQ-010: Persistent Campaign Member State

**Category:** Persistence
**Priority:** SHOULD

`CampaignMember` state (ready, selected_profile_id, active_character_name) should be persisted alongside `CampaignSession` in the JSON store.

**Acceptance Criteria:**
- [ ] `CampaignMember` fields are serializable to JSON
- [ ] `PersistenceStore.save_campaign_session()` includes member state
- [ ] `PersistenceStore.load_campaign_session()` restores member state
- [ ] Test coverage for member state round-trip

**Rationale:** Currently `player_ready`, `selected_profiles`, and `active_characters` are persisted, but scattered across separate dicts. Consolidating into `CampaignMember` requires updated persistence.

---

## Secondary Impact on Track C

Track C (Discord 交互层) will need to consume the stricter ownership model:

- `/join_campaign` now validates membership
- `/ready` now validates membership and profile selection
- `/select_profile` now validates membership and ownership
- Error messages must be user-friendly (not internal errors)

**Contracts Changed:**
- `SessionStore.join_campaign()` - may return validation errors
- `SessionStore.ready_for_adventure()` - may return validation errors
- `SessionStore.select_archive_profile()` - may return validation errors

---

## Phase Decomposition

Based on dependencies, these requirements could be split into phases:

**Phase 1: Foundation (REQ-001)**
- Create `CampaignMember` model
- Migrate existing data structures

**Phase 2: Validation Gates (REQ-002, REQ-003, REQ-007, REQ-009)**
- Add membership verification to all commands
- Add guard clauses for robustness

**Phase 3: Identity Separation (REQ-004)**
- Add role field to `CampaignMember`
- Separate owner/admin/member paths

**Phase 4: Projection Contract (REQ-006, REQ-008)**
- Create explicit projection linkage
- Enforce ownership chain

**Phase 5: Persistence (REQ-010)**
- Update persistence layer for new model

---

*Generated by GSD new-milestone workflow for vB.1.4*
