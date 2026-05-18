# S8: Clue Board & View Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Present runtime-approved shared knowledge via clue boards, with view layer separated from Discord formatting.

**Architecture:** New `ViewPayload` data model decouples "what to display" from "how to format". `DiscordFormatter` converts payloads to Discord markdown. `ClueBoard` uses `RevealChecker`/`KnowledgeState` to enforce visibility. Existing boards incrementally adopt `ViewPayload`.

**Tech Stack:** Python, Pydantic v2, ABC

---

### Task 1: ViewPayload Models — Structured Display Data

**Files:**
- Create: `src/dm_bot/surface/view_payload.py`
- Test: `tests/test_surface.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_surface.py`:

```python
class TestViewPayload:
    def test_create_payload(self):
        from dm_bot.surface.view_payload import ViewPayload, ViewSection

        section = ViewSection(heading="Findings", body="The team discovered...")
        payload = ViewPayload(title="Clue Report", sections=[section])
        assert payload.title == "Clue Report"
        assert payload.sections[0].heading == "Findings"

    def test_payload_with_fields(self):
        from dm_bot.surface.view_payload import ViewPayload, FieldEntry

        payload = ViewPayload(
            title="Scene Status",
            fields=[FieldEntry(name="Round", value="3"), FieldEntry(name="Actions", value="2", inline=True)],
        )
        assert len(payload.fields) == 2
        assert payload.fields[1].inline is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_surface.py::TestViewPayload -v`
Expected: ImportError (ViewPayload not defined)

- [ ] **Step 3: Implement ViewPayload models**

Create `src/dm_bot/surface/view_payload.py`:

```python
"""Structured view payload — separates what to display from how to format."""

from pydantic import BaseModel, Field


class FieldEntry(BaseModel):
    """A named key-value pair for compact display."""

    name: str
    value: str
    inline: bool = False


class ViewSection(BaseModel):
    """A titled content block within a view."""

    heading: str
    body: str
    fields: list[FieldEntry] = Field(default_factory=list)


class ViewPayload(BaseModel):
    """Structured display data independent of formatting target."""

    title: str
    description: str = ""
    sections: list[ViewSection] = Field(default_factory=list)
    fields: list[FieldEntry] = Field(default_factory=list)
    footer: str = ""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_surface.py::TestViewPayload -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/dm_bot/surface/view_payload.py tests/test_surface.py
git commit -m "feat(s8): add ViewPayload structured display data models"
```

---

### Task 2: DiscordFormatter — ViewPayload to Discord Markdown

**Files:**
- Create: `src/dm_bot/surface/discord_formatter.py`
- Modify: `tests/test_surface.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_surface.py`:

```python
class TestDiscordFormatter:
    def test_format_title_and_fields(self):
        from dm_bot.surface.discord_formatter import DiscordFormatter
        from dm_bot.surface.view_payload import ViewPayload, FieldEntry

        payload = ViewPayload(
            title="Session: The Haunting",
            fields=[FieldEntry(name="Phase", value="exploration"), FieldEntry(name="Players", value="Alice, Bob")],
        )
        result = DiscordFormatter.format(payload)
        assert "Session: The Haunting" in result
        assert "Phase" in result
        assert "exploration" in result
        assert "Alice, Bob" in result

    def test_format_sections(self):
        from dm_bot.surface.discord_formatter import DiscordFormatter
        from dm_bot.surface.view_payload import ViewPayload, ViewSection

        payload = ViewPayload(
            title="Clue Report",
            sections=[ViewSection(heading="Bloody Footprint", body="A trail leads east.")],
        )
        result = DiscordFormatter.format(payload)
        assert "Bloody Footprint" in result
        assert "A trail leads east." in result

    def test_format_empty_payload(self):
        from dm_bot.surface.discord_formatter import DiscordFormatter
        from dm_bot.surface.view_payload import ViewPayload

        result = DiscordFormatter.format(ViewPayload(title="Empty"))
        assert "Empty" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_surface.py::TestDiscordFormatter -v`
Expected: ImportError (DiscordFormatter not defined)

- [ ] **Step 3: Implement DiscordFormatter**

