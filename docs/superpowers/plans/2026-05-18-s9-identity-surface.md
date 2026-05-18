# S9: Identity Surface Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Players can view/select characters and understand campaign state from Discord.

**Architecture:** New character boards use ViewPayload + DiscordFormatter. SessionContext extended with character binding. BotCommands wired to display characters.

**Tech Stack:** Python, Pydantic v2

---

### Task 1: CharacterCardBoard — Full Sheet Display

**Files:**
- Create: `src/dm_bot/surface/character_board.py`
- Modify: `tests/test_surface.py`

- [ ] **Step 1: Write failing tests**

```python
class TestCharacterBoard:
    def test_render_sheet(self):
        from dm_bot.surface.character_board import CharacterCardBoard

        state = {
            "name": "Alice",
            "age": 30,
            "occupation": "Detective",
            "strength": 60, "constitution": 50, "size": 50,
            "dexterity": 50, "appearance": 50, "intelligence": 70,
            "power": 60, "education": 65, "luck": 40,
            "hit_points": 10, "magic_points": 12, "sanity": 60, "sanity_max": 99,
            "skills": {"Spot Hidden": 60, "Library Use": 50},
        }
        board = CharacterCardBoard()
        output = board.render(state)
        assert "Alice" in output
        assert "Detective" in output
        assert "STR:60" in output or "Strength:60" in output.replace(" ", "")
        assert "Spot Hidden" in output

    def test_render_minimal_sheet(self):
        from dm_bot.surface.character_board import CharacterCardBoard

        board = CharacterCardBoard()
        output = board.render({"name": "Bob", "occupation": "Writer"})
        assert "Bob" in output
```

- [ ] **Step 2: Run tests -> ImportError**
- [ ] **Step 3: Implement CharacterCardBoard**

```python
"""Character sheet display board."""

from dm_bot.surface.board import Board
from dm_bot.surface.view_payload import ViewPayload, ViewSection, FieldEntry
from dm_bot.surface.discord_formatter import DiscordFormatter


class CharacterCardBoard(Board):
    """Renders a character archive as a Discord-readable card."""

    def render(self, state: dict) -> str:
        name = state.get("name", "?")
        occupation = state.get("occupation", "")
        fields = [
            FieldEntry(name="Age", value=str(state.get("age", "?"))),
            FieldEntry(name="Occupation", value=occupation or "?"),
        ]
        stats = ViewSection(
            heading="Attributes",
            fields=[
                FieldEntry(name=f"{k.split('_')[0].upper()[:3]}", value=str(state.get(k, 0)), inline=True)
                for k in ["strength", "constitution", "size", "dexterity",
                           "appearance", "intelligence", "power", "education", "luck"]
                if k in state
            ],
        )
        hp_fields = [
            FieldEntry(name="HP", value=str(state.get("hit_points", "?")), inline=True),
            FieldEntry(name="MP", value=str(state.get("magic_points", "?")), inline=True),
            FieldEntry(name="SAN", value=f"{state.get('sanity', '?')}/{state.get('sanity_max', 99)}", inline=True),
        ]
        vitals = ViewSection(heading="Vitals", fields=hp_fields)

        skills = state.get("skills", {})
        skill_section = ViewSection(
            heading="Skills",
            body=", ".join(f"{k}:{v}%" for k, v in sorted(skills.items())) if skills else "None",
        ) if skills else None

        sections = [stats, vitals]
        if skill_section:
            sections.append(skill_section)

        payload = ViewPayload(
            title=f"{name} ({occupation})" if occupation else name,
            fields=fields,
            sections=sections,
        )
        return DiscordFormatter.format(payload)
```

- [ ] **Step 4: Tests pass**
- [ ] **Step 5: Commit**

---

### Task 2: CharacterListBoard — Player Roster

**Files:**
- Modify: `src/dm_bot/surface/character_board.py`
- Modify: `tests/test_surface.py`

- [ ] **Step 1: Write failing tests**

```python
class TestCharacterListBoard:
    def test_list_characters(self):
        from dm_bot.surface.character_board import CharacterListBoard

        state = {
            "characters": [
                {"name": "Alice", "occupation": "Detective"},
                {"name": "Bob", "occupation": "Doctor"},
            ]
        }
        board = CharacterListBoard()
        output = board.render(state)
        assert "Alice" in output
        assert "Bob" in output
        assert "2" in output or "2 character" in output.lower()

    def test_list_empty(self):
        from dm_bot.surface.character_board import CharacterListBoard

        board = CharacterListBoard()
        output = board.render({"characters": []})
        assert "No characters" in output
```

