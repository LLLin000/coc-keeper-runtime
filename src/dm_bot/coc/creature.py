"""Creature instance management for runtime encounters."""

from uuid import uuid4

from pydantic import BaseModel, Field

from dm_bot.coc.bestiary import CreatureTemplate, Bestiary


class CreatureCondition(BaseModel):
    """Condition affecting a creature."""

    name: str
    duration: int | None = None  # Rounds, None = permanent
    effect: str = ""


class CreatureInstance(BaseModel):
    """A creature instance in play.

    This represents a specific creature in an encounter,
    with its current HP and conditions.
    """

    # Identity
    instance_id: str
    template_id: str
    name: str  # May be customized per instance

    # Current state
    hp: int
    hp_max: int
    mp: int = 0
    conditions: list[CreatureCondition] = Field(default_factory=list)

    # Attributes (may vary from template)
    attributes: dict[str, int]

    # Combat
    initiative: int = 0
    has_acted: bool = False

    # Encounter tracking
    seen_by: set[str] = Field(
        default_factory=set
    )  # Player IDs who have seen this creature

    def is_alive(self) -> bool:
        """Check if creature is alive."""
        return self.hp > 0

    def take_damage(self, damage: int) -> int:
        """Apply damage and return actual damage taken."""
        actual = min(damage, self.hp)
        self.hp -= actual
        return actual

    def heal(self, amount: int) -> int:
        """Heal creature and return actual healing."""
        actual = min(amount, self.hp_max - self.hp)
        self.hp += actual
        return actual

    def add_condition(self, condition: CreatureCondition) -> None:
        """Add a condition to the creature."""
        self.conditions.append(condition)

    def remove_condition(self, condition_name: str) -> None:
        """Remove a condition by name."""
        self.conditions = [c for c in self.conditions if c.name != condition_name]

    def has_condition(self, condition_name: str) -> bool:
        """Check if creature has a condition."""
        return any(c.name == condition_name for c in self.conditions)

    def mark_seen_by(self, player_id: str) -> bool:
        """Mark that a player has seen this creature.

        Returns True if this is the first time this player sees it.
        """
        is_first = player_id not in self.seen_by
        self.seen_by.add(player_id)
        return is_first

    def has_seen(self, player_id: str) -> bool:
        """Check if a player has seen this creature."""
        return player_id in self.seen_by

    def to_combatant_stats(self) -> dict:
        """Convert to CombatantStats-compatible dict."""
        from dm_bot.coc.bestiary import CreatureTemplate

        # Get template for combat values
        # This is a placeholder - in real usage, pass template
        return {
            "name": self.name,
            "dex": self.attributes.get("dex", 50),
            "hp": self.hp,
            "hp_max": self.hp_max,
        }


class CreatureManager:
    """Manages creature instances in a session."""

    def __init__(self, bestiary: Bestiary) -> None:
        self.bestiary = bestiary
        self.instances: dict[str, CreatureInstance] = {}

    def spawn(
        self,
        template_id: str,
        name: str | None = None,
        hp_modifier: int = 0,
    ) -> CreatureInstance:
        """Spawn a new creature instance from a template.

        Args:
            template_id: ID of the creature template
            name: Custom name (uses template name if None)
            hp_modifier: Modifier to HP (+/-)

        Returns:
            The created creature instance
        """
        template = self.bestiary.get(template_id)
        if not template:
            raise ValueError(f"Unknown creature template: {template_id}")

        # Roll random attributes if template has ranges
        attributes = template.attributes.roll_random()

        # Calculate HP
        hp = template.calculate_hp(attributes) + hp_modifier

        instance = CreatureInstance(
            instance_id=str(uuid4()),
            template_id=template_id,
            name=name or template.name_cn,
            hp=hp,
            hp_max=hp,
            mp=attributes.get("pow", 50) // 5,
            attributes=attributes,
        )

        self.instances[instance.instance_id] = instance
        return instance

    def get(self, instance_id: str) -> CreatureInstance | None:
        """Get a creature instance by ID."""
        return self.instances.get(instance_id)

    def remove(self, instance_id: str) -> None:
        """Remove a creature instance."""
        self.instances.pop(instance_id, None)

    def list_alive(self) -> list[CreatureInstance]:
        """List all alive creatures."""
        return [c for c in self.instances.values() if c.is_alive()]

    def list_by_template(self, template_id: str) -> list[CreatureInstance]:
        """List instances of a specific template."""
        return [c for c in self.instances.values() if c.template_id == template_id]

    def clear_dead(self) -> int:
        """Remove dead creatures and return count removed."""
        dead_ids = [cid for cid, c in self.instances.items() if not c.is_alive()]
        for cid in dead_ids:
            self.instances.pop(cid)
        return len(dead_ids)

    def export_state(self) -> dict:
        """Export all instances state."""
        return {iid: instance.model_dump() for iid, instance in self.instances.items()}

    def import_state(self, payload: dict) -> None:
        """Import instances state."""
        self.instances = {}
        for iid, data in payload.items():
            self.instances[iid] = CreatureInstance.model_validate(data)
