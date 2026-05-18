# Full Roadmap Redesign — Discord AI Keeper

## Context

After shipping track-runtime v1.0 (Shared Scene Batch Resolution) and completing a major architecture refactor (-20k LOC, rebuilt to 6 modules), the previous GSD-based planning with 54 micro-phases proved too granular for this project's scale. This document consolidates all 4 tracks into 15 executable stages.

Key constraints preserved from earlier planning:
- 4-track ownership model (runtime, surface, identity, ops)
- Delivery gate: `uv run pytest -q` + `uv run python -m dm_bot.main smoke-check`
- Execution order: runtime -> surface -> identity -> ops
- Each stage produces a verifiable deliverable (testable or demonstrable)

## Stage Map

```
runtime    [S1] [S2] [S3] [S4] [S5] [S6]
surface                 [S7] [S8] [S9] [S10]
identity                          [S11][S12][S13]
ops                                     [S14][S15]
```

Dependencies flow left-to-right and top-to-bottom. Stages in the same column can parallelize where noted.

---

## Track: runtime (S1-S6)

### S1: Run Core Verification

**Source:** GSD Phase 1-3 (already shipped pre-refactor)

**Goal:** Confirm v1.0 abstractions survived the refactor intact. No new features.

**Checklist:**
- `SceneLifecycle` / `PlayerFocusScope` enum and state machine
- `fork()` / `switch_focus()` / `submit_action()` / `resolve_scene()` / `merge_proposal()`
- `BlockerState` computation logic
- Deterministic ordering (DEX desc, user_id asc tiebreaker)
- All 49 existing tests pass

**Deliverable:** Verified v1.0 core with any gaps documented and fixed. State marked DONE.

**Out of scope:** New feature work.

---

### S2: Trigger & Blocker

**Source:** GSD Phase 4-6

**Goal:** Turn trigger/reaction execution into a resumable runtime state machine.

**Scope:**
- Normalized trigger-event entry point + trigger registration
- Reaction ordering, effect grouping, atomic application semantics
- Blocker as first-class runtime checkpoint (not an implicit state dict)

**Deliverable:** Triggers can be registered, fired, and rolled back. Blockers are persistable and resumable.

**Depends on:** S1

---

### S3: Resumable Chains & Audit

**Source:** GSD Phase 7-8

**Goal:** Trigger chain execution can be interrupted, resumed safely, and audited.

**Scope:**
- Persist trigger chains to SQLite
- Safe resume after interruption
- Auditable execution trail for replay and diagnosis

**Deliverable:** Trigger chain can survive process restart and resume from checkpoint. Audit log is human-readable.

**Depends on:** S2

---

### S4: Reveal Gates & Knowledge

**Source:** GSD Phase 9-11

**Goal:** Clues and reveals are enforced by runtime rules, not narrative convention.

**Scope:**
- Reveal gate primitives and lifecycle
- Clue ownership, scope transitions, transfer semantics
- Per-player private knowledge state + visibility queries

**Deliverable:** "Clue X is visible to player Y only under condition Z" — enforced at runtime.

**Depends on:** S3

---

### S5: Publication Contracts

**Source:** GSD Phase 12-13

**Goal:** Define the contract surface must consume. Runtime outputs partitioned visibility, not "should I show this?".

**Scope:**
- Table-visible vs KP-only publication path separation
- Renderer consumption contract (interface surface must implement)

**Deliverable:** Contract document + runtime correctly emits partitioned events. Surface consuming those events is testable.

**Depends on:** S4

---

### S6: Runtime Hardening

**Source:** GSD Phase 14-18

**Goal:** Lock all preceding capabilities into reliable state.

**Scope:**
- Runtime/module compatibility contract and validation
- Load-time schema migration, versioned runtime evolution
- Recovery package + integrity checks
- Integration tests covering v1.0-v1.3 core flows
- Remove correctness-critical placeholders

**Deliverable:** All gates pass. Old modules loadable. Restart recoverable. No critical TODO/FIXME.

**Depends on:** S5

---

## Track: surface (S7-S10)

### S7: Session Board Core

**Source:** GSD Phase 30-32

**Goal:** Render canonical runtime state into Discord-readable boards.

**Scope:**
- Current session identity, phase, pending participants, blocker summary
- Focused scene context, cross-cut transitions, waiting reasons (KP-readable)
- Public/shared/KP-only consequence output (no narrative convention)

**Depends on:** S5 (publication contract). Board framework and placeholder contracts can be built earlier.

**Deliverable:** Runtime state is readable as Discord boards. Visibility rules are enforced from runtime contract, not presentation code.

---

### S8: Clue Board & View Contracts

**Source:** GSD Phase 33-34

**Goal:** Present runtime-approved shared knowledge, separate view payload from Discord formatting.