- [ ] **Step 2: Tests fail -> ImportError**
- [ ] **Step 3: Implement CharacterListBoard** (add to same file)

```python
class CharacterListBoard(Board):
    """Renders player's character roster."""

    def render(self, state: dict) -> str:
        chars: list[dict] = state.get("characters", [])
        if not chars:
            return "No characters."
        sections = [
            ViewSection(heading=c.get("name", "?"), body=c.get("occupation", ""))
            for c in chars
        ]
        payload = ViewPayload(title=f"Characters ({len(chars)})", sections=sections)
        return DiscordFormatter.format(payload)
```

- [ ] **Step 4: Tests pass**
- [ ] **Step 5: Commit**

---

### Task 3: Session Character Binding

**Files:**
- Modify: `src/dm_bot/surface/session_context.py`
- Modify: `tests/test_surface.py`

- [ ] **Step 1: Tests**

```python
class TestSessionCharacterBinding:
    def test_select_character(self):
        from dm_bot.surface.session_context import SessionContext

        ctx = SessionContext(session_id="ses_1")
        ctx.select_character("c1", "Alice", "Detective")
        assert ctx.selected_character_id == "c1"
        assert ctx.selected_character_name == "Alice"

    def test_to_dict_includes_character(self):
        from dm_bot.surface.session_context import SessionContext

        ctx = SessionContext(session_id="ses_1")
        ctx.select_character("c1", "Alice", "Detective")
        d = ctx.to_dict()
        assert d["selected_character_name"] == "Alice"
```

- [ ] **Step 2: Tests fail -> AttributeError**
- [ ] **Step 3: Add to SessionContext**

```python
    def __init__(self, ...):
        ...
        self.selected_character_id: str = ""
        self.selected_character_name: str = ""
        self.selected_character_occupation: str = ""

    def select_character(self, char_id: str, name: str, occupation: str = "") -> None:
        self.selected_character_id = char_id
        self.selected_character_name = name
        self.selected_character_occupation = occupation
```

Update `to_dict` to include:
```python
            "selected_character_id": self.selected_character_id,
            "selected_character_name": self.selected_character_name,
```

- [ ] **Step 4: Tests pass**
- [ ] **Step 5: Commit**

---

### Task 4: BotCommands Integration

**Files:**
- Modify: `src/dm_bot/discord_bot/commands.py`
- Modify: `tests/test_surface.py`

- [ ] **Step 1: Integration tests**

```python
class TestCharacterBoardIntegration:
    def test_character_card_from_store(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        from dm_bot.surface.character_board import CharacterCardBoard
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_char_board.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        try:
            sheet = CharacterSheet(character_id="u1", name="Alice", age=30, occupation="Writer")
            archive = CharacterArchive(character_id="u1", player_id="u1", sheet=sheet)
            store.save_character(archive)

            loaded = store.load_character("u1")
            state = loaded.sheet.model_dump()
            output = CharacterCardBoard().render(state)
            assert "Alice" in output
            assert "Writer" in output
        finally:
            del store
            gc.collect()
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_character_list_from_store(self):
        from dm_bot.store.db import Store
        from dm_bot.character.archive import CharacterArchive
        from dm_bot.character.sheet import CharacterSheet
        from dm_bot.surface.character_board import CharacterListBoard
        import tempfile, os, gc

        db_path = os.path.join(tempfile.gettempdir(), "test_char_list2.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        store = Store(db_path)
        try:
            for cid, name, occ in [("c1", "Alice", "Writer"), ("c2", "Bob", "Doctor")]:
                sheet = CharacterSheet(character_id=cid, name=name, occupation=occ)
                store.save_character(CharacterArchive(character_id=cid, player_id="u1", sheet=sheet))
            chars = [s.model_dump() for s in (store.load_character(c) for c in ["c1", "c2"]) if s]
            state = {"player_id": "u1", "characters": [{"name": c["name"], "occupation": c["occupation"]} for c in chars]}
            output = CharacterListBoard().render(state)
            assert "Alice" in output
            assert "Bob" in output
        finally:
            del store
            gc.collect()
            if os.path.exists(db_path):
                os.remove(db_path)
```

(Can also update main.py to include a placeholder /sheet or /char command. Since we can't run Discord here, the tests verify the plumbing.)

- [ ] **Step 2: Tests pass**
- [ ] **Step 3: Commit**

---

### Task 5: Smoke Check and Final Verification

- [ ] **Step 1: Run full test suite**
Run: `uv run pytest -q` -> ALL PASS

- [ ] **Step 2: Run smoke check**
Run: `uv run python -m dm_bot.main smoke-check` -> OK

- [ ] **Step 3: Commit**
