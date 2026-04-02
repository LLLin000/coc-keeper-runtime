---
phase: E91
plan: 01
type: execute
wave: 1
depends_on:
  - E90
files_modified:
  - src/dm_bot/orchestrator/session_store.py
  - src/dm_bot/discord_bot/commands.py
  - tests/test_session_phase_transitions.py
autonomous: true
requirements: []

must_haves:
  truths:
    - "Last player's ready triggers awaiting_ready → awaiting_admin_start"
    - "Early ready calls don't advance phase prematurely"
    - "Phase history records the transition"
    - "all_ready() helper method works correctly"
  artifacts:
    - path: "src/dm_bot/orchestrator/session_store.py"
      provides: "all_ready() and transition_on_all_ready() methods on CampaignSession"
      contains: "def all_ready(self) -> bool:"
    - path: "src/dm_bot/discord_bot/commands.py"
      provides: "ready() command calls transition_on_all_ready() and broadcasts message"
      contains: "transition_on_all_ready()"
    - path: "tests/test_session_phase_transitions.py"
      provides: "6 new test functions for ready command phase transitions"
      contains: "def test_all_ready_false_when_not_all_ready"
  key_links:
    - from: "src/dm_bot/discord_bot/commands.py"
      to: "src/dm_bot/orchestrator/session_store.py"
      via: "ready() calls session.transition_on_all_ready()"
      pattern: "transition_on_all_ready\\(\\)"
---

<objective>
Wire `ready()` command to advance session phase when all players are ready, completing the second phase transition: `awaiting_ready → awaiting_admin_start`.

Purpose: Fix the root cause of scenarios stuck at `awaiting_ready` phase — `ready()` currently only marks individual readiness without checking all-ready condition or advancing phase.
Output: Modified `ready()` command with phase transition logic, new `all_ready()` and `transition_on_all_ready()` methods on CampaignSession, tests verifying the behavior.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/workstreams/track-e/ROADMAP.md
@.planning/workstreams/track-e/STATE.md

@src/dm_bot/orchestrator/session_store.py
@src/dm_bot/discord_bot/commands.py
@tests/test_session_phase_transitions.py

<interfaces>
From src/dm_bot/orchestrator/session_store.py:

```python
class CampaignSession(BaseModel):
    session_phase: SessionPhase = SessionPhase.LOBBY
    player_ready: dict[str, bool] = Field(default_factory=dict)
    def transition_to(self, new_phase: SessionPhase) -> None:
        self.session_phase = new_phase
        self.phase_history.append((new_phase.value, datetime.now()))
    def set_player_ready(self, user_id: str, ready: bool) -> None:
        self.player_ready[user_id] = ready
```

From src/dm_bot/discord_bot/commands.py:
- `ready()` method marks player as ready but never checks all-ready condition
- Need to add phase transition check after setting player ready
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add all_ready() and transition_on_all_ready() methods to CampaignSession</name>
  <files>src/dm_bot/orchestrator/session_store.py</files>
  <read_first>
    - src/dm_bot/orchestrator/session_store.py (CampaignSession class, existing methods)
  </read_first>
  <action>
    Add two methods to `CampaignSession` class in session_store.py:

    1. `all_ready() -> bool`:
       - Returns True if all member_ids have player_ready set to True
       - Returns True for empty member_ids (vacuous truth, consistent with can_start_session pattern)
       - Uses `all(self.player_ready.get(uid, False) for uid in self.member_ids)`

    2. `transition_on_all_ready() -> bool`:
       - If session_phase == AWAITING_READY and all_ready() is True:
         - Call transition_to(AWAITING_ADMIN_START)
         - Return True
       - Otherwise return False
       - Guard-gated: only transitions from AWAITING_READY phase

    Place these methods after the existing `can_start_session()` method.
  </action>
  <acceptance_criteria>
    - session_store.py contains `def all_ready(self) -> bool:`
    - session_store.py contains `def transition_on_all_ready(self) -> bool:`
    - all_ready() returns True for empty member_ids
    - transition_on_all_ready() only transitions from AWAITING_READY phase
    - Both methods have docstrings
  </acceptance_criteria>
  <verify>
    <automated>grep -n "def all_ready" src/dm_bot/orchestrator/session_store.py</automated>
  </verify>
  <done>CampaignSession has all_ready() and transition_on_all_ready() methods with correct logic</done>
