# track-runtime v1.x Implementation Plan

> **Non-canonical note:** This file is supplementary planning context only. GSD phase discovery and `/gsd-plan-phase` use numeric `Phase N:` sections in [ROADMAP.md](C:/Users/Lin/Documents/Playground/.planning/workstreams/track-runtime/ROADMAP.md) as the source of truth.

> **For agentic workers:** REQUIRED SUB-SKILL: use `subagent-driven-development` or `executing-plans` when implementing this plan. This file is the execution-facing runtime plan for milestones `v1.0` through `v1.3`.

**Goal:** Turn the runtime roadmap into an execution-ready phase stack that can be implemented sequentially without re-opening milestone structure each time.

**Architecture:** Four milestones executed in order. `v1.0` establishes shared-scene and batch truth. `v1.1` makes trigger/blocker execution resumable. `v1.2` formalizes reveal and knowledge ownership. `v1.3` hardens compatibility, recovery, and regression coverage.

**Tech Stack:** Python + Pydantic v2 + SQLAlchemy 2.0 + existing `dm_bot.orchestrator`, `dm_bot.adventures`, `dm_bot.router`, `dm_bot.persistence`, and `dm_bot.runtime` modules.

---

## Current State Snapshot

These are the runtime facts the plan is built around:

| Issue | Evidence | Why It Matters |
| ----- | -------- | -------------- |
| Turn handling is campaign-serialized | `src/dm_bot/orchestrator/turns.py` uses one `asyncio.Lock` per campaign | Blocks true shared-scene batching and hides resolution-order semantics |
| Trigger effects mutate state inline | `src/dm_bot/adventures/trigger_engine.py` writes directly into `adventure_state` | Hard to pause, rollback, audit, and resume |
| Blockers are ad hoc dicts | `pending_roll` and `pending_clarification` live inside runtime state without formal contracts | Resume/recovery behavior is implicit rather than canonical |
| Knowledge ownership is partial | `knowledge_log` mixes scopes and recipient IDs in free-form entries | Reveal gates and private/shared state are not enforceable enough |
| Consequence aggregation is incomplete | `src/dm_bot/orchestrator/consequence_aggregator.py` still has placeholder summarization | Runtime ownership and publication contracts are not finalized |
| Smoke check still fails operationally | `src/dm_bot/runtime/smoke_check.py` exits on missing sync marker | Not a planning blocker, but a release-readiness signal for `track-ops` |

---

## Milestone Index

| Milestone | Name | Phase Count | Status |
| --------- | ---- | ----------- | ------ |
| v1.0 | Shared Scene Batch Resolution | 3 | phase-planned |
| v1.1 | Transactional Trigger And Blocker Runtime | 5 | phase-planned |
| v1.2 | Reveal Gates And Knowledge Ownership | 5 | phase-planned |
| v1.3 | Runtime Compatibility And Recovery Hardening | 5 | phase-planned |

---

## Milestone v1.0: Shared Scene Batch Resolution

**Goal:** Make scene-round batching and shared consequence ownership canonical runtime behavior instead of a Discord-surface convention.

### Phase 01: scene-lifecycle

**Goal:** Introduce explicit runtime data models for world state, scene state, scene lifecycle, and focus ownership.

**Primary deliverables:**
- `WorldState` and `SceneState` canonical models
- lifecycle enum for collect/lock/resolve/publish
- separation between scene lifecycle and player focus
- migration path from current single-scene assumptions

**Code hotspots:**
- `src/dm_bot/orchestrator/session_store.py`
- `src/dm_bot/orchestrator/gameplay.py`
- `src/dm_bot/gameplay/modes.py`

**Verification:**
- new unit tests for scene lifecycle transitions
- existing session and ready-gate tests still pass

### Phase 02: fork-switch

**Goal:** Decouple scene creation from focus switching and establish the narrator/runtime contract for cross-cut play.

**Depends on:** `v1.0 / 01-scene-lifecycle`

**Primary deliverables:**
- explicit `fork()` and `switch_focus()` runtime operations
- validation rules for player membership and max-open-scene policy
- narrator-facing cross-cut contract for focus shifts
- persistence updates for fork/switch events

**Code hotspots:**
- `src/dm_bot/orchestrator/gameplay.py`
- `src/dm_bot/orchestrator/session_store.py`
- `src/dm_bot/narration/service.py`

