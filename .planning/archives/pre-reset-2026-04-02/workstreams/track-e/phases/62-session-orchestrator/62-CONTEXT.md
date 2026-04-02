# Phase 62: Session / Orchestrator Layer - Context

**Status:** Planned  
**Phase Directory:** `.planning/workstreams/track-e/phases/62-session-orchestrator`
**Primary Goal:** Validate campaign lifecycle flows: bind → join → select_profile → ready → load_adventure across multiple players, verifying SessionStore state transitions and phase changes.
**Depends on:** Phase 61 (Discord Command Layer)

## Why This Phase Exists

Track E vE.2.1 targets multi-user session reliability. Phase 61 validated the Discord command layer with 40 passing tests covering command handlers and channel enforcement. Phase 62 extends that foundation to validate:

1. **Multi-user campaign lifecycle** (SESS-01): The full bind→join→select_profile→ready→load_adventure flow across 3 players
2. **SessionPhase transitions under load** (SESS-02): LOBBY→SCENE_ROUND_OPEN→COMBAT transitions with concurrent multi-user operations

The test coverage survey explicitly identified the gap: **no multi-user session tests exist**. All existing tests (`test_ready_gate.py`, `test_join_gates.py`, `test_round_collection.py`) focus on single-user or single-session scenarios.

## Inputs Read For This Context

- `.planning/workstreams/track-e/codebase-architecture.md`
- `.planning/workstreams/track-e/test-coverage-survey.md`
- `.planning/workstreams/track-e/test-module-design.md`
- `.planning/workstreams/track-e/phases/61-discord-command-layer/61-CONTEXT.md`
- `.planning/workstreams/track-e/phases/61-discord-command-layer/61-01-SUMMARY.md`
- `src/dm_bot/orchestrator/session_store.py`
- `src/dm_bot/orchestrator/turn_runner.py`
- `tests/test_ready_gate.py`
- `tests/test_join_gates.py`
- `tests/test_round_collection.py`

## SessionStore Multi-Player State Machine

### Core Types

```python
class CampaignSession:
    campaign_id: str
    channel_id: str
    guild_id: str
    owner_id: str
    member_ids: set[str]           # All campaign members
    members: dict[str, CampaignMember]  # Structured member data
    character_instances: dict[str, CampaignCharacterInstance]
    session_phase: SessionPhase   # ONBOARDING → LOBBY → AWAITING_READY → SCENE_ROUND_OPEN → ...
    player_ready: dict[str, bool] # Per-user ready state
    admin_started: bool           # Admin triggered game start
    pending_actions: dict[str, str]  # Round collection
    action_submitters: set[str]

class CampaignMember:
    user_id: str
    campaign_id: str
    role: CampaignRole  # OWNER, ADMIN, MEMBER
    ready: bool
    selected_profile_id: str | None
    active_character_name: str | None

class SessionPhase(str, Enum):
    ONBOARDING = "onboarding"
    LOBBY = "lobby"
    AWAITING_READY = "awaiting_ready"
    AWAITING_ADMIN_START = "awaiting_admin_start"
    SCENE_ROUND_OPEN = "scene_round_open"
    SCENE_ROUND_RESOLVING = "scene_round_resolving"
    COMBAT = "combat"
    PAUSED = "paused"
```

### Key Multi-Player Operations

| Operation | Method | Multi-User Behavior |
|-----------|--------|---------------------|
| Create campaign | `bind_campaign()` | Owner auto-added to member_ids and members dict |
| Add member | `join_campaign()` | Creates CampaignCharacterInstance for user |
| Select profile | `select_archive_profile()` | Updates selected_profiles[user_id] and member.selected_profile_id |
| Ready check | `validate_ready()` | Checks member.selected_profile_id OR member.active_character_name |
| Set ready | `set_player_ready()` | Updates player_ready[user_id] and members[user_id].ready |
| Can start | `can_start_session()` | All members ready AND admin_started=True |
| Transition phase | `transition_to()` | Records in phase_history with timestamp |
| Collect actions | `set_player_action()` | Adds to pending_actions and action_submitters |

### Phase Transition Rules

```python
def can_start_session(self) -> bool:
    ready_players = sum(1 for r in self.player_ready.values() if r)
    return ready_players >= len(self.member_ids) and self.admin_started
```

Transitions to expect:
1. `LOBBY` → `AWAITING_READY` (when load_adventure called)
2. `AWAITING_READY` → `SCENE_ROUND_OPEN` (when can_start_session=True)
3. `SCENE_ROUND_OPEN` → `SCENE_ROUND_RESOLVING` (when all submitted)
4. `SCENE_ROUND_OPEN` → `COMBAT` (triggered by encounter)

## Specific Multi-User Gaps to Close

### Gap 1: No 3-Player Campaign Lifecycle Test
- Phase 61 tests single player bind→join→ready
- No test validates 3 players through full lifecycle
- SESS-01 requires: "3 players complete bind→join→ready→load_adventure without error"

### Gap 2: No Concurrent Ready Submission Test
- `test_ready_gate.py` tests ready one player at a time
- No test verifies 3 players ready simultaneously
- Race condition: what if 2 players ready at exact same time?

### Gap 3: No Multi-User Phase Transition Test
- `test_round_collection.py` tests phase transitions with 1-2 players
- No test verifies LOBBY→SCENE_ROUND_OPEN→COMBAT with 3+ players
- SESS-02 requires: "SessionPhase transitions correct under multi-user load"

### Gap 4: No Round Collection with 3+ Players
- Round collection assumes all_submitted() checks all member_ids
- No stress test with 3+ players submitting in various orders

## Test Adventure Module

Use **fuzhe_mini** ("Wetland Park Investigation") as defined in `test-module-design.md`:
- Entry: `car_crash_intersection`
- Pivot: `wetland_gate`
- Combat: `wetland_ambush`

This provides a minimal but complete adventure structure for load_adventure testing.

## Constraints For The Plan

- **TDD approach**: Write failing tests first, then implement
- **Phase 61 dependency**: FakeInteraction infrastructure available
- **In-memory only**: No live Discord connection needed
- **Deterministic**: All tests must be reproducible without timing dependencies where possible
- **Atomic commits**: RED→GREEN→REFACTOR cycle per requirement

## Expected Outputs

1. `tests/test_multi_user_session.py` - SESS-01 multi-player lifecycle tests
2. `tests/test_session_phase_transitions.py` - SESS-02 phase transition tests
3. `tests/test_multi_user_round_collection.py` - Round collection with 3+ players
4. Phase summary after implementation

## Success Shape

After Phase 62, the multi-user session layer is validated:
- 3 players can complete full campaign lifecycle
- SessionPhase transitions work correctly under concurrent load
- Round collection handles 3+ players robustly
- No race conditions in ready/check-in flow