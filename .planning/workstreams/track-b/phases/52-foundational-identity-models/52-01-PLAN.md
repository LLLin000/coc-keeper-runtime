---
phase: 52-foundational-identity-models
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/orchestrator/session_store.py
  - tests/test_identity_models.py
  - tests/test_persistence_store.py
autonomous: true
requirements:
  - REQ-001
  - REQ-004
  - REQ-006
  - REQ-010
user_setup: []

must_haves:
  truths:
    - "CampaignMember model exists with user_id, campaign_id, joined_at, role, ready, selected_profile_id, active_character_name"
    - "CampaignCharacterInstance model exists with campaign_id, user_id, archive_profile_id, character_name, panel_id, created_at, source"
    - "CampaignSession.members replaces member_ids as the canonical membership store"
    - "CampaignSession.character_instances replaces the implicit InvestigatorPanel+session maps"
    - "All old field access patterns (member_ids, active_characters, player_ready, selected_profiles) still work via backward-compatible computed properties"
    - "dump_sessions serializes CampaignMember and CampaignCharacterInstance to JSON-safe dicts"
    - "load_sessions restores CampaignMember and CampaignCharacterInstance from persisted JSON"
    - "Round-trip: dump then load produces structurally identical data"
  artifacts:
    - path: "src/dm_bot/orchestrator/session_store.py"
      provides: "CampaignMember, CampaignCharacterInstance, updated CampaignSession, updated SessionStore"
      contains: "class CampaignMember, class CampaignCharacterInstance"
    - path: "tests/test_identity_models.py"
      provides: "TDD tests for model construction, serialization, session operations, backward compat"
    - path: "tests/test_persistence_store.py"
      provides: "Updated persistence round-trip test using new model structure"
  key_links:
    - from: "CampaignSession.members"
      to: "commands.py, visibility.py, onboarding_controller.py"
      via: "backward-compatible member_ids property"
      pattern: "session.member_ids"
    - from: "CampaignSession.character_instances"
      to: "commands.py"
      via: "backward-compatible active_characters property"
      pattern: "session.active_characters"
    - from: "CampaignMember"
      to: "dump_sessions/load_sessions"
      via: "model_dump()/model_validate() serialization"
      pattern: "model_dump|model_validate"
    - from: "CampaignCharacterInstance"
      to: "dump_sessions/load_sessions"
      via: "model_dump()/model_validate() serialization"
      pattern: "model_dump|model_validate"
---

# Phase 52: Foundational Identity Models

## Objective

Replace the primitive set-of-strings and dict-of-strings structures in `CampaignSession` with structured Pydantic models (`CampaignMember` and `CampaignCharacterInstance`). This phase is purely about internal data structures — no Discord command enforcement.

**Purpose:** Make campaign membership and character ownership explicit, typed, and auditable. The current implicit string-keyed maps (`member_ids: set[str]`, `active_characters: dict[str, str]`, etc.) make ownership validation error-prone and prevent lifecycle management in future phases.

**Output:**
- `CampaignMember` Pydantic model in `session_store.py`
- `CampaignCharacterInstance` Pydantic model in `session_store.py`
- `CampaignSession` refactored to use `members: dict[str, CampaignMember]` and `character_instances: dict[str, CampaignCharacterInstance]`
- Backward-compatible computed properties so existing consumers (commands.py, visibility.py, onboarding_controller.py) keep working
- Updated persistence serialization in `dump_sessions`/`load_sessions`
- TDD tests covering model construction, serialization, session operations, and round-trip persistence

## Execution Context

@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md

## Context

@.planning/workstreams/track-b/ROADMAP.md
@.planning/workstreams/track-b/REQUIREMENTS-vB.1.4.md
@.planning/research/vB.1.4-identity-research-SUMMARY.md

@src/dm_bot/orchestrator/session_store.py
@src/dm_bot/persistence/store.py
@src/dm_bot/coc/archive.py
@src/dm_bot/coc/panels.py

### Existing Interfaces (consumers that must keep working)

From `src/dm_bot/orchestrator/session_store.py` — current `CampaignSession` fields accessed externally:

