# Adventure & Character Package Analysis

## 1. Package Purpose & Responsibilities

### `adventure/`
**Purpose:** Load and provide access to module data (scenes, NPCs, clues).

**Responsibilities:**
- Define data models for adventure modules (Scene, NPC, Clue, Adventure)
- Load module data from storage (currently in-memory; designed for JSON/YAML expansion)
- Provide scene lookup by ID within an adventure

**Does NOT do:** State management, narrative generation, rule computation

### `character/`
**Purpose:** Manage investigator character sheets and conversational creation.

**Responsibilities:**
- Define the character sheet data model (COC stats, derived attributes, skills)
- Provide a step-by-step conversational character creation flow
- Store temporary creation session state per user

**Does NOT do:** Rules computation, persistence, Discord I/O

---

## 2. Key Classes/Functions & Signatures

### `adventure/models.py`

```python
class Clue(BaseModel):
    clue_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    required_skill: str = ""
    difficulty: str = "regular"

class NPC(BaseModel):
    npc_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = ""
    stats: dict[str, int] = Field(default_factory=dict)

class Scene(BaseModel):
    scene_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    exits: list[str] = Field(default_factory=list)      # scene IDs player can navigate to
    clues: list[Clue] = Field(default_factory=list)
    npcs: list[NPC] = Field(default_factory=list)

class Adventure(BaseModel):
    adventure_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    scenes: dict[str, Scene] = Field(default_factory=dict)
    opening_scene_id: str = ""
```

### `adventure/loader.py`

```python
class AdventureLoader:
    """Loads module data (in-memory implementation; expandable to JSON/YAML)"""

    def load_module(self, module_name: str) -> Adventure:
        """Load specified module. Currently returns empty adventure with only ID set."""

    def get_scene(self, adventure: Adventure, scene_id: str) -> Scene | None:
        """Retrieve a scene from an adventure by scene_id."""
```

### `character/sheet.py`

```python
class CharacterSheet(BaseModel):
    """COC Investigator Character Sheet"""

    character_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    age: int = 20
    occupation: str = ""

    # Primary Attributes (base value 50)
    strength: int = 50
    constitution: int = 50
    size: int = 50
    dexterity: int = 50
    appearance: int = 50
    intelligence: int = 50
    power: int = 50
    education: int = 50
    luck: int = 50

    # Derived Attributes
    hit_points: int = 10
    magic_points: int = 10
    sanity: int = 50
    sanity_max: int = 99

    # Skills (skill_name -> success_rate)
    skills: dict[str, int] = Field(default_factory=dict)

    def get_skill_value(self, skill_name: str) -> int:
        """Get skill value; returns 0 if not set."""
```

### `character/builder.py`

```python
class CharacterBuilder:
    """Conversational character creation flow"""

    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}  # user_id -> creation session state

    def begin_creation(self, user_id: str) -> str:
        """Start creation flow; returns opening prompt."""

    def handle_response(self, user_id: str, text: str) -> str:
        """Process player response; returns next prompt or final sheet summary."""

    def get_sheet(self, user_id: str) -> CharacterSheet | None:
        """Retrieve completed sheet; returns None if creation incomplete."""
```

**Creation Steps:** `name` -> `age` -> `occupation` -> `done`

---

## 3. How Adventure and Character Interact

```
adventure/                         character/
    |                                    |
    |-- Scene, NPC, Clue, Adventure      |-- CharacterSheet, CharacterBuilder
    |                                    |
    v                                    v
Provides module data to           Provides player avatar data to
scene/round resolution           scene/round resolution

Both are READ-ONLY data containers consumed by the scene/ round state machine.
They do not directly interact with each other.
```

**In the round resolution flow** (per architecture spec 5.2):
- `adventure.get_scene()` retrieves current scene for narration
- `adventure.get_clue()` checks if an action reveals a clue
- `CharacterSheet` (via `scene.round`) provides stats for `rules.checks.skill_roll()` and `rules.sanity.check()`
- `CharacterBuilder` creates sheets used by the session before round play begins

**Interaction Point:** Both packages feed data into `scene/round.py` and `rules/` during round resolution. They have no direct coupling.

---

## 4. Key Design Patterns

### Data Transfer Object (DTO) Pattern
- `Adventure`, `Scene`, `NPC`, `Clue`, `CharacterSheet` are all Pydantic `BaseModel`
- They serve as pure data containers with no business logic
- Validation via `Field` constraints (e.g., `min_length=1`)

### Builder Pattern
- `CharacterBuilder` implements a step-by-step conversational factory
- Session state stored in `self._sessions` dict keyed by `user_id`
- Transitions managed by `step` field in session data

### In-Memory Loader Pattern
- `AdventureLoader.load_module()` currently returns a bare `Adventure` with only IDs set
- Design explicitly allows future JSON/YAML loading without changing the interface
- `get_scene()` delegates to `Adventure.scenes` dict lookup

### Stateless Session Storage
- `CharacterBuilder._sessions` is an in-memory dict (not persisted)
- Designed for DM Bot conversational flow where sessions are short-lived
- Not appropriate for long-term campaign storage (would need `store/` persistence)

---

## 5. Dependencies

### `adventure/` imports from elsewhere
| Source | What | Purpose |
|--------|------|---------|
| `pydantic` | `BaseModel`, `Field` | Data validation and serialization |

### `character/` imports from elsewhere
| Source | What | Purpose |
|--------|------|---------|
| `pydantic` | `BaseModel`, `Field` | Data validation and serialization |
| `random` | (inline import) | Stat generation during character creation |

### What these packages DO NOT depend on
- No internal `dm_bot` imports -- these are leaf packages
- `adventure/` does not import `character/` (and vice versa)
- No `rules/`, `scene/`, `store/`, `narrator/`, or `discord_bot/` dependencies

### Who depends on these packages
| Consumer | Usage |
|----------|-------|
| `scene/round.py` | Reads `CharacterSheet` for checks; reads `Adventure`/`Scene` for clue resolution |
| `scene/state.py` | Likely holds references to current `CharacterSheet` per player |
| `discord_bot/commands.py` | Calls `CharacterBuilder.begin_creation()` and `handle_response()` |
| `store/` (future) | Would persist `CharacterSheet` and `Adventure` data |

---

## 6. Notes & Observations

### Adventure Loader is a Skeleton
- `load_module()` returns an `Adventure` with no scenes, NPCs, or clues
- The `TODO: 从文件系统加载` comment confirms this is placeholder
- Full module loading from JSON/YAML is the next major work item

### Character Builder Has No Persistence
- Sessions are lost on bot restart
- `get_sheet()` returns `None` if session is missing or incomplete
- No `save()` method -- sheets exist only in memory during creation flow

### Skill System is Minimal
- `CharacterSheet.skills` is a flat `dict[str, int]` (skill_name -> success_rate)
- `get_skill_value()` returns `0` for unknown skills (not the COC default of `1d20` or `EDU*2`)
- No skill definitions or lookup table; assumes caller knows skill names

### Derived HP/MP/SAN Formula (in `CharacterBuilder`)
```
HP   = (CON + SIZ) // 10
MP   = POW // 5
SAN  = POW
SAN_MAX = 99 - skills_bonus (if present) else 99
```
This is a simplified version of COC7 rules.

### `adventure/__init__.py` and `character/__init__.py` are Empty
- No package-level exports
- Importers must use full path: `from dm_bot.adventure.models import Adventure`
