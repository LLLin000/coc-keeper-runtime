# Architecture Refactor: Simplified Discord COC Bot

**Date:** 2026-04-24
**Status:** Approved
**Scope:** Radical simplification of 14-package architecture to 7-package design

---

## 1. Problem Statement

The current codebase has evolved into an "enterprise microservices runtime" when the actual need is a "simple Discord COC (Call of Cthulhu) bot." Key issues:

- **14 top-level packages** with scattered responsibilities
- `orchestrator/` became a "garbage dump" mixing session, turn, gameplay, visibility
- Dependency injection hell: 20+ objects wired together in `build_runtime()`
- No clear interface boundaries
- User experience: 4+ Discord channels, 4 startup modes, concept overload (SceneLifecycle, PlayerFocusScope, fork/switch, batch resolution)
- No zero-config out-of-box experience

## 2. Target User Experience

### 2.1 Discord Channel Structure
- **#大厅** — Everyone plays together. Normal descriptions + `/action` for secret actions
- **DM Bot** — Personal character sheet management

### 2.2 Round Flow
1. **AI Opens Round** — "Round 3 begins. What do you do?"
2. **Player Actions** — Describe in lobby, `/action` for secret moves
3. **Instant Feedback** — AI DMs player brief acknowledgments
4. **All Players Done** — AI publishes unified scene resolution
5. **Emergency Push** — AI can force resolution when story demands

### 2.3 Dice Rolling
- Normal checks: AI auto-rolls
- Combat/contested: Player manual `/roll`

### 2.4 Character Creation
- DM Bot conversational step-by-step

### 2.5 Story Source
- Choose from preset module list

---

## 3. New Architecture (7 Packages)

```
src/dm_bot/
├── main.py              # Entry point
├── config.py            # Configuration
├── discord_bot/         # I/O only: receive/send messages, slash commands
│   ├── bot.py
│   ├── commands.py      # /action, /roll, /start, /sheet
│   └── messages.py
├── scene/               # [CORE] Round state machine
│   ├── state.py         # SceneState: waiting → collecting → resolving → narrating
│   ├── round.py         # Action collection, DEX sort, result computation
│   └── action.py        # Action model (public/private)
├── adventure/           # Module data: scene graph, NPCs, clues
│   ├── loader.py        # Load JSON/YAML modules
│   └── models.py        # Scene, NPC, Clue
├── character/           # Character sheets
│   ├── sheet.py         # Stats, skills, SAN
│   └── builder.py       # Conversational creation flow
├── rules/               # COC rules: dice, checks, combat, SAN
│   ├── dice.py
│   ├── checks.py
│   ├── combat.py
│   └── sanity.py
├── narrator/            # AI narrative: call local model for responses
│   ├── client.py        # qwen3:4b / qwen3:1.7b calls
│   └── prompts.py       # Scene, NPC roleplay, rule judgment prompts
└── store/               # SQLite persistence
    ├── db.py
    └── session.py
```

## 4. Package Responsibilities

| Package | Responsibility | Does NOT do |
|---------|---------------|-------------|
| `discord_bot` | Parse Discord messages/slash commands, send replies | Business logic, state management |
| `scene` | Round lifecycle, action collection ordering, result orchestration | Dice computation, text generation |
| `adventure` | Load module data (scenes, NPCs, clues) | State management, narrative |
| `character` | Sheet CRUD, builder conversation | Rules computation |
| `rules` | Deterministic computation (dice, checks, combat, SAN) | State changes, narrative |
| `narrator` | Generate narrative text from state + results | State changes, rule computation |
| `store` | SQLite persistence | Business logic |

## 5. Data Flow (Complete Round Example)

### 5.1 Action Collection
```
Player sends message in #大厅
  → discord_bot receives
  → discord_bot parses (/action or normal)
  → discord_bot calls scene.round.submit_action()
  → scene stores action, state = COLLECTING
  → scene calls narrator for instant feedback
  → narrator generates acknowledgment
  → discord_bot DMs player
```

