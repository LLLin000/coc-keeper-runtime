---
phase: E90
plan: 01
type: summary
status: complete
---

# E90-01 Summary: Auto-Advance Lobby → Awaiting Ready

## Objective

Add automatic phase transition `lobby → awaiting_ready` when first non-owner player joins a campaign session.

## What Was Built

### 1. Auto-Transition Logic in `join_campaign()`

**File:** `src/dm_bot/orchestrator/session_store.py`

Added 3-line conditional block before `return session` in `join_campaign()` method (line ~353):

```python
# Auto-transition lobby → awaiting_ready when first non-owner joins
if session.session_phase == SessionPhase.LOBBY and user_id != session.owner_id:
    session.transition_to(SessionPhase.AWAITING_READY)
```

### 2. Updated Test Fixture

**File:** `tests/test_session_phase_transitions.py`

- Updated `multi_player_session` fixture to expect `AWAITING_READY` phase (auto-transition happens on first non-owner join)
- Added `lobby_session` fixture for tests that need to stay in LOBBY (owner-only)

### 3. New Tests (4 added)

| Test | What It Verifies |
|------|------------------|
| `test_join_campaign_triggers_lobby_to_awaiting_ready` | First non-owner join auto-transitions LOBBY → AWAITING_READY |
| `test_owner_join_does_not_trigger_phase_transition` | Owner-only session stays in LOBBY |
| `test_second_join_does_not_overshoot_phase` | Multiple joins stay in AWAITING_READY (no overshoot) |
| `test_join_on_non_lobby_does_not_transition` | Join on non-LOBBY phase doesn't transition |

## Requirements Addressed

| Requirement | Status |
|-------------|--------|
| First non-owner player join transitions lobby → awaiting_ready | ✅ |
| Owner-only session stays in lobby | ✅ |
| Multiple joins stay in awaiting_ready (no overshoot) | ✅ |
| Phase history records the transition | ✅ |

## Verification

- `uv run pytest tests/test_session_phase_transitions.py -x -v` — **10 passed** (6 existing + 4 new)
- `uv run pytest -q` — **846 passed, 13 failed** (scenario failures expected — need E91/E92 for remaining phase transitions)
- Scenarios now correctly show `['lobby', 'awaiting_ready']` instead of stuck at `['lobby']`

## Impact on Scenarios

The E90 change fixed the root cause of scenarios being stuck at `['lobby']`. All 13 remaining scenario failures are now legitimate PHASE_TRANSITION_MISMATCH errors because subsequent phase transitions (ready command → awaiting_admin_start → onboarding → scene_round_open) are not yet implemented. These will be fixed in E91 and E92.

## Next Steps

Execute: `/gsd-execute-phase E91` (Ready Command Phase Transitions)
