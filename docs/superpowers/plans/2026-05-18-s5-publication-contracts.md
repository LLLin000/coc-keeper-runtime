# S5: Publication Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Define the runtime-to-surface API boundary with structured publication events, visibility paths, and a renderer contract.

**Architecture:** New `publish/` module with PublicationEvent (base + concrete types), Publisher (routes events by visibility), and RendererContract (abstract interface). Runtime modules emit events via Publisher; surface implements contract to consume them.

**Tech Stack:** Python, Pydantic v2, ABC

---

### Task 1: Publication Models

**Files:**
- Create: `src/dm_bot/publish/__init__.py`
- Create: `src/dm_bot/publish/models.py`
- Create: `tests/test_publish.py`

- [ ] **Step 1: Write failing tests**

Write `tests/test_publish.py`:

```python
"""Tests for publication models."""

from dm_bot.publish.models import (
    PublicationEvent, PublicationPath,
    ActionSubmittedEvent, RoundResolvedEvent,
    ClueRevealedEvent, SceneTransitionEvent,
    BlockerCreatedEvent, NarrationRequestedEvent,
)


class TestPublicationModels:
    def test_action_submitted_event(self):
        event = ActionSubmittedEvent(
            session_id="session_1",
            user_id="u1",
            action_text="search the desk",
            scene_id="s1",
        )
        assert event.event_type == "action.submitted"
        assert event.visibility == PublicationPath.TABLE_VISIBLE
        assert event.timestamp is not None

    def test_round_resolved_event(self):
        event = RoundResolvedEvent(
            session_id="session_1",
            scene_id="s1",
            round_number=1,
            ordered_actions=["u1", "u2"],
        )
        assert event.event_type == "round.resolved"
        assert event.visibility == PublicationPath.TABLE_VISIBLE

    def test_clue_revealed_event(self):
        event = ClueRevealedEvent(
            session_id="session_1",
            clue_id="clue_1",
            description="A hidden letter",
            player_id="u1",
        )
        assert event.event_type == "clue.revealed"
        assert event.visibility == PublicationPath.PRIVATE

    def test_scene_transition_event(self):
        event = SceneTransitionEvent(
            session_id="session_1",
            from_scene_id="s1",
            to_scene_id="s2",
            reason="players opened the door",
        )
        assert event.event_type == "scene.transition"
        assert event.visibility == PublicationPath.TABLE_VISIBLE

    def test_blocker_created_event(self):
        event = BlockerCreatedEvent(
            session_id="session_1",
            blocker_id="blk_1",
            reason="awaiting_kp_decision",
            visibility=PublicationPath.KP_ONLY,
        )
        assert event.event_type == "blocker.created"
        assert event.visibility == PublicationPath.KP_ONLY

    def test_narration_requested_event(self):
        event = NarrationRequestedEvent(
            session_id="session_1",
            context={"scene_id": "s1", "trigger": "round.resolve"},
            prompt_text="Describe the result of the action",
        )
        assert event.event_type == "narration.requested"
        assert event.visibility == PublicationPath.KP_ONLY

    def test_publication_path_values(self):
        assert PublicationPath.TABLE_VISIBLE == "table_visible"
        assert PublicationPath.KP_ONLY == "kp_only"
        assert PublicationPath.PRIVATE == "private"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_publish.py -v`
Expected: ModuleNotFoundError

- [ ] **Step 3: Implement models**

Create `src/dm_bot/publish/__init__.py`:
```python
"""Publication models and contracts for runtime-to-surface communication."""
```

Create `src/dm_bot/publish/models.py`:
```python
"""Publication event models with partitioned visibility."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class PublicationPath(str, Enum):
    TABLE_VISIBLE = "table_visible"
    KP_ONLY = "kp_only"
    PRIVATE = "private"


class PublicationEvent(BaseModel):
    """Base class for all publishable runtime events."""

    event_type: str
    session_id: str
    visibility: PublicationPath = PublicationPath.TABLE_VISIBLE
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActionSubmittedEvent(PublicationEvent):
    event_type: Literal["action.submitted"] = "action.submitted"
    user_id: str
    action_text: str
    scene_id: str


class RoundResolvedEvent(PublicationEvent):
    event_type: Literal["round.resolved"] = "round.resolved"
    scene_id: str
    round_number: int = 0
    ordered_actions: list[str] = Field(default_factory=list)


class ClueRevealedEvent(PublicationEvent):
    event_type: Literal["clue.revealed"] = "clue.revealed"
    visibility: PublicationPath = PublicationPath.PRIVATE
    clue_id: str
    description: str = ""
    player_id: str = ""


class SceneTransitionEvent(PublicationEvent):
    event_type: Literal["scene.transition"] = "scene.transition"
    from_scene_id: str = ""
    to_scene_id: str = ""
    reason: str = ""


class BlockerCreatedEvent(PublicationEvent):
    event_type: Literal["blocker.created"] = "blocker.created"
    blocker_id: str
    reason: str = ""


class BlockerResolvedEvent(PublicationEvent):
    event_type: Literal["blocker.resolved"] = "blocker.resolved"
    blocker_id: str
    reason: str = ""


class NarrationRequestedEvent(PublicationEvent):
    event_type: Literal["narration.requested"] = "narration.requested"
    context: dict[str, Any] = Field(default_factory=dict)
    prompt_text: str = ""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_publish.py -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/publish/ tests/test_publish.py
git commit -m "feat(s5): add publication event models with visibility paths"
```

---

### Task 2: Publisher — Event Dispatcher

