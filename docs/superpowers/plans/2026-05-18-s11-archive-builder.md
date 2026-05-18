# S11: Archive & Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze archive schema for characters/investigators with versioning, CRUD persistence, and fast-path builder.

**Architecture:** `CharacterArchive` wraps pre-existing `CharacterSheet` with schema version + metadata. `Store` gets CRUD methods. `CharacterBuilder` persists via Store. Pre-existing `characters` table reused.

**Tech Stack:** Python, Pydantic v2, SQLite

---

### Task 1: CharacterArchive Model

**Files:**
- Create: `src/dm_bot/character/archive.py`
- Test: `tests/test_character.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_character.py`:

```python
"""Tests for character archive models."""

from dm_bot.character.sheet import CharacterSheet


class TestCharacterArchive:
    def test_create_archive(self):
        from dm_bot.character.archive import CharacterArchive

        sheet = CharacterSheet(character_id="c1", name="Alice", occupation="Detective")
        archive = CharacterArchive(character_id="c1", player_id="user_1", sheet=sheet)
        assert archive.schema_version == 1
        assert archive.sheet.name == "Alice"
        assert archive.player_id == "user_1"

    def test_archive_default_version(self):
        from dm_bot.character.archive import CharacterArchive

        sheet = CharacterSheet(character_id="c2", name="Bob")
        archive = CharacterArchive(character_id="c2", player_id="user_2", sheet=sheet)
        assert archive.schema_version == 1

    def test_archive_versioned_serialization(self):
        from dm_bot.character.archive import CharacterArchive

        sheet = CharacterSheet(character_id="c3", name="Charlie", strength=60)
        archive = CharacterArchive(character_id="c3", player_id="user_3", sheet=sheet)
        data = archive.model_dump()
        assert data["schema_version"] == 1
        assert data["sheet"]["name"] == "Charlie"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_character.py -v`
Expected: ImportError (CharacterArchive not found)

- [ ] **Step 3: Implement CharacterArchive**

Create `src/dm_bot/character/archive.py`:

```python
"""Character archive — versioned wrapper around CharacterSheet."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from dm_bot.character.sheet import CharacterSheet


class CharacterArchive(BaseModel):
    """Versioned character archive with player binding.

    Canonical fields:
    - schema_version: int — archive schema version (currently 1)
    - character_id: str — unique identifier (matches player user_id for fast path)
    - player_id: str — Discord user ID who owns this character
    - sheet: CharacterSheet — the COC investigator stats, skills, metadata
    - created_at: datetime — archive creation timestamp
    - updated_at: datetime — last modification timestamp
    """

    schema_version: int = Field(default=1, description="Archive schema version")
    character_id: str = Field(min_length=1, description="Unique character identifier")
    player_id: str = Field(min_length=1, description="Discord user ID of owner")
    sheet: CharacterSheet = Field(description="COC investigator sheet data")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Archive creation time")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last modification time")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_character.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/dm_bot/character/archive.py tests/test_character.py
git commit -m "feat(s11): add CharacterArchive versioned wrapper"
```

---

### Task 2: Full-Path Builder Stub

**Files:**
- Modify: `src/dm_bot/character/builder.py`
- Modify: `tests/test_character.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_character.py`:

```python
class TestFullPathBuilder:
    def test_full_path_creates_character(self):
        from dm_bot.character.builder import FullPathBuilder

        builder = FullPathBuilder()
        result = builder.build_fast()
        assert result.name is not None
        assert result.strength >= 30

    def test_full_path_heuristic_fallback(self):
        from dm_bot.character.builder import FullPathBuilder

        builder = FullPathBuilder(use_model=False)
        result = builder.build()
        assert isinstance(result.name, str)
        assert len(result.name) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_character.py::TestFullPathBuilder -v`
Expected: ImportError (FullPathBuilder)

- [ ] **Step 3: Implement FullPathBuilder**

Append to `src/dm_bot/character/builder.py`:

