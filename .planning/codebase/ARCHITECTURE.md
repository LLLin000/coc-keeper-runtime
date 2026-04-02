# ARCHITECTURE.md

## System Architecture

### Layer Diagram

```
Discord Users
    │
    ▼
┌───────────────────────────────────────────────────────────────┐
│  Discord Bot Layer (discord_bot/)                            │
│  - Slash commands / normal messages / streaming               │
│  - 40+ app commands registered via @tree.command              │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│  Session Orchestrator (orchestrator/)                        │
│  - Campaign binding / channel roles / turn coordination       │
│  - TurnRunner / TurnCoordinator / SessionStore               │
│  - Message filters / visibility dispatcher                    │
└───────┬─────────────┬─────────────┬─────────────┬─────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌───────────────┐ ┌─────────┐ ┌────────────┐ ┌──────────────────┐
│ Adventure     │ │ Rules   │ │ Character  │ │ Model Layer      │
│ Runtime       │ │ Engine  │ │ Layer      │ │                   │
│ (adventures/) │ │ (rules/)| │ (coc/)     │ │ (router/)        │
│               │ │         │ │            │ │ (models/)        │
│ - room graph  │ │ - dice  │ │ - archive  │ │ (narration/)     │
│ - scene graph │ │ - COC   │ │ - builder  │ │                   │
│ - trigger     │ │ - SAN   │ │ - panels   │ │ OllamaClient     │
│ - consequence │ │ - skills│ │            │ │ Router + Narrator │
└───────────────┘ └─────────┘ └────────────┘ └──────────────────┘
        │             │             │             │
        └──────────────┴─────────────┴─────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│  Persistence Layer (persistence/)                             │
│  - SQLite-backed state store                                  │
│  - Archive profiles, sessions, event logs                     │
└───────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

1. **State Truth Not in Model**
   - AI narrates but canonical truth lives in structured state
   - Rules engine (`rules/`) is deterministic
   - Model outputs are interpretative, not authoritative

2. **Dual-Model Pattern**
   - **Router** (`qwen3:1.7b`): Fast intent classification, turn routing
   - **Narrator** (`qwen3:4b+`): Rich streaming narration

3. **Adventure as Data, Not Prompt**
   - Modules have structured graphs (room/scene/event)
   - Trigger trees drive consequences
   - Reveal policies gate information

4. **Character Separation**
   - **Long-term Archive**: Player's persistent investigator profiles
   - **Campaign Instance**: In-module SAN, secrets, temporary state
   - `InvestigatorArchiveRepository` manages archive
   - `CharacterRegistry` manages campaign instances

5. **SQLite for Local Persistence**
   - Single file, no external DB dependency
   - Suitable for consumer hardware (8GB VRAM + 32GB RAM)

### Data Flow

```
Player Message → Discord Client → TurnCoordinator
    → RouterService (intent classification)
    → RulesEngine (deterministic resolution)
    → AdventureRuntime (trigger/consequence)
    → PersistenceStore (state + event log)
    → NarrationService (streaming output)
    → Discord Client (stream to user)
```

### Module Boundaries

| Module | Responsibility | Key Classes |
|--------|----------------|--------------|
| `discord_bot/` | Discord API, commands, streaming | `DiscordDmBot`, `BotCommands` |
| `orchestrator/` | Session lifecycle, turns, coordination | `GameplayOrchestrator`, `TurnCoordinator` |
| `adventures/` | Module runtime, graphs, triggers | `AdventureLoader`, `TriggerEngine` |
| `rules/` | COC dice, checks, SAN, skills | `RulesEngine`, `CocChecker` |
| `coc/` | Character archive, builder, panels | `InvestigatorArchiveRepository`, `ConversationalCharacterBuilder` |
| `router/` | Intent classification | `IntentClassifier`, `RouterService` |
| `models/` | Ollama client | `OllamaClient` |
| `narration/` | Narrator service | `NarrationService` |
| `persistence/` | SQLite store | `PersistenceStore` |
| `runtime/` | App lifecycle, health, control | `RuntimeControlService`, `smoke_check` |
| `diagnostics/` | Runtime summaries | `DiagnosticsService` |
| `gameplay/` | Combat, scene presentation | `Combat`, `scene_formatter` |
