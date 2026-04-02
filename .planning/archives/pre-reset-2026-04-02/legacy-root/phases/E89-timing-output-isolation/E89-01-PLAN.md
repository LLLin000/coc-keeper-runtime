---
phase: E89
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/testing/scenario_runner.py
  - src/dm_bot/testing/runtime_driver.py
  - tests/test_scenario_runner.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "Scenarios report non-zero duration in ms"
    - "Each step's outputs only contain outputs from that step"
    - "Artifact reports show accurate timing"
  artifacts:
    - path: "src/dm_bot/testing/scenario_runner.py"
      provides: "Duration measurement via time.monotonic() wrapping step execution"
      contains: "time.monotonic()"
    - path: "src/dm_bot/testing/runtime_driver.py"
      provides: "Output isolation via output_start index slicing"
      contains: "output_start"
    - path: "tests/test_scenario_runner.py"
      provides: "Tests for duration and output isolation"
      contains: "test_step_duration_is_measured"
  key_links:
    - from: "src/dm_bot/testing/scenario_runner.py"
      to: "src/dm_bot/testing/step_result.py"
      via: "StepResult.duration_ms assignment"
      pattern: "duration_ms\\s*="
    - from: "src/dm_bot/testing/runtime_driver.py"
      to: "src/dm_bot/testing/scenario_runner.py"
      via: "emitted_outputs slicing"
      pattern: "output_records\\[output_start:\\]"
---

<objective>
Fix duration measurement and output isolation in the scenario runner so artifact reports show accurate timing and per-step outputs.

Purpose: Scenarios currently report Duration: 0ms and cumulative outputs, making debugging impossible.
Output: Accurate per-step timing, isolated per-step output records, passing tests.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/workstreams/track-e/ROADMAP.md
@.planning/workstreams/track-e/STATE.md
@src/dm_bot/testing/scenario_runner.py
@src/dm_bot/testing/runtime_driver.py
@src/dm_bot/testing/step_result.py
@src/dm_bot/testing/artifact_writer.py
</context>

<interfaces>
From src/dm_bot/testing/step_result.py:
```python
@dataclass
class StepResult:
    phase_before: str
    phase_after: str
    emitted_outputs: list[OutputRecord] = field(default_factory=list)
    state_diff: dict[str, tuple[Any, Any]] = field(default_factory=dict)
    persistence_events: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    duration_ms: float = 0.0
```

From src/dm_bot/testing/artifact_writer.py (reads duration_ms):
- Line 60: `"duration_ms": step.duration_ms`
- Line 85: `"duration_ms": sum(s.duration_ms for s in result.steps)`
- Line 114: `f"**Duration:** {sum(s.duration_ms for s in result.steps):.0f}ms"`
</interfaces>

<tasks>

