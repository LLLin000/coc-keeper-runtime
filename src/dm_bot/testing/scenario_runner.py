from __future__ import annotations
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, cast

import yaml

from dm_bot.testing.runtime_driver import RuntimeTestDriver
from dm_bot.testing.step_result import StepResult


class FailureCode(str, Enum):
    PHASE_TRANSITION_MISMATCH = "phase_transition_mismatch"
    ASSERTION_FAILED = "assertion_failed"
    COMMAND_ERROR = "command_error"
    UNKNOWN_STEP_TYPE = "unknown_step_type"
    MISSING_ACTOR = "missing_actor"
    MISSING_STEP_FIELD = "missing_step_field"


@dataclass
class Failure:
    code: FailureCode
    message: str
    step_index: int
    details: dict[str, object] = field(default_factory=dict)


@dataclass
class ScenarioResult:
    scenario_id: str
    passed: bool
    steps: list[StepResult]
    phase_timeline: list[str]
    final_state: dict[str, object]
    failure: Failure | None
    artifact_dir: Path | None


class ScenarioRunner:
    def __init__(self, driver: RuntimeTestDriver) -> None:
        self._driver = driver

    async def run(
        self,
        scenario_path: str | Path,
        *,
        write_artifacts: bool = True,
        artifact_dir: str | Path = "artifacts/scenarios",
        fail_fast: bool = False,
    ) -> ScenarioResult:
        path = Path(scenario_path)
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        scenario: dict[str, Any] = (
            cast(dict[str, Any], raw) if isinstance(raw, dict) else {}
        )
        scenario_id = str(scenario.get("id", path.stem))

        steps_def: list[dict[str, Any]] = cast(
            list[dict[str, Any]], scenario.get("steps", [])
        )
        actors: dict[str, dict[str, Any]] = {
            str(a["id"]): a
            for a in cast(list[dict[str, Any]], scenario.get("actors", []))
        }
        fixtures: dict[str, Any] = cast(dict[str, Any], scenario.get("fixtures", {}))

        self._configure_driver(fixtures)

        await self._driver.start()

        step_results: list[StepResult] = []
        phase_timeline: list[str] = []
        failure: Failure | None = None
        last_result: StepResult | None = None

        for idx, step_def in enumerate(steps_def):
            phase_before = self._driver.get_phase()

            if "command" in step_def:
                result = await self._run_command_step(step_def, actors)
                step_results.append(result)
                last_result = result
            elif "message" in step_def:
                result = await self._run_message_step(step_def, actors)
                step_results.append(result)
                last_result = result
            elif "assert" in step_def:
                if last_result is None:
                    failure = Failure(
                        code=FailureCode.MISSING_STEP_FIELD,
                        message=f"Step {idx} is an assert with no preceding command",
                        step_index=idx,
                    )
                    break
                ok, msg = _check_assertion(last_result, step_def["assert"])
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
                    message=f"Step {idx} has no 'command', 'message', or 'assert' key",
                    step_index=idx,
                )
                break

            if fail_fast and last_result.error is None and failure is None:
                assert_def = step_def.get("assert")
                if assert_def:
                    ok, msg = _check_assertion(last_result, assert_def)
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
            artifact_path = Path(artifact_dir) / scenario_id
            _write_artifacts(
                artifact_path, scenario_id, step_results, phase_timeline, final_state
            )

        if failure is None:
            assertion_idx = 0
            for idx, step_def in enumerate(steps_def):
                assert_def = step_def.get("assert")
                if assert_def:
                    cmd_idx = idx - assertion_idx - 1
                    if cmd_idx < len(step_results):
                        ok, msg = _check_assertion(step_results[cmd_idx], assert_def)
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
            passed=failure is None,
            steps=step_results,
            phase_timeline=phase_timeline,
            final_state=final_state,
            failure=failure,
            artifact_dir=artifact_path,
        )

    def _configure_driver(self, _fixtures: dict[str, Any]) -> None:
        pass

    async def _run_command_step(
        self, step_def: dict[str, Any], _actors: dict[str, dict[str, Any]]
    ) -> StepResult:
        actor_id = str(step_def.get("actor", "u_kp"))
        command = str(step_def["command"])
        args: dict[str, Any] = dict(step_def.get("args", {}))
        return await self._driver.run_command(actor_id, command, args)

    async def _run_message_step(
        self, step_def: dict[str, Any], _actors: dict[str, dict[str, Any]]
    ) -> StepResult:
        actor_id = str(step_def.get("actor", "u_p1"))
        content = str(step_def["message"])
        channel: str | None = (
            str(step_def["channel"]) if step_def.get("channel") else None
        )
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


def _write_artifacts(
    artifact_dir: Path,
    scenario_id: str,
    step_results: list[StepResult],
    phase_timeline: list[str],
    final_state: dict[str, object],
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)

    timeline_path = artifact_dir / "timeline.json"
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(
            {"scenario_id": scenario_id, "timeline": phase_timeline},
            f,
            ensure_ascii=False,
            indent=2,
        )

    outputs_path = artifact_dir / "outputs.json"
    outputs_data: list[dict[str, Any]] = []
    for idx, sr in enumerate(step_results):
        for o in sr.emitted_outputs:
            outputs_data.append(
                {
                    "step": idx,
                    "audience": o.audience,
                    "content": o.content,
                    "timestamp": o.timestamp,
                    "message_type": o.message_type,
                }
            )
    with open(outputs_path, "w", encoding="utf-8") as f:
        json.dump(outputs_data, f, ensure_ascii=False, indent=2)

    state_path = artifact_dir / "final_state.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(final_state, f, ensure_ascii=False, indent=2, default=str)

    steps_path = artifact_dir / "steps.json"
    steps_data: list[dict[str, Any]] = [
        {
            "phase_before": sr.phase_before,
            "phase_after": sr.phase_after,
            "error": sr.error,
            "output_count": len(sr.emitted_outputs),
        }
        for sr in step_results
    ]
    with open(steps_path, "w", encoding="utf-8") as f:
        json.dump(steps_data, f, ensure_ascii=False, indent=2)
