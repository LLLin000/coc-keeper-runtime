# S4: Reveal Gates & Knowledge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clues and reveals are enforced by runtime rules — "Clue X is visible to player Y only under condition Z."

**Architecture:** New `reveal/` module with RevealGate (condition model), KnowledgeState (per-player known clues), and RevealChecker (visibility query engine). Clue model gains optional gate reference. RevealChecker answers `is_clue_visible(clue_id, player_id)` by checking gate conditions and player knowledge.

**Tech Stack:** Python, Pydantic v2, SQLite

---

### Task 1: RevealGate and KnowledgeState Models

**Files:**
- Create: `src/dm_bot/reveal/__init__.py`
- Create: `src/dm_bot/reveal/models.py`
- Create: `tests/test_reveal.py`

- [ ] **Step 1: Write failing tests**

Write `tests/test_reveal.py`:

```python
"""Tests for reveal gate and knowledge models."""

from dm_bot.reveal.models import RevealGate, KnowledgeState


class TestRevealGate:
    def test_create_gate(self):
        gate = RevealGate(
            clue_id="clue_1",
            gate_type="skill_check",
            condition={"skill": "spot_hidden", "difficulty": "hard"},
        )
        assert gate.gate_id is not None
        assert gate.is_open is False
        assert gate.opened_at is None

    def test_open_gate(self):
        import datetime
        gate = RevealGate(clue_id="clue_1", gate_type="skill_check", condition={})
        gate.open()
        assert gate.is_open is True
        assert gate.opened_at is not None

    def test_gate_with_trigger(self):
        gate = RevealGate(
            clue_id="clue_1",
            gate_type="trigger",
            condition={"trigger_id": "tr_search_desk"},
        )
        assert gate.gate_type == "trigger"


class TestKnowledgeState:
    def test_empty_knowledge(self):
        ks = KnowledgeState(player_id="p1")
        assert ks.player_id == "p1"
        assert len(ks.known_clue_ids) == 0

    def test_learn_clue(self):
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("clue_1")
        assert "clue_1" in ks.known_clue_ids

    def test_learn_clue_idempotent(self):
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("clue_1")
        ks.learn_clue("clue_1")
        assert len(ks.known_clue_ids) == 1

    def test_knows_clue(self):
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("clue_1")
        assert ks.knows_clue("clue_1") is True
        assert ks.knows_clue("clue_2") is False

    def test_forget_clue(self):
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("clue_1")
        ks.forget_clue("clue_1")
        assert ks.knows_clue("clue_1") is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_reveal.py -v`
Expected: ModuleNotFoundError

- [ ] **Step 3: Implement models**

Create `src/dm_bot/reveal/__init__.py`:
```python
"""Reveal gate and knowledge models for visibility control."""
```

Create `src/dm_bot/reveal/models.py`:
```python
"""Reveal gate and knowledge tracking models."""

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class RevealGate(BaseModel):
    """A condition that must be met before a clue is revealed."""

    gate_id: str = Field(default_factory=lambda: f"rg_{uuid.uuid4().hex[:12]}")
    clue_id: str
    gate_type: str  # skill_check, trigger, scene_state, manual
    condition: dict[str, Any] = Field(default_factory=dict)
    is_open: bool = False
    opened_at: datetime | None = None
    opened_by: str = ""  # user_id, trigger_id, etc.

    def open(self, opened_by: str = "") -> None:
        self.is_open = True
        self.opened_at = datetime.now(timezone.utc)
        self.opened_by = opened_by


class KnowledgeState(BaseModel):
    """Per-player knowledge tracking within a session."""

    player_id: str
    known_clue_ids: list[str] = Field(default_factory=list)

    def learn_clue(self, clue_id: str) -> None:
        if clue_id not in self.known_clue_ids:
            self.known_clue_ids.append(clue_id)

    def knows_clue(self, clue_id: str) -> bool:
        return clue_id in self.known_clue_ids

    def forget_clue(self, clue_id: str) -> None:
        if clue_id in self.known_clue_ids:
            self.known_clue_ids.remove(clue_id)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_reveal.py -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/reveal/ tests/test_reveal.py
git commit -m "feat(s4): add RevealGate and KnowledgeState models"
```

---

### Task 2: RevealGate Persistence in Store

**Files:**
- Modify: `src/dm_bot/store/db.py`
- Modify: `tests/test_reveal.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_reveal.py`:

