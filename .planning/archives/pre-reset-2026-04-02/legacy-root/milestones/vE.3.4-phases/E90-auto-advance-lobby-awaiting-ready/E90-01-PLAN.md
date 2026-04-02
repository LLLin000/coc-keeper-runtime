---
phase: E90
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/orchestrator/session_store.py
  - tests/test_session_phase_transitions.py
autonomous: true
requirements: []

must_haves:
  truths:
    - "First non-owner player join transitions lobby → awaiting_ready"
    - "Owner-only session stays in lobby"
    - "Multiple joins stay in awaiting_ready (no overshoot)"
    - "Phase history records the transition"
  artifacts:
    - path: "src/dm_bot/orchestrator/session_store.py"
      provides: "Auto-transition logic in join_campaign()"
      contains: "session.session_phase == SessionPhase.LOBBY and user_id != session.owner_id"
    - path: "tests/test_session_phase_transitions.py"
      provides: "4 new test functions for join_campaign phase transitions"
      contains: "def test_join_campaign_triggers_lobby_to_awaiting_ready"
  key_links:
    - from: "src/dm_bot/orchestrator/session_store.py"
      to: "SessionPhase.AWAITING_READY"
      via: "conditional transition in join_campaign"
      pattern: "transition_to\\(SessionPhase\\.AWAITING_READY\\)"
---

<objective>
Add automatic phase transition `lobby → awaiting_ready` when first non-owner player joins a campaign.

Purpose: Fix the root cause of scenarios stuck at `lobby` phase — `join_campaign()` currently only adds members without advancing phase, so 12/13 scenarios report `Actual: ['lobby']` despite executing join commands.
Output: Modified `join_campaign()` with conditional phase transition, updated tests verifying the behavior.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/workstreams/track-e/ROADMAP.md
@.planning/workstreams/track-e/STATE.md

@src/dm_bot/orchestrator/session_store.py
@tests/test_session_phase_transitions.py

<interfaces>
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
    phase_history: list[tuple[str, datetime]] = Field(default_factory=list)
    def transition_to(self, new_phase: SessionPhase) -> None:
        self.session_phase = new_phase
        self.phase_history.append((new_phase.value, datetime.now()))

class SessionStore:
    def join_campaign(self, *, channel_id: str, user_id: str) -> CampaignSession:
        # Currently: adds member_ids, creates CampaignMember + CampaignCharacterInstance
        # MISSING: no phase transition logic
