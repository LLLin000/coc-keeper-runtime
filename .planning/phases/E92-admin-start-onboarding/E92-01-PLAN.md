---
phase: E92
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
    - "start_session() transitions awaiting_admin_start → onboarding"
    - "Onboarding completion transitions onboarding → scene_round_open"
    - "Phase history correctly tracks all transitions"
    - "Scenario tests pass with full phase progression"
  artifacts:
    - path: "src/dm_bot/discord_bot/commands.py"
      provides: "start_session() command with awaiting_admin_start → onboarding transition"
      pattern: "transition_to.*ONBOARDING"
    - path: "src/dm_bot/discord_bot/commands.py"
      provides: "complete_onboarding command with onboarding → scene_round_open transition"
      pattern: "transition_to.*SCENE_ROUND_OPEN"
    - path: "tests/test_session_phase_transitions.py"
      provides: "Tests for admin_start and onboarding transitions"
      contains: "test_admin_start"
  key_links:
    - from: "src/dm_bot/discord_bot/commands.py"
      to: "SessionPhase.ONBOARDING"
      via: "start_session() calls transition_to(SessionPhase.ONBOARDING)"
      pattern: "transition_to.*ONBOARDING"
    - from: "src/dm_bot/discord_bot/commands.py"
      to: "SessionPhase.SCENE_ROUND_OPEN"
      via: "complete_onboarding() calls transition_to(SessionPhase.SCENE_ROUND_OPEN)"
      pattern: "transition_to.*SCENE_ROUND_OPEN"
---

<objective>
Wire remaining phase transitions: `awaiting_admin_start → onboarding → scene_round_open`.

Purpose: Complete the final phase transitions in the session lifecycle so scenarios can progress from lobby through to scene round.
Output: Verified transition wiring in commands.py, new tests for admin_start and onboarding transitions
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/workstreams/track-e/STATE.md
@.planning/workstreams/track-e/ROADMAP.md
@.planning/phases/E91-ready-command-phase-transitions/E91-01-PLAN.md
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

    def transition_to(self, new_phase: SessionPhase) -> None:
        self.session_phase = new_phase
        self.phase_history.append((new_phase.value, datetime.now()))
```

From src/dm_bot/discord_bot/commands.py (lines 946-989):
```python
async def start_session(self, interaction) -> None:
    # ... validation ...
    if session.session_phase not in (
        SessionPhase.LOBBY,
        SessionPhase.AWAITING_ADMIN_START,
    ):
        await interaction.response.send_message(
            f"无法从当前阶段启动：{session.session_phase.value}。需要玩家先 /ready。",
            ephemeral=True,
        )
        return
    # ...
    session.transition_to(SessionPhase.ONBOARDING)  # Line 983
    for member_id in session.member_ids:
        session.set_onboarding_complete(member_id, False)