```python
# commands.py accesses:
session.member_ids                    # set[str] — line 333, 823, 839, 878, 880, 887, 947, 957, 1272, 1422
session.active_characters             # dict[str, str] — line 254, 291, 320, 968, 971, 1015
session.player_ready                  # dict[str, bool] — line 822
session.action_submitters             # set[str] — line 1004
session.set_player_ready()            # line 821
session.set_player_action()           # line 1607, 1621
session.get_pending_member_names()    # line 1628

# visibility.py accesses:
session.member_ids                    # line 100, 109, 173, 181
session.player_ready.get(uid)         # line 109, 193
session.is_onboarding_complete(uid)   # line 100

# onboarding_controller.py accesses:
session.member_ids                    # line 44, 61

# diagnostics/service.py accesses:
session.selected_profiles.items()     # line 65

# SessionStore methods accessed externally:
store.bind_campaign()                 # commands.py line 173
store.join_campaign()                 # commands.py line 341
store.leave_campaign()                # commands.py line 352
store.bind_character()                # commands.py line 629, 768, 784, 1745
store.active_character_for()          # commands.py line 1590, 1847
store.get_by_channel()                # many places
store.select_archive_profile()        # persistence test
```

### Phase 52 Scope Boundary

**IN SCOPE:**
- New Pydantic model definitions
- Internal refactoring of `CampaignSession` fields
- Backward-compatible computed properties for old field names
- Updated `SessionStore` methods that construct `CampaignMember` instances
- Updated serialization in `dump_sessions`/`load_sessions`
- Tests

**OUT OF SCOPE (Phase 53+):**
- Updating commands.py to use new models directly
- Membership validation gates in Discord commands
- Duplicate join prevention
- Ready-gate enforcement

---

## Tasks

### Task 1 (TDD): Define CampaignMember and CampaignCharacterInstance Models

**TDD cycle:** RED → GREEN

**Test file:** `tests/test_identity_models.py`

**Behavior (tests to write first):**

```python
# CampaignMember tests
def test_campaign_member_constructs_with_defaults():
    member = CampaignMember(user_id="u1", campaign_id="c1")
    assert member.role == "member"
    assert member.ready is False
    assert member.selected_profile_id is None
    assert member.active_character_name is None
    assert member.joined_at is not None  # auto-set to now

def test_campaign_member_owner_role():
    member = CampaignMember(user_id="u1", campaign_id="c1", role=CampaignRole.OWNER)
    assert member.role == CampaignRole.OWNER

def test_campaign_member_serializes_to_dict():
    member = CampaignMember(user_id="u1", campaign_id="c1", role=CampaignRole.ADMIN)
    data = member.model_dump()
    assert data["user_id"] == "u1"
    assert data["role"] == "admin"

def test_campaign_member_deserializes_from_dict():
    data = {"user_id": "u1", "campaign_id": "c1", "joined_at": "2026-03-29T10:00:00", "role": "admin", "ready": True, "selected_profile_id": "p1", "active_character_name": "Alice"}
    member = CampaignMember.model_validate(data)
    assert member.ready is True
    assert member.active_character_name == "Alice"

# CampaignCharacterInstance tests
def test_character_instance_constructs_with_defaults():
    inst = CampaignCharacterInstance(campaign_id="c1", user_id="u1", character_name="Alice")
    assert inst.source == "archive"
    assert inst.archive_profile_id is None
    assert inst.panel_id is None
    assert inst.created_at is not None

def test_character_instance_serializes_to_dict():
    inst = CampaignCharacterInstance(campaign_id="c1", user_id="u1", character_name="Alice", archive_profile_id="prof-1", source="archive")
    data = inst.model_dump()
    assert data["archive_profile_id"] == "prof-1"
    assert data["source"] == "archive"

def test_character_instance_deserializes_from_dict():
    data = {"campaign_id": "c1", "user_id": "u1", "character_name": "Alice", "archive_profile_id": None, "panel_id": None, "created_at": "2026-03-29T10:00:00", "source": "ad_hoc"}
    inst = CampaignCharacterInstance.model_validate(data)
    assert inst.source == "ad_hoc"
```

**Action:**

