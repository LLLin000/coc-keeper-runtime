# Roadmap: `track-runtime`

## Status

Milestone sequence defined on `2026-04-03` after the `pre-reset-2026-04-02` archive reset.

This workstream owns canonical gameplay/runtime truth:

- session lifecycle at play time
- multi-actor scene resolution
- module trigger/consequence execution
- reveal and blocker state that must exist before any surface renders it
- runtime compatibility and recovery contracts that other tracks depend on

## Milestones

### `v1.0` — Shared Scene Batch Resolution

**Goal:** Make scene-round batching and shared consequence ownership canonical runtime behavior for multiplayer play instead of a Discord-surface convention.

**Why first:** Current multiplayer flow works, but `TurnCoordinator`, buffered submission, and consequence rendering still assume a mostly sequential world. Other tracks should not build richer surfaces on top of that ambiguity.

**Focus:**

- scene-round batch contract
- multi-actor submission lifecycle
- deterministic resolution order against shared state
- canonical consequence ownership before rendering
- runtime-visible pending/blocker truth

**Exit criteria:**

- the runtime has an explicit batch state model for collecting, locking, resolving, and publishing a round
- rule outcomes, trigger effects, and narrative consequences attach to canonical ownership scopes
- existing multiplayer scenarios and stress tests validate shared-scene behavior

**Recommended phase breakdown:**

1. `01-scene-lifecycle` — WorldState/Scene data model, lifecycle enum, focus orthogonality
2. `02-fork-switch` — decoupled fork() and switch_focus(), cross-cut narrator contract
3. `03-batch-merge` — "see all, act local" collection, semi-auto merge with KP confirmation

**Supporting spec:** `v1.0-SCENE-FORK-SPEC.md`

### `v1.1` — Transactional Trigger And Blocker Runtime

**Goal:** Turn trigger/reaction execution into a resumable runtime state machine instead of a chain of direct mutations.

**Why second:** The current trigger system is already useful, but it still applies effects inline and treats blocker states such as clarifications and pending rolls as side effects. That makes complex module behavior hard to reason about and harder to recover.

**Recommended phase breakdown:**

1. `01-trigger-entry` — formalize TriggerEvent, TriggerSpec, trigger registration
2. `02-reaction-classification` — formalize ReactionSpec, effect application model
3. `03-blocker-checkpoints` — formalize BlockerSpec, savepoint/resume semantics
4. `04-resumable-chains` — implement TriggerChain persistence and recovery
5. `05-audit-trail` — implement AuditEntry logging, integrate with PersistenceStore

**Supporting spec:** `v1.1-TRIGGER-BLOCKER-SPEC.md`

**Exit criteria:**

- trigger execution can pause and resume without losing canonical state
- blocker truth is explicit, queryable, and not inferred from surface behavior
- consequence chains stop mutating state in opaque order

### `v1.2` — Reveal Gates And Knowledge Ownership

**Goal:** Formalize knowledge, clue, and reveal ownership so private and shared information flow from runtime rules instead of narrative discipline.

**Why third:** Once batch and trigger flow are canonical, the next missing runtime truth is reveal gating. This is currently only partially represented in visibility logic and knowledge logs.

**Recommended phase breakdown:**

1. `01-reveal-gate-model` — formalize RevealGate, visibility levels, gate conditions
2. `02-clue-ownership` — formalize Clue, scope transitions, ownership transfer
3. `03-private-knowledge` — implement PlayerKnowledge, query_visible()
4. `04-table-kp-partition` — formalize what surfaces to where, visibility dispatch
5. `05-surface-contract` — define contract for track-surface renderers

**Supporting spec:** `v1.2-REVEAL-GATES-SPEC.md`

**Exit criteria:**

- private knowledge and shared table knowledge have distinct runtime contracts
- reveal transitions are recorded explicitly
- surface renderers consume runtime-owned visibility decisions rather than inventing them

### `v1.3` — Runtime Compatibility And Recovery Hardening

**Goal:** Make the runtime durable across larger modules, restart/resume flows, and future feature work by locking in compatibility and recovery contracts.

**Why fourth:** After runtime semantics are clean, the next risk is erosion: new modules, longer campaigns, and restart paths will drift unless compatibility and recovery expectations are formalized.

**Recommended phase breakdown:**

1. `01-compat-contract` — formalize ModuleContract, validate() algorithm
2. `02-migration-paths` — implement schema versioning, MigrationPath registry
3. `03-resume-package` — implement ResumePackage, integrity_check()
4. `04-integration-tests` — scenario coverage for complex paths, restart tests
5. `05-placeholder-cleanup` — address CONCERNS.md items, code quality fixes

**Supporting spec:** `v1.3-COMPAT-RECOVERY-SPEC.md`

**Exit criteria:**

- runtime-owned state survives restart/recovery without semantic drift
- core shipped modules run against the same canonical contracts
- placeholder runtime logic called out in the current map is either removed or replaced

## Recommended Execution Order

1. `v1.0` — stabilize shared scene truth
2. `v1.1` — make trigger/blocker execution resumable
3. `v1.2` — formalize reveal and knowledge ownership
4. `v1.3` — harden compatibility and recovery

## Dependency Notes

- `track-surface` should consume `v1.0` and `v1.2` contracts rather than redefining them.
- `track-identity` should remain the owner of long-lived profile truth, but `track-runtime` owns campaign-instance state derived from those profiles.
- `track-ops` should validate and monitor the contracts defined here instead of becoming the place where runtime semantics are invented.
