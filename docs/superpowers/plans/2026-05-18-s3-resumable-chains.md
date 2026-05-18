# S3: Resumable Chains & Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trigger chain execution can be interrupted, resumed safely, and audited with a durable trace that survives process restart.

**Architecture:** Two new models (TriggerChain, AuditEntry) in `trigger/models.py`. Two new tables in Store. TriggerEngine gains chain lifecycle management with Store integration — creates chains and persists audit entries on `fire_event`, auto-recovers running/blocked chains from Store in `__init__`, supports `resume_chain()` for manual recovery.

**Tech Stack:** Python, Pydantic v2, SQLite

---

### Task 1: TriggerChain and AuditEntry Models

**Files:**
- Modify: `src/dm_bot/trigger/models.py`
- Modify: `tests/test_trigger.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_trigger.py`:

```python
class TestTriggerChain:
    def test_create_chain(self):
        from dm_bot.trigger.models import TriggerChain
        chain = TriggerChain(event_type="action.submit", trigger_id="tr_1")
        assert chain.chain_id is not None
        assert chain.status == "running"
        assert chain.completed_at is None

    def test_complete_chain(self):
        from dm_bot.trigger.models import TriggerChain
        chain = TriggerChain(event_type="action.submit", trigger_id="tr_1")
        chain.complete()
        assert chain.status == "completed"
        assert chain.completed_at is not None

    def test_mark_blocked(self):
        from dm_bot.trigger.models import TriggerChain
        chain = TriggerChain(event_type="action.submit", trigger_id="tr_1")
        chain.mark_blocked()
        assert chain.status == "blocked"


class TestAuditEntry:
    def test_create_audit(self):
        from dm_bot.trigger.models import AuditEntry
        entry = AuditEntry(
            chain_id="ch_1",
            step="trigger.match",
            detail={"trigger_id": "tr_1"},
        )
        assert entry.entry_id is not None
        assert entry.timestamp is not None

    def test_audit_ordering(self):
        from dm_bot.trigger.models import AuditEntry
        e1 = AuditEntry(chain_id="ch_1", step="event.fire", detail={})
        e2 = AuditEntry(chain_id="ch_1", step="reaction.exec", detail={})
        assert e2.timestamp >= e1.timestamp
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_trigger.py::TestTriggerChain tests/test_trigger.py::TestAuditEntry -v`
Expected: ImportError for TriggerChain / AuditEntry

- [ ] **Step 3: Implement models**

Add to `src/dm_bot/trigger/models.py`:

```python
class TriggerChain(BaseModel):
    """Tracks execution of a trigger event chain."""

    chain_id: str = Field(default_factory=lambda: f"ch_{uuid.uuid4().hex[:12]}")
    event_id: str = ""
    event_type: str
    trigger_id: str
    status: str = "running"  # running | completed | blocked | failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    def complete(self) -> None:
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)

    def mark_blocked(self) -> None:
        self.status = "blocked"

    def mark_failed(self) -> None:
        self.status = "failed"


class AuditEntry(BaseModel):
    """A single auditable step in a trigger chain."""

    entry_id: str = Field(default_factory=lambda: f"aud_{uuid.uuid4().hex[:12]}")
    chain_id: str
    step: str  # event.fire, trigger.match, reaction.exec, blocker.create, blocker.resolve, chain.resume
    detail: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_trigger.py::TestTriggerChain tests/test_trigger.py::TestAuditEntry -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/trigger/models.py tests/test_trigger.py
git commit -m "feat(s3): add TriggerChain and AuditEntry models"
```

---

### Task 2: Chain and Audit Persistence in Store

**Files:**
- Modify: `src/dm_bot/store/db.py`
- Modify: `tests/test_trigger.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_trigger.py`:

```python
class TestChainPersistence:
    def test_save_and_load_chain(self):
        from dm_bot.store.db import Store
        from dm_bot.trigger.models import TriggerChain
        import tempfile, os

        db_path = os.path.join(tempfile.gettempdir(), "test_chains.db")
        store = Store(db_path)
        chain = TriggerChain(event_type="action.submit", trigger_id="tr_1")
        store.save_chain(chain)
        loaded = store.load_chain(chain.chain_id)
        assert loaded is not None
        assert loaded.chain_id == chain.chain_id
        assert loaded.status == "running"
        os.remove(db_path)

    def test_save_and_list_chains_by_status(self):
        from dm_bot.store.db import Store
        from dm_bot.trigger.models import TriggerChain
        import tempfile, os

        db_path = os.path.join(tempfile.gettempdir(), "test_chains2.db")
        store = Store(db_path)
        c1 = TriggerChain(event_type="test", trigger_id="t1")
        c2 = TriggerChain(event_type="test", trigger_id="t2")
        c2.complete()
        store.save_chain(c1)
        store.save_chain(c2)
        running = store.list_chains_by_status("running")
        assert len(running) == 1
        assert running[0].chain_id == c1.chain_id
        os.remove(db_path)

    def test_save_and_load_audit_entries(self):
        from dm_bot.store.db import Store
        from dm_bot.trigger.models import AuditEntry
        import tempfile, os

        db_path = os.path.join(tempfile.gettempdir(), "test_audit.db")
        store = Store(db_path)
        e1 = AuditEntry(chain_id="ch_1", step="event.fire", detail={"type": "test"})
        e2 = AuditEntry(chain_id="ch_1", step="trigger.match", detail={"trigger_id": "tr_1"})
        store.save_audit_entry(e1)
        store.save_audit_entry(e2)
        entries = store.list_audit_entries("ch_1")
        assert len(entries) == 2
        assert entries[0].step == "event.fire"
        assert entries[1].step == "trigger.match"
        os.remove(db_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_trigger.py::TestChainPersistence -v`
Expected: AttributeError (Store has no save_chain method)

- [ ] **Step 3: Implement chain and audit persistence**

In `src/dm_bot/store/db.py`, update the import:

```python
from dm_bot.trigger.models import BlockerCheckpoint, TriggerChain, AuditEntry
```

Add tables to `_init_db` (append to the SQL string before the closing `"""`):

```python
                CREATE TABLE IF NOT EXISTS trigger_chains (
                    chain_id TEXT PRIMARY KEY,
                    event_id TEXT DEFAULT '',
                    event_type TEXT NOT NULL,
                    trigger_id TEXT NOT NULL,
                    status TEXT DEFAULT 'running',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS audit_entries (
                    entry_id TEXT PRIMARY KEY,
                    chain_id TEXT NOT NULL,
                    step TEXT NOT NULL,
                    detail TEXT DEFAULT '{}',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
```

Add methods to the Store class:

```python
    def save_chain(self, chain: TriggerChain) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO trigger_chains
                   (chain_id, event_id, event_type, trigger_id, status, created_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (chain.chain_id, chain.event_id, chain.event_type,
                 chain.trigger_id, chain.status,
                 chain.created_at.isoformat(),
                 chain.completed_at.isoformat() if chain.completed_at else None),
            )

    def load_chain(self, chain_id: str) -> TriggerChain | None:
        from datetime import datetime
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM trigger_chains WHERE chain_id = ?", (chain_id,)
            ).fetchone()
            if not row:
                return None
            return TriggerChain(
                chain_id=row[0], event_id=row[1] or "", event_type=row[2],
                trigger_id=row[3], status=row[4],
                created_at=datetime.fromisoformat(row[5]),
                completed_at=datetime.fromisoformat(row[6]) if row[6] else None,
            )

    def list_chains_by_status(self, status: str) -> list[TriggerChain]:
        from datetime import datetime
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM trigger_chains WHERE status = ?", (status,)
            ).fetchall()
            return [
                TriggerChain(
                    chain_id=r[0], event_id=r[1] or "", event_type=r[2],
                    trigger_id=r[3], status=r[4],
                    created_at=datetime.fromisoformat(r[5]),
                    completed_at=datetime.fromisoformat(r[6]) if r[6] else None,
                )
                for r in rows
            ]

    def save_audit_entry(self, entry: AuditEntry) -> None:
        import json
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO audit_entries
                   (entry_id, chain_id, step, detail, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (entry.entry_id, entry.chain_id, entry.step,
                 json.dumps(entry.detail), entry.timestamp.isoformat()),
            )

    def list_audit_entries(self, chain_id: str) -> list[AuditEntry]:
        import json
        from datetime import datetime
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM audit_entries WHERE chain_id = ? ORDER BY timestamp ASC",
                (chain_id,)
            ).fetchall()
            return [
                AuditEntry(
                    entry_id=r[0], chain_id=r[1], step=r[2],
                    detail=json.loads(r[3]) if r[3] else {},
                    timestamp=datetime.fromisoformat(r[4]),
                )
                for r in rows
            ]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_trigger.py::TestChainPersistence -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/store/db.py tests/test_trigger.py
git commit -m "feat(s3): add chain and audit persistence to Store"
```