1. Create `tests/test_identity_models.py` with the test cases above
2. Run `uv run pytest tests/test_identity_models.py -x` — expect ALL FAIL (RED)
3. In `src/dm_bot/orchestrator/session_store.py`:
   - Add `class CampaignRole(str, Enum)` with values `OWNER = "owner"`, `ADMIN = "admin"`, `MEMBER = "member"`
   - Add `class CampaignMember(BaseModel)` with fields:
     - `user_id: str`
     - `campaign_id: str`
     - `joined_at: datetime = Field(default_factory=datetime.now)`
     - `role: CampaignRole = CampaignRole.MEMBER`
     - `ready: bool = False`
     - `selected_profile_id: str | None = None`
     - `active_character_name: str | None = None`
   - Add `class CampaignCharacterInstance(BaseModel)` with fields:
     - `campaign_id: str`
     - `user_id: str`
     - `character_name: str`
     - `archive_profile_id: str | None = None`
     - `panel_id: str | None = None`
     - `created_at: datetime = Field(default_factory=datetime.now)`
     - `source: str = "archive"`  (literal "archive" | "ad_hoc" | "import")
4. Run `uv run pytest tests/test_identity_models.py -x` — expect ALL PASS (GREEN)

**Verify:** `uv run pytest tests/test_identity_models.py -x`

**Done:** Two new Pydantic models exist, all model construction and serialization tests pass.

---

### Task 2: Refactor CampaignSession to Use New Models

**Files:** `src/dm_bot/orchestrator/session_store.py`

**Action:**

1. Add new fields to `CampaignSession`:
   ```python
   members: dict[str, CampaignMember] = Field(default_factory=dict)
   character_instances: dict[str, CampaignCharacterInstance] = Field(default_factory=dict)
   ```

2. Replace old primitive fields with backward-compatible computed properties:
   - Remove `member_ids: set[str]` field → add `@property member_ids` returning `set(self.members.keys())`
   - Keep `active_characters: dict[str, str]` field BUT add `@property` that syncs from `members[uid].active_character_name`. Actually, for maximum backward compat, keep the old fields as real fields initially, and sync them when `members` changes. **Better approach:** Keep old fields but make `members` the source of truth. Add a `_sync_legacy_fields()` method called after any `members` mutation.

   **Refined approach (safe, incremental):**
   - Keep ALL old fields (`member_ids`, `active_characters`, `player_ready`, `selected_profiles`, `action_submitters`) as they are
   - ADD `members` and `character_instances` as new fields
   - Modify `SessionStore.bind_campaign()` to populate BOTH old fields AND new `members` dict
   - Modify `SessionStore.join_campaign()` to populate BOTH
   - Modify `SessionStore.leave_campaign()` to clean up BOTH
   - Modify `SessionStore.bind_character()` to populate BOTH `active_characters` AND `members[uid].active_character_name`
   - Modify `SessionStore.select_archive_profile()` to populate BOTH `selected_profiles` AND `members[uid].selected_profile_id`
   - Add helper: `CampaignSession._get_or_create_member(user_id, campaign_id) -> CampaignMember`
   - Modify `set_player_ready()` to also update `members[uid].ready`
   - Modify `set_player_action()` — leave as-is (action_submitters stays separate)

3. Update `SessionStore` methods:
   - `bind_campaign()`: Create `CampaignMember(user_id=owner_id, campaign_id=campaign_id, role=CampaignRole.OWNER)` in `session.members`
   - `join_campaign()`: Create `CampaignMember(user_id=user_id, campaign_id=session.campaign_id)` in `session.members`
   - `leave_campaign()`: Pop from `session.members`, also pop from `session.character_instances`
   - `bind_character()`: Update `session.members[user_id].active_character_name`, create/update `session.character_instances[user_id]`
   - `select_archive_profile()`: Update `session.members[user_id].selected_profile_id`
   - `bind_role()`: Update `session.members[user_id].role` if appropriate

4. Add new `SessionStore` methods:
   - `get_member(channel_id, user_id) -> CampaignMember | None`
   - `get_character_instance(channel_id, user_id) -> CampaignCharacterInstance | None`
   - `list_members(channel_id) -> list[CampaignMember]`

5. Update `dump_sessions()` to include:
   ```python
   "members": {uid: m.model_dump() for uid, m in session.members.items()},
   "character_instances": {uid: ci.model_dump() for uid, ci in session.character_instances.items()},
   ```

6. Update `load_sessions()` to restore:
   ```python
   members={uid: CampaignMember.model_validate(m) for uid, m in raw.get("members", {}).items()},
   character_instances={uid: CampaignCharacterInstance.model_validate(ci) for uid, ci in raw.get("character_instances", {}).items()},
   ```