**Verification:**
- scenario coverage for fork and focus switch
- no regression in multiplayer governance tests

### Phase 03: batch-merge

**Goal:** Implement "see all, act local" batch collection and semi-manual merge with KP confirmation.

**Depends on:** `v1.0 / 01-scene-lifecycle`, `v1.0 / 02-fork-switch`

**Primary deliverables:**
- batch collection contract across open scenes
- deterministic resolution ordering for multi-actor submissions
- publication contract for shared/private consequences
- merge proposal and confirmation flow

**Code hotspots:**
- `src/dm_bot/orchestrator/turns.py`
- `src/dm_bot/router/message_buffer.py`
- `src/dm_bot/orchestrator/consequence_aggregator.py`

**Verification:**
- stress and chaos tests for multi-actor round collection
- new scenario covering fork -> local actions -> merge proposal

---

## Milestone v1.1: Transactional Trigger And Blocker Runtime

**Goal:** Turn trigger/reaction execution into a resumable runtime state machine instead of a chain of direct mutations.

### Phase 01: trigger-entry

**Goal:** Formalize normalized trigger event entry and trigger registration contracts.

**Primary deliverables:**
- `TriggerEvent` model
- trigger registry / entry normalization
- replacement of ad hoc event dict entry points where feasible

**Code hotspots:**
- `src/dm_bot/adventures/trigger_engine.py`
- `src/dm_bot/adventures/models.py`
- `src/dm_bot/orchestrator/gameplay.py`

**Verification:**
- unit tests for trigger-event normalization
- existing trigger-chain tests remain green

### Phase 02: reaction-classification

**Goal:** Formalize reaction ordering, effect grouping, and atomic application semantics.

**Depends on:** `v1.1 / 01-trigger-entry`

**Primary deliverables:**
- `ReactionSpec` classification
- deterministic reaction ordering
- reaction-level atomic mutation boundary
- bridge from existing runtime events into reaction model

**Code hotspots:**
- `src/dm_bot/adventures/reaction_engine.py`
- `src/dm_bot/adventures/trigger_engine.py`
- `src/dm_bot/orchestrator/consequence_aggregator.py`

**Verification:**
- tests for ordering and atomicity
- representative rollback scenario

### Phase 03: blocker-checkpoints

**Goal:** Make blockers first-class runtime checkpoints rather than side effects in state dicts.

**Depends on:** `v1.1 / 01-trigger-entry`, `v1.1 / 02-reaction-classification`

**Primary deliverables:**
- `BlockerSpec`
- checkpoint/savepoint model
- explicit statuses such as blocked, suspended, resolved
- persistence shape for pending clarification and pending roll

**Code hotspots:**
- `src/dm_bot/adventures/reaction_engine.py`
- `src/dm_bot/orchestrator/gameplay.py`
- `src/dm_bot/persistence/store.py`

**Verification:**
- tests for blocker creation and serialization
- scenario coverage for pending-roll resume boundary

### Phase 04: resumable-chains

**Goal:** Implement persisted trigger chains that can be resumed safely after interruption or restart.

**Depends on:** `v1.1 / 01-trigger-entry`, `v1.1 / 02-reaction-classification`, `v1.1 / 03-blocker-checkpoints`

**Primary deliverables:**
- `TriggerChain` state model
- persistence and reload path
- resume logic from event or blocker checkpoints
- safe handling for already-completed or invalid checkpoints

**Code hotspots:**
- `src/dm_bot/adventures/reaction_engine.py`
- `src/dm_bot/persistence/store.py`
- `src/dm_bot/runtime/restart_system.py`

**Verification:**
- resume-after-blocker scenario
- restart/reload integration test for in-flight chain

### Phase 05: audit-trail

**Goal:** Record auditable trigger-chain execution so runtime behavior is replayable and diagnosable.

**Depends on:** `v1.1 / 04-resumable-chains`

**Primary deliverables:**
- `AuditEntry` schema
- integration with `PersistenceStore`
- runtime query surface for audit events

**Code hotspots:**
- `src/dm_bot/persistence/store.py`
- `src/dm_bot/diagnostics/service.py`
- `src/dm_bot/orchestrator/gameplay.py`

**Verification:**
- tests for audit logging completeness
- resumed chain emits consistent audit trail

---