</task>

<task type="auto">
  <name>Task 2: Wire ready() command to call transition_on_all_ready()</name>
  <files>src/dm_bot/discord_bot/commands.py</files>
  <read_first>
    - src/dm_bot/discord_bot/commands.py (ready() method implementation)
  </read_first>
  <action>
    In the `ready()` method in commands.py, after setting the player as ready:

    1. Call `session.transition_on_all_ready()` 
    2. If it returns True (transition occurred):
       - Get the player's character name
       - Send broadcast message: "**{char_name}** 已就位！所有调查员已就位，等待管理员开始。"
    3. If it returns False (no transition):
       - Send individual confirmation message as before

    Do NOT modify any other methods. Only add the transition check and conditional messaging.
  </action>
  <acceptance_criteria>
    - commands.py ready() method calls session.transition_on_all_ready()
    - When all ready: broadcasts Chinese message about all players ready
    - When not all ready: shows individual confirmation message
    - No other methods modified
  </acceptance_criteria>
  <verify>
    <automated>grep -n "transition_on_all_ready" src/dm_bot/discord_bot/commands.py</automated>
  </verify>
  <done>ready() command checks all-ready condition and transitions phase when appropriate</done>
</task>

<task type="auto">
  <name>Task 3: Add phase transition tests for ready command</name>
  <files>tests/test_session_phase_transitions.py</files>
  <read_first>
    - tests/test_session_phase_transitions.py (existing test patterns)
    - src/dm_bot/orchestrator/session_store.py (CampaignSession methods)
  </read_first>
  <action>
    Add 6 new test functions to tests/test_session_phase_transitions.py:

    1. `test_all_ready_false_when_not_all_ready`:
       - Create session with 2 members, only 1 ready
       - Assert all_ready() returns False

    2. `test_all_ready_true_when_all_ready`:
       - Create session with 2 members, both ready
       - Assert all_ready() returns True

    3. `test_all_ready_empty_members_returns_true`:
       - Create session with no members
       - Assert all_ready() returns True (vacuous truth)

    4. `test_ready_triggers_awaiting_ready_to_awaiting_admin_start`:
       - Bind campaign, join player, set phase to AWAITING_READY
       - Call ready() for all players
       - Assert session.session_phase == SessionPhase.AWAITING_ADMIN_START
       - Assert phase_history contains the transition

    5. `test_ready_does_not_transition_prematurely`:
       - Bind campaign, join 2 players, only 1 ready
       - Set phase to AWAITING_READY
       - Assert session.session_phase stays AWAITING_READY

    6. `test_ready_does_not_transition_from_wrong_phase`:
       - Create session in LOBBY phase
       - Call transition_on_all_ready()
       - Assert session.session_phase stays LOBBY (no transition from wrong phase)
  </action>
  <acceptance_criteria>
    - tests/test_session_phase_transitions.py contains all 6 new test functions
    - All 6 new tests pass: `uv run pytest tests/test_session_phase_transitions.py -x -v`
    - All existing tests still pass: `uv run pytest -q`
  </acceptance_criteria>
  <verify>
    <automated>uv run pytest tests/test_session_phase_transitions.py -x -v</automated>
  </verify>
  <done>6 new tests verify: (1) all_ready false/partial, (2) all_ready true, (3) empty members, (4) phase transition on all ready, (5) no premature transition, (6) no wrong-phase transition</done>
</task>

</tasks>

<verification>
- `uv run pytest tests/test_session_phase_transitions.py -x -v` — all tests pass
- `uv run pytest -q` — no regressions in full test suite
- `uv run python -m dm_bot.main smoke-check` — passes
- `grep -c "def all_ready" src/dm_bot/orchestrator/session_store.py` — returns 1
- `grep -c "transition_on_all_ready" src/dm_bot/discord_bot/commands.py` — returns 1
</verification>

<success_criteria>
- CampaignSession has all_ready() method that correctly checks all members
- CampaignSession has transition_on_all_ready() method that guards phase transition
- ready() command calls transition_on_all_ready() and broadcasts message when all ready
- Phase transitions from AWAITING_READY → AWAITING_ADMIN_START only when all players ready
- No premature transitions with partial ready
- No transitions from wrong phases
- All 846+ tests pass with no regressions
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-e/phases/E91-ready-command-phase-transitions/E91-01-SUMMARY.md`
</output>
