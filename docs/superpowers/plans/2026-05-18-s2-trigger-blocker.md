# S2: Trigger & Blocker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a normalized trigger-event entry system with registrable triggers, ordered reaction execution, and first-class blocker checkpoints.

**Architecture:** New `trigger/` module handles event→trigger→reaction→blocker pipeline. Scene and adventure models gain trigger/blocker references. Blockers persist to SQLite via existing store layer.

**Tech Stack:** Python, Pydantic v2, SQLite

---

### Task 1: Trigger and Reaction Models

**Files:**
- Create: `src/dm_bot/trigger/__init__.py`

```python
"""Trigger, event, reaction, and blocker models for the trigger system."""
```

- Create: `src/dm_bot/trigger/models.py`
- Test: `tests/test_trigger.py`

- [ ] **Step 1: Write failing tests for models**

```python
"""Tests for trigger/blocker data models."""

import pytest
from dm_bot.trigger.models import TriggerEvent, Trigger, Reaction, BlockerCheckpoint


class TestTriggerEvent:
    def test_create_event(self):
        event = TriggerEvent(
            event_type="action.submit",
            source={"scene_id": "s1", "user_id": "u1", "action_text": "search"},
        )
        assert event.event_type == "action.submit"
        assert event.source["scene_id"] == "s1"
        assert event.event_id is not None


class TestTrigger:
    def test_create_trigger(self):
        trigger = Trigger(
            trigger_id="tr_1",
            event_type="action.submit",
            condition={"skill": "spot_hidden"},
            reactions=[Reaction(reaction_id="rx_1", effect_type="add_clue")],
        )
        assert trigger.trigger_id == "tr_1"
        assert trigger.reactions[0].effect_type == "add_clue"

    def test_reaction_ordering(self):
        r1 = Reaction(reaction_id="r1", effect_type="message", priority=10)
        r2 = Reaction(reaction_id="r2", effect_type="block", priority=1)
        assert r2.priority < r1.priority  # lower = earlier


class TestBlockerCheckpoint:
    def test_create_checkpoint(self):
        cp = BlockerCheckpoint(trigger_chain_id="chain_1", reason="awaiting_kp_input")
        assert cp.blocker_id is not None
        assert cp.resolved_at is None

    def test_resolve(self):
        cp = BlockerCheckpoint(trigger_chain_id="chain_1", reason="test")
        cp.resolve()
        assert cp.resolved_at is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_trigger.py -v`
Expected: ImportError or ModuleNotFoundError

- [ ] **Step 3: Implement models**

```python
"""Trigger, event, reaction, and blocker models."""

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class TriggerEvent(BaseModel):
    """Something that happened in the game that may trigger reactions."""

    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    event_type: str  # e.g. "action.submit", "scene.enter", "clue.discover"
    source: dict[str, Any] = Field(default_factory=dict)  # scene_id, user_id, etc.
    payload: dict[str, Any] = Field(default_factory=dict)


class Reaction(BaseModel):
    """What happens when a trigger fires."""

    reaction_id: str
    effect_type: str  # "message", "add_clue", "block", "damage", "transform"
    params: dict[str, Any] = Field(default_factory=dict)
    priority: int = 100  # lower runs first
    atomic_group: str | None = None  # reactions in same group commit together


class Trigger(BaseModel):
    """A condition-reaction pair associated with a scene or adventure."""

    trigger_id: str
    event_type: str
    condition: dict[str, Any] = Field(default_factory=dict)  # filter criteria
    reactions: list[Reaction] = Field(default_factory=list)


class BlockerCheckpoint(BaseModel):
    """A persisted checkpoint where trigger execution paused."""

    blocker_id: str = Field(default_factory=lambda: f"blk_{uuid.uuid4().hex[:12]}")
    trigger_chain_id: str
    scene_id: str = ""
    reason: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None

    def resolve(self) -> None:
        self.resolved_at = datetime.now(timezone.utc)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_trigger.py::TestTriggerEvent -v && uv run pytest tests/test_trigger.py::TestTrigger -v && uv run pytest tests/test_trigger.py::TestBlockerCheckpoint -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/dm_bot/trigger/__init__.py src/dm_bot/trigger/models.py tests/test_trigger.py
git commit -m "feat(s2): add trigger, reaction, and blocker models"
```

---

### Task 2: Scene Schema — Add Trigger/Reaction to Adventure Models

**Files:**
- Modify: `src/dm_bot/adventure/models.py`

- [ ] **Step 1: Write failing tests first**

Add to `tests/test_trigger.py`:

