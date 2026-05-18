# S7: Session Board Core — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render canonical runtime state into Discord-readable boards with visibility enforcement from runtime contracts.

**Architecture:** New `surface/` module with Board ABC producing Discord-formatted strings from runtime state. Four boards (session identity, scene context, blocker summary, consequence output). Publisher and TriggerEngine wired into a SessionContext that boards read from.

**Tech Stack:** Python, Pydantic v2, discord.py >=2.7

---

### Task 1: Surface Board Framework + SessionBoard

**Files:**
- Create: `src/dm_bot/surface/__init__.py`
- Create: `src/dm_bot/surface/board.py`
- Create: `src/dm_bot/surface/session_board.py`
- Create: `tests/test_surface.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_surface.py`:

```python
"""Tests for surface board views."""

from dm_bot.surface.board import Board
from dm_bot.surface.session_board import SessionBoard


class TestSessionBoard:
    def test_render_session_identity(self):
        state = {
            "session_id": "ses_abc123",
            "phase": "exploration",
            "participants": ["Alice", "Bob"],
            "module_name": "The Haunting",
        }
        board = SessionBoard()
        output = board.render(state)
        assert "The Haunting" in output
        assert "ses_abc123" in output
        assert "exploration" in output
        assert "Alice" in output
        assert "Bob" in output

    def test_board_abc_cannot_instantiate(self):
        import pytest
        with pytest.raises(TypeError):
            Board()  # ABC with abstractmethod
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_surface.py -v`
Expected: ModuleNotFoundError or ImportError

- [ ] **Step 3: Implement Board ABC**

Create `src/dm_bot/surface/board.py`:

```python
"""Base board abstraction for surface views."""

from abc import ABC, abstractmethod
from typing import Any


class Board(ABC):
    """A view that renders runtime state into Discord-formatted output."""

    @abstractmethod
    def render(self, state: dict[str, Any]) -> str:
        """Render board state as Discord-formatted string."""
```

Create `src/dm_bot/surface/__init__.py`:

```python
"""Discord surface views — boards rendering runtime state."""
```

Create `src/dm_bot/surface/session_board.py`:

```python
"""Session identity and phase board."""

from typing import Any

from dm_bot.surface.board import Board


class SessionBoard(Board):
    """Renders session identity, phase, and participant info."""

    def render(self, state: dict[str, Any]) -> str:
        lines = [
            f"**Session:** {state.get('session_id', 'N/A')}",
            f"**Module:** {state.get('module_name', 'N/A')}",
            f"**Phase:** {state.get('phase', 'N/A')}",
        ]
        participants = state.get("participants", [])
        if participants:
            lines.append(f"**Players:** {', '.join(participants)}")
        else:
            lines.append("**Players:** (none)")
        return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_surface.py -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/surface/ tests/test_surface.py
git commit -m "feat(s7): add Board ABC and SessionBoard"
```

---

### Task 2: SceneBoard — Scene Context and Round State

**Files:**
- Create: `src/dm_bot/surface/scene_board.py`
- Modify: `tests/test_surface.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_surface.py`:

```python
class TestSceneBoard:
    def test_render_scene_context(self):
        from dm_bot.surface.scene_board import SceneBoard

        state = {
            "scene_id": "s1",
            "scene_name": "Creaky Hallway",
            "scene_desc": "A dark corridor.",
            "round_state": "COLLECTING",
            "action_count": 2,
            "waiting_for": ["KP decision on lockpick"],
        }
        board = SceneBoard()
        output = board.render(state)
        assert "Creaky Hallway" in output
        assert "COLLECTING" in output
        assert "KP decision on lockpick" in output
        assert "2" in output

    def test_render_no_waiting_reason(self):
        from dm_bot.surface.scene_board import SceneBoard

        state = {
            "scene_id": "s2",
            "scene_name": "Empty Room",
            "round_state": "WAITING",
            "action_count": 0,
        }
        board = SceneBoard()
        output = board.render(state)
        assert "Empty Room" in output
        assert "WAITING" in output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_surface.py::TestSceneBoard -v`
