---
phase: E91
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/orchestrator/session_store.py
  - src/dm_bot/discord_bot/commands.py
  - tests/test_session_phase_transitions.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "Player can mark themselves ready via /ready command"
    - "Last player's ready triggers awaiting_ready → awaiting_admin_start"
    - "Early ready calls don't advance phase prematurely"
    - "Phase history records the transition"
  artifacts:
    - path: "src/dm_bot/orchestrator/session_store.py"
      provides: "all_ready() and transition_on_all_ready() methods on CampaignSession"
      contains: "def all_ready"
    - path: "src/dm_bot/discord_bot/commands.py"
      provides: "ready() command with phase transition wiring"
      pattern: "transition_on_all_ready"
    - path: "tests/test_session_phase_transitions.py"
      provides: "Tests for all_ready and transition behavior"
      contains: "test_all_ready"
  key_links:
    - from: "src/dm_bot/discord_bot/commands.py"
      to: "src/dm_bot/orchestrator/session_store.py"
      via: "session.transition_on_all_ready() call in ready()"
      pattern: "transition_on_all_ready"
    - from: "src/dm_bot/orchestrator/session_store.py"
      to: "SessionPhase.AWAITING_ADMIN_START"
      via: "transition_to call in transition_on_all_ready"
      pattern: "transition_to.*AWAITING_ADMIN_START"
---

<objective>
Wire `ready()` command to advance session phase when all players are ready.

Purpose: Complete the second phase transition in the session lifecycle — `awaiting_ready → awaiting_admin_start` — so that scenarios no longer get stuck after the lobby join phase.
Output: `all_ready()` helper in SessionStore, phase transition logic in `ready()` command, 3 new tests
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/workstreams/track-e/STATE.md
@.planning/workstreams/track-e/ROADMAP.md
@.planning/workstreams/track-e/phases/E90-auto-advance-lobby-awaiting-ready/E90-01-SUMMARY.md
@src/dm_bot/orchestrator/session_store.py
@src/dm_bot/discord_bot/commands.py
@tests/test_session_phase_transitions.py

<interfaces>
Key types and contracts the executor needs. Extracted from codebase.

From src/dm_bot/orchestrator/session_store.py:
```python
class SessionPhase(str, Enum):
    ONBOARDING = "onboarding"
    LOBBY = "lobby"
    AWAITING_READY = "awaiting_ready"
    AWAITING_ADMIN_START = "awaiting_admin_start"
    SCENE_ROUND_OPEN = "scene_round_open"
    SCENE_ROUND_RESOLVING = "scene_round_resolving"
    COMBAT = "combat"
    PAUSED = "paused"

class CampaignSession(BaseModel):
    session_phase: SessionPhase = SessionPhase.LOBBY
    player_ready: dict[str, bool] = Field(default_factory=dict)
    admin_started: bool = False
    member_ids: set[str] = Field(default_factory=set)
    members: dict[str, CampaignMember] = Field(default_factory=dict)

    def set_player_ready(self, user_id: str, ready: bool) -> None:
        self.player_ready[user_id] = ready
        if user_id in self.members:
            self.members[user_id].ready = ready

    def can_start_session(self) -> bool:
        ready_players = sum(1 for r in self.player_ready.values() if r)
        return ready_players >= len(self.member_ids) and self.admin_started

    def transition_to(self, new_phase: SessionPhase) -> None:
        self.session_phase = new_phase
        self.phase_history.append((new_phase.value, datetime.now()))

class SessionStore:
    def get_by_channel(self, channel_id: str) -> CampaignSession | None
    def validate_ready(self, *, channel_id: str, user_id: str) -> ValidationResult
```

