# Architecture

**Analysis Date:** 2026-03-31

## System Overview

**Discord AI Keeper** — Local model-driven Call of Cthulhu tabletop RPG system for Discord.

The system enables multiple players to run COC sessions in Discord where a local AI Keeper narrates, roleplays NPCs, and enforces COC7 rules.

## Architecture Pattern

**Overall:** Layered modular architecture with clear separation of concerns

```
Discord Users
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Discord Bot Layer (discord_bot/)                       │
│  - Slash commands / normal messages / streaming         │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Session Orchestrator (orchestrator/)                  │
│  - Campaign binding / channel roles / turn coordination │
│  - Phase management (lobby → scene_round → combat)     │
└───────┬─────────┬─────────┬─────────┬─────────────────┘
        │         │         │         │
        ▼         ▼         ▼         ▼
┌───────────┐ ┌─────────┐ ┌──────────┐ ┌────────────────┐
│ Adventure │ │ Rules   │ │ Model    │ │ Persistence & │
│ Runtime   │ │ Engine  │ │ Layer    │ │ Diagnostics   │
│           │ │         │ │          │ │               │
│(room graph│ │ (coc/   │ │ Router   │ │ SQLite        │
│ scene     │ │ skills, │ │ qwen3:1b │ │ event log     │
│ trigger   │ │ combat, │ │ Narrator │ │ session       │
│ tree)     │ │ sanity, │ │ qwen3:4b │ │ recovery      │
│           │ │ magic)  │ │          │ │               │
└───────────┘ └─────────┘ └──────────┘ └───────────────┘
```

## Directory Layout

```
src/dm_bot/
├── adventures/        # Structured modules, graphs, triggers, extraction
├── characters/        # Character import sources and models
│   └── models.py      # CharacterRecord, COCInvestigatorProfile
├── coc/               # Track A: COC panels, archive
├── diagnostics/        # Runtime summaries and debug output
├── discord_bot/        # Discord client, commands, streaming transport
├── gameplay/           # Combat and scene presentation helpers
├── models/             # Ollama/OpenAI-compatible client and model schemas
├── narration/          # Narrator prompt and response shaping
├── orchestrator/        # Turn pipeline, session runtime, gameplay integration
│   ├── gameplay.py     # GameplayOrchestrator, CharacterRegistry
│   └── turn_runner.py  # TurnRunner (stream/async execution)
├── persistence/         # SQLite-backed state store
├── router/              # Structured turn routing contracts and service
│   ├── intent.py        # MessageIntent types, phase priorities
│   └── intent_handler.py # IntentHandlerRegistry
├── rules/               # COC rules engine (core subsystem)
│   ├── engine.py        # RulesEngine - action execution
│   ├── actions.py       # RuleAction, LookupAction models
│   ├── dice.py          # DiceOutcome, PercentileOutcome, dice rollers
│   ├── compendium.py    # FixtureCompendium for SRD lookups
│   ├── skills.py        # Skill definitions and check resolution
│   ├── skill_points.py  # Skill point allocation
│   ├── skill_resolution.py # Skill check resolution helpers
│   ├── skill_triggers.py # Skill trigger system
│   └── coc/             # COC7 rules subsystem
│       ├── __init__.py  # Public API exports
│       ├── skills.py    # 80+ skill definitions
│       ├── combat.py    # Initiative, fighting, shooting, dodge, grapple
│       ├── sanity.py    # SAN loss, madness, phobia/mania, recovery
│       ├── magic.py     # Spells, casting, MP, Cthulhu Mythos
│       ├── derived.py   # HP, MP, Luck, MOV, Build, DB
│       └── experience.py # Skill improvement, occupational/interest points
├── runtime/             # App health, startup checks, smoke check
└── testing/             # Test infrastructure
    ├── scenario_dsl.py  # ScenarioMode types, ScenarioParser, ScenarioRegistry
    └── runtime_driver.py # RuntimeTestDriver for scenario execution
```

## Key Layers

### 1. Discord Bot Layer (`discord_bot/`)

**Purpose:** Discord interaction surface - slash commands, message handling, streaming output

**Key Files:**
- `discord_bot/commands.py` - BotCommands (slash command handlers)
- `discord_bot/client.py` - Discord client setup

**Responsibilities:**
- Slash command registration and handling
- Normal message listening and routing
- Streamed response delivery
- Channel/guild context management

---

### 2. Session Orchestrator (`orchestrator/`)

**Purpose:** Session lifecycle, turn coordination, phase management, gameplay state

**Key Files:**
- `orchestrator/gameplay.py` - `GameplayOrchestrator`, `CharacterRegistry`
- `orchestrator/turn_runner.py` - `TurnRunner` for turn execution
- `orchestrator/turns.py` - `TurnCoordinator`
- `orchestrator/session_store.py` - `SessionStore`

**GameplayOrchestrator Responsibilities:**
- Adventure/模组 loading and scene management
- Combat encounter management (`CombatEncounter`)
- Investigator panel tracking (`InvestigatorPanel`)
- Character registry (user_id → CharacterRecord)
- Scene evaluation and trigger execution
- Roll resolution and consequence application

