# Technology Stack

**Project:** Discord AI DM
**Dimension:** Stack
**Researched:** 2026-03-27
**Overall confidence:** MEDIUM-HIGH

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

**Use `discord.py` 2.7.x.**

This is the practical choice for lowest debugging cost. Its docs are current, the library is actively maintained, it supports app commands/interactions, and it already handles Discord rate limits and async workflow well. Do not optimize for novelty here.

Avoid building on smaller Discord wrappers unless the repo already standardizes on them. For this project, the ecosystem advantage is not worth the migration/debugging tax.

### Model serving

**Use Ollama as the default local model server.**

Why:
- OpenAI-compatible API means you can treat both models the same way.
- It is operationally simpler than running your own `llama.cpp` process management.
- It is much easier to get working on a single local box than a vLLM deployment.
- Dual-model orchestration becomes a normal “call fast controller model, then call narration model” pattern instead of a serving problem.

**Fallback/scale-up path:** move to `vLLM` only if concurrency or throughput becomes the bottleneck and you are willing to pay the ops complexity cost. vLLM is stronger for high-throughput serving, but it is not the lowest-debugging-cost default for v1.

### Orchestration layer

**Keep orchestration thin.**

Use:
- `openai` Python SDK against Ollama’s OpenAI-compatible endpoint
- `pydantic` models for router outputs, action plans, and tool arguments
- a small in-process planner/executor module

Do **not** start with a heavy agent framework graph unless the simple controller/narrator split proves insufficient. For this project, the main risk is bad state management, not lack of framework abstraction.

### Rules, skills, and data sources to reuse

| Source | Use | Recommendation |
|--------|-----|----------------|
| `5e-srd-api` / 5e Bits data | SRD monsters, spells, classes, conditions, equipment, rules lookup | **Use as the primary rules data backbone.** Mature, public, structured, and good enough for v1 heavy-rules support. |
| Avrae product/docs | Reference for Discord UX, initiative flow, automation shape, and character import patterns | **Use as a design reference, not as an embedded runtime dependency.** |
| Avrae-style imports | Character ingestion from D&D Beyond, Dicecloud, or Google Sheet style sources | **Use import adapters, not live bidirectional sync, in v1.** |
| `DND5E-MCP` | MCP-facing rules helper | **Do not make this a core dependency yet.** It appears too new and too unproven to anchor the stack. Low-confidence note based on public repo metadata. |

### Persistence and storage

**Use PostgreSQL 16/17 as the system of record.**

Back it with:
- `SQLAlchemy` 2.0.x
- `Alembic`
- `asyncpg`

Store:
- campaign metadata in normalized tables
- turn/combat state in normalized tables
- session transcript chunks and world-state snapshots in `JSONB`
- tool results and event history as append-only records

This hybrid relational + `JSONB` approach is the practical sweet spot. It gives you reliable queries and migrations without forcing you to fully normalize every piece of narrative state on day one.

**Do not add Redis initially.** Start without a cache/queue tier. Add it only if you have a measured need for job buffering, rate smoothing, or transient locks.

## What To Avoid Building From Scratch

- A custom Discord command/router framework
- A custom model-serving layer
- A full D&D rules compendium/database
- A full dice parser and combat automation engine from first principles
- A live-sync character platform
- A multi-service queue/cache topology before real load exists

## Top 5 Stack Decisions

1. **Python over Node/TypeScript**
   Python gives the cleanest path across Discord, local AI, validation, and database work. This is the least-friction full-stack choice for a local-model game system.

2. **`discord.py` over alternative wrappers**
   The maintenance history, docs quality, and interaction support make it the safest Discord foundation.

3. **Ollama first, vLLM later if needed**
   Ollama minimizes setup and integration cost. vLLM is a scale-up option, not the default.

4. **PostgreSQL as the only required datastore**
   Campaigns, combat, and recovery state need durability and queryability. Postgres plus `JSONB` covers this without introducing extra moving parts.

5. **Reuse SRD data and Avrae patterns instead of inventing a D&D engine**
   The fastest route to a campaign-usable v1 is to assemble mature D&D data and proven bot interaction patterns, not to re-author the tabletop stack.

## Practical Package Set

```bash
uv add discord.py fastapi uvicorn openai pydantic pydantic-settings httpx \
  sqlalchemy alembic asyncpg orjson tenacity structlog
```

Optional later:

```bash
uv add redis arq
```

## Bottom-Line Recommendation

Build v1 as a single Python service:
- `discord.py` for Discord
- Ollama for both local models
- `openai` SDK + typed Pydantic contracts for orchestration
- PostgreSQL + SQLAlchemy for persistent campaign state
- `5e-srd-api` data as the default rules source
- Avrae as a product-pattern reference, not a runtime dependency

That is the most practical stack for a Discord-native local-AI DM with dual-model orchestration and heavy rules support while keeping debugging cost low.

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