From src/dm_bot/discord_bot/commands.py (ready method, line 811-836):
```python
async def ready(self, interaction) -> None:
    # Validates profile selected, then calls session.set_player_ready(user_id, True)
    # Currently: only sets ready flag and sends confirmation message
    # MISSING: no check for all-ready condition, no phase transition
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add all_ready() helper and ready-triggered phase transition to SessionStore</name>
  <files>src/dm_bot/orchestrator/session_store.py, tests/test_session_phase_transitions.py</files>
  <read_first>
    - src/dm_bot/orchestrator/session_store.py (current state, especially CampaignSession class lines 181-301)
    - tests/test_session_phase_transitions.py (existing test patterns)
    - .planning/workstreams/track-e/phases/E90-auto-advance-lobby-awaiting-ready/E90-01-SUMMARY.md (prior phase context)
  </read_first>
  <behavior>
    - Test 1: all_ready() returns False when no players are ready
    - Test 2: all_ready() returns False when only some players are ready
    - Test 3: all_ready() returns True when all member_ids have player_ready=True
    - Test 4: all_ready() handles empty member_ids (returns True — vacuous)
    - Test 5: ready() with all-ready condition triggers awaiting_ready → awaiting_admin_start transition
    - Test 6: ready() with not-all-ready stays in awaiting_ready (no premature transition)
    - Test 7: ready() from non-awaiting_ready phase does not transition (e.g., already past awaiting_admin_start)
  </behavior>
  <action>
    1. Add `all_ready()` method to `CampaignSession` class in session_store.py:
       ```python
       def all_ready(self) -> bool:
           """Check if all campaign members have marked themselves ready."""
           if not self.member_ids:
               return True
           return all(self.player_ready.get(uid, False) for uid in self.member_ids)
       ```
    2. Add `transition_on_all_ready()` method to `CampaignSession` class:
       ```python
       def transition_on_all_ready(self) -> bool:
           """If all players are ready and phase is AWAITING_READY, advance to AWAITING_ADMIN_START.
           Returns True if transition occurred, False otherwise."""
           if self.session_phase == SessionPhase.AWAITING_READY and self.all_ready():
               self.transition_to(SessionPhase.AWAITING_ADMIN_START)
               return True
           return False
       ```
    3. Add 3 new test functions to tests/test_session_phase_transitions.py:
       - `test_all_ready_false_when_not_all_ready` — 3-player session, only 2 ready, all_ready() returns False
       - `test_all_ready_true_when_all_ready` — 3-player session, all 3 ready, all_ready() returns True
       - `test_ready_triggers_awaiting_ready_to_awaiting_admin_start` — set all players ready, call transition_on_all_ready(), verify phase is AWAITING_ADMIN_START and phase_history records it
       - `test_ready_does_not_transition_prematurely` — only 1 of 3 players ready, transition_on_all_ready() returns False, phase stays AWAITING_READY
       - `test_ready_does_not_transition_from_wrong_phase` — session in AWAITING_ADMIN_START, all ready, transition_on_all_ready() returns False (no double-transition)
  </action>
  <verify>
    <automated>uv run pytest tests/test_session_phase_transitions.py -x -v</automated>
  </verify>
  <done>
    - CampaignSession.all_ready() method exists and returns correct boolean for all/none/partial ready states
    - CampaignSession.transition_on_all_ready() method exists and transitions AWAITING_READY → AWAITING_ADMIN_START only when all members ready
    - 5 new test functions added and passing in test_session_phase_transitions.py
    - Total tests in file: 15+ (10 existing + 5 new)
  </done>
</task>

<task type="auto">
  <name>Task 2: Wire ready() command to trigger phase transition</name>
  <files>src/dm_bot/discord_bot/commands.py</files>
  <read_first>
    - src/dm_bot/discord_bot/commands.py (ready method at line 811-836)
    - src/dm_bot/orchestrator/session_store.py (CampaignSession.transition_on_all_ready method from Task 1)
  </read_first>
  <action>
    Modify the `ready()` method in commands.py (line 811-836) to check all-ready condition and trigger phase transition after setting player ready:

    After the existing line `session.set_player_ready(user_id, True)` (line 830), add:
    ```python
    transitioned = session.transition_on_all_ready()
    if transitioned:
        self._persist_sessions()
        # Broadcast to channel that session is ready for admin start
        await interaction.followup.send(
            f"**{char_name}** 已就位！所有调查员已就位，等待管理员开始。",
            ephemeral=False,
        )
        return
    ```

    The existing confirmation message (`**{char_name}** 已就位！`) should remain as the default response when not all players are ready. Restructure as:
    1. Validate ready (existing)
    2. Set player ready (existing)
    3. Persist sessions (existing)
    4. Check transition_on_all_ready() — if True, send "all ready" message and return
    5. Otherwise, send individual "ready" confirmation (existing)

    Note: The `_persist_sessions()` call should happen regardless of transition, but the "all ready" broadcast message should only fire when transition actually occurs.
  </action>
  <verify>
    <automated>uv run python -m dm_bot.main smoke-check</automated>
  </verify>
  <done>
    - ready() command calls session.transition_on_all_ready() after setting player ready
    - When all players ready: phase transitions to AWAITING_ADMIN_START, broadcast message sent
    - When not all players ready: individual confirmation message sent, phase stays AWAITING_READY
    - _persist_sessions() called after ready flag is set
    - No changes to ready() validation logic (validate_ready still runs first)
  </done>
</task>

<task type="auto">
  <name>Task 3: Run full test suite and verify scenario progress</name>
  <files></files>
  <read_first>
    - tests/test_session_phase_transitions.py
  </read_first>
  <action>
    Run the full test suite to verify no regressions from E91 changes:
    1. Run `uv run pytest tests/test_session_phase_transitions.py -x -v` — all 15+ tests must pass
    2. Run `uv run pytest -q` — 846+ tests must pass (13 scenario failures expected — those need E92 for remaining transitions)
    3. Run `uv run python -m dm_bot.main smoke-check` — must pass
    4. Optionally run one scenario to verify phase progress: `uv run python -m dm_bot.main run-scenario --scenario tests/scenarios/acceptance/scen_session_happy_path.yaml` — should now show phase advancing past AWAITING_READY
  </action>
  <verify>
    <automated>uv run pytest -q && uv run python -m dm_bot.main smoke-check</automated>
  </verify>
  <done>
    - All unit tests pass (846+ passing)
    - smoke-check passes
    - Scenario phase history shows progression beyond AWAITING_READY (at least ['lobby', 'awaiting_ready', 'awaiting_admin_start'] for scenarios with all players ready)
    - 13 scenario failures remain expected (need E92 for onboarding/scene_round transitions)
  </done>
</task>

</tasks>

<verification>
- `uv run pytest tests/test_session_phase_transitions.py -x -v` — all tests pass
- `uv run pytest -q` — 846+ tests pass
- `uv run python -m dm_bot.main smoke-check` — passes
- Scenario runs show phase advancing to AWAITING_ADMIN_START when all players ready
</verification>

<success_criteria>
- [ ] CampaignSession.all_ready() method added to session_store.py
- [ ] CampaignSession.transition_on_all_ready() method added to session_store.py
- [ ] ready() command in commands.py triggers phase transition when all players ready
- [ ] 5+ new tests added to test_session_phase_transitions.py
- [ ] All 846+ existing tests still pass
- [ ] smoke-check passes
- [ ] Phase transitions: AWAITING_READY → AWAITING_ADMIN_START when all players ready
- [ ] No premature transitions (partial ready stays in AWAITING_READY)
</success_criteria>

<output>
After completion, create `.planning/phases/E91-ready-command-phase-transitions/E91-01-SUMMARY.md`
</output>