7. Add backward-compat load logic: If `members` is empty in loaded data but `member_ids` exists, reconstruct `members` from the old fields:
   ```python
   if not members and raw.get("member_ids"):
       for uid in raw["member_ids"]:
           role = CampaignRole.OWNER if uid == raw.get("owner_id") else CampaignRole.MEMBER
           members[uid] = CampaignMember(
               user_id=uid,
               campaign_id=str(raw["campaign_id"]),
               role=role,
               ready=bool(raw.get("player_ready", {}).get(uid, False)),
               selected_profile_id=raw.get("selected_profiles", {}).get(uid),
               active_character_name=raw.get("active_characters", {}).get(uid),
           )
   ```

**Verify:** `uv run pytest tests/test_identity_models.py tests/test_persistence_store.py tests/test_investigator_panels.py tests/test_round_collection.py -x`

**Done:**
- `CampaignSession` has `members` and `character_instances` fields
- `SessionStore` methods populate both old and new fields
- `dump_sessions`/`load_sessions` handle new models
- Old field access patterns still work (backward compat)
- Legacy load reconstructs `members` from old-format JSON

---

### Task 3: Add Persistence Round-Trip Tests for New Models

**Files:** `tests/test_persistence_store.py`

**Action:**

1. Add test `test_persistence_round_trip_campaign_members`:
   ```python
   def test_persistence_round_trip_campaign_members(tmp_path: Path) -> None:
       store = PersistenceStore(tmp_path / "campaign.sqlite3")
       sessions = SessionStore()
       sessions.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
       sessions.join_campaign(channel_id="chan-1", user_id="user-2")
       sessions.bind_character(channel_id="chan-1", user_id="user-1", character_name="Alice")
       sessions.select_archive_profile(channel_id="chan-1", user_id="user-1", profile_id="prof-1")

       store.save_sessions(sessions.dump_sessions())
       restored_payload = store.load_sessions()

       restored = SessionStore()
       restored.load_sessions(restored_payload)

       session = restored.get_by_channel("chan-1")
       assert session is not None

       # New model checks
       assert "user-1" in session.members
       assert "user-2" in session.members
       assert session.members["user-1"].role == CampaignRole.OWNER
       assert session.members["user-2"].role == CampaignRole.MEMBER
       assert session.members["user-1"].active_character_name == "Alice"
       assert session.members["user-1"].selected_profile_id == "prof-1"

       # Backward compat still works
       assert session.member_ids == {"user-1", "user-2"}
       assert session.active_characters["user-1"] == "Alice"
       assert session.selected_profiles["user-1"] == "prof-1"
   ```

2. Add test `test_persistence_legacy_format_reconstructs_members`:
   ```python
   def test_persistence_legacy_format_reconstructs_members(tmp_path: Path) -> None:
       """Old JSON without 'members' key should auto-reconstruct CampaignMember objects."""
       store = PersistenceStore(tmp_path / "campaign.sqlite3")
       sessions = SessionStore()
       sessions.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
       sessions.join_campaign(channel_id="chan-1", user_id="user-2")

       # Simulate old format by dumping, stripping 'members', and reloading
       payload = sessions.dump_sessions()
       del payload["chan-1"]["members"]
       del payload["chan-1"]["character_instances"]

       restored = SessionStore()
       restored.load_sessions(payload)

       session = restored.get_by_channel("chan-1")
       assert session is not None
       assert "user-1" in session.members
       assert "user-2" in session.members
       assert session.members["user-1"].role == CampaignRole.OWNER
       assert session.members["user-2"].role == CampaignRole.MEMBER
   ```

3. Run `uv run pytest tests/test_persistence_store.py -x` and fix any issues.

4. Run full test suite: `uv run pytest -q` — ensure no regressions.

5. Run smoke check: `uv run python -m dm_bot.main smoke-check`

**Verify:** `uv run pytest tests/test_persistence_store.py -x`

**Done:**
- Persistence round-trip test passes with new models
- Legacy format backward-compat test passes
- Full test suite green
- Smoke check passes

---

## Task Dependency Graph

| Task | Depends On | Reason |
|------|------------|--------|
| Task 1: Define Models + TDD | None | Foundation — no prerequisites |
| Task 2: Refactor CampaignSession | Task 1 | Needs CampaignMember and CampaignCharacterInstance classes defined |
| Task 3: Persistence Tests | Task 2 | Needs updated dump_sessions/load_sessions to test round-trip |

