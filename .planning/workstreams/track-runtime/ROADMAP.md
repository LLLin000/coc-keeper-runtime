# Roadmap: `track-runtime`

## Status

Standardized on `2026-04-09` for GSD phase parsing.

**Ownership**
- session lifecycle at play time
- multi-actor scene resolution
- module trigger/consequence execution
- reveal and blocker state that surfaces must consume rather than infer
- runtime compatibility and recovery contracts

## v1.0 Shared Scene Batch Resolution

**Goal:** Make scene-round batching and shared consequence ownership canonical runtime behavior for multiplayer play instead of a Discord-surface convention.

### Phase 1: Scene Lifecycle

**Goal:** Introduce explicit world-state and scene-state models with lifecycle state separate from player focus.
**Depends on:** Nothing
**Requirements:** RTR-01, RTR-02
**Plans:** 1 plan

### Phase 2: Fork And Switch Focus

**Goal:** Decouple scene creation from focus switching and define cross-cut runtime behavior.
**Depends on:** Phase 1
**Requirements:** RTR-01, RTR-02, RTR-03
**Plans:** 0 plans

### Phase 3: Batch And Merge

**Goal:** Implement local batch collection, deterministic shared resolution, and merge proposal flow.
**Depends on:** Phase 1, Phase 2
**Requirements:** RTR-03, RTR-04, RTR-05
**Plans:** 0 plans

## v1.1 Transactional Trigger And Blocker Runtime

**Goal:** Turn trigger and reaction execution into a resumable runtime state machine instead of a chain of inline mutations.

### Phase 4: Trigger Entry

**Goal:** Formalize normalized trigger-event entry and trigger registration.
**Depends on:** Phase 3
**Requirements:** RTR-06
**Plans:** 0 plans

### Phase 5: Reaction Classification

**Goal:** Formalize reaction ordering, effect grouping, and atomic application semantics.
**Depends on:** Phase 4
**Requirements:** RTR-07, RTR-08
**Plans:** 0 plans

### Phase 6: Blocker Checkpoints

**Goal:** Make blockers first-class runtime checkpoints rather than implicit state dicts.
**Depends on:** Phase 4, Phase 5
**Requirements:** RTR-07, RTR-09
**Plans:** 0 plans

### Phase 7: Resumable Chains

**Goal:** Persist trigger chains and resume them safely after interruption or restart.
**Depends on:** Phase 4, Phase 5, Phase 6
**Requirements:** RTR-07, RTR-08, RTR-09
**Plans:** 0 plans

### Phase 8: Audit Trail

**Goal:** Record auditable trigger-chain execution for replay and diagnosis.
**Depends on:** Phase 7
**Requirements:** RTR-08, RTR-09
**Plans:** 0 plans

## v1.2 Reveal Gates And Knowledge Ownership

**Goal:** Formalize knowledge, clue, and reveal ownership so private and shared information flow from runtime rules instead of narrative discipline.

### Phase 9: Reveal Gate Model

**Goal:** Introduce canonical reveal-gate primitives and their lifecycle.
**Depends on:** Phase 8
**Requirements:** RTR-10
**Plans:** 0 plans

### Phase 10: Clue Ownership

**Goal:** Formalize clue ownership, scope transitions, and transfer semantics.
**Depends on:** Phase 9
**Requirements:** RTR-10, RTR-11
**Plans:** 0 plans

### Phase 11: Private Knowledge

**Goal:** Implement per-player knowledge state and visible-query semantics.
**Depends on:** Phase 9, Phase 10
**Requirements:** RTR-11
**Plans:** 0 plans

### Phase 12: Table And KP Partition

**Goal:** Separate runtime-owned table-visible and KP-only publication paths.
**Depends on:** Phase 9, Phase 10, Phase 11
**Requirements:** RTR-10, RTR-11, RTR-12
**Plans:** 0 plans

### Phase 13: Surface Contract

**Goal:** Define the renderer contract that `track-surface` must consume.
**Depends on:** Phase 9, Phase 10, Phase 11, Phase 12
**Requirements:** RTR-12, RTR-13
**Plans:** 0 plans

## v1.3 Runtime Compatibility And Recovery Hardening

**Goal:** Make runtime semantics durable across larger modules, restart/resume flows, and future feature work.

### Phase 14: Compatibility Contract

**Goal:** Define and validate the runtime/module compatibility contract.
**Depends on:** Phase 13
**Requirements:** RTR-14
**Plans:** 0 plans

### Phase 15: Migration Paths

**Goal:** Add load-time migration support and versioned runtime-state evolution.
**Depends on:** Phase 14
**Requirements:** RTR-14, RTR-15
**Plans:** 0 plans

### Phase 16: Resume Package

**Goal:** Package runtime recovery state and enforce integrity checks before resume.
**Depends on:** Phase 14, Phase 15
**Requirements:** RTR-15
**Plans:** 0 plans

### Phase 17: Integration Tests

**Goal:** Expand regression coverage to representative runtime flows across v1.0-v1.3 contracts.
**Depends on:** Phase 14, Phase 15, Phase 16
**Requirements:** RTR-14, RTR-15, RTR-17
**Plans:** 0 plans

### Phase 18: Placeholder Cleanup

**Goal:** Remove correctness-critical placeholders and align code with the new contracts before widening scope.
**Depends on:** Phase 14, Phase 15, Phase 16, Phase 17
**Requirements:** RTR-16, RTR-17
**Plans:** 0 plans
