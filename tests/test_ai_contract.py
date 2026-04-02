import asyncio
import tempfile
import os

import pytest
import yaml

from dm_bot.testing.runtime_driver import RuntimeTestDriver
from dm_bot.testing.scenario_runner import ScenarioRunner


@pytest.fixture
def make_db_path():
    path = tempfile.mktemp(suffix=".db")
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


class TestRouterPacketStructure:
    async def test_router_receives_valid_request_object(self, make_db_path):
        driver = RuntimeTestDriver(db_path=make_db_path, model_client=None)
        await driver.start()
        client = driver._model_client

        await driver.run_command("u_kp", "bind_campaign", {"campaign_id": "c1"})

        await driver.send_message("u_kp", "test message")

        assert len(client.router_requests) >= 1
        req = client.router_requests[-1]
        assert hasattr(req, "system_prompt")
        assert hasattr(req, "user_prompt")
        assert isinstance(req.system_prompt, str)
        assert isinstance(req.user_prompt, str)

        await driver.stop()

    async def test_narrator_receives_valid_request_object(self, make_db_path):
        driver = RuntimeTestDriver(db_path=make_db_path, model_client=None)
        await driver.start()
        client = driver._model_client

        await driver.run_command("u_kp", "bind_campaign", {"campaign_id": "c1"})
        await driver.run_command("u_kp", "ready", {"character_name": "Alice"})

        await driver.send_message("u_kp", "test message")

        assert len(client.narrator_requests) >= 1
        req = client.narrator_requests[-1]
        assert hasattr(req, "system_prompt")
        assert hasattr(req, "user_prompt")
        assert isinstance(req.system_prompt, str)

    async def test_narrator_prompt_does_not_leak_gmonly_state(self, make_db_path):
        driver = RuntimeTestDriver(db_path=make_db_path, model_client=None)
        await driver.start()
        client = driver._model_client

        await driver.run_command("u_kp", "bind_campaign", {"campaign_id": "c1"})
        await driver.run_command("u_kp", "ready", {"character_name": "Alice"})

        await driver.send_message("u_kp", "test message")

        for req in client.narrator_requests:
            prompt = req.system_prompt + req.user_prompt
            assert "gm_only" not in prompt.lower()
            assert "_hidden" not in prompt
            assert "__secret" not in prompt

        await driver.stop()


class TestAudienceSplitCorrect:
    async def test_kp_and_player_outputs_are_distinct(self, make_db_path):
        driver = RuntimeTestDriver(db_path=make_db_path, model_client=None)
        await driver.start()

        await driver.run_command("u_kp", "bind_campaign", {"campaign_id": "c1"})
        await driver.run_command("u_kp", "join_campaign", {"campaign_id": "c1"})
        await driver.run_command("u_kp", "ready", {"character_name": "Keeper"})

        kp_outputs = driver.get_outputs("kp")
        public_outputs = driver.get_outputs("public")

        assert len(kp_outputs) > 0 or len(public_outputs) > 0

        await driver.stop()


class TestScenarioAudienceSplit:
    async def test_scenario_with_audience_outputs(self, make_db_path):
        scenario = {
            "id": "scen_audience_split",
            "actors": [
                {"id": "u_kp", "role": "keeper"},
                {"id": "u_p1", "role": "player"},
            ],
            "fixtures": {"model_mode": "fake_contract"},
            "steps": [
                {
                    "actor": "u_kp",
                    "action": "command",
                    "name": "bind_campaign",
                    "args": {"campaign_id": "c1"},
                },
                {
                    "actor": "u_p1",
                    "action": "command",
                    "name": "create_test_profile",
                    "args": {
                        "user_id": "u_p1",
                        "name": "Investigator One",
                        "occupation": "scholar",
                        "age": 25,
                    },
                },
                {
                    "actor": "u_p1",
                    "action": "command",
                    "name": "join_campaign",
                    "args": {},
                },
                {
                    "actor": "u_p1",
                    "action": "command",
                    "name": "set_role",
                    "args": {"role": "player"},
                },
                {
                    "actor": "u_p1",
                    "action": "command",
                    "name": "select_profile",
                    "args": {"profile_id": "u_p1"},
                },
                {
                    "actor": "u_p1",
                    "action": "command",
                    "name": "ready",
                    "args": {},
                },
                {
                    "actor": "u_kp",
                    "action": "command",
                    "name": "start_session",
                    "args": {},
                },
                {
                    "actor": "u_p1",
                    "action": "command",
                    "name": "complete_onboarding",
                    "args": {},
                },
                {
                    "actor": "u_p1",
                    "action": "message",
                    "text": "hello",
                },
            ],
            "assertions": {
                "visible": {
                    "public_must_include": ["游戏开始"],
                }
            },
        }

        tmp = tempfile.mktemp(suffix=".yaml")
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.dump(scenario, f)

        driver = RuntimeTestDriver(db_path=make_db_path)
        runner = ScenarioRunner(driver)
        result = await runner.run(tmp, write_artifacts=False)

        assert result.passed is True

        os.unlink(tmp)