**TurnRunner Responsibilities:**
- Orchestrates router → rules → narrator pipeline
- Supports both streaming and async turn execution
- Formats scene output

---

### 3. Rules Engine (`rules/`)

**Purpose:** Deterministic rule resolution - dice, checks, combat, sanity, magic

**Entry Point:** `rules/engine.py` - `RulesEngine` class

**Action Types Supported:**
```python
RuleAction.action = Literal[
    "attack_roll",           # D&D-style attack
    "ability_check",         # D&D-style check
    "saving_throw",          # D&D-style save
    "damage_roll",          # D&D-style damage
    "raw_roll",             # Raw dice expression
    "coc_skill_check",      # COC percentile skill check
    "coc_sanity_check",     # COC SAN loss resolution
    "coc_fighting_attack",  # COC opposed fighting check
    "coc_shooting_attack",  # COC shooting check
    "coc_brawl_attack",     # COC brawl/unarmed check
    "coc_dodge",            # COC dodge (defensive)
    "coc_grapple_attack",   # COC grapple check
    "coc_cast_spell",       # COC spell casting
]
```

**Key Classes:**
- `RulesEngine` - Main executor, delegates to COC subsystems
- `D20DiceRoller` - D&D dice rolling (d20 + advantage)
- `SeededDiceRoller` - Deterministic seeded roller for tests
- `_LegacyDiceRoller` - Backward-compatible roller

**Dice Resolution (`dice.py`):**
- `PercentileOutcome` - COC-style: success/failure/critical/fumble
- Success ranks: `critical` (01), `extreme` (≤1/5), `hard` (≤1/2), `regular` (≤value), `failure`
- Fumble on 96-100

---

### 4. COC Rules Subsystem (`rules/coc/`)

**Purpose:** Complete COC7 rule implementation

**Public API (`rules/coc/__init__.py` exports 60+ items):**

**Skills Module (`skills.py`):**
- `COC_SKILLS` - 80+ skill definitions
- `SkillDefinition` - name, name_cn, category, base_points, occupational, interest, specialized, subtypes
- `SkillCategory` enum - COMBAT, LANGUAGE, KNOWLEDGE, INTERPERSONAL, OBSERVATION, PRACTICAL, CRAFT, MAGIC
- `resolve_skill_check()` - Percentile check with difficulty
- `get_skills_by_category()`, `is_specialized_skill()`, `expand_specialized_skill()`

**Combat Module (`combat.py`):**
- `CombatantStats` - dex, fighting, shooting, brawl, dodge, grapple, hp, armor, damage_bonus, build
- `CombatAction` enum - FIGHT, SHOOT, BRAWL, DODGE, GRAPPLE, THROW, RETREAT, GUARD, RELOAD
- `resolve_fighting_attack()` - Opposed check: attacker_roll vs defender_roll
- `resolve_shooting_attack()` - Range modifier, recoil modifier
- `resolve_brawl_attack()` - Unarmed combat
- `resolve_grapple_attack()` - Grappling
- `calculate_damage_bonus()` - DB from STR+SIZ
- `roll_initiative()` - DEX×2 + 1d100

**Sanity Module (`sanity.py`):**
- `SanityLossType` - UNKNOWN, SEEN, COMBAT, DEATH, MYTHOS
- `InsanityType` - NONE, TEMPORARY, INDEFINITE
- `COMMON_PHOBIAS`, `COMMON_MANIAS` - 30+ each
- `resolve_sanity_check()` - SAN loss with Mythos gain
- `roll_insanity_break()` - Acute response or phobia/mania acquisition
- `calculate_sanity_recovery()` - Rest, therapy, real-world gains
- `spend_luck_for_sanity()` - Luck expenditure to reduce loss

**Magic Module (`magic.py`):**
- `SpellSchool` - CONJURATION, DIVINATION, ENCHANTMENT, EVOCATION, NECROMANCY, TRANSMUTATION, GENERAL
- `SpellType` - SPELL, RITUAL, SUMMONING, BINDING, SUMMONING_BINDING
- `SpellDefinition` - name, school, type, casting_time, mp_cost, ingredients, prerequisite
- `COC_SPELLS` - 10+ built-in spells (Contact Ghoul, Elder Sign, etc.)
- `resolve_spell_cast()` - INT×2 + POW×2 threshold check
- `Spellbook`, `SpellbookEntry` - Character spellbook management

**Derived Attributes Module (`derived.py`):**
- `calculate_luck()` - POW × 5
- `calculate_hp()` - (CON + SIZ) / 10
- `calculate_mp()` - POW / 5
- `calculate_sanity()` - POW × 5
- `calculate_move_rate()` - STR/DEX/SIZ based with age modifiers
- `calculate_build()` - STR + SIZ → build rating
- `calculate_damage_bonus()` - Build → DB string/dice expression
- `apply_age_modifiers()` - MOV reduction for age 40+

**Experience Module (`experience.py`):**
- `roll_skill_improvement()` - 1d100 < skill → +1d10
- `calculate_new_session_skill_points()` - Occupational + Interest points
- `CREDIT_RATING_OCCUPATIONAL_POINTS` - Credit → occupational points
- `INT_INTEREST_POINTS` - INT → interest points
- `OCCUPATION_SKILL_SUGGESTIONS` - Suggested skills per occupation