## Parallel Execution Graph

Wave 1 (Start immediately):
└── Task 1: Define CampaignMember and CampaignCharacterInstance models (no dependencies)

Wave 2 (After Task 1):
└── Task 2: Refactor CampaignSession to use new models (depends: Task 1)

Wave 3 (After Task 2):
└── Task 3: Add persistence round-trip tests and full regression (depends: Task 2)

**Critical Path:** Task 1 → Task 2 → Task 3
**All tasks sequential** — hard dependency chain (models → refactoring → testing)

## Category + Skills Recommendations

### Task 1: Define Models + TDD

**Delegation Recommendation:**
- Category: `quick` — Simple Pydantic model definitions with TDD
- Skills: [`superpowers/test-driven-development`] — TDD cycle required

**Skills Evaluation:**
- INCLUDED `superpowers/test-driven-development`: Core methodology for this task — write tests first, implement after
- OMITTED `superpowers/brainstorming`: Requirements are fully specified in the plan, no creative exploration needed
- OMITTED `superpowers/systematic-debugging`: No bugs to debug, greenfield model creation

### Task 2: Refactor CampaignSession

**Delegation Recommendation:**
- Category: `unspecified-high` — Refactoring with many consumer touchpoints, backward compat constraints
- Skills: [`superpowers/test-driven-development`, `superpowers/verification-before-completion`]

**Skills Evaluation:**
- INCLUDED `superpowers/test-driven-development`: Each refactoring step should be verified against existing tests
- INCLUDED `superpowers/verification-before-completion`: Must verify all backward-compat properties work before claiming done
- OMITTED `superpowers/systematic-debugging`: If tests pass, no debugging needed

### Task 3: Persistence Tests

**Delegation Recommendation:**
- Category: `quick` — Writing tests for already-implemented serialization
- Skills: [`superpowers/test-driven-development`]

**Skills Evaluation:**
- INCLUDED `superpowers/test-driven-development`: Tests should verify the serialization contracts
- OMITTED `superpowers/verification-before-completion`: The test run IS the verification

---

## Commit Strategy

Three atomic commits following TDD structure:

```
test(52): add failing tests for CampaignMember and CampaignCharacterInstance models
feat(52): implement identity models and refactor CampaignSession
test(52): add persistence round-trip tests for new identity models
```

If refactoring in Task 2 is large, split into:
```
feat(52): add CampaignMember and CampaignCharacterInstance Pydantic models
refactor(52): migrate CampaignSession to use structured member model
refactor(52): update SessionStore methods for new member/instance models
feat(52): add legacy-format backward compat in load_sessions
test(52): add persistence round-trip and legacy format tests
```

## Verification Checklist

After all tasks complete:

- [ ] `CampaignMember` model has: user_id, campaign_id, joined_at, role (owner/admin/member), ready, selected_profile_id, active_character_name
- [ ] `CampaignCharacterInstance` model has: campaign_id, user_id, archive_profile_id, character_name, panel_id, created_at, source
- [ ] `CampaignSession.members: dict[str, CampaignMember]` exists and is the canonical membership store
- [ ] `CampaignSession.character_instances: dict[str, CampaignCharacterInstance]` exists
- [ ] Old field access patterns (`member_ids`, `active_characters`, `player_ready`, `selected_profiles`) still work
- [ ] `dump_sessions()` produces JSON-safe output including `members` and `character_instances`
- [ ] `load_sessions()` restores `CampaignMember` and `CampaignCharacterInstance` from JSON
- [ ] Legacy JSON (without `members` key) auto-reconstructs `CampaignMember` objects
- [ ] All existing tests pass: `uv run pytest -q`
- [ ] Smoke check passes: `uv run python -m dm_bot.main smoke-check`

## Success Criteria

1. ✅ `CampaignMember` exists tracking Discord ID and role (owner, admin, member)
2. ✅ `CampaignCharacterInstance` exists representing the active investigator projection
3. ✅ `CampaignSession` stores these structured models alongside (and syncing with) the old string sets
4. ✅ System successfully serializes and deserializes the new objects to/from the JSON store

## Output

After completion, create `.planning/workstreams/track-b/phases/52-foundational-identity-models/52-01-SUMMARY.md`