## Milestone v1.2: Reveal Gates And Knowledge Ownership

**Goal:** Formalize knowledge, clue, and reveal ownership so private and shared information flow from runtime rules instead of narrative discipline.

### Phase 01: reveal-gate-model

**Goal:** Introduce canonical reveal-gate primitives and their lifecycle.

**Primary deliverables:**
- `RevealGate` model
- visibility levels and unlock conditions
- candidate-to-canonical confirmation path

**Code hotspots:**
- `src/dm_bot/adventures/models.py`
- `src/dm_bot/orchestrator/gameplay.py`
- `src/dm_bot/orchestrator/visibility.py`

**Verification:**
- tests for gate lifecycle and unlock evaluation

### Phase 02: clue-ownership

**Goal:** Formalize clue ownership, scope transitions, and transfer semantics.

**Depends on:** `v1.2 / 01-reveal-gate-model`

**Primary deliverables:**
- `Clue` model and ownership scope
- explicit expansion modes
- no arbitrary IC propagation

**Code hotspots:**
- `src/dm_bot/adventures/trigger_engine.py`
- `src/dm_bot/orchestrator/gameplay.py`
- `src/dm_bot/adventures/models.py`

**Verification:**
- tests for clue scope expansion and transfer
- regression coverage for existing reveal-heavy adventures

### Phase 03: private-knowledge

**Goal:** Implement per-player knowledge state and visible-query semantics.

**Depends on:** `v1.2 / 01-reveal-gate-model`, `v1.2 / 02-clue-ownership`

**Primary deliverables:**
- `PlayerKnowledge` model
- `query_visible()` behavior
- structured handling of private clues, shared clues, secrets, and SAN-adjacent knowledge

**Code hotspots:**
- `src/dm_bot/orchestrator/gameplay.py`
- `src/dm_bot/orchestrator/visibility.py`
- `src/dm_bot/persistence/store.py`

**Verification:**
- tests for per-player visibility isolation
- scenario coverage for private -> shared transitions

### Phase 04: table-kp-partition

**Goal:** Separate runtime-owned table-visible and KP-only publication paths.

**Depends on:** `v1.2 / 01-reveal-gate-model`, `v1.2 / 02-clue-ownership`, `v1.2 / 03-private-knowledge`

**Primary deliverables:**
- canonical partition between table, player-private, and KP-only outcomes
- visibility dispatch boundary owned by runtime
- no accidental secret leakage via generic summaries

**Code hotspots:**
- `src/dm_bot/orchestrator/consequence_aggregator.py`
- `src/dm_bot/orchestrator/visibility.py`
- `src/dm_bot/discord_bot/visibility_dispatcher.py`

**Verification:**
- tests for publication partitioning
- scenario coverage for KP-only clue visibility

### Phase 05: surface-contract

**Goal:** Define the renderer contract that `track-surface` must consume.

**Depends on:** `v1.2 / 01-reveal-gate-model`, `v1.2 / 02-clue-ownership`, `v1.2 / 03-private-knowledge`, `v1.2 / 04-table-kp-partition`

**Primary deliverables:**
- stable runtime-facing visibility payload
- surface compatibility notes and examples
- no surface-side re-derivation of visibility truth

**Code hotspots:**
- `src/dm_bot/orchestrator/visibility.py`
- `src/dm_bot/orchestrator/player_status_renderer.py`
- `src/dm_bot/orchestrator/kp_ops_renderer.py`

**Verification:**
- contract tests for renderer inputs
- no regression in visibility-related test modules

---

## Milestone v1.3: Runtime Compatibility And Recovery Hardening

**Goal:** Make runtime semantics durable across larger modules, restart/resume flows, and future feature work.

### Phase 01: compat-contract

**Goal:** Define and validate the runtime/module compatibility contract.

**Primary deliverables:**
- `ModuleContract`
- required and optional capability checks
- field-schema compatibility validation

**Code hotspots:**
- `src/dm_bot/adventures/loader.py`
- `src/dm_bot/adventures/models.py`
- `src/dm_bot/orchestrator/gameplay.py`

**Verification:**
- tests for full/partial/incompatible outcomes
- representative shipped modules validated against declared capabilities

### Phase 02: migration-paths

**Goal:** Add load-time migration support and versioned runtime-state evolution.

**Depends on:** `v1.3 / 01-compat-contract`

