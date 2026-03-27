<!-- GSD:project-start source:PROJECT.md -->
## Project

**Discord AI DM**

This project is a Discord-native Dungeons & Dragons DM system powered by local models. Multiple real players can participate in the same session, the bot acts as the DM, and the system can switch between normal DM-led play and multi-character performance scenes where the bot speaks as several NPCs or enemies.

The target is not a lightweight chat toy. It should be reliable enough to run short-to-medium campaigns with strong rules support, persistent state, and external character data connected through the simplest viable integration path.

**Core Value:** Run a real multiplayer D&D session in Discord where a local AI DM can narrate, roleplay multiple characters, and enforce heavy rules flow without constant manual bookkeeping.

### Constraints

- **Platform**: Discord-first — the system must work naturally in Discord channels or threads because that is the chosen runtime surface.
- **Inference**: Local models — narration and control should run through local model infrastructure rather than a hosted LLM dependency.
- **Target Hardware**: Consumer local machine — the default stack should remain practical on `8GB`-class consumer GPUs with `32GB` system RAM.
- **Architecture**: Reuse mature projects first — stable existing tools, APIs, and datasets should be integrated before writing custom subsystems.
- **Rules Scope**: Heavy rules support in v1 — combat, initiative, HP, conditions, spells, and resource tracking are not optional side features.
- **Delivery**: First release should optimize for campaign-usable reliability over maximal scope — reducing integration and debugging cost is a priority.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core runtime
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.12+ | Main runtime | Lowest integration friction across Discord, local AI serving, Postgres, and automation code. |
| `uv` | current | Package/env management | Fast, simple Python workflow with less dependency pain than ad hoc `pip` usage. |
| FastAPI | current stable | Local control API, health checks, admin endpoints, webhooks | Keeps the bot process observable and debuggable without building custom HTTP plumbing. |
| `pydantic` + `pydantic-settings` | v2 line | Typed config and structured LLM I/O | Important for dual-model orchestration and tool payload validation. |
| `httpx` | current stable | Calls to model server and external services | Solid async HTTP client; standard choice in modern Python services. |
### Discord bot framework
### Model serving
- OpenAI-compatible API means you can treat both models the same way.
- It is operationally simpler than running your own `llama.cpp` process management.
- It is much easier to get working on a single local box than a vLLM deployment.
- Dual-model orchestration becomes a normal “call fast controller model, then call narration model” pattern instead of a serving problem.
### Orchestration layer
- `openai` Python SDK against Ollama’s OpenAI-compatible endpoint
- `pydantic` models for router outputs, action plans, and tool arguments
- a small in-process planner/executor module
### Rules, skills, and data sources to reuse
| Source | Use | Recommendation |
|--------|-----|----------------|
| `5e-srd-api` / 5e Bits data | SRD monsters, spells, classes, conditions, equipment, rules lookup | **Use as the primary rules data backbone.** Mature, public, structured, and good enough for v1 heavy-rules support. |
| Avrae product/docs | Reference for Discord UX, initiative flow, automation shape, and character import patterns | **Use as a design reference, not as an embedded runtime dependency.** |
| Avrae-style imports | Character ingestion from D&D Beyond, Dicecloud, or Google Sheet style sources | **Use import adapters, not live bidirectional sync, in v1.** |
| `DND5E-MCP` | MCP-facing rules helper | **Do not make this a core dependency yet.** It appears too new and too unproven to anchor the stack. Low-confidence note based on public repo metadata. |
### Persistence and storage
- `SQLAlchemy` 2.0.x
- `Alembic`
- `asyncpg`
- campaign metadata in normalized tables
- turn/combat state in normalized tables
- session transcript chunks and world-state snapshots in `JSONB`
- tool results and event history as append-only records
## What To Avoid Building From Scratch
- A custom Discord command/router framework
- A custom model-serving layer
- A full D&D rules compendium/database
- A full dice parser and combat automation engine from first principles
- A live-sync character platform
- A multi-service queue/cache topology before real load exists
## Top 5 Stack Decisions
## Practical Package Set
## Bottom-Line Recommendation
- `discord.py` for Discord
- Ollama for both local models
- `openai` SDK + typed Pydantic contracts for orchestration
- PostgreSQL + SQLAlchemy for persistent campaign state
- `5e-srd-api` data as the default rules source
- Avrae as a product-pattern reference, not a runtime dependency
## Sources
- discord.py docs: https://discordpy.readthedocs.io/en/stable/
- Ollama OpenAI compatibility: https://docs.ollama.com/api/openai-compatibility
- vLLM OpenAI-compatible server: https://docs.vllm.ai/en/stable/serving/openai_compatible_server.html
- D&D 5e SRD API docs: https://5e-bits.github.io/docs/
- Avrae site: https://avrae.io/
- Avrae docs: https://avrae.readthedocs.io/en/latest/
- SQLAlchemy 2.0 docs: https://docs.sqlalchemy.org/en/20/intro.html
- PostgreSQL overview: https://www.postgresql.org/about/
- DND5E-MCP repo: https://github.com/njseeber1/DND5E-MCP
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