Create `src/dm_bot/surface/discord_formatter.py`:

```python
"""Discord markdown formatter for ViewPayload."""

from dm_bot.surface.view_payload import ViewPayload


class DiscordFormatter:
    """Converts ViewPayload to Discord-formatted markdown string."""

    @staticmethod
    def format(payload: ViewPayload) -> str:
        lines: list[str] = []
        lines.append(f"**{payload.title}**")
        if payload.description:
            lines.append(payload.description)
            lines.append("")
        for field in payload.fields:
            lines.append(f"**{field.name}:** {field.value}")
        if payload.fields:
            lines.append("")
        for section in payload.sections:
            lines.append(f"**{section.heading}**")
            if section.body:
                lines.append(section.body)
            for field in section.fields:
                lines.append(f"  {field.name}: {field.value}")
            lines.append("")
        if payload.footer:
            lines.append(f"_{payload.footer}_")
        return "\n".join(lines).strip()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_surface.py::TestDiscordFormatter -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/dm_bot/surface/discord_formatter.py tests/test_surface.py
git commit -m "feat(s8): add DiscordFormatter for ViewPayload to markdown conversion"
```

---

### Task 3: ClueBoard — Visibility-Enforced Clue Display

**Files:**
- Create: `src/dm_bot/surface/clue_board.py`
- Modify: `tests/test_surface.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_surface.py`:

```python
class TestClueBoard:
    def test_render_visible_clues(self):
        from dm_bot.surface.clue_board import ClueBoard

        state = {
            "clues": [
                {"clue_id": "c1", "title": "Bloody Knife", "description": "Found under the bed."},
                {"clue_id": "c2", "title": "Strange Symbol", "description": "Carved into the wall."},
            ],
            "visible_clue_ids": ["c1"],
            "player_id": "Alice",
        }
        board = ClueBoard()
        output = board.render(state)
        assert "Bloody Knife" in output
        assert "Strange Symbol" not in output

    def test_render_no_clues(self):
        from dm_bot.surface.clue_board import ClueBoard

        board = ClueBoard()
        output = board.render({"clues": [], "visible_clue_ids": [], "player_id": "Alice"})
        assert "No visible clues" in output

    def test_render_known_clues(self):
        from dm_bot.surface.clue_board import ClueBoard

        state = {
            "clues": [
                {"clue_id": "c1", "title": "Letter", "description": "A torn letter."},
                {"clue_id": "c2", "title": "Key", "description": "An iron key."},
            ],
            "visible_clue_ids": ["c1", "c2"],
            "known_clue_ids": ["c1"],
            "player_id": "Alice",
        }
        board = ClueBoard()
        output = board.render(state)
        assert "[Known]" in output or "Known" in output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_surface.py::TestClueBoard -v`
Expected: ImportError (ClueBoard not defined)

- [ ] **Step 3: Implement ClueBoard**

Create `src/dm_bot/surface/clue_board.py`:

```python
"""Clue board — presents runtime-approved shared knowledge."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, ViewSection


class ClueBoard(Board):
    """Renders visible clues filtered by runtime visibility rules."""

    def render(self, state: dict) -> str:
        clues: list[dict] = state.get("clues", [])
        visible_ids: list[str] = state.get("visible_clue_ids", [])
        known_ids: list[str] = state.get("known_clue_ids", [])
        player_id: str = state.get("player_id", "")

        visible = [c for c in clues if c.get("clue_id") in visible_ids]
        if not visible:
            return "No visible clues."

        sections: list[ViewSection] = []
        for clue in visible:
            cid = clue.get("clue_id", "")
            label = clue.get("title", "Unknown")
            if cid in known_ids:
                label = f"{label} [Known]"
            sections.append(ViewSection(
                heading=label,
                body=clue.get("description", ""),
            ))

        payload = ViewPayload(
            title=f"Clues — {player_id}" if player_id else "Clues",
            sections=sections,
            footer=f"{len(visible)} clue(s) visible" if not player_id else "",
        )
        from dm_bot.surface.discord_formatter import DiscordFormatter
        return DiscordFormatter.format(payload)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_surface.py::TestClueBoard -v`
