# S12: Data Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans.

**Goal:** Characters can be imported, validated, and deleted with recovery option.

**Architecture:** Import parser validates JSON/structured paste. Store gets soft-delete with recovery. COC validation rules enforce skill/stat compliance.

**Tech Stack:** Python, Pydantic v2, SQLite

---

### Task 1: CharacterImport — Parse and Validate Input

**Files:**
- Create: `src/dm_bot/character/importer.py`
- Create: `tests/test_character_import.py`

- [ ] **Step 1: Tests**

```python
"""Tests for character import."""

from dm_bot.character.sheet import CharacterSheet


class TestCharacterImport:
    def test_import_valid_json(self):
        from dm_bot.character.importer import import_character

        data = '{"name": "Alice", "age": 30, "strength": 60, "constitution": 50}'
        result = import_character(data, player_id="u1")
        assert result is not None
        assert result.sheet.name == "Alice"
        assert result.sheet.strength == 60

    def test_import_invalid_json(self):
        from dm_bot.character.importer import import_character

        result = import_character("not json", player_id="u1")
        assert result is None

    def test_import_missing_required(self):
        from dm_bot.character.importer import import_character

        result = import_character('{"age": 30}', player_id="u1")
        assert result is None
```

- [ ] **Step 2: Run -> ImportError**
- [ ] **Step 3: Implement**

Create `src/dm_bot/character/importer.py`:

```python
"""Character import — parse and validate structured input."""

import json

from dm_bot.character.archive import CharacterArchive
from dm_bot.character.sheet import CharacterSheet


def import_character(data: str, player_id: str) -> CharacterArchive | None:
    """Parse JSON string into CharacterArchive. Returns None on failure."""
    try:
        parsed = json.loads(data)
    except (json.JSONDecodeError, ValueError):
        return None
    try:
        if "name" not in parsed:
            return None
        sheet = CharacterSheet(**parsed)
        cid = parsed.get("character_id", player_id)
        return CharacterArchive(character_id=cid, player_id=player_id, sheet=sheet)
    except Exception:
        return None
```

- [ ] **Step 4: Tests pass**
- [ ] **Step 5: Commit**

---

### Task 2: Store Soft Delete + Recovery

**Files:**
- Modify: `src/dm_bot/store/db.py`
- Modify: `tests/test_character.py`

- [ ] **Step 1: Tests**

```python
class TestCharacterSoftDelete:
    def test_soft_delete(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_softdel.db")
        if os.path.exists(db_path): os.remove(db_path)
        store = Store(db_path)
        try:
            sheet = CharacterSheet(character_id="c1", name="Alice")
            store.save_character(CharacterArchive(character_id="c1", player_id="u1", sheet=sheet))
            store.soft_delete_character("c1")
            loaded = store.load_character("c1")
            assert loaded is None
            archived = store.load_character("c1", include_deleted=True)
            assert archived is not None
        finally:
            del store; gc.collect()
            if os.path.exists(db_path): os.remove(db_path)

    def test_hard_delete(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_harddel.db")
        if os.path.exists(db_path): os.remove(db_path)
        store = Store(db_path)
        try:
            sheet = CharacterSheet(character_id="c1", name="Bob")
            store.save_character(CharacterArchive(character_id="c1", player_id="u1", sheet=sheet))
            store.delete_character("c1")  # hard delete
            assert store.load_character("c1") is None
            assert store.load_character("c1", include_deleted=True) is None
        finally:
            del store; gc.collect()
            if os.path.exists(db_path): os.remove(db_path)

    def test_recover_soft_deleted(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_recover.db")
        if os.path.exists(db_path): os.remove(db_path)
        store = Store(db_path)
        try:
            sheet = CharacterSheet(character_id="c1", name="Charlie")
            store.save_character(CharacterArchive(character_id="c1", player_id="u1", sheet=sheet))
            store.soft_delete_character("c1")
            store.recover_character("c1")
            loaded = store.load_character("c1")
            assert loaded is not None
            assert loaded.sheet.name == "Charlie"
        finally:
            del store; gc.collect()
            if os.path.exists(db_path): os.remove(db_path)
```

- [ ] **Step 2: Run -> AttributeError**
- [ ] **Step 3: Implement in Store**

Add `deleted_at` column to characters table in `_init_db`:
```python
deleted_at TIMESTAMP
```

Methods:

```python
def soft_delete_character(self, character_id: str) -> None:
    from datetime import datetime, timezone
    with sqlite3.connect(self.db_path) as conn:
        conn.execute(
            "UPDATE characters SET deleted_at = ? WHERE character_id = ?",
            (datetime.now(timezone.utc).isoformat(), character_id),
        )

def recover_character(self, character_id: str) -> None:
    with sqlite3.connect(self.db_path) as conn:
        conn.execute(
            "UPDATE characters SET deleted_at = NULL WHERE character_id = ?",
            (character_id,),
        )
```