Expected: ImportError for SceneBoard

- [ ] **Step 3: Implement SceneBoard**

Create `src/dm_bot/surface/scene_board.py`:

```python
"""Scene context and round state board."""

from typing import Any

from dm_bot.surface.board import Board


class SceneBoard(Board):
    """Renders current scene context, round state, and waiting reasons."""

    def render(self, state: dict[str, Any]) -> str:
        lines = [
            f"**Scene:** {state.get('scene_name', 'N/A')}",
            f"**Round:** {state.get('round_state', 'N/A')}",
            f"**Actions:** {state.get('action_count', 0)}",
        ]
        waiting = state.get("waiting_for")
        if waiting:
            lines.append(f"**Waiting:** {', '.join(waiting)}")
        return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_surface.py::TestSceneBoard -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/surface/scene_board.py tests/test_surface.py
git commit -m "feat(s7): add SceneBoard with round state and waiting reasons"
```

---

### Task 3: BlockerBoard — KP-Readable Blocker Summary

**Files:**
- Create: `src/dm_bot/surface/blocker_board.py`
- Modify: `tests/test_surface.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_surface.py`:

```python
class TestBlockerBoard:
    def test_render_blocker_summary(self):
        from dm_bot.surface.blocker_board import BlockerBoard

        state = {
            "blockers": [
                {"blocker_id": "blk_1", "reason": "KP decides lockpick DC", "scene_id": "s1"},
                {"blocker_id": "blk_2", "reason": "Awaiting player response", "scene_id": "s2"},
            ]
        }
        board = BlockerBoard()
        output = board.render(state)
        assert "KP decides lockpick DC" in output
        assert "Awaiting player response" in output
        assert "2" in output

    def test_render_no_blockers(self):
        from dm_bot.surface.blocker_board import BlockerBoard

        board = BlockerBoard()
        output = board.render({"blockers": []})
        assert "No blockers" in output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_surface.py::TestBlockerBoard -v`
Expected: ImportError for BlockerBoard

- [ ] **Step 3: Implement BlockerBoard**

Create `src/dm_bot/surface/blocker_board.py`:

```python
"""Blocker summary board for KP visibility."""

from typing import Any

from dm_bot.surface.board import Board


class BlockerBoard(Board):
    """Renders unresolved blockers as a KP-readable summary."""

    def render(self, state: dict[str, Any]) -> str:
        blockers = state.get("blockers", [])
        if not blockers:
            return "**Blockers:** No unresolved blockers."

        lines = [f"**Blockers ({len(blockers)}):**"]
        for b in blockers:
            blocker_id = b.get("blocker_id", "?")
            reason = b.get("reason", "?")
            scene_id = b.get("scene_id", "")
            scene_info = f" (scene: {scene_id})" if scene_id else ""
            lines.append(f"- `{blocker_id}`{scene_info}: {reason}")
        return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_surface.py::TestBlockerBoard -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/surface/blocker_board.py tests/test_surface.py
git commit -m "feat(s7): add BlockerBoard with KP-readable blocker summary"
```

---

### Task 4: ConsequenceBoard — Public/Shared/KP-Only Event Output

**Files:**
- Create: `src/dm_bot/surface/consequence_board.py`
- Modify: `tests/test_surface.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_surface.py`:

