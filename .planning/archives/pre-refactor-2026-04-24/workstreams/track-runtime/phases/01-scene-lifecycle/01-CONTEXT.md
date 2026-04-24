# Phase 1: Scene Lifecycle - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Define the canonical runtime model for scene lifecycle and player focus so later shared-scene batching work has structured state to build on.
</domain>

<decisions>
## Implementation Decisions

### Runtime Ownership
- The canonical scene lifecycle model lives in `track-runtime`, not in Discord renderers or message timing.
- Scene lifecycle state and player focus state are separate concepts and must not be collapsed into one field.
- This phase defines data models and transition rules first; it does not yet implement reveal gates or full trigger resumability.

### Compatibility Constraints
- Existing single-scene flows must continue to work while the new lifecycle model is introduced.
- New lifecycle state should be persistence-friendly and inspectable from session/runtime code.

### the agent's Discretion
- Exact class and file decomposition for the new lifecycle models.
- Whether transition helpers live in `session_store.py`, a new runtime-state module, or a narrowly scoped helper file.
</decisions>

<canonical_refs>
## Canonical References

### Planning Truth
- `.planning/workstreams/track-runtime/ROADMAP.md` — phase goal, dependencies, and requirement mapping
- `.planning/workstreams/track-runtime/REQUIREMENTS.md` — `RTR-01` and `RTR-02`
- `.planning/workstreams/track-runtime/STATE.md` — active milestone and phase position
- `AGENTS.md` — repository workflow and verification rules

### Existing Runtime Code
- `src/dm_bot/orchestrator/session_store.py` — current session state and phase handling
- `src/dm_bot/orchestrator/gameplay.py` — gameplay-side adventure/session state usage
- `src/dm_bot/orchestrator/turns.py` — current serialized turn model
- `src/dm_bot/gameplay/modes.py` — gameplay mode semantics
</canonical_refs>

<specifics>
## Specific Ideas

- Introduce explicit `WorldState` / `SceneState` style models instead of continuing with ad hoc dict growth.
- Keep room for future multi-scene support without requiring it to be fully active in this phase.
</specifics>

<deferred>
## Deferred Ideas

- Merge policy and KP-confirmation flow belong to later phases.
- Reveal-gate and knowledge ownership belong to `v1.2`.
</deferred>
