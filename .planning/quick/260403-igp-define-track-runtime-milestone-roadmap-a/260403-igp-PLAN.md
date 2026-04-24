# Quick Plan — `260403-igp`

## Task

Define the first post-reset milestone roadmap for `track-runtime` and establish a requirements baseline that turns the fresh reset into an executable planning sequence.

## Why This Task Exists

`track-runtime` is the default workstream after the `pre-reset-2026-04-02` archive, but it only has a placeholder first milestone. The codebase already shows concrete runtime gaps:

- multiplayer turn collection is still serialized around campaign locks and sequential assumptions
- trigger and consequence handling lacks transactional semantics
- reveal/private knowledge flow is partial rather than formally gated
- module/runtime compatibility and recovery expectations are not yet expressed as milestone contracts

The planning baseline should therefore reflect the real runtime center of gravity instead of carrying over the older overlapping Track A/Track C split.

## Planned Changes

1. Expand `track-runtime/ROADMAP.md` from a placeholder into a milestone sequence.
2. Create a `track-runtime/REQUIREMENTS.md` baseline aligned to those milestones.
3. Update `track-runtime/STATE.md` so the next workflow step is unambiguous.
4. Record the outcome in this quick task summary after verification.

## Proposed Milestone Stack

### `runtime.1` — Shared Scene Batch Resolution

Make scene-round batching and consequence ownership canonical runtime truth for multiplayer play.

### `runtime.2` — Transactional Trigger And Blocker Runtime

Turn trigger/reaction execution into a resumable and auditable state machine instead of a chain of ad hoc mutations.

### `runtime.3` — Reveal Gates And Knowledge Ownership

Formalize who learns what, when, and through which runtime contract.

### `runtime.4` — Runtime Compatibility And Recovery Hardening

Make runtime behavior durable across module growth, restart/recovery flows, and future phase work in other tracks.
