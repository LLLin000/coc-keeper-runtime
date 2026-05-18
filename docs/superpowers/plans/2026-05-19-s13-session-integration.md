# S13: Session Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Post-session character evolution with durable history and skill improvement tracking.

**Architecture:** SessionCheckpoint updates CharacterArchive skills using existing COC improvement rolls. AdventureLog stores structured session events from Publisher.

**Tech Stack:** Python, Pydantic v2, SQLite

---

### Task 1: SessionCheckpoint — Post-Session Character Update

**Files:**
- Create: `src/dm_bot/character/checkpoint.py`
- Create: `tests/test_checkpoint.py`

- [ ] **Step 1: Tests**

Create `C:\Users\Lin\Projects\discord-ai-keeper\tests\test_checkpoint.py`:

```python
class TestSessionCheckpoint:
    def test_improve_skills(self):
        from dm_bot.character.checkpoint import SessionCheckpoint
        from dm_bot.character.sheet import CharacterSheet

        sheet = CharacterSheet(character_id="c1", name="Alice", skills={"spot_hidden": 40, "library_use": 30})
        # improvement_roll < current_value = success
        cp = SessionCheckpoint()
        result = cp.process(sheet, skills_used=["spot_hidden", "library_use"],
                            improvement_rolls={"spot_hidden": 30, "library_use": 99})
        assert result.skills_tried == 2
        assert result.skills_improved >= 1  # spot_hidden: 30 < 40 -> success
        assert result.updated_sheet.skills["spot_hidden"] > 40

    def test_no_skills_no_change(self):
        from dm_bot.character.checkpoint import SessionCheckpoint
        from dm_bot.character.sheet import CharacterSheet

        sheet = CharacterSheet(character_id="c1", name="Alice")
        cp = SessionCheckpoint()
        result = cp.process(sheet, skills_used=[])
        assert result.skills_tried == 0
        assert result.skills_improved == 0
```

- [ ] **Step 2: Run -> ImportError**
- [ ] **Step 3: Implement**

Create `C:\Users\Lin\Projects\discord-ai-keeper\src\dm_bot\character\checkpoint.py`:

```python
"""Post-session character checkpoint processing."""

from pydantic import BaseModel, Field

from dm_bot.character.sheet import CharacterSheet
from dm_bot.rules.coc.experience import roll_all_skill_improvements


class CheckpointResult(BaseModel):
    """Result of a session checkpoint."""

    skills_tried: int = 0
    skills_improved: int = 0
    improved_skills: list[str] = Field(default_factory=list)
    updated_sheet: CharacterSheet | None = None


class SessionCheckpoint:
    """Processes post-session character evolution."""

    def process(
        self,
        sheet: CharacterSheet,
        skills_used: list[str],
        improvement_rolls: dict[str, int] | None = None,
    ) -> CheckpointResult:
        if not skills_used:
            return CheckpointResult(updated_sheet=sheet)

        results = roll_all_skill_improvements(skills_used, sheet.skills, improvement_rolls)
        improved = [r for r in results if r.improved]

        new_skills = dict(sheet.skills)
        for r in improved:
            new_skills[r.skill_key] = r.new_value

        new_sheet = sheet.model_copy(update={"skills": new_skills})
        return CheckpointResult(
            skills_tried=len(results),
            skills_improved=len(improved),
            improved_skills=[r.skill_key for r in improved],
            updated_sheet=new_sheet,
        )
```

- [ ] **Step 4: Tests pass**
- [ ] **Step 5: Commit**

---

### Task 2: AdventureLog — Structured Session History

**Files:**
- Create: `src/dm_bot/character/adventure_log.py`
- Modify: `src/dm_bot/store/db.py`
- Create: `tests/test_adventure_log.py`

- [ ] **Step 1: Tests**

```python
class TestAdventureLog:
    def test_log_entry(self):
        from dm_bot.character.adventure_log import AdventureLog, LogEntry

        entry = LogEntry(session_id="ses_1", entry_type="skill_improvement", detail="spot_hidden 40->50")
        log = AdventureLog()
        log.add_entry(entry)
        entries = log.get_entries("ses_1")
        assert len(entries) == 1
        assert entries[0].entry_type == "skill_improvement"

    def test_log_order(self):
        from dm_bot.character.adventure_log import AdventureLog, LogEntry

        log = AdventureLog()
        log.add_entry(LogEntry(session_id="ses_1", entry_type="first", detail="a"))
        log.add_entry(LogEntry(session_id="ses_1", entry_type="second", detail="b"))
        entries = log.get_entries("ses_1")
        assert entries[0].entry_type == "first"
        assert entries[1].entry_type == "second"
```

- [ ] **Step 2: Run -> ImportError**
- [ ] **Step 3: Implement**

Create `C:\Users\Lin\Projects\discord-ai-keeper\src\dm_bot\character\adventure_log.py`:

```python
"""Structured adventure session log."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """A single entry in the adventure log."""

    session_id: str
    entry_type: str  # skill_improvement, checkpoint, scene_enter, clue_found
    detail: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AdventureLog:
    """In-memory adventure log (persisted via Store later)."""

    def __init__(self) -> None:
        self._entries: list[LogEntry] = []

    def add_entry(self, entry: LogEntry) -> None:
        self._entries.append(entry)

    def get_entries(self, session_id: str | None = None) -> list[LogEntry]:
        if session_id:
            return [e for e in self._entries if e.session_id == session_id]
        return list(self._entries)
```

- [ ] **Step 4: Tests pass**
- [ ] **Step 5: Commit**

---

### Task 3: Store Integration — Persist Checkpoint + Log

**Files:**
- Modify: `src/dm_bot/store/db.py`
- Modify: `tests/test_checkpoint.py`

- [ ] **Step 1: Tests**

```python
class TestCheckpointPersistence:
    def test_save_checkpoint(self):
        from dm_bot.store.db import Store
        from dm_bot.character.checkpoint import SessionCheckpoint
        from dm_bot.character.sheet import CharacterSheet
        from dm_bot.character.archive import CharacterArchive
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_chkpt.db")
        if os.path.exists(db_path): os.remove(db_path)
        store = Store(db_path)
        try:
            sheet = CharacterSheet(character_id="c1", name="Alice", skills={"spot_hidden": 40})
            archive = CharacterArchive(character_id="c1", player_id="u1", sheet=sheet)
            store.save_character(archive)

            cp = SessionCheckpoint()
            result = cp.process(sheet, skills_used=["spot_hidden"], improvement_rolls={"spot_hidden": 30})
            assert result.skills_improved == 1

            updated = CharacterArchive(character_id="c1", player_id="u1", sheet=result.updated_sheet)
            store.save_character(updated)
            loaded = store.load_character("c1")
            assert loaded.sheet.skills["spot_hidden"] > 40
        finally:
            del store; gc.collect()
            if os.path.exists(db_path): os.remove(db_path)
```

- [ ] **Step 2: Tests pass**
- [ ] **Step 3: Commit**

---

### Task 4: Smoke Check

- [ ] **Step 1: `uv run pytest -q` -> ALL PASS**
- [ ] **Step 2: `uv run python -m dm_bot.main smoke-check` -> OK**
- [ ] **Step 3: Commit**
