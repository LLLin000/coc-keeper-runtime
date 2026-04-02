# Phase E83 Context: Archive Repository Completion

## Goal
Complete the archive repository with full CRUD operations and integrate it with RuntimeTestDriver.

## Background

### Current State
- `archive.py` exists with basic profile creation
- Has: create_profile, list_profiles, get_profile, archive_profile
- Missing: update_profile, full persistence, RuntimeTestDriver integration

### Current Implementation
```python
class InvestigatorArchiveRepository:
    def __init__(self) -> None:
        self._profiles: dict[str, dict[str, InvestigatorArchiveProfile]] = {}
    
    def create_profile(...) -> InvestigatorArchiveProfile
    def list_profiles(user_id: str) -> list[InvestigatorArchiveProfile]
    def get_profile(user_id: str, profile_id: str) -> InvestigatorArchiveProfile
    def archive_profile(...) -> InvestigatorArchiveProfile
    def replace_active_with(...) -> InvestigatorArchiveProfile
    def delete_profile(...) -> None
    def export_state() -> dict
    def import_state(payload: dict) -> None
```

## Design Decisions

### 1. Missing Operations

**Update Profile**: Modify existing profile fields
- Partial updates (only provided fields)
- Validation of changes
- Version tracking

**Full Persistence**: Save to SQLite
- Profiles table with JSON storage
- User index for fast lookup
- Export/import for backup

### 2. CRUD Completeness

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ | create_profile exists |
| Read | ✅ | get_profile, list_profiles exist |
| Update | ❌ | Need update_profile |
| Delete | ✅ | delete_profile exists |

### 3. RuntimeTestDriver Integration

Add methods to RuntimeTestDriver:
- `create_test_profile(user_id, ...)` - Create profile in tests
- `get_profile(user_id, profile_id)` - Retrieve profile
- `update_profile(user_id, profile_id, ...)` - Update profile
- `list_profiles(user_id)` - List user's profiles
- `delete_profile(user_id, profile_id)` - Delete profile

### 4. Validation

**Update Validation**:
- Check profile exists
- Validate field types
- Prevent changing read-only fields (profile_id, user_id)
- Return updated profile

## Implementation Requirements

### ARCHIVE-01: Update Operation
- update_profile method
- Partial update support
- Field validation
- Return updated profile

### ARCHIVE-02: Persistence Layer
- SQLite table for profiles
- Save/load operations
- Transaction support
- Migration handling

### ARCHIVE-03: RuntimeTestDriver Integration
- Methods for all CRUD operations
- Test assertions for profiles
- State verification

### ARCHIVE-04: Validation & Error Handling
- Profile existence checks
- Field validation
- Error messages in Chinese
- Edge case handling

### ARCHIVE-05: E2E Testing
- Full CRUD scenario
- Persistence verification
- Cross-session profile retention

## Files to Modify

- `src/dm_bot/coc/archive.py` - Add update_profile, persistence
- `src/dm_bot/persistence/store.py` - Add profile storage
- `src/dm_bot/testing/runtime_driver.py` - Add CRUD methods
- `tests/coc/test_archive.py` - Unit tests
- `tests/scenarios/acceptance/scen_archive_crud.yaml` - E2E

## Success Criteria

- [ ] Archive repository supports Create, Read, Update, Delete operations
- [ ] Character profiles can be stored and retrieved
- [ ] Campaign state can be persisted across sessions
- [ ] Archive is fully wired into RuntimeTestDriver
- [ ] E2E tests validate archive CRUD operations
