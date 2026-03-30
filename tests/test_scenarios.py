import asyncio
import pytest
from pathlib import Path

from dm_bot.testing.runtime_driver import RuntimeTestDriver
from dm_bot.testing.scenario_runner import ScenarioRunner
from dm_bot.testing.scenario_dsl import ScenarioRegistry


def scenarios() -> list[tuple[str, Path]]:
    registry = ScenarioRegistry()
    registry.scan()
    return [(sid, s.path) for sid, s in registry._scenarios.items() if s.path]


@pytest.mark.parametrize("scenario_id,scenario_path", scenarios())
def test_scenario(scenario_id: str, scenario_path: Path):
    asyncio.run(_run_scenario(scenario_id, scenario_path))


async def _run_scenario(scenario_id: str, scenario_path: Path) -> None:
    driver = RuntimeTestDriver(dice_seed=42, db_path=":memory:")
    runner = ScenarioRunner(driver)
    result = await runner.run(scenario_path, write_artifacts=False)
    if not result.passed:
        failure_msg = (
            f"{result.failure.code}: {result.failure.message}"
            if result.failure
            else "unknown"
        )
        pytest.fail(f"Scenario {scenario_id} failed: {failure_msg}")
