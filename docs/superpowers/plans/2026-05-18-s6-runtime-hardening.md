# S6: Runtime Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lock S1-S5 capabilities into reliable state with integration tests, schema versioning, module validation, and placeholder cleanup.

**Architecture:** Add lightweight integration tests for the full trigger→reveal→publish pipeline. Add schema versioning to Store for forward migrations. Enhance preflight with module compatibility checks. Wire AdventureLoader to file system.

**Tech Stack:** Python, Pydantic v2, SQLite, pytest

---

### Task 1: Store Schema Versioning

**Files:**
- Modify: `src/dm_bot/store/db.py`
- Create: `tests/test_store.py`

- [ ] **Step 1: Write failing test**

In `tests/test_store.py`:
```python
"""Tests for Store persistence."""

from dm_bot.store.db import Store
import tempfile, os, gc

SCHEMA_VERSION = 1

class TestSchemaVersion:
    def test_schema_version_table_exists(self):
        db_path = os.path.join(tempfile.gettempdir(), "test_schema.db")
        try:
            store = Store(db_path)
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute(
                    "SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1"
                ).fetchall()
            assert len(rows) == 1
            assert rows[0][0] == SCHEMA_VERSION
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_store.py::TestSchemaVersion -v`
Expected: OperationalError (no such table)

- [ ] **Step 3: Add schema versioning to Store**

In `src/dm_bot/store/db.py`, add to `_init_db`:

```python
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

After `executescript`, add:

```python
row = conn.execute(
    "SELECT MAX(version) FROM schema_version"
).fetchone()
current = row[0] if row[0] else 0
if current < 1:
    conn.execute(
        "INSERT INTO schema_version (version) VALUES (1)"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_store.py::TestSchemaVersion -v`
Expected: PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/store/db.py tests/test_store.py
git commit -m "feat(s6): add schema version tracking to Store"
```

---

### Task 2: AdventureLoader File Loading

**Files:**
- Modify: `src/dm_bot/adventure/loader.py`
- Create: `tests/test_adventure_loader.py`

- [ ] **Step 1: Write failing test**

In `tests/test_adventure_loader.py`:
```python
"""Tests for adventure loader."""

import tempfile, json, os, gc
from dm_bot.adventure.loader import AdventureLoader


class TestAdventureLoader:
    def test_load_from_file(self):
        loader = AdventureLoader()
        data = {
            "adventure_id": "test_mansion",
            "name": "The Haunted Mansion",
            "scenes": {
                "hall": {
                    "scene_id": "hall",
                    "name": "Entrance Hall",
                    "description": "A dark hallway.",
                }
            },
        }
        tmp = os.path.join(tempfile.gettempdir(), "test_adventure.json")
        try:
            with open(tmp, "w") as f:
                json.dump(data, f)
            adv = loader.load_module(tmp)
            assert adv.adventure_id == "test_mansion"
            assert adv.name == "The Haunted Mansion"
            assert "hall" in adv.scenes
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_adventure_loader.py::TestAdventureLoader -v`
Expected: test_load_from_file loads but returns Adventure with empty scenes (current behavior = no file loading)

- [ ] **Step 3: Implement file loading in AdventureLoader**

In `src/dm_bot/adventure/loader.py`, replace:

```python
def load_module(self, module_name: str) -> Adventure:
    # TODO: 从文件系统加载
    return Adventure(adventure_id=module_name, name=module_name)
```

With:

```python
import json
from pathlib import Path

def load_module(self, module_name: str) -> Adventure:
    path = Path(module_name)
    if path.suffix == ".json":
        try:
            with open(path) as f:
                data = json.load(f)
            return Adventure.model_validate(data)
        except FileNotFoundError:
            raise
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in adventure file {module_name}: {e}")
    return Adventure(adventure_id=module_name, name=module_name)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_adventure_loader.py::TestAdventureLoader -v`
Expected: PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/adventure/loader.py tests/test_adventure_loader.py
git commit -m "feat(s6): file-based adventure loading in AdventureLoader"
```

---

### Task 3: Preflight Enhancement

**Files:**
- Modify: `src/dm_bot/main.py`
- Test: None (manual verification via `uv run python -m dm_bot.main preflight`)

- [ ] **Step 1: Enhance `describe_runtime` and `preflight` command**

In `src/dm_bot/main.py`, update `describe_runtime` to include module compatibility info:

```python
def describe_runtime(settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    token_status = "configured" if settings.discord_token else "missing"

    module_checks = []
    modules = [
        ("adventure.models", "Scene model"),
        ("trigger.models", "Trigger models"),
        ("trigger.engine", "Trigger engine"),
        ("reveal.models", "Reveal models"),
        ("reveal.checker", "Reveal checker"),
        ("publish.models", "Publish models"),
        ("publish.publisher", "Publisher"),
        ("publish.contract", "Renderer contract"),
        ("store.db", "Store"),
    ]
    for mod_path, label in modules:
        try:
            __import__(f"dm_bot.{mod_path}")
            module_checks.append(f"  [OK] {label}")
        except Exception as e:
            module_checks.append(f"  [FAIL] {label}: {e}")

    return (
        f"discord_token={token_status}\n"
        f"narrator_model={settings.narrator_model}\n"
        f"ollama_base_url={settings.ollama_base_url}\n"
        f"module_checks:\n" + "\n".join(module_checks)
    )
```

- [ ] **Step 2: Verify preflight output**

Run: `uv run python -m dm_bot.main preflight`
Expected: Clean output showing all modules [OK]

- [ ] **Step 3: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add src/dm_bot/main.py
git commit -m "feat(s6): enhance preflight with module compatibility checks"
```

---

### Task 4: Integration Tests — Full Pipeline

**Files:**
- Create: `tests/test_integration_pipeline.py`

- [ ] **Step 1: Write integration tests**

```python
"""Integration tests for the full trigger->reveal->publish pipeline."""

import tempfile, os, gc
from dm_bot.trigger.models import (
    Trigger, Reaction, TriggerEvent, TriggerChain,
)
from dm_bot.trigger.engine import TriggerEngine
from dm_bot.reveal.models import RevealGate, KnowledgeState
from dm_bot.reveal.checker import RevealChecker
from dm_bot.publish.models import (
    ActionSubmittedEvent, ClueRevealedEvent,
    PublicationPath,
)
from dm_bot.publish.publisher import Publisher
from dm_bot.store.db import Store


class TestIntegrationPipeline:
    def test_trigger_fire_reveal_publish_flow(self):
        db_path = os.path.join(tempfile.gettempdir(), "test_pipeline.db")
        try:
            store = Store(db_path)
            engine = TriggerEngine(store=store)

            trigger = Trigger(
                trigger_id="tr_clue",
                event_type="action.submit",
                reactions=[Reaction(reaction_id="rx_clue", effect_type="reveal_clue")],
            )
            engine.register_trigger(trigger)

            event = TriggerEvent(event_type="action.submit", source={"scene_id": "s1"})
            reactions = engine.fire_event(event)
            assert len(reactions) == 1
            assert len(engine.chains) == 1
            assert engine.chains[0].status == "completed"

            gate = RevealGate(gate_id="g1", clue_id="secret_door", gate_type="skill_check")
            assert gate.is_open is False
            gate.open()
            assert gate.is_open is True

            knowledge = KnowledgeState(player_id="p1")
            knowledge.learn("secret_door")
            assert knowledge.knows("secret_door")

            checker = RevealChecker()
            assert checker.is_clue_visible("secret_door", "p1", [gate], knowledge) is True

            publisher = Publisher()
            event = ActionSubmittedEvent(
                event_id="e1", user_id="p1", action_text="search", visibility=PublicationPath.TABLE_VISIBLE
            )
            publisher.publish(event)
            assert len(publisher.get_events()) == 1
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_pipeline_with_blocker(self):
        db_path = os.path.join(tempfile.gettempdir(), "test_pipeline2.db")
        try:
            store = Store(db_path)
            engine = TriggerEngine(store=store)

            trigger = Trigger(
                trigger_id="tr_block",
                event_type="action.submit",
                reactions=[Reaction(reaction_id="rx_block", effect_type="block")],
            )
            engine.register_trigger(trigger)

            event = TriggerEvent(event_type="action.submit", source={})
            engine.fire_event(event)
            assert len(engine.chains) == 1

            persisted = store.list_chains_by_status("completed")
            assert len(persisted) == 1
            assert persisted[0].trigger_id == "tr_block"
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_scene_trigger_round_publish(self):
        from dm_bot.scene.round import Round
        from dm_bot.scene.action import Action

        db_path = os.path.join(tempfile.gettempdir(), "test_pipeline3.db")
        try:
            store = Store(db_path)
            engine = TriggerEngine(store=store)

            trigger = Trigger(
                trigger_id="tr_round",
                event_type="action.submit",
                reactions=[Reaction(reaction_id="rx_log", effect_type="log")],
            )
            engine.register_trigger(trigger)

            round_obj = Round(trigger_engine=engine)
            round_obj.start_collection()
            round_obj.submit_action(Action(user_id="u1", character_id="c1", action_text="search"))

            assert len(engine.chains) == 1
            assert engine.chains[0].status == "completed"

            resolved = round_obj.resolve()
            assert len(resolved) == 1

            publisher = Publisher()
            for action in resolved:
                publisher.publish(ActionSubmittedEvent(
                    event_id=f"evt_{action.action_id}",
                    user_id=action.user_id,
                    action_text=action.action_text,
                    visibility=PublicationPath.TABLE_VISIBLE,
                ))
            assert len(publisher.get_events()) == 1
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)
```

- [ ] **Step 2: Run integration tests**

Run: `uv run pytest tests/test_integration_pipeline.py -v`
Expected: ALL PASS

- [ ] **Step 3: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration_pipeline.py
git commit -m "feat(s6): add integration tests for full trigger->reveal->publish pipeline"
```

---

### Task 5: Store Integrity Check

**Files:**
- Modify: `src/dm_bot/store/db.py`
- Modify: `tests/test_store.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_store.py`:
```python
class TestStoreIntegrity:
    def test_check_integrity_with_empty_db(self):
        import tempfile, os, gc
        db_path = os.path.join(tempfile.gettempdir(), "test_integrity.db")
        try:
            store = Store(db_path)
            result = store.check_integrity()
            assert result["status"] == "ok"
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_check_integrity_reports_crashed_db(self):
        db_path = os.path.join(tempfile.gettempdir(), "test_corrupt.db")
        try:
            with open(db_path, "wb") as f:
                f.write(b"not a sqlite file")
            store = Store(db_path)
            result = store.check_integrity()
            assert result["status"] == "corrupt"
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_store.py::TestStoreIntegrity -v`
Expected: AttributeError (Store has no check_integrity)

- [ ] **Step 3: Implement `check_integrity` on Store**

Add to `src/dm_bot/store/db.py`:

```python
def check_integrity(self) -> dict:
    """Validate Store health. Returns dict with status and details."""
    import sqlite3
    try:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA quick_check").fetchone()
            table_count = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            ).fetchone()[0]
            return {"status": "ok", "tables": table_count}
    except sqlite3.DatabaseError as e:
        return {"status": "corrupt", "error": str(e)}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_store.py::TestStoreIntegrity -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/store/db.py tests/test_store.py
git commit -m "feat(s6): add Store integrity check"
```

---

### Task 6: Smoke Check and Final Verification

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 2: Run smoke check**

Run: `uv run python -m dm_bot.main smoke-check`
Expected: "All core modules import successfully."

- [ ] **Step 3: Run preflight**

Run: `uv run python -m dm_bot.main preflight`
Expected: All modules [OK]

- [ ] **Step 4: Commit any remaining changes**

```bash
git add -A && git commit -m "chore(s6): final gate pass for runtime hardening"
```