```python
from dm_bot.store.db import Store
from dm_bot.reveal.models import RevealGate


class TestRevealGatePersistence:
    def test_save_and_load_gate(self):
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_gates.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        gate = RevealGate(clue_id="clue_1", gate_type="skill_check", condition={"skill": "spot"})
        store.save_reveal_gate(gate)
        del store
        gc.collect()

        store2 = Store(db_path)
        loaded = store2.load_reveal_gate(gate.gate_id)
        assert loaded is not None
        assert loaded.clue_id == "clue_1"
        assert loaded.is_open is False
        del store2
        gc.collect()
        os.remove(db_path)

    def test_save_and_list_gates_by_clue(self):
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_gates2.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        g1 = RevealGate(clue_id="clue_1", gate_type="skill_check", condition={})
        g2 = RevealGate(clue_id="clue_1", gate_type="trigger", condition={"trigger_id": "tr_1"})
        store.save_reveal_gate(g1)
        store.save_reveal_gate(g2)
        del store
        gc.collect()

        store2 = Store(db_path)
        gates = store2.list_reveal_gates_by_clue("clue_1")
        assert len(gates) == 2
        del store2
        gc.collect()
        os.remove(db_path)

    def test_update_gate_status(self):
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_gates3.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        gate = RevealGate(clue_id="clue_1", gate_type="manual", condition={})
        store.save_reveal_gate(gate)
        gate.open(opened_by="kp")
        store.save_reveal_gate(gate)
        del store
        gc.collect()

        store2 = Store(db_path)
        loaded = store2.load_reveal_gate(gate.gate_id)
        assert loaded.is_open is True
        assert loaded.opened_by == "kp"
        del store2
        gc.collect()
        os.remove(db_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_reveal.py::TestRevealGatePersistence -v`
Expected: AttributeError (Store has no save_reveal_gate)

- [ ] **Step 3: Add persistence to Store**

In `src/dm_bot/store/db.py`, update import:
```python
from dm_bot.trigger.models import BlockerCheckpoint, TriggerChain, AuditEntry
from dm_bot.reveal.models import RevealGate
```

Add table to `_init_db` (within executescript, before closing `"""`):
```python
                CREATE TABLE IF NOT EXISTS reveal_gates (
                    gate_id TEXT PRIMARY KEY,
                    clue_id TEXT NOT NULL,
                    gate_type TEXT NOT NULL,
                    condition TEXT DEFAULT '{}',
                    is_open INTEGER DEFAULT 0,
                    opened_at TIMESTAMP,
                    opened_by TEXT DEFAULT ''
                );
```

Add methods:
```python
    def save_reveal_gate(self, gate: RevealGate) -> None:
        import json
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO reveal_gates
                   (gate_id, clue_id, gate_type, condition, is_open, opened_at, opened_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (gate.gate_id, gate.clue_id, gate.gate_type,
                 json.dumps(gate.condition),
                 1 if gate.is_open else 0,
                 gate.opened_at.isoformat() if gate.opened_at else None,
                 gate.opened_by),
            )

    def load_reveal_gate(self, gate_id: str) -> RevealGate | None:
        import json
        from datetime import datetime
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM reveal_gates WHERE gate_id = ?", (gate_id,)
            ).fetchone()
            if not row:
                return None
            return RevealGate(
                gate_id=row[0], clue_id=row[1], gate_type=row[2],
                condition=json.loads(row[3]) if row[3] else {},
                is_open=bool(row[4]),
                opened_at=datetime.fromisoformat(row[5]) if row[5] else None,
                opened_by=row[6] or "",
            )

    def list_reveal_gates_by_clue(self, clue_id: str) -> list[RevealGate]:
        import json
        from datetime import datetime
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM reveal_gates WHERE clue_id = ?", (clue_id,)
            ).fetchall()
            return [
                RevealGate(
                    gate_id=r[0], clue_id=r[1], gate_type=r[2],
                    condition=json.loads(r[3]) if r[3] else {},
                    is_open=bool(r[4]),
                    opened_at=datetime.fromisoformat(r[5]) if r[5] else None,
                    opened_by=r[6] or "",
                )
                for r in rows
            ]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_reveal.py::TestRevealGatePersistence -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/store/db.py tests/test_reveal.py
git commit -m "feat(s4): add reveal gate persistence to Store"
```

---

### Task 3: RevealChecker — Visibility Query Engine

**Files:**
- Create: `src/dm_bot/reveal/checker.py`
- Modify: `tests/test_reveal.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_reveal.py`:

