import asyncio
import os
import tempfile
from pathlib import Path

import pytest
import yaml

from dm_bot.testing.runtime_driver import RuntimeTestDriver
from dm_bot.testing.scenario_runner import FailureCode, ScenarioRunner


@pytest.fixture
def make_db_path():
    path = tempfile.mktemp(suffix=".db")
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def tmp_yaml():
    def make(scenario_yaml: str) -> Path:
        path = Path(tempfile.mktemp(suffix=".yaml"))
        path.write_text(scenario_yaml, encoding="utf-8")
        return path

    return make


@pytest.fixture
def runner(make_db_path):
    driver = RuntimeTestDriver(db_path=make_db_path)
    return ScenarioRunner(driver)


class TestScenarioRunnerHappyPath:
    async def test_bind_campaign_and_assert_phase(self, make_db_path, runner, tmp_yaml):
        scenario = {
            "id": "test_happy",
            "actors": [{"id": "u_kp", "role": "keeper"}],
            "steps": [
                {
                    "command": "bind_campaign",
                    "actor": "u_kp",
                    "args": {"campaign_id": "camp_test"},
                },
                {"assert": {"phase": "lobby"}},
            ],
        }
        path = tmp_yaml(yaml.dump(scenario))
        result = await runner.run(path, write_artifacts=False)
        assert result.passed is True
        assert result.failure is None
        assert len(result.steps) == 2
        assert result.steps[0].phase_after == "lobby"
        assert result.steps[1].phase_before == "lobby"
        assert result.steps[1].phase_after == "lobby"

    async def test_snapshot_state_populated(self, make_db_path, runner, tmp_yaml):
        scenario = {
            "id": "test_state",
            "actors": [{"id": "u_kp", "role": "keeper"}],
            "steps": [
                {
                    "command": "bind_campaign",
                    "actor": "u_kp",
                    "args": {"campaign_id": "camp_test"},
                },
            ],
        }
        path = tmp_yaml(yaml.dump(scenario))
        result = await runner.run(path, write_artifacts=False)
        assert result.passed is True
        assert "sessions" in result.final_state


class TestScenarioRunnerAssertions:
    async def test_phase_assertion_passes(self, make_db_path, runner, tmp_yaml):
        scenario = {
            "id": "test_phase_ok",
            "actors": [{"id": "u_kp", "role": "keeper"}],
            "steps": [
                {
                    "command": "bind_campaign",
                    "actor": "u_kp",
                    "args": {"campaign_id": "c1"},
                },
                {"assert": {"phase": "lobby"}},
            ],
        }
        path = tmp_yaml(yaml.dump(scenario))
        result = await runner.run(path, write_artifacts=False)
        assert result.passed is True

    async def test_phase_assertion_fails_wrong_phase(
        self, make_db_path, runner, tmp_yaml
    ):
        scenario = {
            "id": "test_phase_wrong",
            "actors": [{"id": "u_kp", "role": "keeper"}],
            "steps": [
                {
                    "command": "bind_campaign",
                    "actor": "u_kp",
                    "args": {"campaign_id": "c1"},
                },
                {"assert": {"phase": "combat"}},
            ],
        }
        path = tmp_yaml(yaml.dump(scenario))
        result = await runner.run(path, write_artifacts=False)
        assert result.passed is False
        assert result.failure is not None
        assert result.failure.code == FailureCode.ASSERTION_FAILED

    async def test_unknown_command_returns_error_assertion(
        self, make_db_path, runner, tmp_yaml
    ):
        scenario = {
            "id": "test_unknown_cmd",
            "actors": [{"id": "u_kp", "role": "keeper"}],
            "steps": [
                {
                    "command": "bind_campaign",
                    "actor": "u_kp",
                    "args": {"campaign_id": "c1"},
                },
                {"command": "nonexistent_command", "actor": "u_kp", "args": {}},
                {"assert": {"error": "unknown command: nonexistent_command"}},
            ],
        }
        path = tmp_yaml(yaml.dump(scenario))
        result = await runner.run(path, write_artifacts=False)
        assert result.passed is True


class TestScenarioRunnerOutputs:
    async def test_outputs_contain_assertion(self, make_db_path, runner, tmp_yaml):
        scenario = {
            "id": "test_outputs",
            "actors": [{"id": "u_kp", "role": "keeper"}],
            "steps": [
                {
                    "command": "bind_campaign",
                    "actor": "u_kp",
                    "args": {"campaign_id": "camp_test"},
                },
                {
                    "assert": {
                        "outputs_contain": "campaign",
                    }
                },
            ],
        }
        path = tmp_yaml(yaml.dump(scenario))
        result = await runner.run(path, write_artifacts=False)
        assert result.passed is True


class TestRuntimeTestDriverStandalone:
    async def test_run_command_returns_step_result(self, make_db_path):
        driver = RuntimeTestDriver(db_path=make_db_path)
        await driver.start()
        result = await driver.run_command(
            "u_kp", "bind_campaign", {"campaign_id": "test"}
        )
        assert result.phase_after == "lobby"
        assert result.error is None
        await driver.stop()

    async def test_get_phase_after_bind(self, make_db_path):
        driver = RuntimeTestDriver(db_path=make_db_path)
        await driver.start()
        phase = driver.get_phase()
        assert phase == ""
        await driver.run_command("u_kp", "bind_campaign", {"campaign_id": "test"})
        phase = driver.get_phase()
        assert phase == "lobby"
        await driver.stop()

    async def test_simulate_crash_clears_state(self, make_db_path):
        driver = RuntimeTestDriver(db_path=make_db_path)
        await driver.start()
        await driver.run_command("u_kp", "bind_campaign", {"campaign_id": "test"})
        assert driver.get_phase() == "lobby"
        await driver.simulate_crash()
        assert driver.get_phase() == ""
        await driver.stop()

    async def test_restart_runtime_preserves_state(self, make_db_path):
        driver = RuntimeTestDriver(db_path=make_db_path)
        await driver.start()
        await driver.run_command("u_kp", "bind_campaign", {"campaign_id": "test"})
        await driver.restart_runtime()
        phase = driver.get_phase()
        assert phase == "lobby"
        await driver.stop()
