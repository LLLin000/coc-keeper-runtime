---
phase: E87
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/testing/runtime_driver.py
  - src/dm_bot/discord_bot/commands.py
  - tests/scenarios/acceptance/scen_fuzhe_15turn.yaml
  - tests/scenarios/contract/visibility/scen_awaiting_ready_visibility.yaml
  - tests/scenarios/contract/visibility/scen_gmonly_reaches_kp.yaml
  - tests/scenarios/contract/visibility/scen_no_gmonly_to_player.yaml
  - tests/scenarios/contract/visibility/test_visibility_leak.yaml
  - tests/scenarios/contract/reveal/scen_investigation_before_reveal.yaml
  - tests/scenarios/contract/reveal/scen_wrong_path_no_premature_reveal.yaml
  - tests/scenarios/acceptance/scen_smoke.yaml
  - tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml
autonomous: true
requirements: []
gap_closure: true
must_haves:
  truths:
    - "Scenario steps resolve to callable methods without 'unknown command' errors"
    - "YAML parameter names match actual method signatures (adventure_id, not adventure_slug)"
    - "join_campaign steps don't pass unnecessary campaign_id args"
    - "Reveal policy scenarios can execute advance_story, move_to_location, interact steps"
    - "Driver-level methods (get_phase, trigger_improvement_phase) callable from scenario steps"
  artifacts:
    - path: "src/dm_bot/testing/runtime_driver.py"
      provides: "run_command resolves driver-level methods; get_phase and trigger_improvement_phase callable"
      contains: "getattr(self, command, None)"
    - path: "src/dm_bot/discord_bot/commands.py"
      provides: "Stub adventure navigation methods for reveal scenarios"
      contains: "async def advance_story"
    - path: "tests/scenarios/contract/visibility/scen_awaiting_ready_visibility.yaml"
      provides: "Uses adventure_id parameter matching BotCommands.load_adventure"
      contains: "adventure_id: fuzhe"
  key_links:
    - from: "tests/scenarios/**/*.yaml"
      to: "src/dm_bot/testing/runtime_driver.py"
      via: "run_command method resolution"
      pattern: "getattr.*_commands.*command"
    - from: "tests/scenarios/**/*.yaml"
      to: "src/dm_bot/discord_bot/commands.py"
      via: "BotCommands method calls via interaction"
      pattern: "async def (join_campaign|load_adventure|advance_story)"
---

<objective>
Fix API signature mismatches between scenario YAML definitions and actual BotCommands/RuntimeTestDriver methods so all scenario steps resolve to real, callable methods.

Purpose: 14 scenarios contain step commands that either don't exist on BotCommands (get_phase, advance_story, move_to_location, interact, trigger_improvement_phase) or use wrong parameter names (adventure_slug vs adventure_id, campaign_id on join_campaign). The scenario runner's `run_command` does `getattr(self._commands, command)` and returns "unknown command" errors for all of these.
Output: All scenario steps resolve to callable methods; no "unknown command" errors in scenario runs.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/workstreams/track-e/ROADMAP.md
@.planning/workstreams/track-e/phases/86-scenario-runner-assertion-fix/E86-01-SUMMARY.md
@src/dm_bot/testing/runtime_driver.py
@src/dm_bot/discord_bot/commands.py
@tests/scenarios/acceptance/scen_session_happy_path.yaml
@tests/scenarios/acceptance/scen_fuzhe_15turn.yaml
@tests/scenarios/acceptance/scen_combat_san.yaml
@tests/scenarios/acceptance/scen_character_creation.yaml
@tests/scenarios/contract/visibility/scen_awaiting_ready_visibility.yaml
@tests/scenarios/contract/reveal/scen_investigation_before_reveal.yaml
@tests/scenarios/contract/reveal/scen_wrong_path_no_premature_reveal.yaml
@tests/scenarios/acceptance/scen_smoke.yaml
@tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml

<interfaces>
From src/dm_bot/testing/runtime_driver.py:
```python
class RuntimeTestDriver:
    async def run_command(self, actor_id: str, command: str, args: dict[str, Any]) -> StepResult:
        # Current: only checks self._commands (BotCommands)
        method = getattr(self._commands, command, None)
        if method is None:
            return StepResult(..., error=f"unknown command: {command}")
        # Calls via: await cmd(interaction, **args) or await cmd(**args)

    def get_phase(self) -> str:
        # Driver-level method, NOT on BotCommands
        # Used by: scen_smoke.yaml, scen_awaiting_ready_visibility.yaml,
        #          scen_investigation_before_reveal.yaml, scen_wrong_path_no_premature_reveal.yaml

    def trigger_improvement_phase(self, player_id: str | None = None) -> dict:
        # Driver-level method, NOT on BotCommands
        # Used by: scen_skill_improvement_lifecycle.yaml
```

