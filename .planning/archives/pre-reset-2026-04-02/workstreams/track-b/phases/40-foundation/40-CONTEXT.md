# Phase 40: Foundation - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning
**Mode:** Auto-generated for autonomous execution

<domain>
## Phase Boundary

This phase establishes the foundational contracts for Track B milestone `vB.1.1`. It should define stable builder-to-archive schemas, normalization seams, and backward-compatible archive extensions before any higher-level AI synthesis or presentation work is expanded.

</domain>

<decisions>
## Implementation Decisions

### Scope
- Do not change the visible builder interview flow yet.
- Do not redesign archive presentation in this phase.
- Focus on contract definition, normalization seams, and backward compatibility.

### Builder-to-Archive Direction
- Builder answers should move toward explicit structured slots rather than remaining loosely coupled freeform strings.
- AI-assisted synthesis will come later, but the phase should define the schemas that such synthesis must satisfy.

### Compatibility
- Existing archive profiles must remain loadable without migration failures.
- Existing commands such as `/profiles`, `/profile_detail`, `/sheet`, and `/select_profile` should not require immediate behavior changes in this phase.

### COC Discipline
- New fields should align with recognizable COC 7e character-sheet or backstory sections.
- This phase may add nullable/defaulted fields and typed contracts, but should not invent new rules behavior.

</decisions>

<code_context>
## Existing Code Insights

### Current Builder
- `src/dm_bot/coc/builder.py` already has:
  - `BuilderSession`
  - dynamic interview planning
  - heuristic/model-guided semantic extraction
- The builder currently writes richer narrative fields, but lacks a formal normalization layer and explicit synthesis contracts.

### Current Archive
- `src/dm_bot/coc/archive.py` already holds a richer `InvestigatorArchiveProfile`.
- Archive detail rendering exists, but schema evolution is still ad hoc.
- One-active-profile lifecycle is already enforced and should remain intact.

### Existing Integration Points
- `src/dm_bot/discord_bot/commands.py` routes builder and archive commands.
- `src/dm_bot/persistence/store.py` serializes state, so any new schema fields must remain serialization-safe.

</code_context>

<specifics>
## Specific Ideas

- Introduce a `schema_version` or equivalent explicit compatibility marker for archive profiles.
- Add a dedicated normalization contract for builder answers rather than mixing normalization logic into archive creation.
- Separate:
  - raw interview answers
  - normalized structured answers
  - archive profile writeback payload

</specifics>

<deferred>
## Deferred Ideas

- Full AI synthesis output shaping belongs to Phase 41.
- Archive-projection sync visualization belongs to Phase 42.
- Richer COC 7e presentation expansion belongs to Phase 43.

</deferred>