```python
class TestSceneTriggerIntegration:
    def test_scene_has_triggers(self):
        from dm_bot.adventure.models import Scene, TriggerRef
        scene = Scene(
            scene_id="s1", name="Hallway",
            triggers=[TriggerRef(trigger_id="tr_enter", event_type="scene.enter")],
        )
        assert len(scene.triggers) == 1
        assert scene.triggers[0].trigger_id == "tr_enter"

    def test_scene_has_blockers(self):
        from dm_bot.adventure.models import Scene, BlockerRef
        scene = Scene(
            scene_id="s1", name="Locked Door",
            blockers=[BlockerRef(blocker_id="bl_door", condition={"skill": "mechanical_repair"})],
        )
        assert len(scene.blockers) == 1
```

- [ ] **Step 2: Run failing test**

Run: `uv run pytest tests/test_trigger.py::TestSceneTriggerIntegration -v`
Expected: ImportError for TriggerRef/BlockerRef

- [ ] **Step 3: Add TriggerRef and BlockerRef to Scene model**

Edit `src/dm_bot/adventure/models.py`. Add:

```python
class TriggerRef(BaseModel):
    trigger_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    condition: dict[str, Any] = Field(default_factory=dict)


class BlockerRef(BaseModel):
    blocker_id: str = Field(min_length=1)
    condition: dict[str, Any] = Field(default_factory=dict)


# Add to Scene model:
#   triggers: list[TriggerRef] = Field(default_factory=list)
#   blockers: list[BlockerRef] = Field(default_factory=list)
```

Also add `from typing import Any` to the import block.

- [ ] **Step 4: Run tests to confirm they pass**

Run: `uv run pytest tests/test_trigger.py::TestSceneTriggerIntegration -v`
Expected: PASS

- [ ] **Step 5: Run existing tests to confirm no regressions**

