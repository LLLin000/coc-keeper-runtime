from pydantic import BaseModel, Field

from dm_bot.rules.actions import RuleAction


class Combatant(BaseModel):
    name: str
    initiative: int
    armor_class: int
    hit_points: int
    conditions: list[str] = Field(default_factory=list)


class CombatEncounter(BaseModel):
    order: list[str] = Field(default_factory=list)
    combatants: dict[str, Combatant] = Field(default_factory=dict)
    active_index: int = 0

    def start(self, combatants: list[Combatant]) -> None:
        sorted_combatants = sorted(combatants, key=lambda item: item.initiative, reverse=True)
        self.order = [item.name for item in sorted_combatants]
        self.combatants = {item.name: item for item in sorted_combatants}
        self.active_index = 0

    @property
    def active_combatant(self) -> Combatant:
        return self.combatants[self.order[self.active_index]]

    def advance_turn(self) -> None:
        self.active_index = (self.active_index + 1) % len(self.order)

    def summary(self) -> str:
        pieces = []
        for index, name in enumerate(self.order):
            combatant = self.combatants[name]
            marker = "->" if index == self.active_index else "  "
            pieces.append(
                f"{marker} {combatant.name} HP {combatant.hit_points} AC {combatant.armor_class}"
            )
        return "\n".join(pieces)

    def resolve_attack(self, engine, action: RuleAction) -> dict[str, object]:
        result = engine.execute(action)
        if result["hit"]:
            target = self.combatants[result["target"]]
            target.hit_points = max(0, target.hit_points - int(result["damage"]))
        return result