Expected: ALL PASS

- [ ] **Step 5: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/dm_bot/surface/clue_board.py tests/test_surface.py
git commit -m "feat(s8): add ClueBoard with reveal-gate enforced visibility"
```

---

### Task 4: Refactor Existing Boards to Use ViewPayload + DiscordFormatter

**Files:**
- Modify: `src/dm_bot/surface/session_board.py`
- Modify: `src/dm_bot/surface/scene_board.py`
- Modify: `src/dm_bot/surface/blocker_board.py`
- Modify: `src/dm_bot/surface/consequence_board.py`
- Modify: `tests/test_surface.py` (update assertions to match new output format)

- [ ] **Step 1: Refactor SessionBoard**

Edit `src/dm_bot/surface/session_board.py`:

```python
"""Session identity board."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, FieldEntry
from dm_bot.surface.discord_formatter import DiscordFormatter


class SessionBoard(Board):
    """Renders session identity and participant list."""

    def render(self, state: dict) -> str:
        payload = ViewPayload(
            title=f"Session: {state.get('module_name', 'Unknown')}",
            fields=[
                FieldEntry(name="ID", value=state.get("session_id", "")),
                FieldEntry(name="Phase", value=state.get("phase", "idle")),
                FieldEntry(name="Participants", value=", ".join(state.get("participants", [])) or "None"),
            ],
        )
        return DiscordFormatter.format(payload)
```

- [ ] **Step 2: Refactor SceneBoard**

Edit `src/dm_bot/surface/scene_board.py`:

```python
"""Scene context and round state board."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, FieldEntry
from dm_bot.surface.discord_formatter import DiscordFormatter


class SceneBoard(Board):
    """Renders focused scene context and round state."""

    def render(self, state: dict) -> str:
        fields = [
            FieldEntry(name="Scene", value=state.get("scene_name", "?")),
            FieldEntry(name="Round State", value=state.get("round_state", "?")),
            FieldEntry(name="Actions", value=str(state.get("action_count", 0))),
        ]
        waiting = state.get("waiting_for")
        if waiting:
            fields.append(FieldEntry(name="Waiting", value=", ".join(waiting) if isinstance(waiting, list) else str(waiting)))
        payload = ViewPayload(
            title=state.get("scene_desc", "Scene")[:80],
            fields=fields,
        )
        return DiscordFormatter.format(payload)
```

- [ ] **Step 3: Refactor BlockerBoard**

Edit `src/dm_bot/surface/blocker_board.py`:

```python
"""Blocker summary board — KP-readable checkpoint list."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, ViewSection
from dm_bot.surface.discord_formatter import DiscordFormatter


class BlockerBoard(Board):
    """Renders unresolved blocker checkpoints."""

    def render(self, state: dict) -> str:
        blockers: list[dict] = state.get("blockers", [])
        if not blockers:
            return "No unresolved blockers."

        sections = [
            ViewSection(heading=b.get("reason", "?"), body=f"Scene: {b.get('scene_id', '?')} | ID: {b.get('blocker_id', '?')}")
            for b in blockers
        ]
        payload = ViewPayload(title=f"Blockers ({len(blockers)})", sections=sections)
        return DiscordFormatter.format(payload)
```

- [ ] **Step 4: Refactor ConsequenceBoard**

Edit `src/dm_bot/surface/consequence_board.py`:

```python
"""Consequence output board — visibility-filtered event display."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, ViewSection
from dm_bot.surface.discord_formatter import DiscordFormatter


class ConsequenceBoard(Board):
    """Renders events filtered by visibility path."""

    def render(self, state: dict, visibility: str | None = None) -> str:
        events: list[dict] = state.get("events", [])
        filtered = events
        if visibility:
            filtered = [e for e in events if e.get("visibility") == visibility]
        if not filtered:
            return "No events."

        sections = [
            ViewSection(heading=e.get("summary", e.get("event_type", "?")), body=f"Type: {e.get('event_type', '?')} | Visibility: {e.get('visibility', '?')}")
            for e in filtered
        ]
        label = visibility.replace("_", " ").title() if visibility else "All"
        payload = ViewPayload(title=f"{label} Events ({len(filtered)})", sections=sections)
        return DiscordFormatter.format(payload)
