---
phase: 03-batch-and-merge
plan: "01"
subsystem: runtime
tags: [batch-collection, deterministic-resolution, merge-proposal, blocker-state, scene-lifecycle]

# Dependency graph
requires:
  - phase: 01-scene-lifecycle
    provides: SceneLifecycle enum (COLLECTING, LOCKED, RESOLVING, PUBLISHED), PlayerFocusScope enum
  - phase: 02-fork-and-switch-focus
    provides: fork() method, OpenScene tracking, switch_focus() method
provides:
  - Visibility enum with PUBLIC/PRIVATE/GROUP/KEEPER values
  - ActionBatchEntry, BatchSubmission, ResolvedAction, MergeProposal, BlockerState models
  - submit_action() accepting submissions in COLLECTING state
  - lock_scene() transitioning scene to LOCKED
  - compute_blocker_state() returning BlockerState tracking pending actors
  - resolve_scene() with deterministic ordering (dex descending, user_id ascending)
  - publish_scene() committing and transitioning to PUBLISHED
  - GameModeState batch/blocker fields and sync integration
affects:
  - Phase 4 trigger entry (uses batch submission and blocker state)
  - Narration system (consumes merge_proposal and resolved_actions)
  - Phase 5 reaction classification (uses deterministic resolution ordering)

# Tech tracking
tech-stack:
  added: [Visibility, ActionBatchEntry, BatchSubmission, ResolvedAction, MergeProposal, BlockerState]
  patterns:
    - Batch collection accepts actions during COLLECTING state only
    - Deterministic ordering via dex_value descending, user_id ascending tiebreaker
    - Visibility-tagged consequences preserved from submission through resolution
    - Runtime blocker truth computed from batch state (no Discord-layer heuristics)

key-files:
  created: []
  modified:
    - src/dm_bot/orchestrator/session_store.py
    - src/dm_bot/gameplay/modes.py
    - tests/test_multi_user_session.py

key-decisions:
  - "Deterministic ordering: dex_value descending, user_id ascending as tiebreaker ensures consistent resolution"
  - "Visibility tagged at submission time and preserved through resolution to MergeProposal"
  - "BlockerState computed from focused_scene keys, not member_ids - follows player focus tracking pattern"
  - "GameModeState.sync_from_session() extended to propagate batch/blocker state for narrator consumption"

patterns-established:
  - "Scene round collection as explicit batch submission with Ownership"
  - "Shared consequences ordered deterministically before computation"
  - "Merge proposal exposes visibility/ownership before commit"

requirements-completed: [RTR-03, RTR-04, RTR-05]

# Metrics
duration: 12 min
completed: 2026-04-24
---

# Phase 3 Plan 1: Batch and Merge Summary

**Batch collection with deterministic resolution ordering and visibility-tagged consequences, enabling multi-actor scene rounds with canonical merge proposal flow**

## Performance

- **Duration:** 12 min
- **Started:** 2026-04-24T12:50:16Z
- **Completed:** 2026-04-24T13:02:00Z
- **Tasks:** 4 completed
- **Files modified:** 3

## Accomplishments

- Added Visibility enum (PUBLIC, PRIVATE, GROUP, KEEPER) for consequence ownership tagging
- Added ActionBatchEntry, BatchSubmission, ResolvedAction, MergeProposal, BlockerState models
- Implemented submit_action() accepting submissions in COLLECTING state, rejecting when LOCKED
- Implemented lock_scene() transitioning scene to LOCKED state
- Implemented compute_blocker_state() returning BlockerState tracking pending actors (RTR-05)
- Implemented resolve_scene() with deterministic ordering: dex_value descending, user_id ascending tiebreaker (RTR-03)
- Implemented publish_scene() committing consequences and transitioning to PUBLISHED
- Extended GameModeState with pending_blocker, merge_proposal, batch_submission_count, resolved_actions fields
- Extended GameModeState.sync_from_session() to propagate batch/blocker state for narrator consumption
- Added 13 regression tests covering all new functionality

## Task Commits

Each task was committed atomically:

1. **Task 1: Add batch collection models and submit_action() method** - `f7d9366` (feat)
2. **Task 2: Implement deterministic resolution and merge proposal generation** - `1804a2f` (feat)
3. **Task 3: Add GameModeState batch/blocker fields and sync integration** - `1804a2f` (feat, same commit as Task 2)
4. **Task 4: Add regression tests for batch resolution and deterministic ordering** - `677d782` (test)

**Plan metadata:** (to be committed after SUMMARY)

## Files Created/Modified

- `src/dm_bot/orchestrator/session_store.py` - Added Visibility, ActionBatchEntry, BatchSubmission, ResolvedAction, MergeProposal, BlockerState models; batch_submissions, merge_proposals, pending_blocker, resolution_log fields to CampaignSession; submit_action(), lock_scene(), compute_blocker_state(), resolve_scene(), publish_scene(), get_merge_proposal() methods
- `src/dm_bot/gameplay/modes.py` - Added pending_blocker, merge_proposal, batch_submission_count, resolved_actions fields; extended sync_from_session() with batch/blocker parameters
- `tests/test_multi_user_session.py` - Added 13 regression tests for batch collection, deterministic resolution, visibility preservation, blocker state, and lifecycle transitions

## Decisions Made

- Deterministic ordering uses dex_value descending (higher agility acts first per COC rules), with user_id ascending as tiebreaker for same dex (alphabetical consistency)
- Visibility is tagged at submission time and preserved through resolution - downstream renderers consume visibility field instead of inferring from content (RTR-04)
- BlockerState computed from focused_scene keys (players currently focused on the scene), following the player focus tracking pattern established in Phase 2
- GameModeState.sync_from_session() extended with batch parameters so the narrator can consume blocker/proposal state directly from canonical runtime models

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Batch collection and deterministic resolution are complete and tested
- Phase 4 (Trigger Entry) can now build on batch submission infrastructure
- Phase 4 will use compute_blocker_state() and merge_proposal to coordinate trigger execution
- No blockers identified

---
*Phase: 03-batch-and-merge*
*Completed: 2026-04-24*