```python
class TestConsequenceBoard:
    def test_render_public_events(self):
        from dm_bot.surface.consequence_board import ConsequenceBoard

        state = {
            "events": [
                {"event_type": "action.submitted", "visibility": "table_visible", "summary": "Alice searched the room"},
                {"event_type": "action.submitted", "visibility": "kp_only", "summary": "Bob found a hidden key"},
            ]
        }
        board = ConsequenceBoard()
        output = board.render(state, visibility="table_visible")
        assert "Alice searched the room" in output
        assert "Bob found a hidden key" not in output

    def test_render_kp_only_events(self):
        from dm_bot.surface.consequence_board import ConsequenceBoard

        state = {
            "events": [
                {"event_type": "clue.revealed", "visibility": "kp_only", "summary": "DC15 Spot Hidden"},
                {"event_type": "clue.revealed", "visibility": "table_visible", "summary": "A clue was found"},
            ]
        }
        board = ConsequenceBoard()
        output = board.render(state, visibility="kp_only")
        assert "DC15 Spot Hidden" in output
        assert "A clue was found" not in output

    def test_render_all_events(self):
        from dm_bot.surface.consequence_board import ConsequenceBoard

        board = ConsequenceBoard()
        output = board.render({"events": []})
        assert "No events" in output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_surface.py::TestConsequenceBoard -v`
Expected: ImportError

- [ ] **Step 3: Implement ConsequenceBoard**

Create `src/dm_bot/surface/consequence_board.py`:

```python
"""Consequence output board with visibility filtering."""

from typing import Any

from dm_bot.surface.board import Board


class ConsequenceBoard(Board):
    """Renders published events filtered by visibility path."""

    def render(self, state: dict[str, Any], **kwargs: Any) -> str:
        events = state.get("events", [])
        if not events:
            return "**Recent Events:** No events."

        visibility_filter = kwargs.get("visibility")
        if visibility_filter:
            events = [e for e in events if e.get("visibility") == visibility_filter]

        if not events:
            return f"**Recent Events:** (none with {visibility_filter} visibility)"

        lines = [f"**Recent Events ({len(events)}):**"]
        for e in events:
            ev_type = e.get("event_type", "?")
            summary = e.get("summary", "")
            vis = e.get("visibility", "public")
            lines.append(f"- [{vis}] {summary} ({ev_type})")
        return "\n".join(lines)
```

**Note:** `ConsequenceBoard.render` accepts `**kwargs` for optional filters like `visibility`. This deviates from the base `Board.render(state)` signature but adds filtering without breaking the ABC contract (kwargs are allowed in Python).

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_surface.py::TestConsequenceBoard -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/surface/consequence_board.py tests/test_surface.py
git commit -m "feat(s7): add ConsequenceBoard with visibility filtering"
```

---

### Task 5: BotCommands Integration — Wire Boards into Session

**Files:**
- Create: `src/dm_bot/surface/session_context.py`
- Modify: `src/dm_bot/discord_bot/commands.py`
- Modify: `src/dm_bot/main.py`
- Modify: `tests/test_surface.py`

**Problem:** `main.py:68` calls `BotCommands(store=store, loader=loader, narrator=narrator, settings=settings)` but `BotCommands.__init__` expects `adventure_loader=`, not `loader=` and doesn't accept `settings=`. The run-bot command is broken.

- [ ] **Step 1: Write failing test for SessionContext**

Add to `tests/test_surface.py`:

```python
class TestSessionContext:
    def test_session_context_holds_state(self):
        from dm_bot.surface.session_context import SessionContext

        ctx = SessionContext(session_id="ses_1", module_name="Test")
        assert ctx.session_id == "ses_1"
        assert ctx.phase == "idle"

    def test_session_context_participants(self):
        from dm_bot.surface.session_context import SessionContext

        ctx = SessionContext(session_id="ses_1", module_name="Test")
        ctx.add_participant("Alice")
        ctx.add_participant("Bob")
        assert "Alice" in ctx.participants
        assert len(ctx.participants) == 2

    def test_session_board_from_context(self):
        from dm_bot.surface.session_context import SessionContext
        from dm_bot.surface.session_board import SessionBoard

        ctx = SessionContext(session_id="ses_abc", module_name="Haunting")
        ctx.add_participant("Alice")
        ctx.phase = "exploration"

        board = SessionBoard()
        output = board.render(ctx.to_dict())
        assert "ses_abc" in output
        assert "Haunting" in output
        assert "Alice" in output
        assert "exploration" in output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_surface.py::TestSessionContext -v`
Expected: ImportError

- [ ] **Step 3: Implement SessionContext**

Create `src/dm_bot/surface/session_context.py`:

```python
"""Session runtime context — holds active runtime state for board rendering."""

