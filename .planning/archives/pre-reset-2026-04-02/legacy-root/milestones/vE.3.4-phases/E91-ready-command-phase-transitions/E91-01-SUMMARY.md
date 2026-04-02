---
phase: E91
plan: 01
type: summary
status: complete
---

# E91-01 Summary: Ready Command Phase Transitions

## Objective

Wire `ready()` command to advance session phase when all players are ready, completing the second phase transition: `awaiting_ready → awaiting_admin_start`.

## What Was Built

### 1. `all_ready()` and `transition_on_all_ready()` Methods

**File:** `src/dm_bot/orchestrator/session_store.py`

Added two methods to `CampaignSession` class:

```python
def all_ready(self) -> bool:
    """Check if all campaign members have marked themselves ready."""
    if not self.member_ids:
        return True
    return all(self.player_ready.get(uid, False) for uid in self.member_ids)

def transition_on_all_ready(self) -> bool:
    """If all players are ready and phase is AWAITING_READY, advance to AWAITING_ADMIN_START.
    Returns True if transition occurred, False otherwise."""
    if self.session_phase == SessionPhase.AWAITING_READY and self.all_ready():
        self.transition_to(SessionPhase.AWAITING_ADMIN_START)
        return True
    return False
```

### 2. Wired `ready()` Command

**File:** `src/dm_bot/discord_bot/commands.py`

Modified `ready()` method to call `transition_on_all_ready()` after setting player ready. When all players are ready:
- Phase transitions to `AWAITING_ADMIN_START`
- Broadcast message: "**{char_name}** 已就位！所有调查员已就位，等待管理员开始。"
- When not all ready: individual confirmation message as before

### 3. New Tests (6 added)

| Test | What It Verifies |
|------|------------------|
| `test_all_ready_false_when_not_all_ready` | Returns False when not all players ready |
| `test_all_ready_true_when_all_ready` | Returns True when all players ready |
| `test_all_ready_empty_members_returns_true` | Vacuous truth for empty member_ids |
| `test_ready_triggers_awaiting_ready_to_awaiting_admin_start` | Phase transitions when all ready |
| `test_ready_does_not_transition_prematurely` | No premature transition with partial ready |
| `test_ready_does_not_transition_from_wrong_phase` | No double-transition from later phases |

## Requirements Addressed

| Requirement | Status |
|-------------|--------|
| Last player's ready triggers awaiting_ready → awaiting_admin_start | ✅ |
| Early ready calls don't advance phase prematurely | ✅ |
| Phase history records the transition | ✅ |
| all_ready() helper method | ✅ |

## Verification

- `uv run pytest tests/test_session_phase_transitions.py -x -v` — **16 passed** (10 existing + 6 new)
- `uv run pytest -q` — **852 passed, 13 failed** (scenario failures expected — scenarios don't mark KP as ready, need E93 for precondition alignment)
- `uv run python -m dm_bot.main smoke-check` — passes

## Scenario Status

Scenarios still show `['lobby', 'awaiting_ready']` because:
1. Scenarios don't include `ready` command for the KP (owner)
2. `all_ready()` checks ALL members including KP
3. Since KP never calls `ready`, `all_ready()` returns False

This is a scenario precondition issue, not a code bug. E93 will update scenario YAML files to include the KP's `ready` command.

## Next Steps

Execute: `/gsd-execute-phase E92` (Admin Start → Onboarding → Scene Round)
