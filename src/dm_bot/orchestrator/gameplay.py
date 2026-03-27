from dm_bot.gameplay.combat import CombatEncounter, Combatant
from dm_bot.gameplay.modes import GameModeState
from dm_bot.characters.models import CharacterRecord
from dm_bot.router.contracts import TurnPlan
from dm_bot.rules.actions import LookupAction, RuleAction
from dm_bot.adventures.models import AdventurePackage


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
        self.adventure: AdventurePackage | None = None
        self.adventure_state: dict[str, object] = {}

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

    def end_scene(self) -> None:
        self.mode_state.enter_dm()

    def next_combat_turn(self) -> CombatEncounter | None:
        if self.combat is None:
            return None
        self.combat.advance_turn()
        return self.combat

    def active_combatant_name(self) -> str | None:
        if self.combat is None:
            return None
        return self.combat.active_combatant.name

    def combat_summary(self) -> str:
        if self.combat is None:
            return "combat not active"
        return self.combat.summary()

    def load_adventure(self, adventure: AdventurePackage) -> None:
        self.adventure = adventure
        self.adventure_state = {
            "adventure_slug": adventure.slug,
            "scene_id": adventure.scenes[0].id if adventure.scenes else None,
            "clues_found": [],
            "objectives": list(adventure.objectives),
        }

    def export_state(self) -> dict[str, object]:
        return {
            "mode": self.mode_state.model_dump(),
            "combat": self.combat.model_dump() if self.combat else None,
            "registry": {
                user_id: character.model_dump()
                for user_id, character in self.registry._characters.items()
            },
            "adventure_state": self.adventure_state,
        }

    def import_state(self, state: dict[str, object]) -> None:
        self.mode_state = GameModeState.model_validate(state.get("mode", {"mode": "dm", "scene_speakers": []}))
        combat = state.get("combat")
        self.combat = CombatEncounter.model_validate(combat) if combat else None
        registry = {}
        for user_id, payload in dict(state.get("registry", {})).items():
            registry[user_id] = CharacterRecord.model_validate(payload)
        self.registry._characters = registry
        self.adventure_state = dict(state.get("adventure_state", {}))

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