```python
class FullPathBuilder:
    """Model-guided interview with heuristic fallback.

    Full path uses the configured model (qwen3) for interview-style chargen.
    When model is unavailable, falls back to randomized heuristic.
    The model integration is a placeholder until the narration/model layer is wired.
    """

    def __init__(self, use_model: bool = False) -> None:
        self._use_model = use_model

    def build(self) -> CharacterSheet:
        if self._use_model:
            return self._model_guided()
        return self.build_fast()

    def build_fast(self) -> CharacterSheet:
        """Heuristic fallback — random stats, defaults, generic name."""
        import random
        occupations = ["Detective", "Journalist", "Doctor", "Archeologist", "Professor"]
        first_names = ["Alex", "Sam", "Jordan", "Morgan", "Taylor", "Casey"]
        return CharacterSheet(
            character_id=f"full_{random.randint(1000, 9999)}",
            name=random.choice(first_names),
            age=random.randint(20, 60),
            occupation=random.choice(occupations),
            strength=random.randint(40, 80),
            constitution=random.randint(40, 80),
            size=random.randint(40, 80),
            dexterity=random.randint(40, 80),
            appearance=random.randint(40, 80),
            intelligence=random.randint(40, 80),
            power=random.randint(40, 80),
            education=random.randint(40, 80),
            luck=random.randint(30, 80),
        )

    def _model_guided(self) -> CharacterSheet:
        """Placeholder — delegates to build_fast until model layer is wired."""
        return self.build_fast()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_character.py::TestFullPathBuilder -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/dm_bot/character/builder.py tests/test_character.py
git commit -m "feat(s11): add FullPathBuilder with heuristic fallback"
```

---

### Task 3: Store CRUD for Character Archives

**Files:**
- Modify: `src/dm_bot/store/db.py`
- Modify: `tests/test_character.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_character.py`:

```python
class TestCharacterStore:
    def test_save_and_load_character(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_char_store.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        try:
            sheet = CharacterSheet(character_id="c1", name="Alice", occupation="Writer")
            archive = CharacterArchive(character_id="c1", player_id="u1", sheet=sheet)
            store.save_character(archive)
            loaded = store.load_character("c1")
            assert loaded is not None
            assert loaded.sheet.name == "Alice"
            assert loaded.player_id == "u1"
        finally:
            del store
            gc.collect()
            os.remove(db_path)

    def test_list_characters_by_player(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_char_list.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        try:
            alice = CharacterArchive(character_id="c1", player_id="u1", sheet=CharacterSheet(character_id="c1", name="Alice"))
            bob = CharacterArchive(character_id="c2", player_id="u1", sheet=CharacterSheet(character_id="c2", name="Bob"))
            charlie = CharacterArchive(character_id="c3", player_id="u2", sheet=CharacterSheet(character_id="c3", name="Charlie"))
            for a in [alice, bob, charlie]:
                store.save_character(a)
            u1_list = store.list_characters("u1")
            assert len(u1_list) == 2
            u2_list = store.list_characters("u2")
            assert len(u2_list) == 1
            assert u2_list[0].sheet.name == "Charlie"
        finally:
            del store
            gc.collect()
            os.remove(db_path)

    def test_delete_character(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_char_del.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        try:
            sheet = CharacterSheet(character_id="c1", name="ToDelete")
            archive = CharacterArchive(character_id="c1", player_id="u1", sheet=sheet)
            store.save_character(archive)
            store.delete_character("c1")
            assert store.load_character("c1") is None
        finally:
            del store
            gc.collect()
            os.remove(db_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_character.py::TestCharacterStore -v`
Expected: AttributeError (no save_character on Store)

- [ ] **Step 3: Add Store methods**

In `src/dm_bot/store/db.py`, add import and CRUD methods:

```python
from dm_bot.character.archive import CharacterArchive
```

Add methods to `Store`:

