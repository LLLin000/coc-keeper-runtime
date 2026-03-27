from collections.abc import Callable

from dm_bot.rules.actions import LookupAction, RuleAction


class RulesEngineError(RuntimeError):
    pass


class RulesEngine:
    def __init__(
        self,
        *,
        compendium,
        roll_resolver: Callable[[str], int] | None = None,
    ) -> None:
        self._compendium = compendium
        self._roll_resolver = roll_resolver or (lambda expr: 10)

    def lookup(self, action: LookupAction) -> dict[str, object]:
        try:
            return self._compendium.lookup(action)
        except (ValueError, KeyError) as exc:
            raise RulesEngineError(str(exc)) from exc

    def execute(self, action: RuleAction) -> dict[str, object]:
        if action.action == "attack_roll":
            return self._execute_attack_roll(action)
        raise RulesEngineError(f"unsupported action: {action.action}")

    def _execute_attack_roll(self, action: RuleAction) -> dict[str, object]:
        if action.target is None:
            raise RulesEngineError("attack_roll requires a target")

        if "attack_bonus" not in action.parameters:
            raise RulesEngineError("attack_roll requires attack_bonus")

        roll = self._roll_resolver("1d20")
        attack_bonus = int(action.parameters["attack_bonus"])
        total = roll + attack_bonus
        return {
            "action": "attack_roll",
            "actor": action.actor.name,
            "target": action.target.name,
            "weapon": action.parameters.get("weapon", "unarmed"),
            "roll": roll,
            "attack_bonus": attack_bonus,
            "total": total,
            "hit": total >= action.target.armor_class,
        }
