---
phase: E86
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/testing/scenario_runner.py
  - tests/test_scenarios.py
autonomous: true
requirements: []
gap_closure: true
---

<objective>
Fix scenario runner's assertion logic so scenarios actually fail when assertions are not met.

Purpose: Currently 14/14 scenarios false-positive PASS because scenario-level assertions (phase_timeline, state, visible) are parsed by ScenarioParser but never evaluated by ScenarioRunner. The runner must evaluate Assertions dataclass fields against actual runtime state.
Output: Working scenario-level assertion evaluation, scen_session_happy_path properly fails until phase transitions happen
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/workstreams/track-e/ROADMAP.md
@.planning/workstreams/track-e/phases/69-scenario-runner-runtime-driver/69-01-PLAN.md
@src/dm_bot/testing/scenario_runner.py
@src/dm_bot/testing/scenario_dsl.py
@tests/test_scenarios.py
@tests/scenarios/acceptance/scen_session_happy_path.yaml
@src/dm_bot/testing/step_result.py

<interfaces>
From src/dm_bot/testing/scenario_dsl.py:
```python
@dataclass
class Assertions:
    phase_timeline: list[str] = field(default_factory=list)
    final_phase: str = ""
    visible_public_must_include: list[str] = field(default_factory=list)
    visible_kp_must_include: list[str] = field(default_factory=list)
    visible_player_forbidden: list[str] = field(default_factory=list)
    state_campaign_members: int | None = None
    state_no_duplicate_members: bool = False
    persistence_restart_recoverable: bool | None = None
    narration_must_not_reveal_hidden_truth: bool | None = None

@dataclass
class Scenario:
    id: str
    title: str
    assertions: Assertions = field(default_factory=Assertions)
    # ... other fields
```

