from __future__ import annotations

import datetime
from dataclasses import asdict
from pathlib import Path
from typing import Any

import orjson


MAX_CONTENT_SIZE = 10 * 1024


def _truncate_content(
    content: str, max_size: int = MAX_CONTENT_SIZE
) -> tuple[str, bool]:
    if len(content.encode("utf-8")) > max_size:
        return content[:max_size], True
    return content, False


class ArtifactWriter:
    def __init__(self, base_dir: str | Path = "artifacts/scenarios") -> None:
        self._base_dir = Path(base_dir)

    def write_run(
        self,
        scenario_id: str,
        result: Any,
        state_before: dict[str, Any] | None = None,
        state_after: dict[str, Any] | None = None,
    ) -> Path:
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y%m%d_%H%M%S"
        )
        run_dir = self._base_dir / scenario_id / timestamp
        run_dir.mkdir(parents=True, exist_ok=True)

        self._write_run_json(run_dir, scenario_id, result)
        self._write_summary_md(run_dir, scenario_id, result)
        self._write_timeline_json(run_dir, scenario_id, result)
        self._write_outputs_by_audience(run_dir, result)
        if state_before:
            self._write_state_before(run_dir, state_before)
        if state_after:
            self._write_state_after(run_dir, state_after)
        if result.failure:
            self._write_failure_json(run_dir, result)

        return run_dir

    def _write_run_json(self, run_dir: Path, scenario_id: str, result: Any) -> None:
        steps_data = []
        for idx, step in enumerate(result.steps):
            step_dict: dict[str, Any] = {
                "index": idx,
                "phase_before": step.phase_before,
                "phase_after": step.phase_after,
                "outputs": [],
                "duration_ms": step.duration_ms,
            }
            if step.error:
                step_dict["error"] = step.error

            for output in step.emitted_outputs:
                content, truncated = _truncate_content(output.content)
                step_dict["outputs"].append(
                    {
                        "audience": output.audience,
                        "content": content,
                        "truncated": truncated,
                        "timestamp": output.timestamp,
                        "message_type": output.message_type,
                    }
                )

            steps_data.append(step_dict)

        run_data = {
            "scenario_id": scenario_id,
            "title": getattr(result, "title", scenario_id),
            "mode": getattr(result, "mode", "acceptance"),
            "passed": result.passed,
            "run_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "duration_ms": sum(s.duration_ms for s in result.steps),
            "steps": steps_data,
            "phase_timeline": result.phase_timeline,
            "final_state_summary": self._summarize_state(result.final_state),
            "failure": None,
        }

        if result.failure:
            run_data["failure"] = {
                "code": result.failure.code.value
                if hasattr(result.failure.code, "value")
                else str(result.failure.code),
                "message": result.failure.message,
                "step_index": result.failure.step_index,
                "details": result.failure.details,
            }

        run_path = run_dir / "run.json"
        with open(run_path, "wb") as f:
            f.write(orjson.dumps(run_data, option=orjson.OPT_INDENT_2))

    def _write_summary_md(self, run_dir: Path, scenario_id: str, result: Any) -> None:
        status = "PASSED" if result.passed else "FAILED"

        lines = [
            f"# Scenario: {scenario_id}",
            "",
            f"**Status:** {status}",
            "",
            f"**Duration:** {sum(s.duration_ms for s in result.steps):.0f}ms",
            "",
            "## Phase Timeline",
            "",
        ]

        if result.phase_timeline:
            for phase in result.phase_timeline:
                lines.append(f"- {phase}")
        else:
            lines.append("*No phase transitions recorded*")

        lines.extend(
            [
                "",
                "## Steps",
                "",
            ]
        )

        for idx, step in enumerate(result.steps):
            lines.append(f"### Step {idx}")
            lines.append(f"- **Actor:** {getattr(step, 'actor', 'N/A')}")
            lines.append(f"- **Phase:** {step.phase_before} → {step.phase_after}")
            if step.error:
                lines.append(f"- **Error:** {step.error}")
            if step.emitted_outputs:
                lines.append(f"- **Outputs:** {len(step.emitted_outputs)}")
            lines.append("")

        if result.failure:
            lines.extend(
                [
                    "## Failure",
                    "",
                    f"**Code:** {result.failure.code}",
                    f"**Message:** {result.failure.message}",
                    f"**Step:** {result.failure.step_index}",
                    "",
                ]
            )

        summary_path = run_dir / "summary.md"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_timeline_json(
        self, run_dir: Path, scenario_id: str, result: Any
    ) -> None:
        timeline_data = {
            "scenario_id": scenario_id,
            "phases": result.phase_timeline,
        }

        timeline_path = run_dir / "timeline.json"
        with open(timeline_path, "wb") as f:
            f.write(orjson.dumps(timeline_data, option=orjson.OPT_INDENT_2))

    def _write_outputs_by_audience(self, run_dir: Path, result: Any) -> None:
        outputs_by_audience: dict[str, list[dict[str, Any]]] = {}

        for step_idx, step in enumerate(result.steps):
            for output in step.emitted_outputs:
                audience = output.audience
                if audience not in outputs_by_audience:
                    outputs_by_audience[audience] = []

                content, truncated = _truncate_content(output.content)
                outputs_by_audience[audience].append(
                    {
                        "step": step_idx,
                        "content": content,
                        "truncated": truncated,
                        "timestamp": output.timestamp,
                        "message_type": output.message_type,
                    }
                )

        for audience, outputs in outputs_by_audience.items():
            safe_name = audience.replace("/", "_").replace(" ", "_")
            output_path = run_dir / f"outputs_{safe_name}.json"
            with open(output_path, "wb") as f:
                f.write(orjson.dumps(outputs, option=orjson.OPT_INDENT_2))

    def _write_state_before(self, run_dir: Path, state: dict[str, Any]) -> None:
        state_path = run_dir / "state_before.json"
        with open(state_path, "wb") as f:
            f.write(orjson.dumps(state, option=orjson.OPT_INDENT_2, default=str))

    def _write_state_after(self, run_dir: Path, state: dict[str, Any]) -> None:
        state_path = run_dir / "state_after.json"
        with open(state_path, "wb") as f:
            f.write(orjson.dumps(state, option=orjson.OPT_INDENT_2, default=str))

    def _write_failure_json(self, run_dir: Path, result: Any) -> None:
        if not result.failure:
            return

        failure_data = {
            "code": result.failure.code.value
            if hasattr(result.failure.code, "value")
            else str(result.failure.code),
            "message": result.failure.message,
            "step_index": result.failure.step_index,
            "details": result.failure.details,
        }

        if result.failure.details.get("expected"):
            failure_data["expected"] = result.failure.details["expected"]
        if result.failure.details.get("actual"):
            failure_data["actual"] = result.failure.details["actual"]

        failure_path = run_dir / "failure.json"
        with open(failure_path, "wb") as f:
            f.write(orjson.dumps(failure_data, option=orjson.OPT_INDENT_2))

    def _summarize_state(self, state: dict[str, Any]) -> dict[str, Any]:
        summary: dict[str, Any] = {}
        if "sessions" in state:
            sessions = state["sessions"]
            if isinstance(sessions, dict):
                summary["session_count"] = len(sessions)
        return summary
