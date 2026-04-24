# Repository Planning Index

This repository uses workstream-specific roadmaps and states. Since `2026-04-09`, all four workstreams are standardized for GSD phase parsing.

Read planning docs in this order:

1. `.planning/PROJECT.md`
2. `.planning/active-workstream`
3. `.planning/workstreams/<track>/ROADMAP.md`
4. `.planning/workstreams/<track>/STATE.md`
5. `.planning/MILESTONES.md`

## Active Workstreams

- `track-runtime` — gameplay/runtime canonical truth
- `track-identity` — archive/builder/governance truth
- `track-surface` — Discord and presentation surface
- `track-ops` — verification, diagnostics, runtime operations

## GSD Standard

Canonical phase discovery is now based on numeric `Phase N:` sections inside each active workstream roadmap.

This means:

- `/gsd-plan-phase N` must target a numeric phase defined in the active workstream roadmap
- custom consolidated notes under `workstreams/*/phases/PLAN.md` are supplementary only
- future planning changes should preserve numeric global phase IDs

## Current Default

- Active workstream pointer: `.planning/active-workstream`
- Repository state snapshot: `.planning/STATE.md`
- Current active execution-ready phase: `/gsd-execute-phase 1`
