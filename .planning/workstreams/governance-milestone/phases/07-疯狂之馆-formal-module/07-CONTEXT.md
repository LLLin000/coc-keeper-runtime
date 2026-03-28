# Phase 7: 疯狂之馆 Formal Module - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Mode:** Auto-generated for autonomous execution

<domain>
## Phase Boundary

This phase encodes `疯狂之馆` as the first full formal module using the Phase 6 schema and thin runtime helpers for scene progression, clue discovery, special module-state updates, and ending selection.

</domain>

<decisions>
## Implementation Decisions

### Module Scope
- Represent the hall and the four branch wings explicitly as scenes.
- Encode the module's countdown pressure, blood accumulation, sensory loss, saint-state logic, and branching endings as canonical module state.
- Keep the first pass deterministic and data-driven rather than trying to build a complex generic script engine.

### Runtime Support
- Add only thin gameplay helpers needed to move between scenes, record discoveries, update counters, and select endings.
- Preserve the “omniscient DM but gated reveal” contract from Phase 6.

### Story Data
- Use a stable ASCII adventure id for runtime loading, even though the human-facing title remains `疯狂之馆`.
- Preserve the module's hidden-information flavor in the data package so later private-reveal support can build on it.

### the agent's Discretion
- Exact decomposition of clue ids and trigger labels can be pragmatic as long as the package clearly represents branch progression and major consequences.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 6 already added formal `AdventurePackage`, canonical state defaults, and adventure snapshots.
- Existing `load_adventure` command can already load packaged adventures by slug.

### Established Patterns
- Tests define runtime seams first.
- Gameplay state mutations stay in `GameplayOrchestrator`.
- JSON packages under `src/dm_bot/adventures/` are the current module source of truth.

### Integration Points
- `src/dm_bot/adventures/` will hold the `疯狂之馆` package.
- `src/dm_bot/orchestrator/gameplay.py` will grow thin helpers for scene/clue/state progression.
- Existing tests in `tests/test_adventure_loader.py` and `tests/test_gameplay_integration.py` will expand to cover the formal module.

</code_context>

<specifics>
## Specific Ideas

- The package should make the hall the hub scene and model the four colored halls as explicit exits.
- Hidden mechanics like blood progress and saint-state should be first-class state keys, not comments in prose.

</specifics>

<deferred>
## Deferred Ideas

- Per-player secret reveal delivery remains deferred.
- Rich conditional expression parsing for triggers is deferred; this phase can use simple labels and explicit helpers.

</deferred>