---

### Task 3: Engine Chain Integration with Persistence and Resume

**Files:**
- Modify: `src/dm_bot/trigger/engine.py`
- Modify: `tests/test_trigger.py`

- [ ] **Step 1: Write failing tests**

Append new tests AFTER the existing TestTriggerEngine class. The existing tests (test_register_trigger, test_fire_matches_trigger, test_fire_no_match, test_reaction_priority_order) remain unchanged and should continue passing with the new engine signature (optional store param).

New tests for chain lifecycle, persistence, audit, resume, and recovery. The existing TestTriggerEngine class (4 tests) remains unchanged in the file.

```python
class TestEngineChains:
    def test_fire_event_creates_chain(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent

        engine = TriggerEngine()
        trigger = Trigger(
            trigger_id="tr_1",
            event_type="action.submit",
            reactions=[Reaction(reaction_id="rx_1", effect_type="message")],
        )
        engine.register_trigger(trigger)
        event = TriggerEvent(event_type="action.submit", source={"scene_id": "s1"})
        engine.fire_event(event)
        assert len(engine.chains) == 1
        assert engine.chains[0].event_type == "action.submit"

    def test_chain_marked_completed_after_execution(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent

        engine = TriggerEngine()
        trigger = Trigger(
            trigger_id="tr_1",
            event_type="test.event",
            reactions=[Reaction(reaction_id="rx_1", effect_type="log")],
        )
        engine.register_trigger(trigger)
        engine.fire_event(TriggerEvent(event_type="test.event", source={}))
        assert engine.chains[0].status == "completed"

    def test_fire_event_records_audit_trail(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent

        engine = TriggerEngine()
        trigger = Trigger(
            trigger_id="tr_1",
            event_type="test.event",
            reactions=[Reaction(reaction_id="rx_1", effect_type="log")],
        )
        engine.register_trigger(trigger)
        engine.fire_event(TriggerEvent(event_type="test.event", source={}))
        audit = engine.get_audit_trail()
        steps = [e.step for e in audit]
        assert "event.fire" in steps
        assert "trigger.match" in steps

    def test_no_match_no_chain(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import TriggerEvent

        engine = TriggerEngine()
        engine.fire_event(TriggerEvent(event_type="no_match", source={}))
        assert len(engine.chains) == 0

    def test_persists_chain_to_store(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent
        from dm_bot.store.db import Store
        import tempfile, os

        db_path = os.path.join(tempfile.gettempdir(), "test_engine_chains.db")
        store = Store(db_path)
        engine = TriggerEngine(store=store)
        trigger = Trigger(
            trigger_id="tr_1",
            event_type="test.event",
            reactions=[Reaction(reaction_id="rx_1", effect_type="log")],
        )
        engine.register_trigger(trigger)
        engine.fire_event(TriggerEvent(event_type="test.event", source={}))
        loaded = store.load_chain(engine.chains[0].chain_id)
        assert loaded is not None
        assert loaded.status == "completed"
        os.remove(db_path)

    def test_persists_audit_to_store(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent
        from dm_bot.store.db import Store
        import tempfile, os

        db_path = os.path.join(tempfile.gettempdir(), "test_engine_audit.db")
        store = Store(db_path)
        engine = TriggerEngine(store=store)
        trigger = Trigger(
            trigger_id="tr_1",
            event_type="test.event",
            reactions=[Reaction(reaction_id="rx_1", effect_type="log")],
        )
        engine.register_trigger(trigger)
        engine.fire_event(TriggerEvent(event_type="test.event", source={}))
        entries = store.list_audit_entries(engine.chains[0].chain_id)
        assert len(entries) >= 2
        os.remove(db_path)
```

