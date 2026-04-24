# Phase 19: Archive Schema Freeze - Research

## Research Summary

The archive model already exists and is widely referenced, but schema/version boundaries are still too implicit. This phase should freeze the contract before more builder and session-integration work is layered on top.

## Findings

### 1. Archive schema already carries high fan-out

- `src/dm_bot/coc/archive.py` defines `InvestigatorArchiveProfile` and related archive behavior.
- The same model also feeds presentation and builder flows, so schema drift here will ripple quickly.
- A schema-freeze phase is justified before further feature expansion.

### 2. Current schema versioning is not yet clearly locked

- `InvestigatorArchiveProfile` still declares `schema_version: int = 2`.
- The broader planning direction already expects a more explicit schema contract and later migration path.
- This phase should make the version policy intentional rather than incidental.

### 3. Character-model and archive-model boundaries need to be documented

- `src/dm_bot/characters/models.py` contains `COCInvestigatorProfile`, which is used under archive and import paths.
- Without clear documentation, later identity/runtime changes could accidentally redefine which fields belong to archive truth versus campaign-instance truth.

### 4. Existing tests verify behavior, not the full schema contract

- Current archive tests focus on behavior such as lifecycle and repository operations.
- There is room for schema-oriented verification that checks field presence, defaults, and version consistency explicitly.

## Recommended Planning Direction

1. Make schema versioning explicit in code and documentation.
2. Document archive-field ownership clearly enough that later phases can build against it.
3. Add narrow schema verification tests rather than relying only on behavioral coverage.

## Risks

- Overreaching into builder redesign in this phase will blur the boundary with Phases 20-24.
- If schema freeze is documented vaguely, later migration work will still lack a stable baseline.