```python
from dm_bot.reveal.checker import RevealChecker
from dm_bot.reveal.models import RevealGate, KnowledgeState


class TestRevealChecker:
    def test_clue_with_no_gate_is_visible(self):
        checker = RevealChecker()
        visible = checker.is_clue_visible(
            clue_id="clue_1",
            player_id="p1",
            gates=[],
            knowledge=KnowledgeState(player_id="p1"),
        )
        assert visible is True

    def test_clue_with_open_gate_is_visible(self):
        checker = RevealChecker()
        gate = RevealGate(clue_id="clue_1", gate_type="manual", condition={})
        gate.open()
        visible = checker.is_clue_visible(
            clue_id="clue_1",
            player_id="p1",
            gates=[gate],
            knowledge=KnowledgeState(player_id="p1"),
        )
        assert visible is True

    def test_clue_with_closed_gate_not_visible(self):
        checker = RevealChecker()
        gate = RevealGate(clue_id="clue_1", gate_type="skill_check", condition={"skill": "spot"})
        visible = checker.is_clue_visible(
            clue_id="clue_1",
            player_id="p1",
            gates=[gate],
            knowledge=KnowledgeState(player_id="p1"),
        )
        assert visible is False

    def test_known_clue_is_visible_regardless_of_gate(self):
        checker = RevealChecker()
        gate = RevealGate(clue_id="clue_1", gate_type="skill_check", condition={})
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("clue_1")
        visible = checker.is_clue_visible(
            clue_id="clue_1",
            player_id="p1",
            gates=[gate],
            knowledge=ks,
        )
        assert visible is True

    def test_multiple_clues_independent_gates(self):
        checker = RevealChecker()
        gate_a = RevealGate(clue_id="clue_a", gate_type="manual", condition={})
        gate_b = RevealGate(clue_id="clue_b", gate_type="manual", condition={})
        gate_a.open()
        visible_a = checker.is_clue_visible("clue_a", "p1", [gate_a, gate_b], KnowledgeState(player_id="p1"))
        visible_b = checker.is_clue_visible("clue_b", "p1", [gate_a, gate_b], KnowledgeState(player_id="p1"))
        assert visible_a is True
        assert visible_b is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_reveal.py::TestRevealChecker -v`
Expected: ModuleNotFoundError for reveal.checker

- [ ] **Step 3: Implement RevealChecker**

Create `src/dm_bot/reveal/checker.py`:
```python
"""Visibility query engine for reveal gates."""

from dm_bot.reveal.models import RevealGate, KnowledgeState


class RevealChecker:
    """Answers whether a clue is visible to a given player."""

    def is_clue_visible(
        self,
        clue_id: str,
        player_id: str,
        gates: list[RevealGate],
        knowledge: KnowledgeState,
    ) -> bool:
        if knowledge.knows_clue(clue_id):
            return True
        clue_gates = [g for g in gates if g.clue_id == clue_id]
        if not clue_gates:
            return True
        return all(g.is_open for g in clue_gates)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_reveal.py::TestRevealChecker -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/reveal/checker.py tests/test_reveal.py
git commit -m "feat(s4): add RevealChecker visibility query engine"
```

---

### Task 4: Scene Integration

**Files:**
- Modify: `src/dm_bot/adventure/models.py`
- Modify: `tests/test_reveal.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_reveal.py`:

```python
from dm_bot.adventure.models import Scene, Clue
from dm_bot.reveal.checker import RevealChecker
from dm_bot.reveal.models import RevealGate, KnowledgeState


class TestSceneRevealIntegration:
    def test_clue_without_gate_visible_by_default(self):
        scene = Scene(
            scene_id="s1", name="Study", description="A dusty study.",
            clues=[Clue(clue_id="c1", description="A hidden letter")],
        )
        checker = RevealChecker()
        for clue in scene.clues:
            visible = checker.is_clue_visible(
                clue_id=clue.clue_id,
                player_id="p1",
                gates=[],
                knowledge=KnowledgeState(player_id="p1"),
            )
            assert visible is True

    def test_learned_clue_visible_even_with_closed_gate(self):
        ks = KnowledgeState(player_id="p1")
        ks.learn_clue("c1")
        gate = RevealGate(clue_id="c1", gate_type="skill_check", condition={"skill": "spot"})
        scene = Scene(
            scene_id="s1", name="Hall", description="A hall.",
            clues=[Clue(clue_id="c1", description="A clue")],
        )
        checker = RevealChecker()
        visible = checker.is_clue_visible("c1", "p1", [gate], ks)
        assert visible is True

    def test_multiple_players_independent_knowledge(self):
        ks_p1 = KnowledgeState(player_id="p1")
        ks_p2 = KnowledgeState(player_id="p2")
        ks_p1.learn_clue("c1")

        gate = RevealGate(clue_id="c2", gate_type="manual", condition={})
        gate.open()
        checker = RevealChecker()

        assert checker.is_clue_visible("c1", "p1", [gate], ks_p1) is True  # knows it
        assert checker.is_clue_visible("c1", "p2", [gate], ks_p2) is False  # doesn't know it, gate for c1 is closed
        assert checker.is_clue_visible("c2", "p2", [gate], ks_p2) is True  # gate open
```

- [ ] **Step 2: Run tests to verify they pass/fail as expected**

Run: `uv run pytest tests/test_reveal.py::TestSceneRevealIntegration -v`
Expected: ALL PASS (these test existing model + checker integration, no new code needed)

- [ ] **Step 3: Run full suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 4: Commit any needed additions**

```bash
git add tests/test_reveal.py
git commit -m "feat(s4): add scene-reveal integration tests"
```

---

### Task 5: Smoke Check and Final Verification

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 2: Run smoke check**

Run: `uv run python -m dm_bot.main smoke-check`
Expected: "All core modules import successfully."

- [ ] **Step 3: Commit any remaining files**

```bash
git add -A && git commit -m "chore(s4): final gate pass for reveal gates and knowledge"
```
