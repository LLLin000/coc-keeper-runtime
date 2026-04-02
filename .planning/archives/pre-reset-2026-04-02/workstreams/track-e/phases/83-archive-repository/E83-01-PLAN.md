---
phase: E83-archive-repository
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/coc/archive.py
  - src/dm_bot/persistence/store.py
  - src/dm_bot/testing/runtime_driver.py
  - tests/coc/test_archive.py
  - tests/scenarios/acceptance/scen_archive_crud.yaml
autonomous: true
requirements:
  - ARCHIVE-01
  - ARCHIVE-02
  - ARCHIVE-03
  - ARCHIVE-04
  - ARCHIVE-05

must_haves:
  truths:
    - "Archive repository supports Create, Read, Update, Delete operations"
    - "Character profiles can be stored and retrieved"
    - "Campaign state can be persisted across sessions"
    - "Archive is fully wired into RuntimeTestDriver"
    - "E2E tests validate archive CRUD operations"
  artifacts:
    - path: "src/dm_bot/coc/archive.py"
      provides: "update_profile method, full CRUD"
      exports: ["update_profile"]
    - path: "src/dm_bot/persistence/store.py"
      provides: "Profile persistence in SQLite"
      exports: ["save_profile", "load_profile"]
    - path: "src/dm_bot/testing/runtime_driver.py"
      provides: "Archive CRUD methods"
      exports: ["create_test_profile", "get_profile", "update_profile"]
    - path: "tests/coc/test_archive.py"
      provides: "CRUD unit tests"
      min_lines: 100
  key_links:
    - from: "archive.py"
      to: "persistence/store.py"
      via: "save_profile/load_profile calls"
    - from: "runtime_driver.py"
      to: "archive.py"
      via: "archive_repository methods"
---

<objective>
Complete archive repository with full CRUD operations and persistence.

Purpose: Enable full character profile lifecycle with persistence.
Output: Complete CRUD operations, SQLite persistence, RuntimeTestDriver integration.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@src/dm_bot/coc/archive.py
@src/dm_bot/persistence/store.py
@src/dm_bot/testing/runtime_driver.py

## Key Types from Existing Code

From archive.py:
```python
class InvestigatorArchiveProfile(BaseModel):
    profile_id: str
    user_id: str
    name: str
    occupation: str
    # ... many fields
    coc: COCInvestigatorProfile

class InvestigatorArchiveRepository:
    def create_profile(...) -> InvestigatorArchiveProfile
    def get_profile(user_id: str, profile_id: str) -> InvestigatorArchiveProfile
    def delete_profile(user_id: str, profile_id: str) -> None
```

From store.py:
```python
class PersistenceStore:
    def save_session(self, campaign_id: str, state: dict) -> None
    def load_session(self, campaign_id: str) -> dict | None
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add update_profile to archive</name>
  <files>src/dm_bot/coc/archive.py</files>
  <action>
Add update_profile method to InvestigatorArchiveRepository:

```python
def update_profile(
    self,
    *,
    user_id: str,
    profile_id: str,
    **updates,
) -> InvestigatorArchiveProfile:
    """Update an existing profile.
    
    Args:
        user_id: The user ID
        profile_id: The profile ID to update
        **updates: Fields to update (only updatable fields)
        
    Returns:
        The updated profile
        
    Raises:
        ValueError: If profile not found or invalid updates
    """
    # Get existing profile
    profile = self.get_profile(user_id, profile_id)
    
    # Fields that cannot be updated
    read_only = {"profile_id", "user_id", "coc"}  # coc is complex, handle separately
    
    # Validate updates
    invalid = set(updates.keys()) & read_only
    if invalid:
        raise ValueError(f"Cannot update read-only fields: {invalid}")
    
    # Apply updates
    for key, value in updates.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
        else:
            raise ValueError(f"Unknown field: {key}")
    
    # Update in storage
    self._profiles[user_id][profile_id] = profile
    
    return profile

def update_coc_stats(
    self,
    *,
    user_id: str,
    profile_id: str,
    **coc_updates,
) -> InvestigatorArchiveProfile:
    """Update COC-specific stats.
    
    Args:
        user_id: The user ID
        profile_id: The profile ID
        **coc_updates: Updates to COCInvestigatorProfile
        
    Returns:
        The updated profile
    """
    profile = self.get_profile(user_id, profile_id)
    
    # Update COC fields
    for key, value in coc_updates.items():
        if hasattr(profile.coc, key):
            setattr(profile.coc, key, value)
        else:
            raise ValueError(f"Unknown COC field: {key}")
    
    self._profiles[user_id][profile_id] = profile
    return profile