**Primary deliverables:**
- `MigrationPath` registry
- additive-first migration rules
- idempotent migration tests

**Code hotspots:**
- `src/dm_bot/persistence/store.py`
- `src/dm_bot/adventures/loader.py`
- `src/dm_bot/orchestrator/session_store.py`

**Verification:**
- tests for N-1 -> current migration
- migration logging and rollback behavior where possible

### Phase 03: resume-package

**Goal:** Package runtime recovery state and enforce integrity checks before resume.

**Depends on:** `v1.3 / 01-compat-contract`, `v1.3 / 02-migration-paths`

**Primary deliverables:**
- `ResumePackage`
- integrity and preload checks
- valid checkpoint resolution after reload

**Code hotspots:**
- `src/dm_bot/runtime/restart_system.py`
- `src/dm_bot/runtime/control_service.py`
- `src/dm_bot/persistence/store.py`

**Verification:**
- resume integrity tests
- restart/reload scenario with active runtime state

### Phase 04: integration-tests

**Goal:** Expand regression coverage to representative runtime flows across milestones v1.0-v1.3.

**Depends on:** `v1.3 / 01-compat-contract`, `v1.3 / 02-migration-paths`, `v1.3 / 03-resume-package`

**Primary deliverables:**
- scenario coverage for fork/switch/merge
- reaction rollback coverage
- blocker suspend/resume coverage
- reveal gate transition coverage
- migration and resume coverage

**Code hotspots:**
- `tests/scenarios/`
- `src/dm_bot/testing/scenario_runner.py`
- `src/dm_bot/testing/runtime_driver.py`

**Verification:**
- `run-scenario --all`
- targeted runtime integration tests

### Phase 05: placeholder-cleanup

**Goal:** Remove correctness-critical placeholders and align code with the new contracts before broadening track scope.

**Depends on:** `v1.3 / 01-compat-contract`, `v1.3 / 02-migration-paths`, `v1.3 / 03-resume-package`, `v1.3 / 04-integration-tests`

**Primary deliverables:**
- cleanup of correctness-critical placeholder logic
- resolution of sequential-submission assumptions called out in concerns/specs
- documented deferrals for non-critical cleanup

**Code hotspots:**
- `src/dm_bot/orchestrator/turns.py`
- `src/dm_bot/gameplay/chase.py`
- `src/dm_bot/main.py`

**Verification:**
- full repository gate
- placeholder checklist updated to complete/deferred status

---

## Live Gray Zones

These items are not blockers for planning completeness, but they are the places where discussion may still be needed during execution:

1. How aggressively `v1.0` should support more than 2 open scenes before performance and narration quality degrade.
2. Whether `v1.1` resume semantics should always restart from event boundary or allow safe intra-event continuation for some reaction classes.
3. How much of `v1.2` clue confirmation can be delegated to validator heuristics before KP confirmation becomes optional.
4. Whether `v1.3` should hard-block incompatible modules at load time or allow partial degraded play in dev/test modes.

Default rule: if one of these turns from "planning tradeoff" into "interface contract", stop and discuss before implementation.

---

## Execution Order Summary

1. `v1.0 / 01-scene-lifecycle`
2. `v1.0 / 02-fork-switch`
3. `v1.0 / 03-batch-merge`
4. `v1.1 / 01-trigger-entry`
5. `v1.1 / 02-reaction-classification`
6. `v1.1 / 03-blocker-checkpoints`
7. `v1.1 / 04-resumable-chains`
8. `v1.1 / 05-audit-trail`
9. `v1.2 / 01-reveal-gate-model`
10. `v1.2 / 02-clue-ownership`
11. `v1.2 / 03-private-knowledge`
12. `v1.2 / 04-table-kp-partition`
13. `v1.2 / 05-surface-contract`
14. `v1.3 / 01-compat-contract`
15. `v1.3 / 02-migration-paths`
16. `v1.3 / 03-resume-package`
17. `v1.3 / 04-integration-tests`
18. `v1.3 / 05-placeholder-cleanup`

---

## Repository Gate

Before claiming any runtime phase complete:

- `uv run pytest -q`
- `uv run python -m dm_bot.main smoke-check`

If `smoke-check` still fails on startup marker timeout, treat that as an active `track-ops` dependency and call it out explicitly rather than papering over it.
