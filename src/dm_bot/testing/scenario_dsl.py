from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class ScenarioMode(str, Enum):
    ACCEPTANCE = "acceptance"
    CONTRACT = "contract"
    CHAOS = "chaos"
    RECOVERY = "recovery"


class DbMode(str, Enum):
    TEMP_SQLITE = "temp_sqlite"
    PERSISTENT = "persistent"


class ModelMode(str, Enum):
    FAKE_CONTRACT = "fake_contract"
    RECORDED = "recorded"
    LIVE = "live"


@dataclass
class Actor:
    id: str
    kind: str
    user_id: str


@dataclass
class Step:
    actor: str
    action: str
    name: str = ""
    args: dict[str, Any] = field(default_factory=dict)
    message: str = ""
    channel: str | None = None
    assert_: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if "assert" in self.__dict__:
            self.assert_ = self.__dict__.pop("assert")


@dataclass
class Fixtures:
    adventure: str | None = None
    dice_seed: int | None = None
    model_mode: ModelMode = ModelMode.FAKE_CONTRACT
    db_mode: DbMode = DbMode.TEMP_SQLITE


@dataclass
class Assertions:
    phase_timeline: list[str] = field(default_factory=list)
    final_phase: str = ""
    visible_public_must_include: list[str] = field(default_factory=list)
    visible_kp_must_include: list[str] = field(default_factory=list)
    visible_player_forbidden: list[str] = field(default_factory=list)
    state_campaign_members: int | None = None
    state_no_duplicate_members: bool = False
    persistence_restart_recoverable: bool | None = None
    narration_must_not_reveal_hidden_truth: bool | None = None


@dataclass
class Scenario:
    id: str
    title: str
    tags: list[str] = field(default_factory=list)
    mode: ScenarioMode = ScenarioMode.ACCEPTANCE
    actors: dict[str, Actor] = field(default_factory=dict)
    fixtures: Fixtures = field(default_factory=Fixtures)
    steps: list[Step] = field(default_factory=list)
    assertions: Assertions = field(default_factory=Assertions)


class ScenarioValidationError(Exception):
    def __init__(self, message: str, field_name: str | None = None) -> None:
        self.field_name = field_name
        super().__init__(message)


class ScenarioValidator:
    REQUIRED_FIELDS = ["id", "title", "steps"]
    VALID_ACTIONS = ["command", "message", "assert"]

    def validate(self, data: dict[str, Any]) -> None:
        for field_name in self.REQUIRED_FIELDS:
            if field_name not in data:
                raise ScenarioValidationError(
                    f"Missing required field: {field_name}", field_name=field_name
                )

        steps = data.get("steps", [])
        if not steps:
            raise ScenarioValidationError(
                "Scenario must have at least one step", field_name="steps"
            )

        actors = data.get("actors", {})
        for idx, step in enumerate(steps):
            if "actor" not in step:
                raise ScenarioValidationError(
                    f"Step {idx} missing 'actor' field",
                    field_name=f"steps[{idx}].actor",
                )
            actor_id = step["actor"]
            if actor_id not in actors and actor_id not in ["kp", "p1", "p2"]:
                pass

            has_action = any(a in step for a in self.VALID_ACTIONS)
            if not has_action:
                raise ScenarioValidationError(
                    f"Step {idx} must have one of: {self.VALID_ACTIONS}",
                    field_name=f"steps[{idx}]",
                )