Run: `uv run pytest -q`
Expected: 49+ passed (new tests added)

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/adventure/models.py tests/test_trigger.py
git commit -m "feat(s2): add TriggerRef and BlockerRef to Scene model"
```

---

### Task 3: Trigger Engine — Event Processing Pipeline

**Files:**
- Create: `src/dm_bot/trigger/engine.py`
- Modify: `tests/test_trigger.py`

- [ ] **Step 1: Write failing tests**

```python
class TestTriggerEngine:
    def test_register_and_fire(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction

        engine = TriggerEngine()
        trigger = Trigger(
            trigger_id="tr_test",
            event_type="test.event",
            reactions=[Reaction(reaction_id="rx_1", effect_type="message")],
        )
        engine.register_trigger(trigger)
        assert len(engine.triggers) == 1

    def test_fire_matches_trigger(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent

        engine = TriggerEngine()
        fired: list[str] = []

        class TrackingReaction(Reaction):
            def execute(self): fired.append(self.reaction_id)

        trigger = Trigger(
            trigger_id="tr_1",
            event_type="action.submit",
            reactions=[TrackingReaction(reaction_id="rx_1", effect_type="message")],
        )
        engine.register_trigger(trigger)
        event = TriggerEvent(event_type="action.submit", source={"scene_id": "s1"})
        engine.fire_event(event)
        assert "rx_1" in fired

    def test_fire_no_match(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent

        engine = TriggerEngine()
        trigger = Trigger(
            trigger_id="tr_1",
            event_type="action.submit",
            reactions=[Reaction(reaction_id="rx_1", effect_type="message")],
        )
        engine.register_trigger(trigger)
        event = TriggerEvent(event_type="scene.enter", source={})
        results = engine.fire_event(event)
        assert len(results) == 0  # no match

    def test_reaction_priority_order(self):
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent

        engine = TriggerEngine()
        order: list[str] = []

        r1 = Reaction(reaction_id="r_first", effect_type="message", priority=10)
        r2 = Reaction(reaction_id="r_second", effect_type="message", priority=100)

        trigger = Trigger(
            trigger_id="tr_1",
            event_type="test",
            reactions=[r2, r1],  # registered out of order
        )
        engine.register_trigger(trigger)
        engine.fire_event(TriggerEvent(event_type="test", source={}))
        # reactions executed in priority order: r_first (10) then r_second (100)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_trigger.py::TestTriggerEngine -v`
Expected: ImportError for TriggerEngine

- [ ] **Step 3: Implement TriggerEngine**

```python
"""Trigger event processing pipeline."""

from dm_bot.trigger.models import Trigger, TriggerEvent, Reaction


class TriggerEngine:
    """Matches events to triggers and executes reactions in priority order."""

    def __init__(self) -> None:
        self._triggers: dict[str, Trigger] = {}

    @property
    def triggers(self) -> dict[str, Trigger]:
        return self._triggers

    def register_trigger(self, trigger: Trigger) -> None:
        self._triggers[trigger.trigger_id] = trigger

    def unregister(self, trigger_id: str) -> None:
        self._triggers.pop(trigger_id, None)

    def fire_event(self, event: TriggerEvent) -> list[Reaction]:
        """Fire an event, match triggers, and execute reactions ordered."""
        matched = self._find_matching_triggers(event)
        if not matched:
            return []
        reactions = self._collect_reactions(matched)
        ordered = sorted(reactions, key=lambda r: r.priority)
        self._execute_reactions(ordered)
        return ordered

    def _find_matching_triggers(self, event: TriggerEvent) -> list[Trigger]:
        return [t for t in self._triggers.values() if t.event_type == event.event_type]

    def _collect_reactions(self, triggers: list[Trigger]) -> list[Reaction]:
        return [r for t in triggers for r in t.reactions]

    def _execute_reactions(self, reactions: list[Reaction]) -> None:
        for reaction in reactions:
            self._execute_single(reaction)

    def _execute_single(self, reaction: Reaction) -> None:
        pass  # concrete effect execution deferred to higher layers
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_trigger.py::TestTriggerEngine -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/trigger/engine.py tests/test_trigger.py
git commit -m "feat(s2): add TriggerEngine with event matching and reaction ordering"
```

---

### Task 4: Blocker Checkpoint Persistence

**Files:**
- Modify: `src/dm_bot/store/db.py`
- Modify: `tests/test_trigger.py`

- [ ] **Step 1: Write failing tests**

```python
class TestBlockerPersistence:
    def test_save_and_load_blocker(self):
        from dm_bot.store.db import Store
        from dm_bot.trigger.models import BlockerCheckpoint
        import tempfile, os

        db_path = os.path.join(tempfile.gettempdir(), "test_blockers.db")
        store = Store(db_path)
        cp = BlockerCheckpoint(trigger_chain_id="chain_1", reason="kp_decides")
        store.save_blocker(cp)
        loaded = store.load_blocker(cp.blocker_id)
        assert loaded is not None
        assert loaded.blocker_id == cp.blocker_id
        assert loaded.reason == "kp_decides"
        assert loaded.resolved_at is None
        os.remove(db_path)

    def test_list_unresolved_blockers(self):
        from dm_bot.store.db import Store
        from dm_bot.trigger.models import BlockerCheckpoint
        import tempfile, os

        db_path = os.path.join(tempfile.gettempdir(), "test_blockers2.db")
        store = Store(db_path)
        cp1 = BlockerCheckpoint(trigger_chain_id="chain_1", reason="wait")
        cp2 = BlockerCheckpoint(trigger_chain_id="chain_2", reason="wait")
        cp2.resolve()
        store.save_blocker(cp1)
        store.save_blocker(cp2)
        unresolved = store.list_unresolved_blockers()
        assert len(unresolved) == 1
        assert unresolved[0].blocker_id == cp1.blocker_id
        os.remove(db_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_trigger.py::TestBlockerPersistence -v`
Expected: AttributeError (Store has no save_blocker method)

- [ ] **Step 3: Add blocker methods to Store**

In `src/dm_bot/store/db.py`, add blocker table to `_init_db`:

```python
CREATE TABLE IF NOT EXISTS blockers (
    blocker_id TEXT PRIMARY KEY,
    trigger_chain_id TEXT NOT NULL,
    scene_id TEXT DEFAULT '',
    reason TEXT NOT NULL,
    payload TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);
```

Add methods:

```python
def save_blocker(self, blocker: BlockerCheckpoint) -> None:
    import json
    with sqlite3.connect(self.db_path) as conn:
        conn.execute(
            """INSERT OR REPLACE INTO blockers
               (blocker_id, trigger_chain_id, scene_id, reason, payload, resolved_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (blocker.blocker_id, blocker.trigger_chain_id, blocker.scene_id,
             blocker.reason, json.dumps(blocker.payload),
             blocker.resolved_at.isoformat() if blocker.resolved_at else None),
        )

def load_blocker(self, blocker_id: str) -> BlockerCheckpoint | None:
    import json
    from datetime import datetime
    with sqlite3.connect(self.db_path) as conn:
        row = conn.execute(
            "SELECT * FROM blockers WHERE blocker_id = ?", (blocker_id,)
        ).fetchone()
        if not row:
            return None
        return BlockerCheckpoint(
            blocker_id=row[0], trigger_chain_id=row[1], scene_id=row[2] or "",
            reason=row[3], payload=json.loads(row[4]) if row[4] else {},
            resolved_at=datetime.fromisoformat(row[6]) if row[6] else None,
        )

def list_unresolved_blockers(self) -> list[BlockerCheckpoint]:
    import json
    from datetime import datetime
    with sqlite3.connect(self.db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM blockers WHERE resolved_at IS NULL"
        ).fetchall()
        return [
            BlockerCheckpoint(
                blocker_id=r[0], trigger_chain_id=r[1], scene_id=r[2] or "",
                reason=r[3], payload=json.loads(r[4]) if r[4] else {},
            )
            for r in rows
        ]
```

Also add import at top of store/db.py:

```python
from dm_bot.trigger.models import BlockerCheckpoint
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_trigger.py::TestBlockerPersistence -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/store/db.py tests/test_trigger.py
git commit -m "feat(s2): add blocker checkpoint persistence to Store"
```

---

### Task 5: Round Integration — Fire Triggers on Submit and Resolve

**Files:**
- Modify: `src/dm_bot/scene/round.py`
- Modify: `tests/test_scene.py`

- [ ] **Step 1: Write failing test for round-trigger integration**

In `tests/test_trigger.py`:

```python
class TestRoundTriggerIntegration:
    def test_round_has_trigger_engine(self):
        from dm_bot.scene.round import Round
        from dm_bot.trigger.engine import TriggerEngine
        round_obj = Round(trigger_engine=TriggerEngine())
        assert round_obj.trigger_engine is not None

    def test_submit_fires_trigger(self):
        from dm_bot.scene.round import Round
        from dm_bot.trigger.engine import TriggerEngine
        from dm_bot.trigger.models import Trigger, Reaction, TriggerEvent
        from dm_bot.scene.action import Action

        engine = TriggerEngine()
        order: list[str] = []
        trigger = Trigger(
            trigger_id="tr_submit",
            event_type="action.submit",
            reactions=[Reaction(reaction_id="rx_log", effect_type="log")],
        )
        engine.register_trigger(trigger)
        round_obj = Round(trigger_engine=engine)
        round_obj.start_collection()
        round_obj.submit_action(Action(user_id="u1", character_id="c1", action_text="hit"))
        # The submit should have fired a trigger event
```

- [ ] **Step 2: Run failing test**

Run: `uv run pytest tests/test_trigger.py::TestRoundTriggerIntegration -v`
Expected: TypeError (Round.__init__ got unexpected keyword argument)

- [ ] **Step 3: Modify Round to accept and use TriggerEngine**

Edit `src/dm_bot/scene/round.py`. Add import and constructor parameter:

```python
from dm_bot.trigger.models import TriggerEvent
from dm_bot.trigger.engine import TriggerEngine
```

Change `__init__`:

```python
def __init__(self, trigger_engine: TriggerEngine | None = None) -> None:
    self.actions: list[Action] = []
    self.state = SceneState.WAITING
    self.trigger_engine = trigger_engine or TriggerEngine()
```

Add trigger firing to `submit_action`:

```python
def submit_action(self, action: Action) -> None:
    if self.state != SceneState.COLLECTING:
        raise RuntimeError(f"Cannot submit action in state {self.state}")
    self.actions.append(action)
    self.trigger_engine.fire_event(TriggerEvent(
        event_type="action.submit",
        source={"scene_id": "", "user_id": action.user_id, "action_text": action.action_text},
    ))
```

Add trigger firing to `resolve`:

```python
def resolve(self) -> list[Action]:
    ...
    self.trigger_engine.fire_event(TriggerEvent(
        event_type="round.resolve",
        source={"action_count": len(ordered)},
    ))
    ...
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_trigger.py::TestRoundTriggerIntegration -v`
Expected: ALL PASS

- [ ] **Step 5: Confirm existing round/scene tests still pass**

Run: `uv run pytest tests/test_scene.py -v`
Expected: ALL PASS

- [ ] **Step 6: Run full suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add src/dm_bot/scene/round.py tests/test_trigger.py
git commit -m "feat(s2): integrate TriggerEngine into Round for action.submit events"
```

---

### Task 6: Smoke Check and Final Verification

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -q`
Expected: ALL PASS (new tests + existing 49)

- [ ] **Step 2: Run smoke check**

Run: `uv run python -m dm_bot.main smoke-check`
Expected: "All core modules import successfully."

- [ ] **Step 3: Commit any remaining changes**

```bash
git add -A && git commit -m "chore(s2): final gate pass for trigger and blocker implementation"
```
