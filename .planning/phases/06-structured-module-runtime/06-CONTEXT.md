# Phase 6: Structured Module Runtime - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Mode:** Auto-generated for autonomous execution

<domain>
## Phase Boundary

This phase establishes a reusable structured adventure runtime that can validate formal module packages, initialize canonical module state, export public-vs-hidden module context for narration, and fail closed when package data is incomplete.

</domain>

<decisions>
## Implementation Decisions

### Adventure Schema
- Replace the current starter-only schema with a richer but still compact JSON package format.
- Encode start scene, scene summaries, reveal policy, canonical state fields, triggers, and endings in package data rather than prompt prose.
- Keep the schema generic enough for future modules, but only as rich as needed to support `疯狂之馆` next.

### Runtime Ownership
- Canonical module state remains owned by code, not by the narrator.
- The narrator can receive omniscient module data, but public/revealed context must be separately marked so the prompt can enforce reveal boundaries.
- Invalid packages should fail closed during load or validation, not degrade to unstructured play.

### Integration
- Extend the existing `adventures` package and `GameplayOrchestrator` rather than creating a parallel module runtime.
- Preserve compatibility with current persistence/export-import flow so later phases can make session continuity durable.

### the agent's Discretion
- Exact trigger representation and state field typing can stay lightweight as long as the schema clearly distinguishes canonical state from narrated visibility.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/dm_bot/adventures/models.py` and `loader.py` already define the basic package/load seam.
- `src/dm_bot/orchestrator/gameplay.py` already holds `adventure` and `adventure_state`.
- `src/dm_bot/persistence/store.py` already persists arbitrary campaign state JSON.
- `src/dm_bot/narration/service.py` already accepts structured `state_snapshot`.

### Established Patterns
- Pydantic models define runtime contracts.
- Gameplay state is kept in orchestrator and serialized via `export_state`/`import_state`.
- Loader/runtime code is small and direct; new abstractions should remain focused.

### Integration Points
- Adventure schema changes start in `src/dm_bot/adventures/models.py`.
- Load/validate path stays in `src/dm_bot/adventures/loader.py`.
- Canonical module state initialization and snapshotting belong in `src/dm_bot/orchestrator/gameplay.py`.
- Narration context shaping extends `src/dm_bot/narration/service.py` and `src/dm_bot/orchestrator/turn_runner.py`.

</code_context>

<specifics>
## Specific Ideas

- Keep room/scene modeling explicit so `疯狂之馆` can later represent the hall and four branch wings directly.
- Build a clear “gm view vs player-visible view” split now, because that is the core hidden-information requirement for the next phase.

</specifics>

<deferred>
## Deferred Ideas

- Per-player private reveal channels or whisper-only state remain deferred to a later milestone.
- Rich puzzle scripting macros and live GM editing are deferred.

</deferred>
