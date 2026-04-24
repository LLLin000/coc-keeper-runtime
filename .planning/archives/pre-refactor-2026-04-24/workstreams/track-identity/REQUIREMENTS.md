# Requirements — `track-identity`

## `v1.0` — Archive Stability And Two-Tier Builder

### `IDN-01` Archive Schema Freeze

Archive profile schema and versioning rules must be explicit before real user data accumulates.

### `IDN-02` Two-Tier Builder

Character creation must support both a fast path and a full interview path without losing canonical archive truth.

### `IDN-03` Model-Guided With Fallback

Model-guided identity extraction and interview planning must fall back safely when model quality or availability is insufficient.

### `IDN-04` Import Contract

Manual paste import must produce archive-compatible investigator records under a documented contract.

### `IDN-05` Deletion Contract

Soft-delete and permanent-delete behavior must be explicit, recoverable, and auditable.

### `IDN-06` COC Validation Boundary

Identity finalization must respect COC rule authority for characteristics and derived stats while still allowing non-destructive warning flows.

## `v1.1` — Archive Evolution And Session Integration

### `IDN-07` Session Checkpoint

Post-session archive writes must be explicit and player-controlled rather than implicit state sync.

### `IDN-08` Migration Path

Archive schema changes must have a lightweight, documented migration path once real user data exists.

### `IDN-09` Skill Improvement Tracking

Skill growth across sessions must be auditable per character and consistent with COC progression rules.

### `IDN-10` Experience Journal

Structured adventure experience must be queryable separately from free-form narrative notes.

### `IDN-11` Builder Tuning

Builder ergonomics and model-guided quality must be refinable after the v1.0 foundations are in place.
