# Codebase Architecture: Discord COC Keeper

This document maps the major modules and data flows of the Discord COC Keeper bot to support test coverage planning and system understanding.

## Module Overview

| Module | Responsibility | Key Files |
| :--- | :--- | :--- |
| **Discord Bot** | `discord.py` integration, slash commands, message listening, streaming output. | `client.py`, `commands.py`, `streaming.py` |
| **Orchestrator** | Coordinates the turn pipeline, manages session state, and connects all layers. | `turn_runner.py`, `session_store.py`, `gameplay.py` |
| **Router** | Classifies intent and generates a structured `TurnPlan` using a fast model. | `service.py`, `intent_classifier.py`, `contracts.py` |
| **Adventure** | Manages structured module data, rooms/scenes, and trigger/consequence logic. | `loader.py`, `trigger_engine.py`, `models.py` |
| **Rules** | Deterministic resolution of COC checks, dice rolls, and SAN mechanics. | `engine.py`, `dice.py`, `actions.py` |
| **COC** | Character creation (builder), investigator panels, and archive management. | `builder.py`, `panels.py`, `archive.py` |
| **Narration** | Transforms structured turn results into flavorful Keeper prose using a larger model. | `service.py` |
| **Persistence** | SQLite-backed storage for campaign state, sessions, and investigator profiles. | `store.py` |
| **Models** | Ollama client and shared Pydantic schemas for model I/O. | `ollama_client.py`, `schemas.py` |
| **Runtime** | App startup, health checks, control plane, and smoke-test utilities. | `main.py`, `app.py`, `smoke_check.py` |

## Key Class Dependencies

- **`DiscordDmBot`** (discord_bot/client.py) delegates to **`Handlers`** (orchestrator layer).
- **`TurnRunner`** (orchestrator/turn_runner.py) depends on:
    - `RouterService` (router/service.py)
    - `NarrationService` (narration/service.py)
    - `GameplayOrchestrator` (orchestrator/gameplay.py)
- **`GameplayOrchestrator`** depends on:
    - `RulesEngine` (rules/engine.py)
    - `AdventureRuntime` (adventure layer)
- **`SessionStore`** (orchestrator/session_store.py) is the in-memory state manager for active campaigns.
- **`PersistenceStore`** (persistence/store.py) handles the actual disk I/O for `SessionStore`.

## Data Flow: Message to Response

1. **Discord Event**: `DiscordDmBot.on_message` captures a message and calls `handle_channel_message_stream`.
2. **Normalization**: The message is wrapped in a `TurnEnvelope` (trace_id, campaign_id, user_id, content).
3. **Intent Classification**: `IntentClassifier` (optional) determines if it's a rule check or narrative action.
4. **Routing**: `RouterService` calls the Router model to get a `TurnPlan` (mode, tool_calls, narration_brief).
5. **Gameplay Resolution**: `GameplayOrchestrator` processes `tool_calls`:
    - `RulesEngine` executes rolls (e.g., `coc_skill_check`).
    - `TriggerEngine` (Adventure layer) evaluates consequences of actions or rolls.
6. **Persistence**: Updated campaign state and session metadata are saved via `PersistenceStore`.
7. **Narration**: `NarrationService` receives the `TurnPlan` + `tool_results` + `state_snapshot` and calls the Narrator model.
8. **Delivery**: `StreamingTransport` (discord_bot/streaming.py) sends/edits the Discord message in chunks.

## Session Store & Connectivity

The `SessionStore` is the central "hub" for active state:
- **Campaign Binding**: Links a Discord Channel ID to a `CampaignSession`.
- **Membership**: Tracks which users are in which campaign and their active character names.
- **Phases**: Tracks the `SessionPhase` (LOBBY, SCENE_ROUND_OPEN, COMBAT, etc.).
- **Connectivity**:
    - **Persistence**: Loaded at startup and saved after every state-changing command/turn.
    - **Orchestrator**: Provides context (phase, ready status) to the Router and Narrator.
    - **Commands**: Slash commands (`/join`, `/ready`) update `SessionStore` directly.

## Key File Map (src/dm_bot/)

| Path | Description |
| :--- | :--- |
| `main.py` | Entry point for `run-bot`, `smoke-check`, and `restart-system`. |
| `config.py` | Pydantic settings for Discord tokens, Ollama URLs, and model names. |
| `orchestrator/turn_runner.py` | The core "brain" of the turn pipeline. |
| `orchestrator/session_store.py` | In-memory management of campaign sessions and members. |
| `router/service.py` | Interface for structural decision-making (Router model). |
| `narration/service.py` | Interface for prose generation (Narrator model). |
| `rules/engine.py` | Orchestrates dice rolls and COC rule applications. |
| `adventures/trigger_engine.py` | Evaluates effects/consequences based on adventure data. |
| `persistence/store.py` | SQLite implementation for state durability. |
| `discord_bot/client.py` | Subclass of `commands.Bot` with command registrations. |
| `coc/builder.py` | Logic for conversational character creation. |
| `runtime/smoke_check.py` | End-to-end validation of the model and state pipeline. |