Update `load_character` to accept `include_deleted: bool = False` and filter:
```python
def load_character(self, character_id: str, include_deleted: bool = False) -> CharacterArchive | None:
    ...
    query = "SELECT * FROM characters WHERE character_id = ?"
    if not include_deleted:
        query += " AND deleted_at IS NULL"
    row = conn.execute(query, (character_id,)).fetchone()
```

- [ ] **Step 4: Tests pass**
- [ ] **Step 5: Commit**

---

### Task 3: COC Legality Validation

**Files:**
- Create: `src/dm_bot/character/validation.py`
- Modify: `tests/test_character.py`

- [ ] **Step 1: Tests**

```python
class TestCharacterValidation:
    def test_valid_character_passes(self):
        from dm_bot.character.validation import validate_character
        from dm_bot.character.sheet import CharacterSheet

        sheet = CharacterSheet(character_id="c1", name="Alice")
        errors = validate_character(sheet)
        assert len(errors) == 0

    def test_invalid_stats(self):
        from dm_bot.character.validation import validate_character
        from dm_bot.character.sheet import CharacterSheet

        sheet = CharacterSheet(character_id="c1", name="Alice", strength=200)
        errors = validate_character(sheet)
        assert any("strength" in e.lower() or "STR" in e for e in errors)

    def test_underage(self):
        from dm_bot.character.validation import validate_character
        from dm_bot.character.sheet import CharacterSheet

        sheet = CharacterSheet(character_id="c1", name="Kid", age=5)
        errors = validate_character(sheet)
        assert any("age" in e.lower() for e in errors)

    def test_empty_name_fails(self):
        from dm_bot.character.validation import validate_character
        from dm_bot.character.sheet import CharacterSheet

        sheet = CharacterSheet(character_id="c1", name="")
        errors = validate_character(sheet)
        assert len(errors) > 0
```

- [ ] **Step 2: Run -> ImportError**
- [ ] **Step 3: Implement**

Create `src/dm_bot/character/validation.py`:

```python
"""COC character validation rules."""

from dm_bot.character.sheet import CharacterSheet


STAT_MIN = 3
STAT_MAX = 99
AGE_MIN = 15
AGE_MAX = 120


def validate_character(sheet: CharacterSheet) -> list[str]:
    errors: list[str] = []
    if not sheet.name:
        errors.append("Name is required")
    if sheet.age < AGE_MIN:
        errors.append(f"Age {sheet.age} is below minimum {AGE_MIN}")
    if sheet.age > AGE_MAX:
        errors.append(f"Age {sheet.age} exceeds maximum {AGE_MAX}")
    for stat_name in ["strength", "constitution", "size", "dexterity",
                       "appearance", "intelligence", "power", "education"]:
        val = getattr(sheet, stat_name, 0)
        if val < STAT_MIN or val > STAT_MAX:
            errors.append(f"{stat_name.title()} {val} out of range [{STAT_MIN}-{STAT_MAX}]")
    return errors
```

- [ ] **Step 4: Tests pass**
- [ ] **Step 5: Commit**

---

### Task 4: Integration — Import → Validate → Persist → Delete Pipeline

**Files:**
- Modify: `tests/test_character_import.py`
- Modify: `tests/test_character.py`

- [ ] **Step 1: Tests**

In `tests/test_character_import.py`:

```python
class TestImportPipeline:
    def test_import_validate_save(self):
        from dm_bot.character.importer import import_character
        from dm_bot.character.validation import validate_character
        from dm_bot.store.db import Store
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_import_pipe.db")
        if os.path.exists(db_path): os.remove(db_path)
        store = Store(db_path)
        try:
            data = '{"name": "Alice", "age": 30, "strength": 60, "constitution": 50}'
            archive = import_character(data, player_id="u1")
            assert archive is not None
            errors = validate_character(archive.sheet)
            assert len(errors) == 0
            store.save_character(archive)
            loaded = store.load_character(archive.character_id)
            assert loaded is not None
            assert loaded.sheet.name == "Alice"
        finally:
            del store; gc.collect()
            if os.path.exists(db_path): os.remove(db_path)
```

In `tests/test_character.py`, add to `TestCharacterSoftDelete`:

```python
    def test_soft_delete_visible_in_list(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_softlist.db")
        if os.path.exists(db_path): os.remove(db_path)
        store = Store(db_path)
        try:
            sheet = CharacterSheet(character_id="c1", name="Alice")
            store.save_character(CharacterArchive(character_id="c1", player_id="u1", sheet=sheet))
            store.soft_delete_character("c1")
            active = store.list_characters("u1")
            assert len(active) == 0
            store.recover_character("c1")
            active = store.list_characters("u1")
            assert len(active) == 1
        finally:
            del store; gc.collect()
            if os.path.exists(db_path): os.remove(db_path)
```

- [ ] **Step 2: Tests pass**
- [ ] **Step 3: Commit**

---

### Task 5: Smoke Check

- [ ] **Step 1: `uv run pytest -q` -> ALL PASS**
- [ ] **Step 2: `uv run python -m dm_bot.main smoke-check` -> OK**
- [ ] **Step 3: Commit**
