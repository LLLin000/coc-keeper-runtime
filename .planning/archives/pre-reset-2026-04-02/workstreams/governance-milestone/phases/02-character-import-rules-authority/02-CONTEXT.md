# Phase 2: Character Import & Rules Authority - Context

**Gathered:** 2026-03-27 (auto mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Add one low-friction external character import path and a deterministic 2014 SRD rules backbone that becomes the canonical authority for state-changing mechanics. This phase should reuse mature external projects for open data and import patterns, but keep canonical game state and mechanical resolution inside the local runtime.

</domain>

<decisions>
## Implementation Decisions

### Character import
- **D-01:** Phase 2 will support exactly one primary v1 character path and label it clearly as a snapshot import unless live sync proves straightforward.
- **D-02:** The import path should favor the lowest debugging cost mature source pattern rather than broad platform coverage.
- **D-03:** Imported sheets must normalize into one local gameplay model used by checks, attacks, saves, spells, HP, resources, and combat state.

### Rules authority
- **D-04:** The v1 rules baseline stays `2014 SRD only`.
- **D-05:** Open structured SRD data should come from `5e-srd-api` or a mirrored equivalent rather than bespoke scraped content.
- **D-06:** The rules layer is authoritative for state changes; models can request actions but cannot apply them directly.
- **D-07:** Invalid or incomplete model actions must fail closed and surface an explicit orchestration error rather than mutating state heuristically.

### Integration boundaries
- **D-08:** Avrae remains a UX/reference source only; its import and combat patterns may inform the design, but the runtime must not depend on Avrae as its core engine.
- **D-09:** Character import and rules lookup should be implemented behind adapters so later source changes do not leak into Discord handlers or narration code.
- **D-10:** Phase 2 should keep persistence lightweight where possible, but it may introduce the first normalized local gameplay models needed by Phase 3 combat.

### the agent's Discretion
- Exact v1 primary character source, provided it is clearly simpler than multi-source support
- Internal structure of the rules adapter and normalized character models
- Whether compendium access is remote-first with local caching or vendored fixtures for tests

</decisions>

<canonical_refs>
## Canonical References

### Project scope and requirements
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md` — `CHAR-01..04`, `RULE-01`, `RULE-04`, `RULE-05`, `RULE-06`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`

### Research guidance
- `.planning/research/FEATURES.md`
- `.planning/research/STACK.md`
- `.planning/research/ARCHITECTURE.md`
- `.planning/research/PITFALLS.md`

### Upstream phase outputs
- `.planning/phases/01-discord-runtime-dual-model-control/01-02-SUMMARY.md`
- `.planning/phases/01-discord-runtime-dual-model-control/01-03-SUMMARY.md`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/dm_bot/discord_bot/commands.py` already provides setup, bind, join, and turn entry points.
- `src/dm_bot/orchestrator/turns.py` already serializes campaign-scoped turns and delegates into `TurnRunner`.
- `src/dm_bot/router/` and `src/dm_bot/narration/` already enforce the model boundary for structured routing and final prose generation.

### Integration Points
- Character import should attach to the existing session/runtime shape without bypassing `SessionStore` or `TurnCoordinator`.
- Rules execution should plug in behind `TurnRunner` so Phase 3 can add combat and gameplay flow without rewriting Discord-facing code.

</code_context>

<specifics>
## Specific Ideas

- Keep Phase 2 coarse: one character path, one SRD baseline, one deterministic rules adapter.
- Prefer snapshot import over live sync if that cuts implementation and debugging cost significantly.
- Build the normalized character and rules contracts first so Phase 3 can focus on gameplay behaviors rather than data cleanup.

</specifics>

<deferred>
## Deferred Ideas

- Full combat automation belongs mostly to Phase 3, though Phase 2 should define the canonical mechanics interfaces it will need.
- Persistent replay/event history beyond what is required for rules determinism remains Phase 4 work.
- Multi-source character support, live sync, and non-SRD content remain out of scope for this phase.

</deferred>

---

*Phase: 02-character-import-rules-authority*
*Context gathered: 2026-03-27*