class ScenarioParser:
    def __init__(self) -> None:
        self._validator = ScenarioValidator()

    def parse(self, path: str | Path) -> Scenario:
        path = Path(path)
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        if raw is None:
            raise ScenarioValidationError("Empty scenario file", field_name=None)

        if isinstance(raw, dict):
            return self._parse_dict(raw, path.stem)
        raise ScenarioValidationError("Invalid scenario format", field_name=None)

    def parse_json(self, path: str | Path) -> Scenario:
        path = Path(path)
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        if raw is None:
            raise ScenarioValidationError("Empty scenario file", field_name=None)

        if isinstance(raw, dict):
            return self._parse_dict(raw, path.stem)
        raise ScenarioValidationError("Invalid scenario format", field_name=None)

    def _parse_dict(self, data: dict[str, Any], default_id: str) -> Scenario:
        self._validator.validate(data)

        actors: dict[str, Actor] = {}
        for actor_id, actor_data in data.get("actors", {}).items():
            actors[actor_id] = Actor(
                id=actor_id,
                kind=str(actor_data.get("kind", "player")),
                user_id=str(actor_data.get("user_id", actor_id)),
            )

        steps: list[Step] = []
        for step_data in data.get("steps", []):
            step_dict = dict(step_data)
            step = Step(
                actor=str(step_dict.get("actor", "")),
                action=str(step_dict.get("action", "")),
                name=str(step_dict.get("name", "")),
                args=dict(step_dict.get("args", {})),
                message=str(step_dict.get("message", "")),
                channel=step_dict.get("channel"),
            )
            if "assert" in step_dict:
                step.assert_ = dict(step_dict["assert"])
            steps.append(step)

        fixtures_data = data.get("fixtures", {})
        fixtures = Fixtures(
            adventure=fixtures_data.get("adventure"),
            dice_seed=fixtures_data.get("dice_seed"),
            model_mode=ModelMode(fixtures_data.get("model_mode", "fake_contract")),
            db_mode=DbMode(fixtures_data.get("db_mode", "temp_sqlite")),
        )

        assertions_data = data.get("assertions", {})
        assertions = Assertions(
            phase_timeline=list(assertions_data.get("phase_timeline", [])),
            final_phase=str(assertions_data.get("final_phase", "")),
            visible_public_must_include=list(
                assertions_data.get("visible", {}).get("public_must_include", [])
            ),
            visible_kp_must_include=list(
                assertions_data.get("visible", {}).get("kp_must_include", [])
            ),
            visible_player_forbidden=list(
                assertions_data.get("visible", {}).get("player_forbidden", [])
            ),
            state_campaign_members=assertions_data.get("state", {}).get(
                "campaign_members"
            ),
            state_no_duplicate_members=assertions_data.get("state", {}).get(
                "no_duplicate_members", False
            ),
            persistence_restart_recoverable=assertions_data.get("persistence", {}).get(
                "restart_recoverable"
            ),
            narration_must_not_reveal_hidden_truth=assertions_data.get(
                "narration", {}
            ).get("must_not_reveal_hidden_truth"),
        )

        return Scenario(
            id=str(data.get("id", default_id)),
            title=str(data.get("title", default_id)),
            tags=list(data.get("tags", [])),
            mode=ScenarioMode(data.get("mode", "acceptance")),
            actors=actors,
            fixtures=fixtures,
            steps=steps,
            assertions=assertions,
        )


class ScenarioRegistry:
    def __init__(self, base_dir: str | Path = "tests/scenarios") -> None:
        self._base_dir = Path(base_dir)
        self._scenarios: dict[str, Scenario] = {}
        self._parser = ScenarioParser()

    def scan(self) -> dict[str, Scenario]:
        self._scenarios.clear()
        if not self._base_dir.exists():
            return self._scenarios

        for yaml_file in self._base_dir.rglob("*.yaml"):
            try:
                scenario = self._parser.parse(yaml_file)
                self._scenarios[scenario.id] = scenario
            except Exception:
                pass

        for json_file in self._base_dir.rglob("*.json"):
            if json_file.name in ["run.json", "failure.json", "summary.md"]:
                continue
            try:
                scenario = self._parser.parse_json(json_file)
                self._scenarios[scenario.id] = scenario
            except Exception:
                pass

        return self._scenarios

    def get(self, scenario_id: str) -> Scenario | None:
        return self._scenarios.get(scenario_id)

    def list_by_tag(self, tag: str) -> list[Scenario]:
        return [s for s in self._scenarios.values() if tag in s.tags]

    def list_by_mode(self, mode: ScenarioMode) -> list[Scenario]:
        return [s for s in self._scenarios.values() if s.mode == mode]

    @property
    def scenarios(self) -> dict[str, Scenario]:
        return self._scenarios