### 5.2 Round Resolution
```
All players submitted (or AI forces)
  → scene.round.resolve() begins
  → scene sorts actions by DEX descending, user_id ascending
  → for each action:
    - if needs check: scene calls rules.checks.skill_roll()
    - if combat: rules.combat.resolve()
    - if clue: adventure.get_clue()
    - if horror: rules.sanity.check()
  → scene aggregates results
  → scene calls narrator.generate_resolution()
  → narrator produces unified narrative
  → scene calls discord_bot to post to #大厅
  → scene distributes private results via discord_bot DMs
```

### 5.3 Scene Transition
```
Player requests scene change
  → discord_bot forwards to scene
  → scene validates via adventure (is it an exit?)
  → scene changes state
  → scene calls narrator for new scene opening
  → discord_bot posts to #大厅
```

## 6. Deletion List

| Old Package/File | Reason |
|------------------|--------|
| `orchestrator/` | Responsibilities split to `scene/` and `discord_bot/` |
| `gameplay/` | Merged into `scene/` |
| `router/` | Merged into `narrator/` |
| `runtime/` | Too abstract |
| `models/` | Empty or duplicate |
| `narration/` | Renamed to `narrator/` |
| `persistence/` | Renamed to `store/` |
| `diagnostics/` | Reconsider after refactor |
| `governance_event_log` | Over-engineered |
| `PlayerFocusScope`, `SceneLifecycle` enums | Replace with simple string states |
| `fork/switch_focus/merge_propose` | Simplify to `scene.change_location()` |
| `orchestrator/session_store.py` | Split: state→`scene/`, storage→`store/` |
| `orchestrator/gameplay.py` | Merged into `scene/` |
| `orchestrator/turn_manager.py` | Merged into `scene/round.py` |

## 7. Migration Strategy

### Phase 1: Create New Structure
- Create 7 new packages with `__init__.py`
- Implement `scene/` state machine (highest priority)
- Implement `rules/` (extract from existing `coc/`)

### Phase 2: Port Core Logic
- Move dice/checks/combat/SAN from `coc/` → `rules/`
- Move character builder from `orchestrator/` → `character/`
- Move adventure loading from `adventures/` → `adventure/`

### Phase 3: Discord Integration
- Rewrite `discord_bot/commands.py` with new slash commands
- Wire `discord_bot` → `scene` → `narrator`

### Phase 4: Cleanup
- Delete old packages
- Update tests
- Verify: `uv run pytest -q` passes

## 8. State Simplification

Old complex state:
```python
class SceneLifecycle(Enum):
    DRAFT = "draft"
    COLLECTING = "collecting"
    LOCKED = "locked"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class PlayerFocusScope(Enum):
    LOBBY = "lobby"
    SCENE = "scene"
    COMBAT = "combat"
    BUILDER = "builder"
```

New simple state:
```python
class SceneState(str, Enum):
    WAITING = "waiting"        # Waiting for round start
    COLLECTING = "collecting"  # Collecting player actions
    RESOLVING = "resolving"    # Computing results
    NARRATING = "narrating"    # AI generating text
```

Player location tracked simply:
```python
player_locations: dict[str, str]  # user_id -> scene_id
```

## 9. Success Criteria

- [ ] `pytest` passes (all existing tests adapted or replaced)
- [ ] `/start` command creates character via DM conversation
- [ ] `/begin_module <name>` loads adventure and starts first scene
- [ ] Normal message in #大厅 submits public action
- [ ] `/action <text>` submits private action
- [ ] AI gives instant DM feedback per action
- [ ] When all players acted (or AI forces), unified resolution posted to #大厅
- [ ] Private results sent via DM
- [ ] Scene transitions work via player request or story trigger
- [ ] Dice rolls automatic for normal checks, manual for combat

---

**Approved by:** Overseer Lin
**Date:** 2026-04-24