from typing import Any

from dm_bot.trigger.engine import TriggerEngine
from dm_bot.publish.publisher import Publisher
from dm_bot.store.db import Store


class SessionContext:
    """Holds the active session's runtime components and metadata."""

    def __init__(
        self,
        session_id: str,
        module_name: str = "",
        store: Store | None = None,
        trigger_engine: TriggerEngine | None = None,
        publisher: Publisher | None = None,
    ) -> None:
        self.session_id = session_id
        self.module_name = module_name
        self.phase: str = "idle"
        self.participants: list[str] = []
        self.store = store or Store(":memory:")
        self.trigger_engine = trigger_engine or TriggerEngine()
        self.publisher = publisher or Publisher()

    def add_participant(self, user_id: str) -> None:
        if user_id not in self.participants:
            self.participants.append(user_id)

    def to_dict(self) -> dict[str, Any]:
        blockers = []
        if self.store:
            blockers = [
                {
                    "blocker_id": b.blocker_id,
                    "reason": b.reason,
                    "scene_id": b.scene_id,
                }
                for b in self.store.list_unresolved_blockers()
            ]
        return {
            "session_id": self.session_id,
            "module_name": self.module_name,
            "phase": self.phase,
            "participants": list(self.participants),
            "blockers": blockers,
        }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_surface.py::TestSessionContext -v`
Expected: ALL PASS

- [ ] **Step 5: Fix BotCommands constructor and wire boards**

Fix `src/dm_bot/discord_bot/commands.py`:

```python
from dm_bot.surface.session_context import SessionContext
from dm_bot.surface.session_board import SessionBoard
from dm_bot.surface.scene_board import SceneBoard
from dm_bot.surface.blocker_board import BlockerBoard
from dm_bot.surface.consequence_board import ConsequenceBoard
```

Change `__init__` to accept `loader=` (not `adventure_loader=`) and accept `settings=`:

```python
def __init__(
    self,
    *,
    loader: "AdventureLoader",
    narrator: "NarratorClient",
    store: "Store",
    settings: Any = None,
) -> None:
    self.loader = loader
    self.narrator = narrator
    self.store = store
    self.builder = CharacterBuilder()
    self.session: SessionContext | None = None
    self.current_round: Round | None = None
    self.player_sheets: dict[str, dict] = {}
    self.player_locations: dict[str, str] = {}
    self.session_board = SessionBoard()
    self.scene_board = SceneBoard()
    self.blocker_board = BlockerBoard()
    self.consequence_board = ConsequenceBoard()
```

Update `_cmd_begin_module` to create SessionContext:

```python
async def _cmd_begin_module(self, interaction: Any, module_name: str) -> None:
    self.current_adventure = self.loader.load_module(module_name)
    self.session = SessionContext(
        session_id=f"ses_{uuid.uuid4().hex[:8]}",
        module_name=module_name,
        store=self.store,
    )
    self.session.phase = "active"
    self.session.add_participant(str(interaction.user.id))
    self.current_round = Round(trigger_engine=self.session.trigger_engine)
    self.current_round.start_collection()
    await interaction.response.send_message(
        f"模组 **{module_name}** 开始！当前场景：{self.current_adventure.opening_scene_id}\n"
        "请描述你的行动。"
    )
