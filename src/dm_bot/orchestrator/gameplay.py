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
            "scene_id": adventure.start_scene_id,
            "clues_found": [],
            "objectives": list(adventure.objectives),
            "module_state": adventure.state_defaults(),
            "ending_id": None,
        }

    def adventure_snapshot(self) -> dict[str, object]:
        if self.adventure is None:
            return {}
        scene_id = str(self.adventure_state.get("scene_id", self.adventure.start_scene_id))
        scene = self.adventure.scene_by_id(scene_id)
        module_state = dict(self.adventure_state.get("module_state", {}))
        return {
            "public": {
                "slug": self.adventure.slug,
                "title": self.adventure.title,
                "current_scene": scene.model_dump(),
                "objectives": list(self.adventure_state.get("objectives", [])),
                "state": self.adventure.public_state(module_state),
            },
            "gm": {
                "premise": self.adventure.premise,
                "state": self.adventure.gm_state(module_state),
                "endings": [ending.model_dump() for ending in self.adventure.endings],
            },
        }

    def set_adventure_scene(self, scene_id: str) -> None:
        if self.adventure is None:
            raise RuntimeError("adventure not loaded")
        self.adventure.scene_by_id(scene_id)
        self.adventure_state["scene_id"] = scene_id

    def record_adventure_clue(self, clue_id: str) -> None:
        clues = list(self.adventure_state.get("clues_found", []))
        if clue_id not in clues:
            clues.append(clue_id)
        self.adventure_state["clues_found"] = clues

    def update_adventure_state(self, **changes: object) -> None:
        module_state = dict(self.adventure_state.get("module_state", {}))
        module_state.update(changes)
        self.adventure_state["module_state"] = module_state

    def set_adventure_ending(self, ending_id: str) -> None:
        if self.adventure is None:
            raise RuntimeError("adventure not loaded")
        if ending_id not in {ending.id for ending in self.adventure.endings}:
            raise KeyError(ending_id)
        self.adventure_state["ending_id"] = ending_id

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
        slug = self.adventure_state.get("adventure_slug")
        if slug:
            from dm_bot.adventures.loader import load_adventure

            self.adventure = load_adventure(str(slug))

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
