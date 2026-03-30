from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from dm_bot.testing.artifact_writer import ArtifactWriter
from dm_bot.testing.failure_taxonomy import Failure, FailureCode
from dm_bot.testing.runtime_driver import RuntimeTestDriver
from dm_bot.testing.scenario_dsl import ModelMode, ScenarioParser
from dm_bot.testing.step_result import OutputRecord, StepResult


@dataclass
class ScenarioResult:
    scenario_id: str
    title: str = ""
    mode: str = "acceptance"
    passed: bool = False
    steps: list[StepResult] = field(default_factory=list)
    phase_timeline: list[str] = field(default_factory=list)
    final_state: dict[str, object] = field(default_factory=dict)
    failure: Failure | None = None
    artifact_dir: Path | None = None


class ScenarioRunner:
    def __init__(self, driver: RuntimeTestDriver) -> None:
        self._driver = driver
        self._parser = ScenarioParser()

    async def run(
        self,
        scenario_path: str | Path,
        *,
        write_artifacts: bool = True,
        artifact_dir: str | Path = "artifacts/scenarios",
        fail_fast: bool = False,
    ) -> ScenarioResult:
        scenario = self._parser.parse(scenario_path)

        scenario_id = scenario.id
        steps_def = scenario.steps
        actors = scenario.actors

        self._configure_driver(scenario.fixtures)

        await self._driver.start()
        state_before = self._driver.snapshot_state()

        step_results: list[StepResult] = []
        phase_timeline: list[str] = []
        failure: Failure | None = None
        last_result: StepResult | None = None

        for idx, step_def in enumerate(steps_def):
            phase_before = self._driver.get_phase()

            if step_def.action == "command":
                result = await self._run_command_step(step_def, actors)
                step_results.append(result)
                last_result = result
            elif step_def.action == "message":
                result = await self._run_message_step(step_def, actors)
                step_results.append(result)
                last_result = result
            elif step_def.action == "assert":
                if last_result is None:
                    failure = Failure(
                        code=FailureCode.MISSING_STEP_FIELD,
                        message=f"Step {idx} is an assert with no preceding command",
                        step_index=idx,
                    )
                    break
                ok, msg = _check_assertion(last_result, step_def.assert_)
                if not ok:
                    failure = Failure(
                        code=FailureCode.ASSERTION_FAILED,
                        message=msg,
                        step_index=idx - 1,
                    )
                    break
                step_results.append(
                    StepResult(
                        phase_before=last_result.phase_after,
                        phase_after=last_result.phase_after,
                        emitted_outputs=list(last_result.emitted_outputs),
                    )
                )
                continue
            else:
                failure = Failure(
                    code=FailureCode.UNKNOWN_STEP_TYPE,
                    message=f"Step {idx} has unknown action: {step_def.action}",
                    step_index=idx,
                )
                break

            phase_after = self._driver.get_phase()
            if phase_after and phase_after not in phase_timeline:
                phase_timeline.append(phase_after)

            if fail_fast and last_result.error is None and failure is None:
                if step_def.assert_:
                    ok, msg = _check_assertion(last_result, step_def.assert_)
                    if not ok:
                        failure = Failure(
                            code=FailureCode.ASSERTION_FAILED,
                            message=msg,
                            step_index=idx,
                        )
                        break

        final_state = self._driver.snapshot_state()
        artifact_path: Path | None = None

        if write_artifacts:
            artifact_writer = ArtifactWriter(artifact_dir)
            result_for_artifact = ScenarioResult(
                scenario_id=scenario_id,
                title=scenario.title,
                mode=scenario.mode.value,
                passed=failure is None,
                steps=step_results,
                phase_timeline=phase_timeline,
                final_state=final_state,
                failure=failure,
            )
            artifact_path = artifact_writer.write_run(
                scenario_id, result_for_artifact, state_before, final_state
            )

        if failure is None:
            assertion_idx = 0
            for idx, step_def in enumerate(steps_def):
                if step_def.action == "assert":
                    cmd_idx = idx - assertion_idx - 1
                    if cmd_idx < len(step_results):
                        ok, msg = _check_assertion(
                            step_results[cmd_idx], step_def.assert_
                        )
                        if not ok:
                            failure = Failure(
                                code=FailureCode.ASSERTION_FAILED,
                                message=msg,
                                step_index=idx,
                            )
                            break
                    assertion_idx += 1

        await self._driver.stop()

        return ScenarioResult(
            scenario_id=scenario_id,
            title=scenario.title,
            mode=scenario.mode.value,
            passed=failure is None,
            steps=step_results,
            phase_timeline=phase_timeline,
            final_state=final_state,
            failure=failure,
            artifact_dir=artifact_path,
        )

    def _configure_driver(self, fixtures: Any) -> None:
        if hasattr(fixtures, "model_mode") and hasattr(self._driver, "_model_mode"):
            model_mode_value = (
                fixtures.model_mode.value
                if hasattr(fixtures.model_mode, "value")
                else str(fixtures.model_mode)
            )
            if model_mode_value != self._driver._model_mode:
                pass

    async def _run_command_step(self, step_def: Any, _actors: Any) -> StepResult:
        actor_id = str(step_def.actor) if step_def.actor else "u_kp"
        command = str(step_def.name)
        args: dict[str, Any] = dict(step_def.args) if step_def.args else {}

        if command.startswith("driver."):
            method_name = command[len("driver.") :]
            method = getattr(self._driver, method_name, None)
            if method is not None and callable(method):
                import inspect

                sig = inspect.signature(method)
                if "interaction" in sig.parameters:
                    await method(self._driver._interaction_for(actor_id), **args)
                else:
                    await method(**args)
                return StepResult(
                    phase_before=self._driver.get_phase(),
                    phase_after=self._driver.get_phase(),
                    emitted_outputs=list(self._driver._output_records),
                )
            return StepResult(
                phase_before=self._driver.get_phase(),
                phase_after=self._driver.get_phase(),
                error=f"unknown driver method: {method_name}",
            )

        return await self._driver.run_command(actor_id, command, args)

    async def _run_message_step(self, step_def: Any, _actors: Any) -> StepResult:
        actor_id = str(step_def.actor) if step_def.actor else "u_p1"
        content = str(step_def.message)
        channel: str | None = step_def.channel
        return await self._driver.send_message(actor_id, content, channel)

    def _run_assertion_step(
        self, _step_def: dict[str, Any], _idx: int, phase_before: str
    ) -> StepResult:
        return StepResult(
            phase_before=phase_before,
            phase_after=phase_before,
            emitted_outputs=[],
        )


def _check_assertion(
    result: StepResult, assert_def: dict[str, Any]
) -> tuple[bool, str]:
    if "phase" in assert_def:
        expected = str(assert_def["phase"])
        actual = result.phase_after
        if actual != expected:
            return False, f"Expected phase '{expected}', got '{actual}'"

    if "phase_not" in assert_def:
        expected = str(assert_def["phase_not"])
        actual = result.phase_after
        if actual == expected:
            return False, f"Expected phase not to be '{expected}', but it was"

    if "outputs_contain" in assert_def:
        needle = str(assert_def["outputs_contain"])
        found = any(needle in o.content for o in result.emitted_outputs)
        if not found:
            outputs = [o.content for o in result.emitted_outputs]
            return False, f"Expected outputs to contain '{needle}', got {outputs}"

    if "error" in assert_def:
        expected_error = str(assert_def["error"])
        if result.error != expected_error:
            return False, f"Expected error '{expected_error}', got '{result.error}'"

    if "no_error" in assert_def and assert_def["no_error"]:
        if result.error is not None:
            return False, f"Expected no error, got '{result.error}'"

    return True, ""
