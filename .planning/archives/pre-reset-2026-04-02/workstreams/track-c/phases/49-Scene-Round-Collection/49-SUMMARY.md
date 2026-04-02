---
phase: 49
plan: Scene Round Collection
subsystem: Session Orchestration
tags: [round-collection, scene-round, multiplayer]
requires: [ROUND-01, ROUND-02, ROUND-03]
provides:
  - Round collection state in CampaignSession
  - /resolve-round and /next-round commands
  - Status display for action submissions
affects:
  - session_store.py: Round collection tracking
  - commands.py: Message handling and commands
  - client.py: Command registration
tech_stack:
  added: []
  patterns:
    - Phase-based message routing
    - Action collection state machine
key_files:
  created:
    - tests/test_round_collection.py
  modified:
    - src/dm_bot/orchestrator/session_store.py
    - src/dm_bot/discord_bot/commands.py
    - src/dm_bot/discord_bot/client.py
key_decisions:
  - Players submit actions via natural language messages during SCENE_ROUND_OPEN phase
  - KP triggers resolution with /resolve-round after all/majority submit
  - Status displays "已提交: X, Y | 待提交: Z" visible to all
---
# Phase 49 Plan: Scene Round Collection Summary

## One-Liner

Scene round collection implemented with natural language action submission and status tracking for multiplayer COC sessions.

## Goal

Implemented scene round collection where players submit action declarations in natural language, and KP resolves after all players have submitted. Status of who has submitted is visible to all.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Extend Session State for Round Collection | 81d8f6a | session_store.py |
| 2 | Message Handler Integration | 9f78801 | commands.py |
| 3 | Status Display System | 9f78801 | commands.py |
| 4 | Resolution Flow | a23ab6a | commands.py, client.py |
| 5 | Edge Case Handling | d14c129 | session_store.py |
| 6 | Tests and Verification | bd9a7e2 | test_round_collection.py |

## Technical Implementation

### Session State Extensions (Task 1)
- Added `pending_actions: dict[str, str]` field to store player action submissions
- Added `action_submitters: set[str]` tracking for who has submitted
- Added methods: `set_player_action`, `clear_player_action`, `clear_all_actions`
- Added helpers: `has_submitted`, `get_pending_members`, `all_submitted`
- Added name helpers: `get_submitter_names`, `get_pending_member_names`
- Updated dump/load for persistence

### Message Handler Integration (Task 2)
- Modified `handle_channel_message` to detect `SCENE_ROUND_OPEN` phase
- Added `_handle_round_action` and `_handle_round_action_stream` methods
- Empty submissions ignored (whitespace-only)
- Duplicate submissions replace previous (latest wins)

### Status Display (Task 3)
- Created `_build_round_status_message` method
- Shows "已提交: X, Y | 待提交: Z" format
- Updates after each player submission
- Clear visual indicator when all submitted ("✅ 行动已全部提交！")

### Resolution Flow (Task 4)
- Added `/resolve-round` command for KP
- Transitions: `SCENE_ROUND_OPEN` → `SCENE_ROUND_RESOLVING`
- Displays action summary for KP
- Added `/next-round` command to start new round
- Clears pending actions and transitions back to `SCENE_ROUND_OPEN`

### Edge Cases (Task 5)
- KP can proceed with partial submissions (any action_submitters)
- Empty submissions handled (ignored)
- Player leaving mid-round clears their pending action
- Timeout handling: Manual via `/next-round` (optional feature)

### Tests (Task 6)
- 16 new unit tests for round collection
- All 155 tests pass (including existing suite)

## Dependencies

- Phase 47 (Session Phases) - Required for SessionPhase enum ✓
- Phase 48 (Pre-Play Onboarding) - Flow continues from onboarding ✓

## Deviation from Plan

None - plan executed exactly as written.

## Requirements Addressed

| Requirement | Status |
|-------------|--------|
| ROUND-01: Players submit actions via natural language messages | ✅ Complete |
| ROUND-02: Status shows who has submitted and who is pending | ✅ Complete |
| ROUND-03: KP can trigger resolution after submissions | ✅ Complete |

## Duration

- Start: 2026-03-28T16:31:33Z
- End: 2026-03-28T16:37:31Z
- Duration: ~6 minutes

## Next Steps

Ready for Phase 50: Message Intent Routing
