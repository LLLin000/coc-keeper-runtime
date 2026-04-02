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

The codebase already has:

- Discord-native runtime commands and message routing
- structured COC module support
- persistent investigator archives and campaign projections
- scenario-driven verification infrastructure
- local runtime control and smoke-check flows

The new planning cycle starts from a cleaner workstream boundary, not from a greenfield product state.

## Next Step

The recommended first milestone in the new cycle is under `track-runtime`: stabilize shared scene batching and consequence ownership before introducing new presentation-heavy milestones.

---
*Last updated: 2026-04-02 after planning reset baseline creation*
