# Phase 1: Discord Runtime & Dual-Model Control - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the defaults selected in auto mode.

**Date:** 2026-03-27
**Phase:** 01-discord-runtime-dual-model-control
**Areas discussed:** Discord session surface, interaction timing, dual-model orchestration, runtime shape

---

## Discord session surface

| Option | Description | Selected |
|--------|-------------|----------|
| Structured command-first | Slash commands and structured interactions are the canonical entry surface for session control | ✓ |
| Freeform message-first | Channel message parsing is the primary control surface from day one | |
| Hybrid from day one | Both are equal authorities in v1 | |

**Auto choice:** Structured command-first
**Notes:** Recommended default because Discord permissions, timing, and state safety are easier to control with explicit interactions.

---

## Interaction timing

| Option | Description | Selected |
|--------|-------------|----------|
| Async defer/follow-up | Acknowledge quickly, complete longer work through follow-up responses | ✓ |
| Synchronous replies | Try to finish model and tool work inside the initial interaction window | |
| Mixed strategy | Let each command choose ad hoc | |

**Auto choice:** Async defer/follow-up
**Notes:** Recommended default because Discord's interaction timing constraints make local inference unreliable without asynchronous handling.

---

## Turn authority

| Option | Description | Selected |
|--------|-------------|----------|
| Campaign-scoped serialization | One authoritative turn pipeline per campaign/thread | ✓ |
| Best-effort concurrent handling | Allow overlapping player actions and resolve conflicts later | |
| In-memory lock only | Use simple process-local locking without a formal campaign turn contract | |

**Auto choice:** Campaign-scoped serialization
**Notes:** Recommended default because later rules and persistence phases depend on single-writer state ownership.

---

## Dual-model orchestration

| Option | Description | Selected |
|--------|-------------|----------|
| Split router and narrator | `qwen3:1.7b` routes, `collective-v0.1-chinese-roleplay-8b` narrates | ✓ |
| Single-model orchestration | Let the narrator also decide tools and state intents | |
| Router-optional hybrid | Prefer narrator first and fall back to router only when needed | |

**Auto choice:** Split router and narrator
**Notes:** Recommended default because the project already fixed this boundary for reliability and local hardware fit.

---

## Runtime shape

| Option | Description | Selected |
|--------|-------------|----------|
| Single Python service with modular boundaries | One deployable runtime with isolated internal modules | ✓ |
| Multi-service split | Separate Discord, router, narrator, and orchestration services immediately | |
| Bot-only process | Put everything directly inside Discord handlers | |

**Auto choice:** Single Python service with modular boundaries
**Notes:** Recommended default because v1 prioritizes speed and low debugging cost over distributed-system flexibility.

---

## the agent's Discretion

- Exact command naming and internal package structure
- Exact follow-up message formatting after deferred Discord responses

## Deferred Ideas

- Character import provider choice belongs to Phase 2
- Combat and scene orchestration specifics belong to Phase 3
- Rich diagnostics and replay tooling belong to Phase 4
