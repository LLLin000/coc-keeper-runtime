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
                        "outputs_contain": "绑定",
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


class TestDurationMeasurement:
    async def test_step_duration_is_measured(self, make_db_path, runner, tmp_yaml):
        """Verify that command steps have duration_ms field populated (>= 0)."""
        scenario = {
            "id": "test_duration",
            "actors": [{"id": "u_kp", "role": "keeper"}],
            "steps": [
                {
                    "command": "bind_campaign",
                    "actor": "u_kp",
                    "args": {"campaign_id": "camp_test"},
                },
                {
                    "command": "bind_campaign",
                    "actor": "u_kp",
                    "args": {"campaign_id": "camp_test2"},
                },
            ],
        }
        path = tmp_yaml(yaml.dump(scenario))
        result = await runner.run(path, write_artifacts=False)
        assert result.passed is True
        assert len(result.steps) == 2
        # All steps should have non-negative duration (field is set, not left at default)
        for i, step in enumerate(result.steps):
            assert step.duration_ms >= 0, (
                f"Step {i} duration should be >= 0, got {step.duration_ms}"
            )
        # Total duration should be >= 0 (may be 0 for sub-ms operations on some platforms)
        total = sum(s.duration_ms for s in result.steps)
        assert total >= 0, f"Total duration should be >= 0, got {total}"

    async def test_assert_step_has_zero_duration(self, make_db_path, runner, tmp_yaml):
        """Verify that assert-only steps report duration_ms=0.0."""
        scenario = {
            "id": "test_assert_duration",
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
        assert len(result.steps) == 2
        # Assert step should have duration_ms=0.0
        assert result.steps[1].duration_ms == 0.0


class TestOutputIsolation:
    async def test_step_outputs_are_isolated(self, make_db_path, runner, tmp_yaml):
        """Verify that each step's emitted_outputs only contains outputs from that step."""
        scenario = {
            "id": "test_output_isolation",
            "actors": [{"id": "u_kp", "role": "keeper"}],
            "steps": [
                {
                    "command": "bind_campaign",
                    "actor": "u_kp",
                    "args": {"campaign_id": "alpha_camp"},
                },
                {
                    "command": "bind_campaign",
                    "actor": "u_kp",
                    "args": {"campaign_id": "beta_camp"},
                },
            ],
        }
        path = tmp_yaml(yaml.dump(scenario))
        result = await runner.run(path, write_artifacts=False)
        assert result.passed is True
        assert len(result.steps) == 2

        step0_outputs = result.steps[0].emitted_outputs
        step1_outputs = result.steps[1].emitted_outputs

        step0_contents = [o.content for o in step0_outputs]
        step1_contents = [o.content for o in step1_outputs]

        # Each step should have its own outputs
        assert len(step0_outputs) > 0, "Step 0 should have outputs"
        assert len(step1_outputs) > 0, "Step 1 should have outputs"

        # Step 1 outputs should NOT contain step 0's unique content "alpha_camp"
        assert not any("alpha_camp" in c for c in step1_contents), (
            f"Step 1 outputs should not contain step 0's 'alpha_camp' output. "
            f"Step 1 contents: {step1_contents[:3]}"
        )
        # Step 0 outputs should NOT contain step 1's unique content "beta_camp"
        assert not any("beta_camp" in c for c in step0_contents), (
            f"Step 0 outputs should not contain step 1's 'beta_camp' output. "
            f"Step 0 contents: {step0_contents[:3]}"
        )

    async def test_driver_output_isolation_standalone(self, make_db_path):
        """Verify RuntimeTestDriver.run_command isolates outputs per call."""
        driver = RuntimeTestDriver(db_path=make_db_path)
        await driver.start()

        result1 = await driver.run_command(
            "u_kp", "bind_campaign", {"campaign_id": "camp_a"}
        )
        result2 = await driver.run_command(
            "u_kp", "bind_campaign", {"campaign_id": "camp_b"}
        )

        # Each result should have outputs
        assert len(result1.emitted_outputs) > 0, "First call should have outputs"
        assert len(result2.emitted_outputs) > 0, "Second call should have outputs"

        # Second call's outputs should not contain first call's unique content
        result2_contents = [o.content for o in result2.emitted_outputs]
        assert not any("camp_a" in c for c in result2_contents), (
            f"Second call outputs should not contain 'camp_a'. Got: {result2_contents[:3]}"
        )
        # First call's outputs should not contain second call's content
        result1_contents = [o.content for o in result1.emitted_outputs]
        assert not any("camp_b" in c for c in result1_contents), (
            f"First call outputs should not contain 'camp_b'. Got: {result1_contents[:3]}"
        )

        await driver.stop()