**Files:**
- Create: `src/dm_bot/publish/publisher.py`
- Modify: `tests/test_publish.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_publish.py`:

```python
from dm_bot.publish.publisher import Publisher
from dm_bot.publish.models import (
    PublicationEvent, ActionSubmittedEvent, PublicationPath,
)


class TestPublisher:
    def test_publish_stores_event(self):
        pub = Publisher()
        event = ActionSubmittedEvent(
            session_id="s1", user_id="u1",
            action_text="search", scene_id="sc1",
        )
        pub.publish(event)
        assert len(pub.events) == 1
        assert pub.events[0].event_type == "action.submitted"

    def test_publish_sets_timestamp(self):
        pub = Publisher()
        event = ActionSubmittedEvent(
            session_id="s1", user_id="u1",
            action_text="search", scene_id="sc1",
        )
        pub.publish(event)
        assert pub.events[0].timestamp is not None

    def test_get_events_by_visibility(self):
        pub = Publisher()
        pub.publish(ActionSubmittedEvent(session_id="s1", user_id="u1", action_text="a", scene_id="sc1"))
        evt2 = ActionSubmittedEvent(session_id="s1", user_id="u2", action_text="b", scene_id="sc1")
        evt2.visibility = PublicationPath.KP_ONLY
        pub.publish(evt2)

        table = pub.get_events(visibility=PublicationPath.TABLE_VISIBLE)
        kp = pub.get_events(visibility=PublicationPath.KP_ONLY)
        assert len(table) == 1
        assert len(kp) == 1

    def test_get_events_by_type(self):
        pub = Publisher()
        pub.publish(ActionSubmittedEvent(session_id="s1", user_id="u1", action_text="a", scene_id="sc1"))
        from dm_bot.publish.models import RoundResolvedEvent
        pub.publish(RoundResolvedEvent(session_id="s1", scene_id="sc1", round_number=1))

        actions = pub.get_events(event_type="action.submitted")
        rounds = pub.get_events(event_type="round.resolved")
        assert len(actions) == 1
        assert len(rounds) == 1

    def test_clear_events(self):
        pub = Publisher()
        pub.publish(ActionSubmittedEvent(session_id="s1", user_id="u1", action_text="a", scene_id="sc1"))
        pub.clear()
        assert len(pub.events) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_publish.py::TestPublisher -v`
Expected: ModuleNotFoundError

- [ ] **Step 3: Implement Publisher**

Create `src/dm_bot/publish/publisher.py`:
```python
"""Event publisher that routes events by visibility path."""

from dm_bot.publish.models import PublicationEvent, PublicationPath


class Publisher:
    """Stores and routes runtime events by visibility and type."""

    def __init__(self) -> None:
        self._events: list[PublicationEvent] = []

    @property
    def events(self) -> list[PublicationEvent]:
        return list(self._events)

    def publish(self, event: PublicationEvent) -> None:
        self._events.append(event)

    def get_events(
        self,
        visibility: PublicationPath | None = None,
        event_type: str | None = None,
    ) -> list[PublicationEvent]:
        result = self._events
        if visibility:
            result = [e for e in result if e.visibility == visibility]
        if event_type:
            result = [e for e in result if e.event_type == event_type]
        return list(result)

    def clear(self) -> None:
        self._events.clear()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_publish.py::TestPublisher -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/publish/publisher.py tests/test_publish.py
git commit -m "feat(s5): add Publisher with visibility-filtered event dispatch"
```

---

### Task 3: Renderer Contract

**Files:**
- Create: `src/dm_bot/publish/contract.py`
- Modify: `tests/test_publish.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_publish.py`:

```python
from dm_bot.publish.contract import RendererContract
from dm_bot.publish.models import ActionSubmittedEvent


class TestRendererContract:
    def test_cannot_instantiate_abstract(self):
        import pytest
        with pytest.raises(TypeError):
            RendererContract()

    def test_concrete_renderer(self):
        class TestRenderer(RendererContract):
            def render(self, event):
                return f"Rendered: {event.event_type}"

        r = TestRenderer()
        event = ActionSubmittedEvent(
            session_id="s1", user_id="u1",
            action_text="search", scene_id="sc1",
        )
        result = r.render(event)
        assert result == "Rendered: action.submitted"

    def test_multiple_events(self):
        class TestRenderer(RendererContract):
            def render(self, event):
                return f"Event: {event.event_type}"

        r = TestRenderer()
        from dm_bot.publish.models import RoundResolvedEvent
        e1 = ActionSubmittedEvent(session_id="s1", user_id="u1", action_text="a", scene_id="sc1")
        e2 = RoundResolvedEvent(session_id="s1", scene_id="sc1", round_number=1)
        assert r.render(e1) == "Event: action.submitted"
        assert r.render(e2) == "Event: round.resolved"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_publish.py::TestRendererContract -v`
Expected: ModuleNotFoundError for contract

- [ ] **Step 3: Implement RendererContract**

Create `src/dm_bot/publish/contract.py`:
```python
"""Renderer contract that surface layer must implement."""

from abc import ABC, abstractmethod

from dm_bot.publish.models import PublicationEvent


class RendererContract(ABC):
    """Interface that Discord (or any surface) must implement."""

    @abstractmethod
    def render(self, event: PublicationEvent) -> str:
        """Render a publication event into a display string."""
        ...
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_publish.py::TestRendererContract -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/publish/contract.py tests/test_publish.py
git commit -m "feat(s5): add RendererContract abstract interface"
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
git add -A && git commit -m "chore(s5): final gate pass for publication contracts"
```