```

From src/dm_bot/discord_bot/commands.py (lines 1017-1069):
```python
async def complete_onboarding(self, interaction) -> None:
    # ... validation for ONBOARDING phase ...
    session.set_onboarding_complete(user_id_str, True)
    # Check all onboarding complete
    pending = []
    for member_id in session.member_ids:
        if not session.is_onboarding_complete(member_id):
            pending.append(member_id)
    if not pending:
        session.transition_to(SessionPhase.SCENE_ROUND_OPEN)  # Line 1057
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Verify existing transition wiring and add tests for admin_start → onboarding</name>
  <files>src/dm_bot/discord_bot/commands.py, tests/test_session_phase_transitions.py</files>
  <read_first>
    - src/dm_bot/discord_bot/commands.py (start_session method at line 946-989)
    - tests/test_session_phase_transitions.py (existing test patterns)
    - .planning/phases/E91-ready-command-phase-transitions/E91-01-PLAN.md (prior phase context)
  </read_first>
  <action>
    1. Verify start_session() command correctly transitions awaiting_admin_start → ONBOARDING:
       - Line 983: `session.transition_to(SessionPhase.ONBOARDING)` is already present
       - This is triggered when all players are ready (line 974-980) and admin calls /start_session
       
    2. Add test for admin_start triggering transition to ONBOARDING:
       ```python
       def test_admin_start_transitions_awaiting_admin_start_to_onboarding(multi_player_session):
           """start_session() transitions AWAITING_ADMIN_START → ONBOARDING."""
           session = multi_player_session.get_by_channel("ch1")
           # Set all ready and admin_started (simulating what happens after E91)
           session.transition_to(SessionPhase.AWAITING_ADMIN_START)
           for uid in ["owner", "player1", "player2"]:
               session.set_player_ready(uid, True)
           session.admin_started = True
           
           # Simulate start_session() calling transition_to(ONBOARDING)
           if session.session_phase == SessionPhase.AWAITING_ADMIN_START and session.can_start_session():
               session.transition_to(SessionPhase.ONBOARDING)
           
           assert session.session_phase == SessionPhase.ONBOARDING
           assert session.phase_history[-1][0] == "onboarding"
       ```
       
    3. Add test for onboarding complete transition:
       ```python
       def test_onboarding_complete_transitions_to_scene_round_open(multi_player_session):
           """All players completing onboarding transitions to SCENE_ROUND_OPEN."""
           session = multi_player_session.get_by_channel("ch1")
           session.transition_to(SessionPhase.ONBOARDING)
           
           # Simulate all players completing onboarding
           for member_id in session.member_ids:
               session.set_onboarding_complete(member_id, True)
           
           # Check if all complete - this would trigger transition
           all_complete = all(
               session.is_onboarding_complete(mid) 
               for mid in session.member_ids
           )
           if all_complete:
               session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
           
           assert session.session_phase == SessionPhase.SCENE_ROUND_OPEN
           assert session.phase_history[-1][0] == "scene_round_open"
       ```
  </action>
  <verify>
    <automated>uv run pytest tests/test_session_phase_transitions.py -x -v</automated>
  </verify>
  <done>
    - start_session() transition verified in commands.py (line 983)
    - 2 new test functions added for admin_start and onboarding transitions
    - All 18 tests pass (16 existing + 2 new)
  </done>
</task>

<task type="auto">
  <name>Task 2: Verify phase progression works end-to-end with scenarios</name>
  <files></files>
  <read_first>
    - tests/test_session_phase_transitions.py
  </read_first>
  <action>
    Run full test suite and verify scenario phase progression:
    
    1. Run `uv run pytest tests/test_session_phase_transitions.py -x -v` — all 18 tests must pass
    2. Run `uv run pytest -q` — verify test count and overall pass rate
    3. Run `uv run python -m dm_bot.main smoke-check` — must pass
    4. Run scenario to verify full phase progression:
       `uv run python -m dm_bot.main run-scenario --scenario tests/scenarios/acceptance/scen_session_happy_path.yaml`
       
    Expected: Phase timeline should show ['lobby', 'awaiting_ready', 'awaiting_admin_start', 'onboarding', 'scene_round_open']
  </action>
  <verify>
    <automated>uv run pytest -q && uv run python -m dm_bot.main smoke-check</automated>
  </verify>
  <done>
    - All unit tests pass
    - smoke-check passes
    - Scenario shows full phase progression from lobby through to scene_round_open
    - 13 scenario failures reduced (some scenarios now pass with complete transitions)
  </done>
</task>

</tasks>

<verification>
- `uv run pytest tests/test_session_phase_transitions.py -x -v` — all 18 tests pass
- `uv run pytest -q` — all tests pass
- `uv run python -m dm_bot.main smoke-check` — passes
- Scenario runs show phase progression: lobby → awaiting_ready → awaiting_admin_start → onboarding → scene_round_open
</verification>

<success_criteria>
- [ ] start_session() transitions awaiting_admin_start → ONBOARDING (verified in commands.py line 983)
- [ ] complete_onboarding() transitions onboarding → SCENE_ROUND_OPEN (verified in commands.py line 1057)
- [ ] Phase history correctly records all transitions
- [ ] 2+ new tests added for admin_start and onboarding transitions
- [ ] All 18+ tests in test_session_phase_transitions.py pass
- [ ] smoke-check passes
- [ ] Scenario phase progression complete through scene_round_open
</success_criteria>

<output>
After completion, create `.planning/phases/E92-admin-start-onboarding/E92-01-SUMMARY.md`
</output>