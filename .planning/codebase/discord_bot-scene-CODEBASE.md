# Codebase Analysis: discord_bot & scene Packages

**Date:** 2026-04-25
**Packages:** `discord_bot`, `scene`

---

## 1. Package Purpose & Responsibilities

### `discord_bot`
Discord I/O layer: receives user interactions and slash commands, sends replies.

**Responsibilities:**
- Parse Discord slash commands (`/start`, `/begin_module`, `/action`, `/roll`, `/sheet`, `/end_round`, `/status`)
- Handle lobby messages as public actions
- Delegate business logic to `scene` and other packages
- Return ephemeral responses via Discord

**Does NOT do:** Business logic, state management, dice rolling, narrative generation

### `scene`
Core round state machine: manages turn lifecycle, action collection ordering, and result aggregation.

**Responsibilities:**
- Track `SceneState` (WAITING, COLLECTING, RESOLVING, NARRATING)
- Accept player action submissions
- Sort actions by DEX (descending) then user_id (ascending)
- Compute/aggregate results
- Provide private result distribution

**Does NOT do:** Dice computation, text generation, Discord I/O

---

## 2. Key Classes/Functions

### `discord_bot/commands.py`

#### `BotCommands`
```python
class BotCommands:
    def __init__(
        self,
        *,
        adventure_loader: "AdventureLoader",
        narrator: "NarratorClient",
        store: "Store",
    ) -> None: ...
```

**In-memory session state:**
```python
self.current_adventure: "Adventure | None" = None
self.current_round: Round | None = None
self.player_sheets: dict[str, dict] = {}  # user_id -> sheet data
self.player_locations: dict[str, str] = {}  # user_id -> scene_id
```

**Slash Commands:**
| Command | Signature | Purpose |
|---------|-----------|---------|
| `start_cmd` | `(self, interaction: discord.Interaction) -> None` | Begin character creation |
| `begin_module_cmd` | `(self, interaction: discord.Interaction, module_name: str) -> None` | Load adventure, start first round |
| `action_cmd` | `(self, interaction: discord.Interaction, text: str) -> None` | Submit private action |
| `roll_cmd` | `(self, interaction: discord.Interaction, skill: str) -> None` | Manual dice check (placeholder) |
| `sheet_cmd` | `(self, interaction: discord.Interaction) -> None` | Display character sheet |
| `end_round_cmd` | `(self, interaction: discord.Interaction) -> None` | Force resolve current round |
| `status_cmd` | `(self, interaction: discord.Interaction) -> None` | Show current adventure/round state |

**Message Handler:**
```python
async def handle_message(self, interaction: discord.Interaction, text: str) -> None:
    """处理大厅里的普通消息（公开行动）"""
```

**Internal:**
```python
async def _resolve_round(self, interaction: discord.Interaction) -> None:
    """结算当前回合"""
```

---

### `scene/state.py`

#### `SceneState` (Enum)
```python
class SceneState(str, Enum):
    WAITING = "waiting"
    COLLECTING = "collecting"
    RESOLVING = "resolving"
    NARRATING = "narrating"
```

State transitions:
- `WAITING` -> `COLLECTING` (via `Round.start_collection()`)
- `COLLECTING` -> `RESOLVING` (via `Round.resolve()`)
- `RESOLVING` -> `NARRATING` (by end of `Round.resolve()`)
- `NARRATING` -> `COLLECTING` (new round started)

---

### `scene/action.py`

#### `ActionResult` (Pydantic BaseModel)
```python
class ActionResult(BaseModel):
    success: bool
    success_rank: str = "failure"  # critical, extreme, hard, regular, failure
    rolled_value: int = 0
    san_change: int = 0
    discovered_clues: list[str] = Field(default_factory=list)
    extra_info: str = ""
```

#### `Action` (Pydantic BaseModel)
```python
class Action(BaseModel):
    user_id: str = Field(min_length=1)
    character_id: str = Field(min_length=1)
    action_text: str = Field(min_length=1)
    visibility: Literal["public", "private"] = "public"
    dex_value: int = 50  # DEX determines action order
    result: ActionResult | None = None
```

---

### `scene/round.py`

#### `Round`
```python
class Round:
    def __init__(self) -> None:
        self.actions: list[Action] = []
        self.state = SceneState.WAITING
```

