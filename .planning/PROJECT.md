# Discord AI Keeper

## What This Is

This project is a Discord-native, local-model-first Call of Cthulhu Keeper runtime. It is not a chat toy and it is not a pure prompt stack. The system aims to run real multiplayer COC sessions in Discord with structured runtime state, durable character identity, deterministic rules resolution, and AI narration that stays subordinate to canonical state.

## Core Value

Run campaign-usable multiplayer Call of Cthulhu sessions in Discord with local models, structured runtime truth, durable investigator identity, and operator-grade verification.

## Planning Reset

The planning tree was reset on 2026-04-02 after the previous 5-track structure started to accumulate overlapping ownership and execution drift.

The previous planning cycle was archived to:

- `.planning/archives/pre-reset-2026-04-02/`

That archive keeps the historical milestones, workstreams, quick tasks, and legacy planning artifacts from the old cycle.

## New Track Model

All new work must belong to exactly one primary workstream. Cross-track effects are allowed, but canonical ownership must remain singular.

### `track-runtime`

Owns canonical gameplay truth:

- session lifecycle
- gameplay orchestration
- module runtime and trigger/consequence flow
- multiplayer shared-state resolution
- rules-to-module integration

Use this track when the work changes what is legally true in play.

### `track-identity`

Owns durable player/investigator truth:

- archive schema
- conversational builder
- profile lifecycle
- campaign projection
- identity governance and admin authority

Use this track when the work changes who a player is across sessions.

### `track-surface`

Owns the player/operator interaction layer:

- Discord commands
- channel discipline
- DM/ephemeral/public interaction patterns
- presentation contracts and readable boards/cards
- keeper-feel output and UX guidance

Use this track when the work changes how users or operators experience the system.

### `track-ops`

Owns runtime reliability and delivery proof:

- scenario runner
- smoke-check and preflight
- control panel and restart/recovery flows
- diagnostics and operator tooling
- cross-track delivery gates

Use this track when the work changes how the system is verified, operated, recovered, or diagnosed.

## Global Rules

1. Every milestone must declare one primary workstream.
2. Cross-track effects must be documented, but canonical ownership must remain singular.
3. Rules truth, state truth, and identity truth cannot exist only in model context.
4. Critical state changes must be durable and auditable.
5. Delivery claims must pass:
   - `uv run pytest -q`
   - `uv run python -m dm_bot.main smoke-check`
6. New features should prefer reusable runtime primitives over module-specific patches.
7. Planning docs must remain understandable to a fresh GSD agent from repository context alone.

## Current State

**v1.0 Shared Scene Batch Resolution — SHIPPED**

The codebase now has canonical scene lifecycle management with explicit state machine transitions, fork/switch focus operations with max-2-open-scenes enforcement, and batch collection with deterministic resolution ordering and visibility-tagged consequences.

Shipped v1.0 includes:
- Explicit SceneLifecycle enum with COLLECTING/LOCKED/RESOLVING/PUBLISHED states
- PlayerFocusScope enum decoupled from scene lifecycle
- fork() and switch_focus() runtime operations
- Cross-cut signal emission (not narration)
- ActionBatchEntry with visibility tagging
- Deterministic resolution (DEX desc, user_id asc tiebreaker)
- Merge proposal flow with consequence exposure
- Runtime blocker state via compute_blocker_state()

## Requirements

### Validated

- [x] RTR-01 Batch State Machine — v1.0
- [x] RTR-02 Submission Ownership — v1.0
- [x] RTR-03 Deterministic Resolution Order — v1.0
- [x] RTR-04 Consequence Ownership — v1.0
- [x] RTR-05 Runtime Blocker Truth — v1.0

### Active

- [ ] RTR-06 Event Entry Contract — v1.1
- [ ] RTR-07 Resumable Trigger Execution — v1.1
- [ ] RTR-08 Auditable Mutation Order — v1.1
- [ ] RTR-09 Blocker Persistence — v1.1
- [ ] RTR-10 Reveal Gate Contract — v1.2
- [ ] RTR-11 Knowledge Ownership — v1.2
- [ ] RTR-12 Reveal Transition Events — v1.2
- [ ] RTR-13 Surface Consumption Boundary — v1.2
- [ ] RTR-14 Compatibility Contract — v1.3
- [ ] RTR-15 Recovery Integrity — v1.3
- [ ] RTR-16 Placeholder Removal — v1.3
- [ ] RTR-17 Regression Gate Coverage — v1.3

### Out of Scope

- Video/audio integration — use external tools
- Module authoring tools — future track-identity work
- Public deployment infrastructure — operator-controlled only

## Key Decisions

| Decision | Rationale | Status |
| -------- | --------- | ------ |
| SceneLifecycle separated from player focus (RTR-01) | Enables independent state transitions and focus tracking | ✓ Validated |
| fork() does NOT auto-switch focus | Decoupled creation from assignment; owner decides | ✓ Validated |
| Max 2 OPEN scenes per player | Prevents combinatorial explosion; enforced in switch_focus() | ✓ Validated |
| Cross-cut is a signal, not narration | Phase 2 emits signal only; narration comes from surface layer | ✓ Validated |
| Batch collection uses hybrid model (explicit scene_id + fallback) | Flexible for cross-scene and single-scene submissions | ✓ Validated |
| Resolution order: DEX desc, user_id asc tiebreaker | Deterministic without requiring full topological sort | ✓ Validated |
| Merge proposal auto-triggered after both scenes RESOLVED | Keeps focus scene semantics intact | ✓ Validated |
| Focused scene bears consequences; others record potential impact | Clear ownership without double-applied effects | ✓ Validated |

## Context

- Tech stack: Python, Pydantic v2, SQLAlchemy 2.0, Discord.py
- Models: qwen3:1.7b (router), qwen3:4b-instruct-2507-q4_K_M (narrator)
- Hardware target: 8GB-class GPU, 32GB RAM consumer machine
- Delivery gate: `uv run pytest -q` + `uv run python -m dm_bot.main smoke-check`

---
*Last updated: 2026-04-24 after v1.0 milestone*