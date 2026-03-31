import asyncio
import pytest
from pathlib import Path

from dm_bot.testing.runtime_driver import RuntimeTestDriver
from dm_bot.testing.scenario_runner import ScenarioRunner, _evaluate_scenario_assertions
from dm_bot.testing.scenario_dsl import (
    ScenarioRegistry,
    Scenario,
    Assertions,
    ScenarioMode,
)
from dm_bot.testing.step_result import OutputRecord
from dm_bot.testing.failure_taxonomy import FailureCode


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


class TestScenarioAssertions:
    def _make_scenario(self, assertions: Assertions) -> Scenario:
        return Scenario(
            id="test",
            title="Test Scenario",
            mode=ScenarioMode.ACCEPTANCE,
            assertions=assertions,
        )

    def test_phase_timeline_mismatch_fails(self):
        scenario = self._make_scenario(Assertions(phase_timeline=["lobby", "playing"]))
        failure = _evaluate_scenario_assertions(scenario, ["lobby"], {}, [])
        assert failure is not None
        assert failure.code == FailureCode.PHASE_TRANSITION_MISMATCH
        assert "Expected" in failure.message

    def test_phase_timeline_match_passes(self):
        scenario = self._make_scenario(Assertions(phase_timeline=["lobby", "playing"]))
        failure = _evaluate_scenario_assertions(scenario, ["lobby", "playing"], {}, [])
        assert failure is None

    def test_state_campaign_members_mismatch_fails(self):
        scenario = self._make_scenario(Assertions(state_campaign_members=5))
        final_state = {
            "sessions": {"s1": {"members": [{"user_id": "u1"}, {"user_id": "u2"}]}}
        }
        failure = _evaluate_scenario_assertions(scenario, ["lobby"], final_state, [])
        assert failure is not None
        assert failure.code == FailureCode.SESSION_STATE_MISMATCH
        assert "Expected 5" in failure.message

    def test_state_campaign_members_match_passes(self):
        scenario = self._make_scenario(Assertions(state_campaign_members=2))
        final_state = {
            "sessions": {"s1": {"members": [{"user_id": "u1"}, {"user_id": "u2"}]}}
        }
        failure = _evaluate_scenario_assertions(scenario, ["lobby"], final_state, [])
        assert failure is None

    def test_no_duplicate_members_passes(self):
        scenario = self._make_scenario(Assertions(state_no_duplicate_members=True))
        final_state = {
            "sessions": {"s1": {"members": [{"user_id": "u1"}, {"user_id": "u2"}]}}
        }
        failure = _evaluate_scenario_assertions(scenario, ["lobby"], final_state, [])
        assert failure is None

    def test_duplicate_members_fails(self):
        scenario = self._make_scenario(Assertions(state_no_duplicate_members=True))
        final_state = {
            "sessions": {"s1": {"members": [{"user_id": "u1"}, {"user_id": "u1"}]}}
        }
        failure = _evaluate_scenario_assertions(scenario, ["lobby"], final_state, [])
        assert failure is not None
        assert failure.code == FailureCode.CONCURRENCY_INVARIANT_FAILURE

    def test_public_visibility_missing_fails(self):
        scenario = self._make_scenario(Assertions(visible_public_must_include=["就位"]))
        outputs = [
            OutputRecord(
                audience="kp", content="KP only", timestamp=0, message_type="system"
            ),
        ]
        failure = _evaluate_scenario_assertions(scenario, ["lobby"], {}, outputs)
        assert failure is not None
        assert failure.code == FailureCode.VISIBILITY_LEAK

    def test_public_visibility_match_passes(self):
        scenario = self._make_scenario(Assertions(visible_public_must_include=["就位"]))
        outputs = [
            OutputRecord(
                audience="public",
                content="玩家已就位",
                timestamp=0,
                message_type="system",
            ),
        ]
        failure = _evaluate_scenario_assertions(scenario, ["lobby"], {}, outputs)
        assert failure is None

    def test_kp_visibility_missing_fails(self):
        scenario = self._make_scenario(Assertions(visible_kp_must_include=["secret"]))
        outputs = [
            OutputRecord(
                audience="public",
                content="public info",
                timestamp=0,
                message_type="system",
            ),
        ]
        failure = _evaluate_scenario_assertions(scenario, ["lobby"], {}, outputs)
        assert failure is not None
        assert failure.code == FailureCode.VISIBILITY_LEAK

    def test_player_forbidden_fails(self):
        scenario = self._make_scenario(
            Assertions(visible_player_forbidden=["hidden_truth"])
        )
        outputs = [
            OutputRecord(
                audience="public",
                content="This reveals the hidden_truth",
                timestamp=0,
                message_type="system",
            ),
        ]
        failure = _evaluate_scenario_assertions(scenario, ["lobby"], {}, outputs)
        assert failure is not None
        assert failure.code == FailureCode.REVEAL_POLICY_VIOLATION

    def test_player_forbidden_passes(self):
        scenario = self._make_scenario(
            Assertions(visible_player_forbidden=["hidden_truth"])
        )
        outputs = [
            OutputRecord(
                audience="public",
                content="Safe public info",
                timestamp=0,
                message_type="system",
            ),
        ]
        failure = _evaluate_scenario_assertions(scenario, ["lobby"], {}, outputs)
        assert failure is None

    def test_empty_assertions_passes(self):
        scenario = self._make_scenario(Assertions())
        failure = _evaluate_scenario_assertions(scenario, ["lobby"], {}, [])
        assert failure is None