- [ ] **Step 2: Write resume and recovery tests**

Append to the same test block from Step 1:

```python
class TestChainResume:
    def test_resume_creates_chain_in_memory(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import TriggerChain

        engine = TriggerEngine()
        chain = TriggerChain(event_type="test", trigger_id="tr_1", status="blocked")
        engine.resume_chain(chain)
        assert len(engine.chains) == 1
        assert engine.chains[0].chain_id == chain.chain_id

    def test_resume_sets_running_status(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import TriggerChain

        engine = TriggerEngine()
        chain = TriggerChain(event_type="test", trigger_id="tr_1", status="blocked")
        engine.resume_chain(chain)
        assert engine.chains[0].status == "running"

    def test_resume_records_audit_entry(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import TriggerChain

        engine = TriggerEngine()
        chain = TriggerChain(event_type="test", trigger_id="tr_1", status="blocked")
        engine.resume_chain(chain)
        audit = engine.get_audit_trail(chain.chain_id)
        assert any(e.step == "chain.resume" for e in audit)

    def test_recover_from_store(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import TriggerChain
        from dm_bot.store.db import Store
        import tempfile, os

        db_path = os.path.join(tempfile.gettempdir(), "test_recover.db")
        store = Store(db_path)

        old_chain = TriggerChain(event_type="action.submit", trigger_id="tr_1", status="blocked")
        store.save_chain(old_chain)

        engine = TriggerEngine(store=store)
        engine.recover_chains()
        assert len(engine.chains) == 1
        assert engine.chains[0].chain_id == old_chain.chain_id
        assert engine.chains[0].status == "running"
        os.remove(db_path)

    def test_recover_no_store_does_nothing(self):
        from dm_bot.trigger.engine import TriggerEngine

        engine = TriggerEngine()
        engine.recover_chains()
        assert len(engine.chains) == 0

    def test_recover_multiple_chains(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import TriggerChain
        from dm_bot.store.db import Store
        import tempfile, os

        db_path = os.path.join(tempfile.gettempdir(), "test_recover_multi.db")
        store = Store(db_path)
        store.save_chain(TriggerChain(event_type="a", trigger_id="t1", status="blocked"))
        store.save_chain(TriggerChain(event_type="b", trigger_id="t2", status="running"))
        store.save_chain(TriggerChain(event_type="c", trigger_id="t3", status="completed"))

        engine = TriggerEngine(store=store)
        engine.recover_chains()
        assert len(engine.chains) == 2
        os.remove(db_path)

    def test_auto_recover_on_init(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import TriggerChain
        from dm_bot.store.db import Store
        import tempfile, os

        db_path = os.path.join(tempfile.gettempdir(), "test_auto_recover.db")
        store = Store(db_path)
        store.save_chain(TriggerChain(event_type="test", trigger_id="t1", status="blocked"))

        engine = TriggerEngine(store=store)
        assert len(engine.chains) == 1
        os.remove(db_path)
```

- [ ] **Step 3: Run all new tests to verify they fail**

Run: `uv run pytest tests/test_trigger.py::TestTriggerEngine tests/test_trigger.py::TestEngineChains tests/test_trigger.py::TestChainResume -v`
Expected: AttributeError (TriggerEngine has no chains / no Store support / no resume_chain)

- [ ] **Step 4: Rewrite TriggerEngine**

Replace `src/dm_bot/trigger/engine.py`:

```python
"""Trigger event processing pipeline with chain lifecycle and audit trail."""

from dm_bot.trigger.models import (
    Trigger, TriggerEvent, Reaction,
    TriggerChain, AuditEntry,
)
from dm_bot.store.db import Store


class TriggerEngine:
    """Matches events to triggers with persisted chains and auditable trail."""

    def __init__(self, store: Store | None = None) -> None:
        self._triggers: dict[str, Trigger] = {}
        self._chains: list[TriggerChain] = []
        self._audit: list[AuditEntry] = []
        self._store = store
        self.recover_chains()

    @property
    def triggers(self) -> dict[str, Trigger]:
        return dict(self._triggers)

    @property
    def chains(self) -> list[TriggerChain]:
        return list(self._chains)

    def register_trigger(self, trigger: Trigger) -> None:
        self._triggers[trigger.trigger_id] = trigger

    def unregister(self, trigger_id: str) -> None:
        self._triggers.pop(trigger_id, None)

    def fire_event(self, event: TriggerEvent) -> list[Reaction]:
        matched = self._find_matching_triggers(event)
        if not matched:
            return []

        all_reactions: list[Reaction] = []
        for trigger in matched:
            chain = TriggerChain(
                event_id=event.event_id,
                event_type=event.event_type,
                trigger_id=trigger.trigger_id,
            )
            self._chains.append(chain)

            self._record_audit(chain.chain_id, "event.fire", {
                "event_id": event.event_id,
                "event_type": event.event_type,
            })
            self._record_audit(chain.chain_id, "trigger.match", {
                "trigger_id": trigger.trigger_id,
            })

            reactions = self._collect_ordered_reactions(trigger)
            all_reactions.extend(reactions)

            for reaction in reactions:
                self._record_audit(chain.chain_id, "reaction.exec", {
                    "reaction_id": reaction.reaction_id,
                    "effect_type": reaction.effect_type,
                })
                self._execute_single(reaction)

            chain.complete()
            self._persist_chain(chain)

        return all_reactions

    def resume_chain(self, chain: TriggerChain) -> None:
        chain.status = "running"
        self._chains.append(chain)
        self._record_audit(chain.chain_id, "chain.resume", {
            "trigger_id": chain.trigger_id,
            "event_type": chain.event_type,
        })
        self._persist_chain(chain)

    def recover_chains(self, store: Store | None = None) -> None:
        s = store or self._store
        if s is None:
            return
        for status in ("running", "blocked"):
            for chain in s.list_chains_by_status(status):
                self.resume_chain(chain)

    def list_running_chains(self) -> list[TriggerChain]:
        return [c for c in self._chains if c.status == "running"]

    def _find_matching_triggers(self, event: TriggerEvent) -> list[Trigger]:
        return [t for t in self._triggers.values() if t.event_type == event.event_type]

    def _collect_ordered_reactions(self, trigger: Trigger) -> list[Reaction]:
        return sorted(trigger.reactions, key=lambda r: r.priority)

    def _execute_single(self, reaction: Reaction) -> None:
        pass

    def _record_audit(self, chain_id: str, step: str, detail: dict) -> None:
        entry = AuditEntry(chain_id=chain_id, step=step, detail=detail)
        self._audit.append(entry)
        if self._store:
            self._store.save_audit_entry(entry)

    def _persist_chain(self, chain: TriggerChain) -> None:
        if self._store:
            self._store.save_chain(chain)

    def get_audit_trail(self, chain_id: str | None = None) -> list[AuditEntry]:
        if chain_id:
            return [e for e in self._audit if e.chain_id == chain_id]
        return list(self._audit)
```

- [ ] **Step 5: Run all new and existing tests to verify they pass**

Run: `uv run pytest tests/test_trigger.py::TestTriggerEngine tests/test_trigger.py::TestEngineChains tests/test_trigger.py::TestChainResume -v`
Expected: ALL PASS

- [ ] **Step 6: Run full suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add src/dm_bot/trigger/engine.py tests/test_trigger.py
git commit -m "feat(s3): integrate chain lifecycle, Store persistence, and resume into TriggerEngine"
```

---

### Task 4: Smoke Check and Final Verification

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 2: Run smoke check**

Run: `uv run python -m dm_bot.main smoke-check`
Expected: "All core modules import successfully."

- [ ] **Step 3: Commit any remaining files**

```bash
git add -A && git commit -m "chore(s3): final gate pass for resumable chains and audit"
```