```python
def save_character(self, archive: CharacterArchive) -> None:
    import json
    with sqlite3.connect(self.db_path) as conn:
        conn.execute(
            """INSERT OR REPLACE INTO characters
               (character_id, user_id, sheet_json)
               VALUES (?, ?, ?)""",
            (archive.character_id, archive.player_id,
             archive.sheet.model_dump_json()),
        )

def load_character(self, character_id: str) -> CharacterArchive | None:
    import json
    with sqlite3.connect(self.db_path) as conn:
        row = conn.execute(
            "SELECT * FROM characters WHERE character_id = ?", (character_id,)
        ).fetchone()
        if not row:
            return None
        from dm_bot.character.sheet import CharacterSheet
        sheet = CharacterSheet.model_validate(json.loads(row[3]))
        return CharacterArchive(
            character_id=row[0], player_id=row[1], sheet=sheet,
        )

def list_characters(self, user_id: str) -> list[CharacterArchive]:
    import json
    with sqlite3.connect(self.db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM characters WHERE user_id = ?", (user_id,)
        ).fetchall()
        from dm_bot.character.sheet import CharacterSheet
        return [
            CharacterArchive(
                character_id=r[0], player_id=r[1],
                sheet=CharacterSheet.model_validate(json.loads(r[3])),
            )
            for r in rows
        ]

def delete_character(self, character_id: str) -> None:
    with sqlite3.connect(self.db_path) as conn:
        conn.execute(
            "DELETE FROM characters WHERE character_id = ?", (character_id,)
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_character.py::TestCharacterStore -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/store/db.py tests/test_character.py
git commit -m "feat(s11): add character archive CRUD to Store"
```

---

### Task 3: Builder Persistence

**Files:**
- Modify: `src/dm_bot/character/builder.py`
- Modify: `tests/test_character.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_character.py`:

```python
class TestBuilderPersistence:
    def test_builder_persists_to_store(self):
        from dm_bot.character.builder import CharacterBuilder
        from dm_bot.store.db import Store
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_build_persist.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        try:
            builder = CharacterBuilder(store=store)
            builder.begin_creation("user_1")
            builder.handle_response("user_1", "Alice")
            builder.handle_response("user_1", "30")
            result = builder.handle_response("user_1", "Detective")
            assert "角色创建完成" in result
            loaded = store.load_character("user_1")
            assert loaded is not None
            assert loaded.sheet.name == "Alice"
            assert loaded.sheet.age == 30
        finally:
            del store
            gc.collect()
            os.remove(db_path)

    def test_builder_without_store_no_persist(self):
        from dm_bot.character.builder import CharacterBuilder

        builder = CharacterBuilder()
        builder.begin_creation("user_2")
        builder.handle_response("user_2", "Bob")
        builder.handle_response("user_2", "25")
        result = builder.handle_response("user_2", "Doctor")
        assert "角色创建完成" in result
        sheet = builder.get_sheet("user_2")
        assert sheet is not None
        assert sheet.name == "Bob"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_character.py::TestBuilderPersistence -v`
Expected: TypeError (CharacterBuilder got unexpected keyword argument)

- [ ] **Step 3: Update CharacterBuilder**

Edit `src/dm_bot/character/builder.py`:

```python
from dm_bot.character.sheet import CharacterSheet


class CharacterBuilder:
    """对话式角色创建器"""

    def __init__(self, store=None) -> None:
        self._sessions: dict[str, dict] = {}
        self._store = store
```

Add persistence at end of handle_response where `step == "done"`:

```python
            if self._store:
                from dm_bot.character.archive import CharacterArchive
                archive = CharacterArchive(
                    character_id=user_id, player_id=user_id,
                    sheet=self.get_sheet(user_id),
                )
                self._store.save_character(archive)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_character.py::TestBuilderPersistence -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/character/builder.py tests/test_character.py
git commit -m "feat(s11): persist completed characters to Store via builder"
```

---

### Task 4: Smoke Check and Final Verification

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 2: Run smoke check**

Run: `uv run python -m dm_bot.main smoke-check`
Expected: "All core modules import successfully."

- [ ] **Step 3: Commit any remaining changes**

```bash
git add -A && git commit -m "chore(s11): final gate pass for archive and builder"
```
