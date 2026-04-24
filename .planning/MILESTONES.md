# Milestones

## v1.0 Shared Scene Batch Resolution (Shipped: 2026-04-24)

**Phases completed:** 3 phases, 3 plans, 10 tasks

**Key accomplishments:**

- Explicit scene lifecycle and player focus models as canonical runtime state, with structured state machine transitions and backward-compatible defaults
- fork() and switch_focus() runtime operations with cross-cut signaling and max-2-open-scenes policy enforcement
- Batch collection with deterministic resolution ordering and visibility-tagged consequences, enabling multi-actor scene rounds with canonical merge proposal flow

---

## Archive Snapshot

- `pre-reset-2026-04-02` — full planning-cycle archive created before the 4-track reset
  - Location: `.planning/archives/pre-reset-2026-04-02/`
  - Contains the previous 5-track planning tree, milestone history, quick tasks, debug notes, and legacy planning artifacts

## New Cycle

All four workstreams were standardized for GSD phase parsing on `2026-04-09`.

### `track-runtime`

| Milestone | Name | Phase Range | Status |
| --------- | ---- | ----------- | ------ |
| `v1.0` | Shared Scene Batch Resolution | 1-3 | current |
| `v1.1` | Transactional Trigger And Blocker Runtime | 4-8 | queued |
| `v1.2` | Reveal Gates And Knowledge Ownership | 9-13 | queued |
| `v1.3` | Runtime Compatibility And Recovery Hardening | 14-18 | queued |

### `track-identity`

| Milestone | Name | Phase Range | Status |
| --------- | ---- | ----------- | ------ |
| `v1.0` | Archive Stability And Two-Tier Builder | 19-24 | current |
| `v1.1` | Archive Evolution And Session Integration | 25-29 | queued |

### `track-surface`

| Milestone | Name | Phase Range | Status |
| --------- | ---- | ----------- | ------ |
| `v1.0` | Session Boards And Runtime-Aware Presentation | 30-34 | current |
| `v1.1` | Identity And Onboarding Surface Integration | 35-39 | queued |
| `v1.2` | Interactive Discord Surface And Activity Bridge | 40-44 | queued |

### `track-ops`

| Milestone | Name | Phase Range | Status |
| --------- | ---- | ----------- | ------ |
| `v1.0` | Startup And Delivery Gate Reliability | 45-48 | current |
| `v1.1` | Scenario And Recovery Coverage | 49-51 | queued |
| `v1.2` | Diagnostics And Operator Workflow | 52-54 | queued |

## Current Default

- Active workstream: `track-runtime`
- Current execution-ready phase: `/gsd-execute-phase 1`