From src/dm_bot/discord_bot/commands.py:
```python
class BotCommands:
    async def join_campaign(self, interaction) -> None:
        # NO campaign_id parameter — gets channel/user from interaction
        # YAML passes: args: {campaign_id: camp_xxx} — this arg is ignored

    async def load_adventure(self, interaction, *, adventure_id: str) -> None:
        # Takes adventure_id, NOT adventure_slug
        # Some YAML files use adventure_slug: fuzhe — WRONG parameter name
```

From src/dm_bot/testing/step_result.py:
```python
@dataclass
class StepResult:
    phase_before: str
    phase_after: str
    error: str | None = None
    emitted_outputs: list[OutputRecord] = field(default_factory=list)
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Extend RuntimeTestDriver.run_command to resolve driver-level methods</name>
  <files>src/dm_bot/testing/runtime_driver.py</files>
  <read_first>
    - src/dm_bot/testing/runtime_driver.py
    - src/dm_bot/testing/step_result.py
  </read_first>
  <action>
    Modify `RuntimeTestDriver.run_command()` to check both BotCommands AND driver-level methods before returning "unknown command".

    Current code (lines ~178-184):
    ```python
    method = getattr(self._commands, command, None)
    if method is None:
        return StepResult(phase_before=phase_before, phase_after=phase_before, error=f"unknown command: {command}")
    ```

    Replace with:
    ```python
    method = getattr(self._commands, command, None)
    is_driver_method = False
    if method is None:
        method = getattr(self, command, None)
        if method is not None:
            is_driver_method = True
    if method is None:
        return StepResult(phase_before=phase_before, phase_after=phase_before, error=f"unknown command: {command}")
    ```

    Then in the invocation block, for driver methods (which don't take `interaction`), call directly with args:
    ```python
    try:
        if is_driver_method:
            result = method(**args)
            if asyncio.iscoroutine(result):
                await result
            return StepResult(
                phase_before=phase_before,
                phase_after=self._phase_before(),
                emitted_outputs=list(self._output_records),
            )
        cmd = cast(Callable[..., Coroutine[Any, Any, Any]], method)
        import inspect
        sig = inspect.signature(cmd)
        if "interaction" in sig.parameters:
            await cmd(interaction, **args)
        else:
            await cmd(**args)
    except Exception as exc:
        return StepResult(phase_before=phase_before, phase_after=self._phase_before(), error=str(exc))
    ```

    This resolves:
    - `get_phase` → RuntimeTestDriver.get_phase() (sync, no args needed)
    - `trigger_improvement_phase` → RuntimeTestDriver.trigger_improvement_phase() (sync, optional player_id)
  </action>
  <acceptance_criteria>
    - runtime_driver.py: run_command checks self._commands first, then self for driver methods
    - runtime_driver.py: driver methods called without interaction parameter
    - runtime_driver.py: sync driver methods handled (not awaited if not coroutine)
    - get_phase callable from scenario steps without "unknown command" error
    - trigger_improvement_phase callable from scenario steps without "unknown command" error
  </acceptance_criteria>
  <verify>
    <automated>uv run pytest tests/test_scenarios.py -k "scen_smoke" -v 2>&1 | head -20</automated>
  </verify>
  <done>get_phase and trigger_improvement_phase resolve as callable methods from scenario steps; no "unknown command" errors for these two commands</done>
</task>

<task type="auto">
  <name>Task 2: Fix YAML parameter name mismatches (adventure_slug → adventure_id)</name>
  <files>tests/scenarios/contract/visibility/scen_awaiting_ready_visibility.yaml, tests/scenarios/contract/visibility/scen_gmonly_reaches_kp.yaml, tests/scenarios/contract/visibility/scen_no_gmonly_to_player.yaml, tests/scenarios/contract/visibility/test_visibility_leak.yaml</files>
  <read_first>
    - tests/scenarios/contract/visibility/scen_awaiting_ready_visibility.yaml
    - tests/scenarios/contract/visibility/scen_gmonly_reaches_kp.yaml
    - tests/scenarios/contract/visibility/scen_no_gmonly_to_player.yaml
    - tests/scenarios/contract/visibility/test_visibility_leak.yaml
    - src/dm_bot/discord_bot/commands.py (load_adventure signature at line 768)
  </read_first>
  <action>
    BotCommands.load_adventure takes `adventure_id: str`, NOT `adventure_slug`. Fix all YAML files that use the wrong parameter name.

    Files to change — replace `adventure_slug:` with `adventure_id:` in the load_adventure step args:

    1. scen_awaiting_ready_visibility.yaml (line 34): `adventure_slug: fuzhe` → `adventure_id: fuzhe`
    2. scen_gmonly_reaches_kp.yaml (line 34): `adventure_slug: fuzhe` → `adventure_id: fuzhe`
    3. scen_no_gmonly_to_player.yaml (line 34): `adventure_slug: fuzhe` → `adventure_id: fuzhe`
    4. test_visibility_leak.yaml (line 34): `adventure_slug: fuzhe` → `adventure_id: fuzhe`

    Also verify scen_fuzhe_15turn.yaml already uses `adventure_id: fuzhe_mini` (correct, no change needed).
  </action>
  <acceptance_criteria>
    - scen_awaiting_ready_visibility.yaml: load_adventure args contain "adventure_id:" not "adventure_slug:"
    - scen_gmonly_reaches_kp.yaml: load_adventure args contain "adventure_id:" not "adventure_slug:"
    - scen_no_gmonly_to_player.yaml: load_adventure args contain "adventure_id:" not "adventure_slug:"
    - test_visibility_leak.yaml: load_adventure args contain "adventure_id:" not "adventure_slug:"
    - No YAML files contain "adventure_slug:" anywhere
  </acceptance_criteria>
  <verify>
    <automated>rg "adventure_slug" tests/scenarios/ && echo "FAIL: still contains adventure_slug" || echo "PASS: no adventure_slug found"</automated>
  </verify>
  <done>All YAML files use adventure_id (matching BotCommands.load_adventure signature); zero occurrences of adventure_slug in scenario files</done>
</task>

<task type="auto">
  <name>Task 3: Add stub adventure commands for reveal policy scenarios</name>
  <files>src/dm_bot/discord_bot/commands.py, tests/scenarios/contract/reveal/scen_investigation_before_reveal.yaml, tests/scenarios/contract/reveal/scen_wrong_path_no_premature_reveal.yaml</files>
  <read_first>
    - src/dm_bot/discord_bot/commands.py
    - tests/scenarios/contract/reveal/scen_investigation_before_reveal.yaml
    - tests/scenarios/contract/reveal/scen_wrong_path_no_premature_reveal.yaml
    - src/dm_bot/testing/runtime_driver.py (run_command method)
  </read_first>
  <action>
    Three commands used by reveal policy scenarios don't exist on BotCommands: `advance_story`, `move_to_location`, `interact`. These are adventure graph navigation concepts that aren't implemented as Discord slash commands yet.

    Add stub methods to BotCommands that accept the expected parameters and return a no-op success response. These stubs allow the reveal scenarios to run without "unknown command" errors while the actual adventure graph navigation is implemented in a future phase.

    Add to BotCommands class (after load_adventure method, around line 789):

    ```python
    async def advance_story(self, interaction, *, scene_id: str = "") -> None:
        """Stub: advance to a story scene. Full implementation pending adventure graph navigation."""
        await interaction.response.send_message(
            f"[stub] 故事推进到场景: {scene_id}",
            ephemeral=True,
        )

    async def move_to_location(self, interaction, *, location_id: str = "") -> None:
        """Stub: move character to a location. Full implementation pending adventure graph navigation."""
        await interaction.response.send_message(
            f"[stub] 移动到地点: {location_id}",
            ephemeral=True,
        )

    async def interact(self, interaction, *, interactable_id: str = "") -> None:
        """Stub: interact with an object/NPC. Full implementation pending adventure graph navigation."""
        await interaction.response.send_message(
            f"[stub] 与交互对象互动: {interactable_id}",
            ephemeral=True,
        )
    ```

    These stubs:
    - Accept the exact parameters the YAML scenarios pass (scene_id, location_id, interactable_id)
    - Return ephemeral responses so they don't pollute public visibility assertions
    - Are clearly marked as [stub] in output for easy identification
    - Don't modify any game state (safe no-ops)
  </action>
  <acceptance_criteria>
    - commands.py contains "async def advance_story(self, interaction, *, scene_id: str"
    - commands.py contains "async def move_to_location(self, interaction, *, location_id: str"
    - commands.py contains "async def interact(self, interaction, *, interactable_id: str"
    - All three methods call interaction.response.send_message with ephemeral=True
    - All three methods contain "[stub]" in their response message
  </acceptance_criteria>
  <verify>
    <automated>rg "def advance_story|def move_to_location|def interact" src/dm_bot/discord_bot/commands.py</automated>
  </verify>
  <done>advance_story, move_to_location, and interact exist as stub methods on BotCommands; reveal scenarios can execute these steps without "unknown command" errors</done>
</task>

<task type="auto">
  <name>Task 4: Clean up join_campaign YAML args (campaign_id is ignored by actual method)</name>
  <files>tests/scenarios/acceptance/scen_session_happy_path.yaml, tests/scenarios/acceptance/scen_combat_san.yaml, tests/scenarios/acceptance/scen_character_creation.yaml, tests/scenarios/acceptance/scen_fuzhe_15turn.yaml</files>
  <read_first>
    - tests/scenarios/acceptance/scen_session_happy_path.yaml
    - tests/scenarios/acceptance/scen_combat_san.yaml
    - tests/scenarios/acceptance/scen_character_creation.yaml
    - tests/scenarios/acceptance/scen_fuzhe_15turn.yaml
    - src/dm_bot/discord_bot/commands.py (join_campaign at line 339)
  </read_first>
  <action>
    BotCommands.join_campaign takes only `interaction` — no `campaign_id` parameter. The campaign is determined by the interaction's channel_id via SessionStore. The YAML files pass `campaign_id` in args which gets silently ignored by Python's **kwargs handling through inspect.signature.

    Clean up the YAML files by removing the unnecessary `campaign_id` args from join_campaign steps:

    1. scen_session_happy_path.yaml (lines 36, 42): Remove `campaign_id: camp_happy` from join_campaign args → `args: {}`
    2. scen_combat_san.yaml (line 45): Remove `campaign_id: camp_combat` from join_campaign args → `args: {}`
    3. scen_character_creation.yaml (line 43): Remove `campaign_id: camp_char` from join_campaign args → `args: {}`
    4. scen_fuzhe_15turn.yaml (line 34): Remove `campaign_id: camp_fuzhe` from join_campaign args → `args: {}`

    Also check scen_skill_improvement_lifecycle.yaml for same pattern.
  </action>
  <acceptance_criteria>
    - scen_session_happy_path.yaml: join_campaign steps have `args: {}` (no campaign_id)
    - scen_combat_san.yaml: join_campaign step has `args: {}` (no campaign_id)
    - scen_character_creation.yaml: join_campaign step has `args: {}` (no campaign_id)
    - scen_fuzhe_15turn.yaml: join_campaign step has `args: {}` (no campaign_id)
    - No join_campaign step in any YAML file passes campaign_id in args
  </acceptance_criteria>
  <verify>
    <automated>rg "join_campaign" -A3 tests/scenarios/ | rg "campaign_id" && echo "FAIL: join_campaign still has campaign_id" || echo "PASS: no campaign_id in join_campaign args"</automated>
  </verify>
  <done>join_campaign steps in all YAML files use empty args {}; no campaign_id passed to join_campaign</done>
</task>

<task type="auto">
  <name>Task 5: Verify all scenarios run without "unknown command" errors</name>
  <files>tests/test_scenarios.py</files>
  <read_first>
    - tests/test_scenarios.py
    - src/dm_bot/testing/runtime_driver.py
  </read_first>
  <action>
    Run the full scenario test suite and verify no "unknown command" errors appear. After E86, scenarios that fail due to assertion mismatches is expected — the goal here is that NO steps fail with "unknown command".

    Run: `uv run pytest tests/test_scenarios.py -v 2>&1 | tee /tmp/scenario_results.txt`

    Check that no output lines contain "unknown command". If any remain, identify which commands and fix them.

    Expected outcome: Some scenarios will FAIL due to assertion mismatches (phase_timeline not matching, visibility leaks, etc.) — that's correct behavior after E86. But NO step should produce "unknown command" errors.
  </action>
  <acceptance_criteria>
    - `uv run pytest tests/test_scenarios.py -v` produces zero "unknown command" errors in output
    - At least some scenarios PASS (scen_smoke should pass with get_phase stub)
    - Scenario failures are due to assertion mismatches, not missing commands
    - Test output shows step errors like PHASE_TRANSITION_MISMATCH or VISIBILITY_LEAK, not "unknown command"
  </acceptance_criteria>
  <verify>
    <automated>uv run pytest tests/test_scenarios.py -v 2>&1 | rg "unknown command" && echo "FAIL: unknown commands remain" || echo "PASS: no unknown commands"</automated>
  </verify>
  <done>Zero "unknown command" errors across all scenario tests; remaining failures are legitimate assertion mismatches</done>
</task>

</tasks>

<verification>
1. Run `uv run pytest tests/test_scenarios.py -v` — confirm zero "unknown command" errors
2. Check each changed YAML file: rg "adventure_slug" returns nothing
3. Check each changed YAML file: join_campaign steps have empty args
4. Verify stub methods exist on BotCommands: advance_story, move_to_location, interact
5. Verify driver methods resolve: get_phase, trigger_improvement_phase
6. Run `uv run pytest -q` — no regression in non-scenario tests
</verification>

<success_criteria>
1. All 5 unknown commands (get_phase, advance_story, move_to_location, interact, trigger_improvement_phase) resolve to callable methods
2. All adventure_slug parameters renamed to adventure_id across 4 YAML files
3. All join_campaign steps cleaned of unnecessary campaign_id args
4. Zero "unknown command" errors in any scenario test run
5. Stub methods clearly marked with [stub] prefix in output
6. No regression in existing non-scenario tests
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-e/phases/E87-api-signature-alignment/E87-01-SUMMARY.md`
</output>