```

- [ ] **Step 5: Update test assertions to match new output format**

Run tests to find failures:
```bash
uv run pytest tests/test_surface.py -v
```

Fix any assertions that break due to formatting changes. Key differences: `Participant(s)` becomes `Participants`, output structure changes with DiscordFormatter. Update assertions to use `**Bold**` markdown prefixes and `Name: Value` field format.

- [ ] **Step 6: Run full suite to confirm no regressions**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add src/dm_bot/surface/session_board.py src/dm_bot/surface/scene_board.py src/dm_bot/surface/blocker_board.py src/dm_bot/surface/consequence_board.py tests/test_surface.py
git commit -m "feat(s8): refactor all boards to use ViewPayload + DiscordFormatter"
```

---

### Task 5: Integration — ClueBoard from Runtime State

**Files:**
- Modify: `tests/test_surface.py` (add integration tests)

- [ ] **Step 1: Add clue visibility integration test

Append to `tests/test_surface.py`:

```python
class TestClueBoardIntegration:
    def test_clue_board_from_reveal_checker(self):
        from dm_bot.surface.clue_board import ClueBoard
        from dm_bot.reveal.models import RevealGate, KnowledgeState
        from dm_bot.reveal.checker import RevealChecker

        checker = RevealChecker()
        gate = RevealGate(clue_id="c1", gate_type="manual")
        gate.open(opened_by="KP")
        alice_knowledge = KnowledgeState(player_id="Alice")
        bob_knowledge = KnowledgeState(player_id="Bob")

        clues_data = [
            {"clue_id": "c1", "title": "Open Clue", "description": "Visible to all."},
            {"clue_id": "c2", "title": "Hidden Clue", "description": "Not visible."},
        ]
        gates = [gate]

        visible_ids = [
            c["clue_id"] for c in clues_data
            if checker.is_clue_visible(c["clue_id"], "Alice", gates, alice_knowledge)
        ]

        state = {
            "clues": clues_data,
            "visible_clue_ids": visible_ids,
            "known_clue_ids": alice_knowledge.known_clue_ids,
            "player_id": "Alice",
        }
        board = ClueBoard()
        output = board.render(state)
        assert "Open Clue" in output
        assert "Hidden Clue" not in output

    def test_clue_board_in_session_context(self):
        from dm_bot.surface.session_context import SessionContext
        from dm_bot.surface.clue_board import ClueBoard
        from dm_bot.reveal.models import RevealGate, KnowledgeState
        from dm_bot.reveal.checker import RevealChecker

        ctx = SessionContext(session_id="ses_1", module_name="Test")
        checker = RevealChecker()
        gate = RevealGate(clue_id="c1", gate_type="manual")
        gate.open(opened_by="KP")

        clues_data = [
            {"clue_id": "c1", "title": "Open Clue", "description": "Visible."},
            {"clue_id": "c2", "title": "Hidden Clue", "description": "Hidden."},
        ]
        gates_list = [gate]
        player_knowledge = KnowledgeState(player_id="Alice")

        visible_ids = [
            c["clue_id"] for c in clues_data
            if checker.is_clue_visible(c["clue_id"], "Alice", gates_list, player_knowledge)
        ]

        state = ctx.to_dict()
        state.update({
            "clues": clues_data,
            "visible_clue_ids": visible_ids,
            "known_clue_ids": player_knowledge.known_clue_ids,
            "player_id": "Alice",
        })
        board = ClueBoard()
        output = board.render(state)
        assert "Open Clue" in output
        assert "Hidden Clue" not in output
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/test_surface.py::TestClueBoardIntegration -v`
Expected: ALL PASS

- [ ] **Step 3: Run full suite for regression**

Run: `uv run pytest -q`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_surface.py
git commit -m "feat(s8): add clue board integration with reveal gates"
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
git add -A && git commit -m "chore(s8): final gate pass for clue board and view contracts"
```
