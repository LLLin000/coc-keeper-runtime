---
phase: 52-foundational-identity-models
plan: 01
subsystem: database
tags: [pydantic, session-store, campaign-membership, identity-models]

# Dependency graph
requires:
  - phase: 51-session-state-normalization
    provides: SessionStore with campaign binding, join/leave flow
provides:
  - CampaignMember Pydantic model with user_id, campaign_id, joined_at, role, ready, selected_profile_id, active_character_name
  - CampaignCharacterInstance Pydantic model with campaign_id, user_id, archive_profile_id, character_name, panel_id, created_at, source
  - CampaignSession refactored to use structured member and character instance dictionaries
  - Backward-compatible computed properties for member_ids, active_characters, player_ready, selected_profiles
  - dump_sessions/load_sessions round-trip serialization for new models
affects:
  - Phase 53 (join-flow-and-membership-gates)
  - Phase 54 (character-selection-and-ready-validation)
  - commands.py, visibility.py, onboarding_controller.py

# Tech tracking
tech-stack:
  added: [pydantic v2]
  patterns: [structured identity models, backward-compatible computed properties, TDD]

key-files:
  created:
    - tests/test_identity_models.py
  modified:
    - src/dm_bot/orchestrator/session_store.py
    - tests/test_persistence_store.py

key-decisions:
  - "Used Pydantic v2 model_validate() for deserialization instead of manual dict construction"
  - "Backward-compat computed properties preserve existing consumer code without changes"
  - "CampaignRole enum (member/admin/keeper) replaces implicit string role checks"

patterns-established:
  - "Pattern: Structured Pydantic models for session identity — future models should follow this pattern"
  - "Pattern: Backward-compatible computed properties for migration — new phases can refactor internals without breaking consumers"

requirements-completed: [REQ-001, REQ-004, REQ-006, REQ-010]

# Metrics
duration: 45min
completed: 2026-03-29
---

# Phase 52: Foundational Identity Models Summary

**Replaced primitive string sets and dicts with structured Pydantic models (CampaignMember, CampaignCharacterInstance) in CampaignSession with full backward-compatibility**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-03-29
- **Completed:** 2026-03-29
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Defined `CampaignMember` and `CampaignCharacterInstance` Pydantic models with proper defaults and validation
- Refactored `CampaignSession` to use structured `members: dict[str, CampaignMember]` and `character_instances: dict[str, CampaignCharacterInstance]`
- Added backward-compatible computed properties (`member_ids`, `active_characters`, `player_ready`, `selected_profiles`) so existing consumers keep working without changes
- Updated `dump_sessions`/`load_sessions` to serialize/deserialize new models via `model_dump()`/`model_validate()`
- Added TDD tests for model construction, serialization, session operations, and persistence round-trip

## Task Commits

Each task was committed atomically:

1. **Task 1: Define CampaignMember and CampaignCharacterInstance Models (TDD)** - `8ef1180` (test)
2. **Task 2: Refactor CampaignSession to use new models** - `7f786ee` (feat)
3. **Task 3: Add persistence round-trip tests** - `dea9b20` (test)

**Plan metadata:** `52-01-PLAN.md` created during planning phase

## Files Created/Modified
- `src/dm_bot/orchestrator/session_store.py` - Added CampaignMember, CampaignCharacterInstance, CampaignRole models; refactored CampaignSession
- `tests/test_identity_models.py` - TDD tests for model construction, serialization, backward compat
- `tests/test_persistence_store.py` - Added round-trip tests for new models

## Decisions Made
- Used Pydantic v2 `model_validate()` for deserialization (cleaner than manual construction)
- Backward-compat computed properties preserve existing consumer code — no need to update commands.py, visibility.py, onboarding_controller.py in this phase
- `CampaignRole` enum (member/admin/keeper) replaces implicit string role checks for type safety

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Task 3 tests (persistence round-trip) were missing from initial implementation — added in this session to complete the plan

## Next Phase Readiness
- Phase 53 (join-flow-and-membership-gates) can now validate membership using typed `CampaignMember` model instead of string-keyed lookups
- Phase 54 (character-selection-and-ready-validation) can use structured `character_instances` for validation logic
- commands.py, visibility.py, onboarding_controller.py continue to work via backward-compat properties

---
*Phase: 52-foundational-identity-models*
*Completed: 2026-03-29*
