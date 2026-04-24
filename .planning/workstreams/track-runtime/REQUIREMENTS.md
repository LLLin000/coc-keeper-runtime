# Requirements — `track-runtime`

These requirements define the first post-reset runtime baseline. They are grouped by the milestone that should own them.

## `v1.0` — Shared Scene Batch Resolution

### `RTR-01` Batch State Machine - **COMPLETE (Phase 1)**

The runtime must represent round collection as explicit states such as collecting, locked, resolving, and published instead of deriving them from message timing.

### `RTR-02` Submission Ownership - **COMPLETE (Phase 1)**

Every submitted action must carry canonical ownership for actor, scope, and round membership before resolution begins.

### `RTR-03` Deterministic Resolution Order - **COMPLETE (Phase 3)**

Multi-actor scene resolution must use a deterministic ordering contract so shared outcomes do not depend on arbitrary arrival order.

### `RTR-04` Consequence Ownership - **COMPLETE (Phase 3)**

Rule outcomes, trigger effects, and narrative consequences must be associated with canonical visibility/ownership scopes before any renderer formats them.

### `RTR-05` Runtime Blocker Truth - **COMPLETE (Phase 3)**

The runtime must expose who or what a round is waiting on without relying on Discord-layer heuristics.

## `v1.1` — Transactional Trigger And Blocker Runtime

### `RTR-06` Event Entry Contract

Trigger execution must begin from a normalized runtime event contract instead of ad hoc dict payloads.

### `RTR-07` Resumable Trigger Execution

Trigger and reaction execution must be able to pause and resume across clarification and pending-roll checkpoints.

### `RTR-08` Auditable Mutation Order

State mutations caused by trigger/reaction execution must be ordered and auditable rather than applied as opaque side effects.

### `RTR-09` Blocker Persistence

Pending clarification and pending roll state must survive persistence boundaries and be restorable after resume.

## `v1.2` — Reveal Gates And Knowledge Ownership

### `RTR-10` Reveal Gate Contract

The runtime must define whether a consequence is table-visible, player-private, group-private, or keeper-only as canonical truth.

### `RTR-11` Knowledge Ownership

Clues, secrets, and inferred knowledge must record recipient scope and transition history.

### `RTR-12` Reveal Transition Events

Moving information from private to shared scope must be recorded as an explicit runtime event rather than implied by narration.

### `RTR-13` Surface Consumption Boundary

Surface renderers must consume runtime-owned visibility decisions instead of recomputing reveal scope from content strings.

## `v1.3` — Runtime Compatibility And Recovery Hardening

### `RTR-14` Compatibility Contract

Core shipped adventures must execute against a stable runtime contract that is validated by scenario coverage.

### `RTR-15` Recovery Integrity

Runtime-owned state for in-flight rounds, blockers, and reveal ownership must survive restart/recovery without semantic drift.

### `RTR-16` Placeholder Removal

Known placeholder runtime paths identified in codebase mapping must either be replaced with canonical state integration or explicitly retired.

### `RTR-17` Regression Gate Coverage

The repository gate must include scenario or integration coverage for the runtime contracts introduced by these milestones, not only unit-level behavior.