```

From tests/test_session_phase_transitions.py:
- Tests use manual `session.transition_to(SessionPhase.AWAITING_READY)` — need to verify auto-transition via `join_campaign()` instead.
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add lobby → awaiting_ready auto-transition in join_campaign()</name>
  <files>src/dm_bot/orchestrator/session_store.py</files>
  <read_first>
    - src/dm_bot/orchestrator/session_store.py (current join_campaign implementation, lines 331-353)
  </read_first>
  <action>
    In `SessionStore.join_campaign()` (line ~331-353), after the existing member-addition logic and before `return session`, add a conditional phase transition:

    ```python
    # Auto-transition lobby → awaiting_ready when first non-owner joins
    if session.session_phase == SessionPhase.LOBBY and user_id != session.owner_id:
        session.transition_to(SessionPhase.AWAITING_READY)
    ```

    Exact placement: Insert these 3 lines between the `session.character_instances[user_id] = ...` block and the `return session` statement.

    Do NOT modify any other methods. Do NOT refactor existing code. Only add the 3-line conditional block.
  </action>
  <acceptance_criteria>
    - session_store.py contains `if session.session_phase == SessionPhase.LOBBY and user_id != session.owner_id:`
    - session_store.py contains `session.transition_to(SessionPhase.AWAITING_READY)` within join_campaign method
    - The transition code is placed before `return session` in join_campaign
    - No other methods in session_store.py are modified
  </acceptance_criteria>
  <verify>
    <automated>grep -n "session.session_phase == SessionPhase.LOBBY and user_id != session.owner_id" src/dm_bot/orchestrator/session_store.py</automated>
  </verify>
  <done>join_campaign() auto-transitions lobby → awaiting_ready when first non-owner player joins; owner-only joins keep session in lobby</done>
</task>

<task type="auto">
  <name>Task 2: Add phase transition tests for join_campaign auto-transition</name>
  <files>tests/test_session_phase_transitions.py</files>
  <read_first>
    - tests/test_session_phase_transitions.py (existing test patterns)
    - src/dm_bot/orchestrator/session_store.py (SessionPhase enum, join_campaign method)
  </read_first>
  <action>
    Add 4 new test functions to tests/test_session_phase_transitions.py:

    1. `test_join_campaign_triggers_lobby_to_awaiting_ready`:
       - Bind campaign with owner_id="owner"
       - Verify session starts in LOBBY
       - Call join_campaign with user_id="player1" (non-owner)
       - Assert session.session_phase == SessionPhase.AWAITING_READY
       - Assert phase_history contains ("awaiting_ready", ...)

    2. `test_owner_join_does_not_trigger_phase_transition`:
       - Bind campaign with owner_id="owner"
       - Verify session starts in LOBBY
       - Owner is already added by bind_campaign, so test that no additional owner join triggers transition
       - Instead: bind campaign, verify LOBBY, then join_campaign with a different user_id="other_owner"
       - But the real test: bind campaign, check LOBBY stays LOBBY if only owner exists
       - Actually: bind_campaign already adds owner to member_ids. The phase stays LOBBY.
       - Assert session.session_phase == SessionPhase.LOBBY (owner-only = no transition)

    3. `test_second_join_does_not_overshoot_phase`:
       - Bind campaign, join player1 (triggers LOBBY → AWAITING_READY)
       - Join player2 (should stay AWAITING_READY, not advance further)
       - Assert session.session_phase == SessionPhase.AWAITING_READY
       - Assert phase_history has exactly 1 entry

    4. `test_join_on_non_lobby_does_not_transition`:
       - Bind campaign, join player1 (triggers LOBBY → AWAITING_READY)
       - Manually transition to SessionPhase.AWAITING_ADMIN_START
       - Join player3
       - Assert session.session_phase == SessionPhase.AWAITING_ADMIN_START (unchanged)
  </action>
  <acceptance_criteria>
    - tests/test_session_phase_transitions.py contains `def test_join_campaign_triggers_lobby_to_awaiting_ready`
    - tests/test_session_phase_transitions.py contains `def test_owner_join_does_not_trigger_phase_transition`
    - tests/test_session_phase_transitions.py contains `def test_second_join_does_not_overshoot_phase`
    - tests/test_session_phase_transitions.py contains `def test_join_on_non_lobby_does_not_transition`
    - All 4 new tests pass: `uv run pytest tests/test_session_phase_transitions.py -x -v`
    - All 842 existing tests still pass: `uv run pytest -q`
  </acceptance_criteria>
  <verify>
    <automated>uv run pytest tests/test_session_phase_transitions.py -x -v</automated>
  </verify>
  <done>4 new tests verify: (1) non-owner join triggers LOBBY→AWAITING_READY, (2) owner-only stays LOBBY, (3) multiple joins don't overshoot, (4) non-LOBBY phases don't transition on join</done>
</task>

</tasks>

<verification>
- `uv run pytest tests/test_session_phase_transitions.py -x -v` — all tests pass
- `uv run pytest -q` — no regressions in full test suite
- `grep -c "session.session_phase == SessionPhase.LOBBY and user_id != session.owner_id" src/dm_bot/orchestrator/session_store.py` — returns 1
</verification>

<success_criteria>
- join_campaign() transitions LOBBY → AWAITING_READY when first non-owner player joins
- Owner-only sessions remain in LOBBY phase
- Multiple joins stay in AWAITING_READY (no overshoot to awaiting_admin_start or beyond)
- Phase history correctly records the single transition
- All 842+ tests pass with no regressions
</success_criteria>

<output>
After completion, create `.planning/phases/E90-auto-advance-lobby-awaiting-ready/E90-01-SUMMARY.md`
</output>
