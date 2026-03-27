from dm_bot.gameplay.combat import CombatEncounter, Combatant
from dm_bot.gameplay.modes import GameModeState
from dm_bot.characters.models import CharacterRecord
from dm_bot.router.contracts import TurnPlan
from dm_bot.rules.actions import LookupAction, RuleAction


class CharacterRegistry:
    def __init__(self) -> None:
        self._characters: dict[str, CharacterRecord] = {}

    def put(self, user_id: str, character: CharacterRecord) -> None:
        self._characters[user_id] = character

    def get(self, user_id: str) -> CharacterRecord | None:
        return self._characters.get(user_id)


class GameplayOrchestrator:
    def __init__(self, *, importer, registry: CharacterRegistry, rules_engine) -> None:
        self._importer = importer
        self.registry = registry
        self._rules_engine = rules_engine
        self.mode_state = GameModeState()
        self.combat: CombatEncounter | None = None

    def import_character(self, *, user_id: str, provider: str, external_id: str) -> CharacterRecord:
        character = self._importer.import_character(provider, external_id)
        self.registry.put(user_id, character)
        return character

    def enter_scene(self, *, speakers: list[str]) -> None:
        self.mode_state.enter_scene(speakers=speakers)

    def enter_dm(self) -> None:
        self.mode_state.enter_dm()

    def start_combat(self, *, combatants: list[Combatant]) -> CombatEncounter:
        encounter = CombatEncounter()
        encounter.start(combatants)
        self.combat = encounter
        self.mode_state.mode = "combat"
        return encounter

    def resolve_plan(self, plan: TurnPlan) -> list[dict[str, object]]:
        results: list[dict[str, object]] = []
        for call in plan.tool_calls:
            if call.name == "rules.lookup":
                result = self._rules_engine.lookup(LookupAction.model_validate(call.arguments))
            elif call.name == "rules.attack_roll":
                result = self._rules_engine.execute(RuleAction.model_validate(call.arguments))
            else:
                result = {"tool": call.name, "status": "unsupported"}
            results.append(result)
        return results