**Methods:**
| Method | Signature | Purpose |
|--------|-----------|---------|
| `submit_action` | `(self, action: Action) -> None` | Submit player action; raises if not COLLECTING |
| `start_collection` | `(self) -> None` | Reset actions, set state to COLLECTING |
| `all_players_acted` | `(self, expected_count: int) -> bool` | Check if all players have acted |
| `resolve` | `(self) -> list[Action]` | Sort by DEX desc/user_id asc, compute results, set NARRATING |
| `get_private_results` | `(self) -> dict[str, str]` | Returns user_id -> result_text for private actions |

---

## 3. How discord_bot and scene Interact

### Action Submission Flow
```
Discord message (public action)
  -> BotCommands.handle_message()
  -> Round.submit_action()
  -> Round.actions.append()

Discord /action (private action)
  -> BotCommands.action_cmd()
  -> Action(user_id, character_id, text, visibility="private", dex_value)
  -> Round.submit_action()
```

### Round Resolution Flow
```
Discord /end_round
  -> BotCommands.end_round_cmd()
  -> BotCommands._resolve_round()
    1. Round.resolve() -> ordered actions (DEX sorted)
    2. narrator.generate() -> narrative text
    3. interaction.channel.send() -> post to lobby
    4. Round.get_private_results() -> private DM data
    5. New Round() created, start_collection() called
```

### Data Flow Summary
```
discord_bot (receives) --> scene (state) --> discord_bot (sends)
                              |
                              v
                          narrator (generate)
                              |
                              v
                          discord_bot (posts to lobby/DMs)
```

---

## 4. Key Design Patterns

### State Machine Pattern
`scene` implements a simple state machine via `SceneState` enum:
- States clearly defined
- Transitions enforced via RuntimeError checks
- Only valid operations permitted per state

### Command Pattern
`BotCommands` groups related operations under a single class with `register()` method for slash command registration.

### Builder Pattern
`CharacterBuilder` implements a step-by-step conversational flow for character creation, maintaining session state per user.

### Strategy Pattern
`Round.resolve()` is designed to delegate actual rule computation to external rules package (placeholder shows this intent).

### Data Model + Service Separation
- `scene/action.py`: Pure data models (`Action`, `ActionResult`) using Pydantic
- `scene/round.py`: Business logic class (`Round`)

---

## 5. Dependencies

### `discord_bot` Imports From

| Package | Module | What's Imported |
|---------|--------|-----------------|
| `discord` | `discord` | `discord.Interaction` |
| `discord` | `app_commands` | `app_commands.CommandTree`, `app_commands.command`, `app_commands.describe` |
| `character` | `builder` | `CharacterBuilder` |
| `scene` | `action` | `Action` |
| `scene` | `round` | `Round` |
| `scene` | `state` | `SceneState` |
| `adventure` | `loader` | `AdventureLoader` (type annotation only) |
| `adventure` | `models` | `Adventure` (type annotation only) |
| `narrator` | `client` | `NarratorClient` (type annotation only) |
| `store` | `db` | `Store` (type annotation only) |

### `scene` Imports From

| Package | Module | What's Imported |
|---------|--------|-----------------|
| `pydantic` | `BaseModel`, `Field` | Data validation for `Action`, `ActionResult` |
| `enum` | `Enum` | `SceneState` base |
| Local | `action.py` | `Action`, `ActionResult` |
| Local | `state.py` | `SceneState` |

**`scene` has NO external package dependencies** - it is a pure Python state management module.

---

## 6. File Structure

```
src/dm_bot/
├── discord_bot/
│   ├── __init__.py          # Exports BotCommands
│   └── commands.py          # 174 lines - slash commands & message handling
└── scene/
    ├── __init__.py          # Empty
    ├── state.py             # 8 lines - SceneState enum
    ├── action.py            # 25 lines - Action, ActionResult models
    └── round.py             # 54 lines - Round class
```

---

## 7. Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| `SceneState` | Complete | 4-state enum matches spec |
| `Action`/`ActionResult` | Complete | Pydantic models |
| `Round` | Partial | Placeholder resolution (no actual rules) |
| `BotCommands` | Partial | All commands defined; `roll_cmd` is placeholder |
| `CharacterBuilder` | Partial | Works for happy path; no persistence |
| `narrator.generate()` | Placeholder | Called but not implemented in commands.py |

**Spec compliance:** Matches architecture spec dated 2026-04-24 for the `discord_bot` and `scene` packages.