```

Update `_cmd_status` to render boards:

```python
async def _cmd_status(self, interaction: Any) -> None:
    if not self.current_adventure or not self.session:
        await interaction.response.send_message("没有进行中的模组。")
        return

    parts = []
    parts.append(self.session_board.render(self.session.to_dict()))

    scene_id = getattr(self.current_adventure, "opening_scene_id", "")
    scene_name = ""
    scene = getattr(self.current_adventure, "get_scene", None)
    if scene and scene_id:
        s = scene(scene_id)
        if s:
            scene_name = s.name if hasattr(s, 'name') else scene_id

    round_state = self.current_round.state.value if self.current_round else "N/A"
    action_count = len(self.current_round.actions) if self.current_round else 0

    blockers = []
    if self.session.store:
        blockers = [
            {"reason": b.reason, "scene_id": b.scene_id, "blocker_id": b.blocker_id}
            for b in self.session.store.list_unresolved_blockers()
        ]

    scene_output = self.scene_board.render({
        "scene_id": scene_id,
        "scene_name": scene_name,
        "round_state": round_state,
        "action_count": action_count,
        "waiting_for": [b["reason"] for b in blockers] if blockers else None,
    })
    parts.append(scene_output)

    if blockers:
        parts.append(self.blocker_board.render({"blockers": blockers}))

    response_text = "\n---\n".join(parts)
    await interaction.response.send_message(response_text)
```

Also add import for uuid at top of `commands.py`:

```python
import uuid
from typing import TYPE_CHECKING, Any
```

- [ ] **Step 6: Fix main.py constructor call**

In `src/dm_bot/main.py`, change the BotCommands constructor to match. Since we renamed the internal field from `adventure_loader` to `loader`, `main.py:68` already passes `loader=`, so it should work. But we also have `settings=` now — make sure `__init__` accepts it (we added `settings: Any = None`).

- [ ] **Step 7: Add integration test for boards + SessionContext**

Add to `tests/test_surface.py`:

```python
class TestBoardIntegration:
    def test_all_boards_render_session_state(self):
        from dm_bot.surface.session_context import SessionContext
        from dm_bot.surface.session_board import SessionBoard
        from dm_bot.surface.scene_board import SceneBoard
        from dm_bot.surface.blocker_board import BlockerBoard
        from dm_bot.surface.consequence_board import ConsequenceBoard
        from dm_bot.publish.publisher import Publisher
        from dm_bot.publish.models import ActionSubmittedEvent

        ctx = SessionContext(session_id="ses_test", module_name="TestModule")
        ctx.add_participant("Alice")
        ctx.phase = "active"

        # Publish some events
        pub = ctx.publisher
        pub.publish(ActionSubmittedEvent(
            session_id="ses_test", scene_id="s1",
            user_id="Alice", action_text="Alice searched the room"
        ))

        # Board rendering should work
        session_out = SessionBoard().render(ctx.to_dict())
        assert "TestModule" in session_out
        assert "Alice" in session_out

        events = [
            {"event_type": e.event_type, "visibility": e.visibility.value, "summary": getattr(e, 'action_text', '')}
            for e in pub.get_events()
        ]
        conseq_out = ConsequenceBoard().render({"events": events})
        assert "Alice searched the room" in conseq_out
```

- [ ] **Step 8: Run all surface tests**

Run: `uv run pytest tests/test_surface.py -v`
Expected: ALL PASS

- [ ] **Step 9: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 10: Run smoke check**

Run: `uv run python -m dm_bot.main smoke-check`
Expected: "All core modules import successfully."

- [ ] **Step 11: Commit**

```bash
git add src/dm_bot/surface/session_context.py src/dm_bot/discord_bot/commands.py src/dm_bot/main.py tests/test_surface.py
git commit -m "feat(s7): wire boards into BotCommands via SessionContext"
```

---

### Task 6: Smoke Check and Final Verification

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 2: Run smoke check**

Run: `uv run python -m dm_bot.main smoke-check`
Expected: "All core modules import successfully."

- [ ] **Step 3: Commit any remaining changes**

```bash
git add -A && git commit -m "chore(s7): final gate pass for session board core"
```
