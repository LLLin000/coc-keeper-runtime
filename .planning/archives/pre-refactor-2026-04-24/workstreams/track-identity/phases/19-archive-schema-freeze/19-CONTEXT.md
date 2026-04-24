# Phase 19: Archive Schema Freeze - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Freeze the canonical archive schema and document the field contract before more builder and archive features accumulate on top of it.
</domain>

<decisions>
## Implementation Decisions

### Schema Ownership
- Archive schema is owned by `track-identity`, not by runtime panels or presentation layers.
- This phase should lock field shape, version semantics, and writeback expectations before behavior-expanding builder work continues.
- Campaign-instance state stays outside archive truth unless explicitly checkpointed in later phases.

### Change Safety
- Favor additive clarification and explicit versioning over broad model churn.
- Documentation of archive fields is part of the deliverable, not optional follow-up.

### the agent's Discretion
- Exact placement of schema notes and helper types.
- Whether a dedicated schema-oriented test file is new or appended to existing archive tests.
</decisions>

<canonical_refs>
## Canonical References

### Planning Truth
- `.planning/workstreams/track-identity/ROADMAP.md` — phase goal, dependencies, and requirement mapping
- `.planning/workstreams/track-identity/REQUIREMENTS.md` — `IDN-01`
- `.planning/workstreams/track-identity/STATE.md` — milestone and phase position
- `.planning/workstreams/track-identity/identity-DECISIONS.md` — already-decided archive/builder boundaries
- `AGENTS.md` — repository workflow and verification rules

### Existing Identity Code
- `src/dm_bot/coc/archive.py` — current archive models and repository behavior
- `src/dm_bot/characters/models.py` — current investigator profile payload shape
- `tests/test_character_archive_flow.py` — current archive behavior verification
</canonical_refs>

<specifics>
## Specific Ideas

- Lock `schema_version` and ensure archive and character-model structures do not silently disagree.
- Make the schema documentation useful enough that later phases can reference it directly.
</specifics>

<deferred>
## Deferred Ideas

- Builder path design belongs to later phases in the same milestone.
- Session checkpoint and migration execution belong to `v1.1`.
</deferred>