def update_skills(
    self,
    *,
    user_id: str,
    profile_id: str,
    skills: dict[str, int],
) -> InvestigatorArchiveProfile:
    """Update character skills.
    
    Args:
        user_id: The user ID
        profile_id: The profile ID
        skills: Dict of skill_name -> skill_value
        
    Returns:
        The updated profile
    """
    profile = self.get_profile(user_id, profile_id)
    
    for skill, value in skills.items():
        profile.coc.skills[skill] = value
    
    self._profiles[user_id][profile_id] = profile
    return profile
```
  </action>
  <verify>
    <automated>grep -n "def update_profile\|def update_coc_stats\|def update_skills" src/dm_bot/coc/archive.py</automated>
  </verify>
  <done>update_profile and related methods added</done>
</task>

<task type="auto">
  <name>Task 2: Add profile persistence to store</name>
  <files>src/dm_bot/persistence/store.py</files>
  <action>
Add profile persistence methods:

```python
# Add to PersistenceStore class

def save_profile(self, user_id: str, profile: dict) -> None:
    """Save a profile to the database.
    
    Args:
        user_id: The user ID
        profile: Profile data as dict
    """
    import json
    
    profile_id = profile.get("profile_id")
    if not profile_id:
        raise ValueError("Profile must have profile_id")
    
    with self._get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                user_id TEXT NOT NULL,
                profile_id TEXT NOT NULL,
                data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, profile_id)
            )
            """
        )
        
        conn.execute(
            """
            INSERT OR REPLACE INTO profiles (user_id, profile_id, data)
            VALUES (?, ?, ?)
            """,
            (user_id, profile_id, json.dumps(profile))
        )
        conn.commit()

def load_profile(self, user_id: str, profile_id: str) -> dict | None:
    """Load a profile from the database.
    
    Args:
        user_id: The user ID
        profile_id: The profile ID
        
    Returns:
        Profile data as dict, or None if not found
    """
    import json
    
    with self._get_connection() as conn:
        cursor = conn.execute(
            "SELECT data FROM profiles WHERE user_id = ? AND profile_id = ?",
            (user_id, profile_id)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None

def load_user_profiles(self, user_id: str) -> list[dict]:
    """Load all profiles for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        List of profile dicts
    """
    import json
    
    with self._get_connection() as conn:
        cursor = conn.execute(
            "SELECT data FROM profiles WHERE user_id = ?",
            (user_id,)
        )
        return [json.loads(row[0]) for row in cursor.fetchall()]

def delete_profile(self, user_id: str, profile_id: str) -> bool:
    """Delete a profile from the database.
    
    Args:
        user_id: The user ID
        profile_id: The profile ID
        
    Returns:
        True if deleted, False if not found
    """
    with self._get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM profiles WHERE user_id = ? AND profile_id = ?",
            (user_id, profile_id)
        )
        conn.commit()
        return cursor.rowcount > 0
```
  </action>
  <verify>
    <automated>grep -n "def save_profile\|def load_profile\|def delete_profile" src/dm_bot/persistence/store.py</automated>
  </verify>
  <done>Profile persistence methods added</done>
</task>

<task type="auto">
  <name>Task 3: Integrate persistence with archive</name>
  <files>src/dm_bot/coc/archive.py</files>
  <action>
Add persistence integration to archive:

```python
# Add to InvestigatorArchiveRepository

def __init__(self, persistence_store=None) -> None:
    """Initialize repository with optional persistence.
    
    Args:
        persistence_store: Optional PersistenceStore for DB operations
    """
    self._profiles: dict[str, dict[str, InvestigatorArchiveProfile]] = {}
    self._persistence = persistence_store

def save_to_persistence(self, user_id: str, profile_id: str) -> None:
    """Save a profile to persistent storage.
    
    Args:
        user_id: The user ID
        profile_id: The profile ID
    """
    if not self._persistence:
        return
    
    profile = self.get_profile(user_id, profile_id)
    self._persistence.save_profile(user_id, profile.model_dump())

def load_from_persistence(self, user_id: str) -> list[InvestigatorArchiveProfile]:
    """Load all profiles for a user from persistent storage.
    
    Args:
        user_id: The user ID
        
    Returns:
        List of loaded profiles
    """
    if not self._persistence:
        return []
    
    profiles_data = self._persistence.load_user_profiles(user_id)
    profiles = []
    
    for data in profiles_data:
        profile = InvestigatorArchiveProfile.model_validate(data)
        profiles.append(profile)
        
        # Add to memory
        if user_id not in self._profiles:
            self._profiles[user_id] = {}
        self._profiles[user_id][profile.profile_id] = profile
    
    return profiles

def persist_all(self) -> None:
    """Save all profiles to persistent storage."""
    if not self._persistence:
        return
    
    for user_id, profiles in self._profiles.items():
        for profile_id, profile in profiles.items():
            self._persistence.save_profile(user_id, profile.model_dump())
```
  </action>
  <verify>
    <automated>grep -n "save_to_persistence\|load_from_persistence" src/dm_bot/coc/archive.py</automated>
  </verify>
  <done>Persistence integration added</done>
</task>

<task type="auto">
  <name>Task 4: Add RuntimeTestDriver methods</name>
  <files>src/dm_bot/testing/runtime_driver.py</files>
  <action>
Add archive CRUD methods to RuntimeTestDriver:

```python
# Add to RuntimeTestDriver class

def create_test_profile(
    self,
    user_id: str,
    name: str,
    occupation: str,
    age: int,
    **kwargs,
) -> dict:
    """Create a test character profile.
    
    Args:
        user_id: The user ID
        name: Character name
        occupation: Character occupation
        age: Character age
        **kwargs: Additional profile fields
        
    Returns:
        Created profile as dict
    """
    # Get archive repository from gameplay
    if not self._gameplay or not hasattr(self._gameplay, 'archive_repository'):
        raise RuntimeError("Archive repository not available")
    
    repo = self._gameplay.archive_repository
    
    # Generate stats
    generation = kwargs.get('generation', self._generate_test_stats())
    
    profile = repo.create_profile(
        user_id=user_id,
        name=name,
        occupation=occupation,
        age=age,
        background=kwargs.get('background', 'Test background'),
        portrait_summary=kwargs.get('portrait_summary', f'{occupation} test character'),
        concept=kwargs.get('concept', 'Test concept'),
        disposition=kwargs.get('disposition', '冷静'),
        favored_skills=kwargs.get('favored_skills', ['侦查', '图书馆使用']),
        generation=generation,
    )
    
    return profile.model_dump()

def get_profile(self, user_id: str, profile_id: str) -> dict | None:
    """Get a profile.
    
    Args:
        user_id: The user ID
        profile_id: The profile ID
        
    Returns:
        Profile as dict, or None if not found
    """
    if not self._gameplay or not hasattr(self._gameplay, 'archive_repository'):
        return None
    
    repo = self._gameplay.archive_repository
    try:
        profile = repo.get_profile(user_id, profile_id)
        return profile.model_dump()
    except KeyError:
        return None

def update_profile(
    self,
    user_id: str,
    profile_id: str,
    **updates,
) -> dict:
    """Update a profile.
    
    Args:
        user_id: The user ID
        profile_id: The profile ID
        **updates: Fields to update
        
    Returns:
        Updated profile as dict
    """
    if not self._gameplay or not hasattr(self._gameplay, 'archive_repository'):
        raise RuntimeError("Archive repository not available")
    
    repo = self._gameplay.archive_repository
    profile = repo.update_profile(user_id=user_id, profile_id=profile_id, **updates)
    return profile.model_dump()

def list_profiles(self, user_id: str) -> list[dict]:
    """List all profiles for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        List of profile dicts
    """
    if not self._gameplay or not hasattr(self._gameplay, 'archive_repository'):
        return []
    
    repo = self._gameplay.archive_repository
    profiles = repo.list_profiles(user_id)
    return [p.model_dump() for p in profiles]

def delete_profile(self, user_id: str, profile_id: str) -> bool:
    """Delete a profile.
    
    Args:
        user_id: The user ID
        profile_id: The profile ID
        
    Returns:
        True if deleted, False if not found
    """
    if not self._gameplay or not hasattr(self._gameplay, 'archive_repository'):
        return False
    
    repo = self._gameplay.archive_repository
    try:
        repo.delete_profile(user_id=user_id, profile_id=profile_id)
        return True
    except KeyError:
        return False

def _generate_test_stats(self) -> dict[str, int]:
    """Generate test character stats."""
    return {
        "str": 50, "con": 50, "dex": 50, "app": 50,
        "pow": 50, "siz": 50, "int": 50, "edu": 50,
        "luck": 50,
    }
```
  </action>
  <verify>
    <automated>grep -n "def create_test_profile\|def update_profile\|def delete_profile" src/dm_bot/testing/runtime_driver.py</automated>
  </verify>
  <done>RuntimeTestDriver archive CRUD methods</done>
</task>

<task type="auto">
  <name>Task 5: Create unit tests</name>
  <files>tests/coc/test_archive.py</files>
  <action>
Create archive CRUD tests:

```python
"""Tests for archive repository CRUD operations."""

import pytest

from dm_bot.coc.archive import InvestigatorArchiveRepository, InvestigatorArchiveProfile
from dm_bot.coc.bestiary import COCAttributes, COCInvestigatorProfile


class TestArchiveCRUD:
    """Test CRUD operations."""
    
    @pytest.fixture
    def repo(self):
        """Create fresh repository."""
        return InvestigatorArchiveRepository()
    
    @pytest.fixture
    def test_profile_data(self):
        """Test profile data."""
        return {
            "user_id": "user1",
            "name": "测试角色",
            "occupation": "医生",
            "age": 35,
            "background": "Test background",
            "portrait_summary": "Test doctor",
            "concept": "Test concept",
            "disposition": "冷静",
            "favored_skills": ["医学", "急救"],
            "generation": {
                "str": 50, "con": 50, "dex": 50, "app": 50,
                "pow": 50, "siz": 50, "int": 50, "edu": 50,
                "luck": 50,
            },
        }
    
    def test_create_profile(self, repo, test_profile_data):
        """Test profile creation."""
        profile = repo.create_profile(**test_profile_data)
        
        assert profile.name == "测试角色"
        assert profile.occupation == "医生"
        assert profile.coc.attributes.str == 50
    
    def test_get_profile(self, repo, test_profile_data):
        """Test profile retrieval."""
        created = repo.create_profile(**test_profile_data)
        
        retrieved = repo.get_profile("user1", created.profile_id)
        
        assert retrieved.profile_id == created.profile_id
        assert retrieved.name == created.name
    
    def test_update_profile(self, repo, test_profile_data):
        """Test profile update."""
        created = repo.create_profile(**test_profile_data)
        
        updated = repo.update_profile(
            user_id="user1",
            profile_id=created.profile_id,
            name="更新后的名字",
            age=40,
        )
        
        assert updated.name == "更新后的名字"
        assert updated.age == 40
        assert updated.occupation == "医生"  # Unchanged
    
    def test_update_read_only_fields(self, repo, test_profile_data):
        """Test that read-only fields cannot be updated."""
        created = repo.create_profile(**test_profile_data)
        
        with pytest.raises(ValueError, match="read-only"):
            repo.update_profile(
                user_id="user1",
                profile_id=created.profile_id,
                profile_id="new_id",  # Read-only
            )
    
    def test_update_skills(self, repo, test_profile_data):
        """Test skill update."""
        created = repo.create_profile(**test_profile_data)
        
        updated = repo.update_skills(
            user_id="user1",
            profile_id=created.profile_id,
            skills={"医学": 60, "急救": 45},
        )
        
        assert updated.coc.skills["医学"] == 60
        assert updated.coc.skills["急救"] == 45
    
    def test_list_profiles(self, repo, test_profile_data):
        """Test listing profiles."""
        repo.create_profile(**test_profile_data)
        
        # Create another
        data2 = test_profile_data.copy()
        data2["name"] = "第二个角色"
        repo.create_profile(**data2)
        
        profiles = repo.list_profiles("user1")
        
        assert len(profiles) == 2
    
    def test_delete_profile(self, repo, test_profile_data):
        """Test profile deletion."""
        created = repo.create_profile(**test_profile_data)
        
        repo.delete_profile("user1", created.profile_id)
        
        with pytest.raises(KeyError):
            repo.get_profile("user1", created.profile_id)
    
    def test_archive_profile(self, repo, test_profile_data):
        """Test archiving a profile."""
        created = repo.create_profile(**test_profile_data)
        
        archived = repo.archive_profile(
            user_id="user1",
            profile_id=created.profile_id,
        )
        
        assert archived.status == "archived"


class TestArchivePersistence:
    """Test persistence operations."""
    
    def test_export_import_state(self):
        """Test state export and import."""
        repo = InvestigatorArchiveRepository()
        
        # Create profile
        repo.create_profile(
            user_id="user1",
            name="Test",
            occupation="Doctor",
            age=30,
            background="Test",
            portrait_summary="Test",
            concept="Test",
            disposition="冷静",
            favored_skills=["医学"],
            generation={"str": 50, "con": 50, "dex": 50, "app": 50,
                       "pow": 50, "siz": 50, "int": 50, "edu": 50, "luck": 50},
        )
        
        # Export
        state = repo.export_state()
        
        # Import to new repo
        new_repo = InvestigatorArchiveRepository()
        new_repo.import_state(state)
        
        # Verify
        profiles = new_repo.list_profiles("user1")
        assert len(profiles) == 1
        assert profiles[0].name == "Test"
```
  </action>
  <verify>
    <automated>uv run pytest tests/coc/test_archive.py -v</automated>
  </verify>
  <done>Archive CRUD unit tests</done>
</task>

<task type="auto">
  <name>Task 6: Create E2E CRUD scenario</name>
  <files>tests/scenarios/acceptance/scen_archive_crud.yaml</files>
  <action>
Create E2E CRUD scenario:

```yaml
# Archive CRUD E2E Scenario
# Validates: Create → Read → Update → Delete flow

scenario:
  id: scen_archive_crud
  name: "Archive CRUD Operations"
  description: "Validates full archive CRUD lifecycle"
  
actors:
  - id: p1
    role: player
    name: "测试玩家"

initial_state:
  dice_mode: seeded
  dice_seed: 12345
  
steps:
  # Create profile
  - actor: p1
    action: command
    name: create_profile
    args:
      name: "张三"
      occupation: "医生"
      age: 35
      concept: "38岁的落魄临床医生"
      
  - actor: system
    action: assert
    assertions:
      profile_created:
        name: "张三"
        occupation: "医生"
        has_profile_id: true
        has_coc_stats: true
        
  # Read profile
  - actor: p1
    action: command
    name: get_profile
    args:
      profile_id: "{{last_created_profile_id}}"
      
  - actor: system
    action: assert
    assertions:
      profile_retrieved:
        name: "张三"
        coc:
          san: "> 0"
          hp: "> 0"
          
  # Update profile
  - actor: p1
    action: command
    name: update_profile
    args:
      profile_id: "{{last_created_profile_id}}"
      updates:
        name: "张三（已更新）"
        age: 36
        
  - actor: system
    action: assert
    assertions:
      profile_updated:
        name: "张三（已更新）"
        age: 36
        occupation: "医生"  # Unchanged
        
  # Update skills
  - actor: p1
    action: command
    name: update_skills
    args:
      profile_id: "{{last_created_profile_id}}"
      skills:
        医学: 60
        急救: 45
        
  - actor: system
    action: assert
    assertions:
      skills_updated:
        医学: 60
        急救: 45
        
  # List profiles
  - actor: p1
    action: command
    name: list_profiles
    args: {}
    
  - actor: system
    action: assert
    assertions:
      profiles_listed:
        count: 1
        contains:
          - name: "张三（已更新）"
            
  # Delete profile
  - actor: p1
    action: command
    name: delete_profile
    args:
      profile_id: "{{last_created_profile_id}}"
      
  - actor: system
    action: assert
    assertions:
      profile_deleted:
        list_count: 0
        get_returns: null

expected_outcomes:
  - crud_completed: true
  - persistence_verified: true
  - all_operations_successful: true
```
  </action>
  <verify>
    <automated>cat tests/scenarios/acceptance/scen_archive_crud.yaml | head -30</automated>
  </verify>
  <done>E2E archive CRUD scenario</done>
</task>

</tasks>

<verification>
Run verification:
1. `uv run pytest tests/coc/test_archive.py -v`
2. `uv run python -m dm_bot.main smoke-check`
</verification>

<success_criteria>
- update_profile method with partial updates
- update_coc_stats and update_skills methods
- PersistenceStore profile methods
- Archive persistence integration
- RuntimeTestDriver CRUD methods
- Unit tests for all operations
- E2E scenario validates CRUD
- All existing tests pass
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-e/phases/83-archive-repository/E83-01-SUMMARY.md`
</output>