From src/dm_bot/testing/scenario_runner.py:
```python
class ScenarioRunner:
    async def run(self, scenario_path, *, write_artifacts=True, artifact_dir="artifacts/scenarios", fail_fast=False) -> ScenarioResult:
        # scenario.assertions is fully populated but NEVER used

@dataclass
class ScenarioResult:
    scenario_id: str
    passed: bool = False
    phase_timeline: list[str] = field(default_factory=list)
    final_state: dict[str, object] = field(default_factory=dict)
    failure: Failure | None = None
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add scenario-level assertion evaluation to ScenarioRunner.run()</name>
  <files>src/dm_bot/testing/scenario_runner.py</files>
  <behavior>
    - When scenario.assertions.phase_timeline is non-empty, compare against actual phase_timeline collected during run
    - When scenario.assertions.final_phase is non-empty, compare against final phase from driver
    - When scenario.assertions.visible_public_must_include is non-empty, check all public outputs contain each string
    - When scenario.assertions.visible_kp_must_include is non-empty, check all KP outputs contain each string
    - When scenario.assertions.state_campaign_members is set, verify final_state has correct member count
    - When scenario.assertions.state_no_duplicate_members is True, verify no duplicate members in final_state
    - Any failed assertion produces Failure(code=FailureCode.ASSERTION_FAILED, message=description, step_index=-1)
  </behavior>
  <action>
    Replace the broken post-loop assertion block (lines 134-150) with a new `_evaluate_scenario_assertions()` method that checks scenario-level Assertions against collected runtime data.

    Implementation details:
    1. Create new method `_evaluate_scenario_assertions(scenario: Scenario, phase_timeline: list[str], final_state: dict, all_outputs: list[OutputRecord]) -> Failure | None`
    2. For phase_timeline: compare expected list against actual collected timeline. Must match exactly or be a prefix (allow actual to be shorter if scenario ended early).
    3. For final_phase: if set, compare `phase_timeline[-1]` against expected value.
    4. For visible assertions: filter all_outputs by audience ("public" vs "kp"), check each required string appears in at least one output.
    5. For state assertions: extract campaign member count from final_state, check against expected. For no_duplicate_members, verify member IDs are unique.
    6. Replace lines 134-150 with call to this new method. Remove the broken post-loop step assert_ checking (that logic is already handled inline during the main loop).
    7. If any assertion fails, set failure and mark scenario as failed.
  </action>
  <verify>
    <automated>uv run pytest tests/test_scenarios.py -x -v 2>&1 | head -30</automated>
  </verify>
  <done>Scenario-level assertions (phase_timeline, final_phase, visible, state) are evaluated against actual runtime data. Failed assertions produce proper Failure objects.</done>
</task>

<task type="auto">
  <name>Task 2: Fix phase_timeline collection to capture phases BEFORE commands</name>
  <files>src/dm_bot/testing/scenario_runner.py</files>
  <action>
    Fix the phase_timeline collection bug where phase_before is captured AFTER command runs (line 58), causing timeline to always show ['lobby'].

    Current broken pattern:
    ```python
    for idx, step_def in enumerate(steps_def):
        phase_before = self._driver.get_phase()  # Captures AFTER previous command
        # ... run command ...
        phase_after = self._driver.get_phase()
        if phase_after and phase_after not in phase_timeline:
            phase_timeline.append(phase_after)
    ```

    Fix:
    1. Capture phase BEFORE the loop starts: `current_phase = self._driver.get_phase()` after `await self._driver.start()`
    2. Add initial phase to timeline: `if current_phase: phase_timeline.append(current_phase)`
    3. After each command/message step, capture new phase and append if changed:
       ```python
       new_phase = self._driver.get_phase()
       if new_phase and new_phase != current_phase:
           phase_timeline.append(new_phase)
           current_phase = new_phase
       ```
    4. This ensures the timeline captures the FULL progression from initial state through all transitions.
  </action>
  <verify>
    <automated>uv run pytest tests/test_scenarios.py::test_scenario -k "scen_session_happy_path" -v 2>&1 | head -20</automated>
  </verify>
  <done>phase_timeline in ScenarioResult reflects actual phase progression (lobby → awaiting_ready → awaiting_admin_start → onboarding → scene_round_open, etc.) instead of being stuck at ['lobby']</done>
</task>

<task type="auto">
  <name>Task 3: Add assertion-focused tests to verify scenario failures are detected</name>
  <files>tests/test_scenarios.py</files>
  <action>
    Add tests that verify assertion failures are properly detected:
    1. Test that a scenario with wrong phase_timeline expectation fails
    2. Test that a scenario with wrong state expectation fails
    3. Test that a scenario with missing visibility outputs fails
    4. Test that existing scen_session_happy_path now properly evaluates its assertions
    
    Add helper function `_create_test_scenario_with_assertions()` that builds minimal Scenario objects with specific assertions for testing.
    
    Test cases:
    - `test_scenario_phase_timeline_mismatch_fails`: Scenario expects timeline ['lobby', 'playing'] but actual is just ['lobby']
    - `test_scenario_state_assertion_fails`: Scenario expects campaign_members=5 but actual is 2
    - `test_scenario_visibility_assertion_fails`: Scenario expects public output containing "secret" but no such output exists
    - `test_scenario_passing_assertions`: Scenario with correct assertions passes
  </action>
  <verify>
    <automated>uv run pytest tests/test_scenarios.py -x -v 2>&1 | tail -20</automated>
  </verify>
  <done>New tests exist and pass, demonstrating that assertion failures are properly detected and reported</done>
</task>

</tasks>

<verification>
1. Run all scenario tests: `uv run pytest tests/test_scenarios.py -v`
2. Verify scen_session_happy_path properly evaluates its assertions (should fail if phase transitions don't match expected timeline)
3. Check that Failure objects contain meaningful error messages for each assertion type
4. Verify no regression in existing step-level assert_ functionality
</verification>

<success_criteria>
1. scen_session_happy_path FAILS until phase transitions actually happen (currently false-positive PASS)
2. Phase timeline assertions are properly evaluated against actual timeline
3. State assertions (campaign_members, no_duplicate_members) are evaluated
4. Visibility assertions (public_must_include, kp_must_include) are evaluated
5. Scenarios with step errors properly report failure
6. No regression in existing inline step assert_ functionality
7. All new tests pass
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-e/phases/86-scenario-runner-assertion-fix/E86-01-SUMMARY.md`
</output>