---

### 5. Router Subsystem (`router/`)

**Purpose:** Message intent classification and routing

**Key Files:**
- `router/intent.py` - `MessageIntent` enum, `INTENT_PRIORITY_BY_PHASE`
- `router/intent_handler.py` - `IntentHandlerRegistry`
- `router/service.py` - `RouterService`
- `router/contracts.py` - `TurnPlan`

**MessageIntent Types:**
```python
MessageIntent = Literal[
    "ooc",           # Out of character discussion
    "social_ic",     # Social in-character
    "player_action", # Game action requiring resolution
    "rules_query",   # Game rules question
    "admin_action",  # Admin command
    "unknown",       # Unable to determine
]
```

**IntentHandlerRegistry:**
- Phase-dependent message handling
- Message buffering during `scene_round_resolving` and `combat`
- Priority-based processing

---

### 6. Model Layer (`models/`)

**Purpose:** Local LLM integration via Ollama

**Key Classes:**
- `OllamaClient` - OpenAI-compatible Ollama API client
- `RouterModel` - Fast model for intent classification (qwen3:1.7b)
- `NarratorModel` - Narrative model (qwen3:4b-instruct-2507-q4_K_M)

---

### 7. Narration Layer (`narration/`)

**Purpose:** Keeper narrative generation and formatting

**Key Files:**
- `narration/service.py` - `NarrationService`
- Prompt construction and response shaping

---

### 8. Persistence Layer (`persistence/`)

**Purpose:** SQLite-backed state storage

**Key Files:**
- `persistence/store.py` - `PersistenceStore`
- Event sourcing for session state
- Session recovery after restart

---

### 9. Testing Infrastructure (`testing/`)

**Purpose:** Scenario-based integration testing

**Key Files:**
- `testing/scenario_dsl.py` - `ScenarioMode`, `ScenarioParser`, `ScenarioRegistry`
- `testing/runtime_driver.py` - `RuntimeTestDriver`

**Scenario Modes:**
- `ACCEPTANCE` - Standard acceptance tests
- `CONTRACT` - Model contract tests with VCR cassettes
- `CHAOS` - Stress tests
- `RECOVERY` - Persistence recovery tests

**Model Modes:**
- `FAKE_CONTRACT` - StubModelClient (fast, deterministic)
- `RECORDED` - VCR cassette replay
- `LIVE` - Real Ollama API
- `API` - Arbitrary API endpoint

---

## Data Flow

### Turn Execution Flow:
```
Discord Message
    │
    ▼
IntentClassifier (Router) → MessageIntent
    │
    ▼
IntentHandlerRegistry (phase-aware routing)
    │
    ▼
TurnRunner.run_turn()
    ├── RouterService.narrate() → TurnPlan (tool calls)
    ├── GameplayOrchestrator.resolve_plan() → rule results
    └── NarrationService.narrate() → formatted reply
    │
    ▼
Discord Response (streamed or async)
```

### Rule Execution Flow:
```
RuleAction(action="coc_fighting_attack", ...)
    │
    ▼
RulesEngine.execute()
    │
    ▼
_build_combatant_stats() → CombatantStats
    │
    ▼
resolve_fighting_attack(actor_stats, target_stats, attacker_roll, defender_roll)
    │
    ▼
CombatCheckResult (success, damage, critical, fumble, status effects)
```

---

## Key Abstractions

### RuleAction Model (`rules/actions.py`)
```python
class RuleAction(BaseModel):
    action: Literal["coc_fighting_attack", "coc_skill_check", ...]
    actor: StatBlock  # name, armor_class, hit_points
    target: StatBlock | None
    parameters: dict[str, object]
```

### CharacterRecord Model (`characters/models.py`)
```python
class CharacterRecord(BaseModel):
    source: CharacterSourceInfo
    external_id: str
    name: str
    species: str
    abilities: AbilityScores  # D&D-style (STR, DEX, CON, INT, WIS, CHA)
    hp: HitPoints
    coc: COCInvestigatorProfile | None  # COC-specific data
```

### COCInvestigatorProfile (`characters/models.py`)
```python
class COCInvestigatorProfile(BaseModel):
    occupation: str
    age: int
    san: int
    hp: int
    mp: int
    luck: int
    build: int
    damage_bonus: str  # e.g., "+1d4"
    move_rate: int
    attributes: COCAttributes  # STR, CON, DEX, APP, POW, SIZ, INT, EDU
    skills: dict[str, int]  # skill_name → value
```

---

## Error Handling

**Strategy:** Exception-based with typed errors

- `RulesEngineError` - Base rule execution error
- `ScenarioValidationError` - Scenario DSL validation
- `ModelModeError` - Invalid model configuration

---

## Cross-Cutting Concerns

**Logging:** Via `logging.py` - structured logging
**Validation:** Pydantic v2 models throughout
**Type Safety:** No `as any`, `@ts-ignore` suppression

---

*Architecture analysis: 2026-03-31*