**Scope:**
- Shared clue/history boards from runtime-approved knowledge only
- View layer separation: ViewPayload -> DiscordFormatter (enables swapping Discord for richer UI later)

**Depends on:** S7, S4 (reveal gates)

**Deliverable:** Clue/history boards reflect runtime truth. View layer is contract-separated from formatting.

---

### S9: Identity Surface Integration

**Source:** GSD Phase 35-38

**Goal:** Present identity track's artifacts in user-readable Discord form.

**Scope:**
- Archive detail rendering (per identity's card section contract)
- DM-first builder guidance
- Campaign binding, roster state, selected character display
- New player start pack (module intro, flow guidance, basic COC concepts)

**Depends on:** S7, S11 (identity archive)

**Deliverable:** Players can view/select characters and understand campaign state from Discord.

---

### S10: Interactive Surface

**Source:** GSD Phase 39-44

**Goal:** Upgrade static boards to interactive patterns.

**Scope:**
- Pagination and stateful views (long cards within Discord limits)
- Button/select-driven action flows
- Explicit DM/Ephemeral/Public delivery semantics
- Future-facing Activity UI schema
- Full surface QA, Chinese-first copy consistency

**Depends on:** S8, S9

**Deliverable:** Players can interact via buttons/selects. Delivery semantics are explicit and testable.

---

## Track: identity (S11-S13)

### S11: Archive & Builder

**Source:** GSD Phase 19-21

**Goal:** Freeze archive schema, establish two-tier builder.

**Scope:**
- Lock archive schema versioning, document canonical fields
- Fast path: minimal questions -> playable character
- Full path: model-guided interview with safe heuristic fallback

**Depends on:** None (can parallelize with S1)

**Deliverable:** Characters can be created via both paths. Schema is versioned and documented.

---

### S12: Data Lifecycle

**Source:** GSD Phase 22-24

**Goal:** Import, delete, and validate character data.

**Scope:**
- Manual paste import with documented parsing contract
- Soft delete (recoverable) vs hard delete (irreversible)
- COC legality validation (skill point enforcement at finalize time)

**Depends on:** S11

**Deliverable:** Characters can be imported, validated, and deleted with recovery option.

---

### S13: Session Integration

**Source:** GSD Phase 25-29

**Goal:** Post-session character evolution with durable history.

**Scope:**
- Post-session checkpoint writes (campaign-instance -> archive truth)
- Lightweight schema migration (when real user data exists)
- COC skill improvement tracking (auditable history)
- Structured adventure log (separate from free-form journaling)
- Builder tuning from real usage

**Depends on:** S12, S5 (runtime publication contracts), S7 (session board)

**Deliverable:** Characters evolve across sessions with auditable skill improvements and adventure history.

---

## Track: ops (S14-S15)

### S14: Startup & Delivery Gate

**Source:** GSD Phase 45-48

**Goal:** Every startup and delivery is reliable and observable.

**Scope:**
- Standardized preflight output (models, Discord config, assets, prerequisites)
- Smoke-check distinguishes pytest failure from boot failure
- Restart system hardening, observable boot progress
- Control panel and control status around canonical operator facts

**Depends on:** None (can parallelize with S1)

**Deliverable:** Local startup checks and gate signals are dependable.

---

### S15: Scenario & Diagnostics

**Source:** GSD Phase 49-54

**Goal:** Regressions caught by operator tooling, not by play sessions.

**Scope:**
- Scenario taxonomy standardization (suites and metadata)
- Restart/recovery path scenario and integration tests
- Standardized failure artifacts (smoke, scenario, restart)
- Runtime/session/failure diagnostics aggregation into operator-readable summary
- Inspection paths without raw file/DB spelunking
- Local gate semantics aligned with operator tooling

**Depends on:** S14, S6 (hardened runtime), S10 (interactive surface), S13 (session integration)

**Deliverable:** Representative verification coverage + actionable diagnostics.

---

## Open Items

1. **Hardcoded path in config.py:20** — `coc_asset_root` defaults to `C:/Users/Lin/Downloads/COC`. Needs cross-platform default.
2. **macOS PR #7 compatibility wiped** — Cross-platform process management (`runtime/`) was deleted by refactor. Needs re-integration into new architecture.
   - Both items will be handled via a separate `/gsd-quick` before S1 execution.

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| 15 stages instead of 54 GSD phases | Reduces planning overhead while keeping each deliverable verifiable |
| runtime -> surface -> identity -> ops | runtime is foundation; surface and identity consume it; ops caps all |
| S11/S14 can parallelize with S1 | No runtime dependency, can be worked independently |
| S7 framework before S5 contract | Board structure/plumbing can be built with placeholder contracts |
| No wave-based cross-track slicing | Track boundaries make ownership and verification cleaner for this project |