<task type="auto">
  <name>Task 1: Add duration_ms timing to all StepResult constructions in scenario_runner.py</name>
  <files>src/dm_bot/testing/scenario_runner.py</files>
  <action>
    Add timing measurement around step execution in ScenarioRunner.run():

    1. Import `time` at the top of the file (add `import time` after existing imports).

    2. In the step loop (around line 62), wrap each step execution with timing:
       - Record `step_start = time.monotonic()` before calling `_run_command_step` or `_run_message_step`
       - After the step returns, compute `duration_ms = (time.monotonic() - step_start) * 1000`
       - Set `result.duration_ms = duration_ms` on the returned StepResult before appending to step_results

    3. The specific locations to modify:
       - Line 66-68 (command step): Add timing around `await self._run_command_step(step_def, actors)`
       - Line 70-72 (message step): Add timing around `await self._run_message_step(step_def, actors)`
       - Line 188-192 (_run_command_step driver method branch): Add timing around the driver method call
       - Line 193-197 (_run_command_step error branch): Set duration_ms=0.0 explicitly for error results
       - Line 89-95 (assert step): Set duration_ms=0.0 for assertion-only steps (they don't execute anything)

    4. Use `time.monotonic()` (not `time.time()`) for duration measurement — it's immune to system clock changes and is the standard for elapsed time measurement.

    Do NOT change any other fields of StepResult. Only add duration_ms assignment.
  </action>
  <verify>
    <automated>uv run pytest tests/test_scenario_runner.py -x -q</automated>
  </verify>
  <done>
    - `import time` added at top of scenario_runner.py
    - All StepResult instances created in scenario_runner.py have duration_ms set to a non-zero value for command/message steps
    - Assert-only steps have duration_ms=0.0 (acceptable — they don't execute anything)
    - No existing tests broken
  </done>
</task>

<task type="auto">
  <name>Task 2: Isolate output records per step in runtime_driver.py and scenario_runner.py</name>
  <files>src/dm_bot/testing/runtime_driver.py, src/dm_bot/testing/scenario_runner.py</files>
  <action>
    Fix cumulative output problem by capturing output start index before each step and slicing after.

    In runtime_driver.py run_command() method (lines 169-225):
    1. Add `output_start = len(self._output_records)` right after `phase_before = self._phase_before()` (around line 178)
    2. Change all `emitted_outputs=list(self._output_records)` to `emitted_outputs=list(self._output_records[output_start:])`
       - Line 204: driver method success branch
       - Line 224: command success branch
       - Line 217: error branch — also slice to output_start

    In scenario_runner.py _run_command_step() method (lines 172-199):
    1. Add `output_start = len(self._driver._output_records)` before calling the driver method (around line 180)
    2. Change line 191 from `emitted_outputs=list(self._driver._output_records)` to `emitted_outputs=list(self._driver._output_records[output_start:])`
    3. Change line 196 (error branch) similarly to slice from output_start

    The send_message() method (line 283) already does this correctly with `list(self._output_records[output_start:])` — use it as the pattern.

    Do NOT change the _output_records list itself — only change how StepResult captures a snapshot of new outputs since the step began.
  </action>
  <verify>
    <automated>uv run pytest tests/test_scenario_runner.py tests/test_scenarios.py -x -q</automated>
  </verify>
  <done>
    - runtime_driver.py run_command() captures output_start index and slices emitted_outputs
    - scenario_runner.py _run_command_step() captures output_start index and slices emitted_outputs
    - Each step's emitted_outputs only contains outputs generated during that step
    - send_message() behavior unchanged (already correct)
    - No existing tests broken
  </done>
</task>

<task type="auto">
  <name>Task 3: Add tests for duration and output isolation</name>
  <files>tests/test_scenario_runner.py</files>
  <action>
    Add two new test functions to tests/test_scenario_runner.py:

    1. `test_step_duration_is_measured()`:
       - Create a minimal scenario with 2 command steps
       - Run it through ScenarioRunner with a FakeClock or real timing
       - Assert that step_results[0].duration_ms > 0 (non-zero for actual command execution)
       - Assert that step_results[1].duration_ms > 0
       - Assert that total duration (sum of all step duration_ms) > 0

    2. `test_step_outputs_are_isolated()`:
       - Create a scenario with 2 command steps where each step emits outputs
       - Run it through ScenarioRunner
       - Assert that step_results[0].emitted_outputs does NOT contain outputs from step 1
       - Assert that step_results[1].emitted_outputs does NOT contain outputs from step 0
       - Assert that len(step_results[0].emitted_outputs) + len(step_results[1].emitted_outputs) == total unique outputs

    Use existing test patterns from test_scenario_runner.py — import FakeInteraction, StubModelClient, etc. from tests.fakes modules.
  </action>
  <verify>
    <automated>uv run pytest tests/test_scenario_runner.py::test_step_duration_is_measured tests/test_scenario_runner.py::test_step_outputs_are_isolated -x -v</automated>
  </verify>
  <done>
    - test_step_duration_is_measured passes (duration_ms > 0 for command/message steps)
    - test_step_outputs_are_isolated passes (no cross-step output contamination)
    - All existing tests still pass
  </done>
</task>

</tasks>

<verification>
1. `uv run pytest tests/test_scenario_runner.py -x -q` — all tests pass
2. `uv run pytest tests/test_scenarios.py -x -q` — scenario tests still pass
3. Duration in artifact reports shows non-zero values
4. Per-step outputs in artifact reports are isolated (not cumulative)
</verification>

<success_criteria>
1. Duration accurately reflects step execution time (non-zero for actual steps)
2. Each step's outputs only contain outputs emitted during that step
3. Artifact reports show accurate timing and isolated outputs
4. All existing tests continue to pass
5. New tests for duration and output isolation pass
</success_criteria>

<output>
After completion, create `.planning/phases/E89-timing-output-isolation/E89-01-SUMMARY.md`
</output>
