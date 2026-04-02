---
phase: E81-creature-bestiary
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/coc/bestiary.py
  - src/dm_bot/coc/creature.py
  - data/bestiary/creatures.json
  - src/dm_bot/rules/coc/combat.py
  - src/dm_bot/rules/coc/sanity.py
  - tests/rules/coc/test_bestiary.py
  - tests/scenarios/acceptance/scen_creature_encounter.yaml
autonomous: true
requirements:
  - BESTIARY-01
  - BESTIARY-02
  - BESTIARY-03
  - BESTIARY-04
  - BESTIARY-05

must_haves:
  truths:
    - "Bestiary data structure supports COC creature stats (STR, CON, SIZ, etc.)"
    - "At least 10 common creatures defined (Deep One, Shoggoth, Ghoul, etc.)"
    - "Creature stats integrate with combat system (can be targets/attackers)"
    - "Sanity loss values are linked to creature encounters"
    - "Creatures can be used in fuzhe_mini adventure scenarios"
  artifacts:
    - path: "src/dm_bot/coc/bestiary.py"
      provides: "CreatureTemplate, CreatureCategory, SanLoss models"
      min_lines: 150
    - path: "data/bestiary/creatures.json"
      provides: "10+ creature definitions"
      min_lines: 300
    - path: "src/dm_bot/coc/creature.py"
      provides: "CreatureInstance runtime state management"
      min_lines: 100
    - path: "tests/rules/coc/test_bestiary.py"
      provides: "Unit tests for creatures and combat integration"
      min_lines: 80
  key_links:
    - from: "CreatureTemplate"
      to: "CombatantStats"
      via: "to_combatant_stats() method"
    - from: "CreatureInstance"
      to: "combat.py"
      via: "combatants dict"
    - from: "creatures.json"
      to: "BestiaryLoader"
      via: "load() method"
---

<objective>
Create a bestiary system with stats for common COC creatures.

Purpose: Enable creature encounters in adventures with proper combat and sanity mechanics.
Output: Complete bestiary with 10+ creatures, combat integration, and sanity loss tracking.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@src/dm_bot/rules/coc/combat.py
@src/dm_bot/rules/coc/sanity.py
@src/dm_bot/characters/models.py

## Key Types from Existing Code

From combat.py:
```python
class CombatantStats(BaseModel):
    name: str
    dex: int
    fighting: int = 0
    dodge: int = 0
    hp: int
    armor: int = 0
    damage_bonus: int = 0
```

From sanity.py:
```python
class SanityLoss(BaseModel):
    first_encounter: int
    subsequent: int
    indefinite: bool = False
```

From models.py:
```python
class COCAttributes(BaseModel):
    str: int
    con: int
    siz: int
    dex: int
    app: int
    int: int
    pow: int
    edu: int
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create bestiary models</name>
  <files>src/dm_bot/coc/bestiary.py</files>
  <action>
Create bestiary data models:

```python
"""COC 7th Edition Bestiary System.

Creature templates and bestiary management for Call of Cthulhu.
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from dm_bot.characters.models import COCAttributes


class CreatureCategory(StrEnum):
    """Categories of COC creatures."""
    HUMAN = "human"  # Cultists, NPCs
    MONSTER = "monster"  # Ghouls, zombies
    MYTHOS = "mythos"  # Deep Ones, Shoggoths
    BEAST = "beast"  # Animals
    UNDEAD = "undead"  # Zombies, vampires


class CreatureSize(StrEnum):
    """Creature size categories."""
    TINY = "tiny"  # < 1 SIZ
    SMALL = "small"  # 1-15 SIZ
    MEDIUM = "medium"  # 16-30 SIZ
    LARGE = "large"  # 31-60 SIZ
    HUGE = "huge"  # 61-100 SIZ
    COLOSSAL = "colossal"  # > 100 SIZ


class SanLoss(BaseModel):
    """SAN loss from encountering a creature.
    
    COC 7e: First time seeing vs subsequent encounters.
    Some creatures cause indefinite insanity on first sight.
    """
    first_encounter: int = 0  # SAN loss on first seeing
    subsequent: int = 0  # SAN loss on subsequent encounters
    indefinite: bool = False  # Causes indefinite insanity
    
    def get_loss(self, is_first: bool = True) -> int:
        """Get SAN loss for encounter."""
        return self.first_encounter if is_first else self.subsequent


class CreatureAttributes(BaseModel):
    """Creature attributes (may have ranges)."""
    str: int | tuple[int, int] = 50
    con: int | tuple[int, int] = 50
    siz: int | tuple[int, int] = 50
    dex: int | tuple[int, int] = 50
    int: int | tuple[int, int] = 50
    pow: int | tuple[int, int] = 50
    
    def get_fixed(self) -> dict[str, int]:
        """Get fixed attribute values (use average for ranges)."""
        attrs = {}
        for key in ["str", "con", "siz", "dex", "int", "pow"]:
            value = getattr(self, key)
            if isinstance(value, tuple):
                attrs[key] = (value[0] + value[1]) // 2
            else:
                attrs[key] = value
        return attrs
    
    def roll_random(self) -> dict[str, int]:
        """Roll random values for ranged attributes."""
        import random
        attrs = {}
        for key in ["str", "con", "siz", "dex", "int", "pow"]:
            value = getattr(self, key)
            if isinstance(value, tuple):
                attrs[key] = random.randint(value[0], value[1])
            else:
                attrs[key] = value
        return attrs


class CreatureAbility(BaseModel):
    """Special ability a creature has."""
    name: str
    name_cn: str
    description: str
    effect: str = ""  # Mechanical effect


class CreatureTemplate(BaseModel):
    """Template for a COC creature from the bestiary.
    
    This is the static data from the rulebook.
    For runtime instances, see CreatureInstance.
    """
    # Identity
    id: str  # Unique identifier (e.g., "deep_one")
    name: str  # English name
    name_cn: str  # Chinese name
    category: CreatureCategory
    size: CreatureSize = CreatureSize.MEDIUM
    
    # Attributes (typical values or ranges)
    attributes: CreatureAttributes
    
    # Derived stats (calculated from attributes or fixed)
    hp: int | None = None  # None = calculate from CON + SIZ
    mov: int | None = None  # None = calculate from STR/DEX/SIZ
    
    # Combat
    fighting: int = 25
    shooting: int = 0
    dodge: int = 25
    armor: int = 0  # Armor points
    damage_bonus: str = "+0"  # e.g., "+1d4", "+1d6"
    
    # Attacks
    attacks: list[dict] = Field(default_factory=list)
    # Example: [{"name": "Claw", "damage": "1d6+DB", "skill": "fighting"}]
    
    # Sanity
    san_loss: SanLoss = Field(default_factory=SanLoss)
    
    # Special
    abilities: list[CreatureAbility] = Field(default_factory=list)
    spells: list[str] = Field(default_factory=list)
    immunities: list[str] = Field(default_factory=list)  # e.g., ["poison", "disease"]
    
    # Description
    description: str = ""
    tactics: str = ""
    
    def calculate_hp(self, attrs: dict[str, int] | None = None) -> int:
        """Calculate HP from attributes."""
        if self.hp is not None:
            return self.hp
        attrs = attrs or self.attributes.get_fixed()
        con = attrs.get("con", 50)
        siz = attrs.get("siz", 50)
        return (con + siz) // 10
    
    def calculate_mov(self, attrs: dict[str, int] | None = None) -> int:
        """Calculate MOV from attributes."""
        if self.mov is not None:
            return self.mov
        attrs = attrs or self.attributes.get_fixed()
        str_v = attrs.get("str", 50)
        dex_v = attrs.get("dex", 50)
        siz_v = attrs.get("siz", 50)
        
        if str_v < siz_v and dex_v < siz_v:
            return 7
        elif str_v > siz_v and dex_v > siz_v:
            return 9
        else:
            return 8
    
    def to_combatant_stats(self, attrs: dict[str, int] | None = None) -> dict:
        """Convert to CombatantStats-compatible dict."""
        attrs = attrs or self.attributes.get_fixed()
        return {
            "name": self.name_cn,
            "dex": attrs["dex"],
            "fighting": self.fighting,
            "dodge": self.dodge,
            "hp": self.calculate_hp(attrs),
            "hp_max": self.calculate_hp(attrs),
            "armor": self.armor,
            "damage_bonus": self._parse_damage_bonus(),
        }
    
    def _parse_damage_bonus(self) -> int:
        """Parse damage bonus string to integer."""
        db = self.damage_bonus
        if db.startswith("+"):
            db = db[1:]
        if "d" in db.lower():
            # Extract number before 'd' as multiplier
            import re
            match = re.search(r'(\d+)d', db.lower())
            if match:
                return int(match.group(1))
        try:
            return int(db)
        except ValueError:
            return 0


class Bestiary:
    """Collection of creature templates."""
    
    def __init__(self) -> None:
        self._creatures: dict[str, CreatureTemplate] = {}
    
    def add(self, creature: CreatureTemplate) -> None:
        """Add a creature to the bestiary."""
        self._creatures[creature.id] = creature
    
    def get(self, creature_id: str) -> CreatureTemplate | None:
        """Get a creature by ID."""
        return self._creatures.get(creature_id)
    
    def list_all(self) -> list[CreatureTemplate]:
        """List all creatures."""
        return list(self._creatures.values())
    
    def list_by_category(self, category: CreatureCategory) -> list[CreatureTemplate]:
        """List creatures by category."""
        return [c for c in self._creatures.values() if c.category == category]
    
    def export_state(self) -> dict:
        """Export bestiary state."""
        return {
            cid: creature.model_dump() 
            for cid, creature in self._creatures.items()
        }
    
    @classmethod
    def load_from_file(cls, path: str) -> "Bestiary":
        """Load bestiary from JSON file."""
        import json
        bestiary = cls()
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for creature_data in data.get("creatures", []):
            creature = CreatureTemplate.model_validate(creature_data)
            bestiary.add(creature)
        return bestiary
```
  </action>
  <verify>
    <automated>python -c "from dm_bot.coc.bestiary import CreatureTemplate, Bestiary; b = Bestiary(); print('OK')"</automated>
  </verify>
  <done>Bestiary models created with CreatureTemplate, SanLoss, CreatureAbility</done>
</task>

<task type="auto">
  <name>Task 2: Create creature instance manager</name>
  <files>src/dm_bot/coc/creature.py</files>
  <action>
Create creature instance management:

```python
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
    seen_by: set[str] = Field(default_factory=set)  # Player IDs who have seen this creature
    
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
        return {
            iid: instance.model_dump()
            for iid, instance in self.instances.items()
        }
    
    def import_state(self, payload: dict) -> None:
        """Import instances state."""
        self.instances = {}
        for iid, data in payload.items():
            self.instances[iid] = CreatureInstance.model_validate(data)
```
  </action>
  <verify>
    <automated>python -c "from dm_bot.coc.creature import CreatureInstance, CreatureManager; print('OK')"</automated>
  </verify>
  <done>CreatureInstance and CreatureManager for runtime creature management</done>
</task>

<task type="auto">
  <name>Task 3: Create creatures.json with 10+ creatures</name>
  <files>data/bestiary/creatures.json</files>
  <action>
Create bestiary data file with common COC creatures:

```json
{
  "creatures": [
    {
      "id": "deep_one",
      "name": "Deep One",
      "name_cn": "深潜者",
      "category": "mythos",
      "size": "medium",
      "attributes": {
        "str": 100,
        "con": 80,
        "siz": 70,
        "dex": 60,
        "int": 70,
        "pow": 80
      },
      "hp": 15,
      "mov": 8,
      "fighting": 50,
      "dodge": 30,
      "armor": 1,
      "damage_bonus": "+1d4",
      "attacks": [
        {"name": "Claw", "damage": "1d6+DB", "skill": "fighting"}]
      },
      "san_loss": {
        "first_encounter": 5,
        "subsequent": 1,
        "indefinite": false
      },
      "abilities": [
        {
          "name": "Amphibious",
          "name_cn": "两栖",
          "description": "Can breathe underwater",
          "effect": "Immune to drowning"
        }
      ],
      "description": "Fish-like humanoids that serve Cthulhu",
      "tactics": "Attack in groups, prefer underwater combat"
    },
    {
      "id": "shoggoth",
      "name": "Shoggoth",
      "name_cn": "修格斯",
      "category": "mythos",
      "size": "huge",
      "attributes": {
        "str": 150,
        "con": 150,
        "siz": 200,
        "dex": 20,
        "int": 20,
        "pow": 100
      },
      "hp": 35,
      "mov": 10,
      "fighting": 60,
      "dodge": 0,
      "armor": 8,
      "damage_bonus": "+2d6",
      "attacks": [
        {"name": "Crush", "damage": "2d6+DB", "skill": "fighting"}
      ],
      "san_loss": {
        "first_encounter": 10,
        "subsequent": 2,
        "indefinite": true
      },
      "abilities": [
        {
          "name": "Regeneration",
          "name_cn": "再生",
          "description": "Regenerates 2 HP per round",
          "effect": "Heal 2 HP each round"
        }
      ],
      "description": "Protoplasmic servants of the Elder Things",
      "tactics": "Engulf and crush enemies"
    },
    {
      "id": "ghoul",
      "name": "Ghoul",
      "name_cn": "食尸鬼",
      "category": "monster",
      "size": "medium",
      "attributes": {
        "str": 60,
        "con": 50,
        "siz": 50,
        "dex": 70,
        "int": 40,
        "pow": 50
      },
      "hp": 10,
      "mov": 9,
      "fighting": 40,
      "dodge": 35,
      "armor": 1,
      "damage_bonus": "+0",
      "attacks": [
        {"name": "Bite", "damage": "1d6", "skill": "fighting"},
        {"name": "Claw", "damage": "1d4", "skill": "fighting"}
      ],
      "san_loss": {
        "first_encounter": 6,
        "subsequent": 1,
        "indefinite": false
      },
      "abilities": [
        {
          "name": "Paralysis",
          "name_cn": "麻痹",
          "description": "Claw attacks may paralyze",
          "effect": "CON save or paralyzed 1d6 rounds"
        }
      ],
      "description": "Humanoid creatures that feed on corpses",
      "tactics": "Ambush from shadows, attack in packs"
    },
    {
      "id": "byakhee",
      "name": "Byakhee",
      "name_cn": "拜亚基",
      "category": "mythos",
      "size": "large",
      "attributes": {
        "str": 80,
        "con": 60,
        "siz": 90,
        "dex": 70,
        "int": 50,
        "pow": 60
      },
      "hp": 15,
      "mov": 5,
      "fighting": 45,
      "dodge": 35,
      "armor": 2,
      "damage_bonus": "+1d4",
      "attacks": [
        {"name": "Claw", "damage": "1d6+DB", "skill": "fighting"},
        {"name": "Bite", "damage": "1d4", "skill": "fighting"}
      ],
      "san_loss": {
        "first_encounter": 5,
        "subsequent": 1,
        "indefinite": false
      },
      "abilities": [
        {
          "name": "Flight",
          "name_cn": "飞行",
          "description": "Can fly at MOV 12",
          "effect": "Flying speed 12"
        }
      ],
      "description": "Winged servants of Hastur",
      "tactics": "Dive attacks, use flight advantage"
    },
    {
      "id": "zombie",
      "name": "Zombie",
      "name_cn": "僵尸",
      "category": "undead",
      "size": "medium",
      "attributes": {
        "str": 60,
        "con": 100,
        "siz": 60,
        "dex": 30,
        "int": 5,
        "pow": 5
      },
      "hp": 16,
      "mov": 5,
      "fighting": 30,
      "dodge": 0,
      "armor": 2,
      "damage_bonus": "+0",
      "attacks": [
        {"name": "Fist", "damage": "1d3", "skill": "fighting"}
      ],
      "san_loss": {
        "first_encounter": 2,
        "subsequent": 0,
        "indefinite": false
      },
      "abilities": [
        {
          "name": "Mindless",
          "name_cn": "无脑",
          "description": "Immune to mental effects",
          "effect": "Immune to SAN loss, mind control"
        }
      ],
      "description": "Reanimated corpses",
      "tactics": "Slowly approach and attack"
    },
    {
      "id": "cultist",
      "name": "Cultist",
      "name_cn": "邪教徒",
      "category": "human",
      "size": "medium",
      "attributes": {
        "str": 50,
        "con": 50,
        "siz": 50,
        "dex": 50,
        "int": 60,
        "pow": 60
      },
      "hp": 10,
      "mov": 8,
      "fighting": 35,
      "shooting": 30,
      "dodge": 25,
      "armor": 0,
      "damage_bonus": "+0",
      "attacks": [
        {"name": "Knife", "damage": "1d4", "skill": "fighting"},
        {"name": "Pistol", "damage": "1d8", "skill": "shooting"}
      ],
      "san_loss": {
        "first_encounter": 1,
        "subsequent": 0,
        "indefinite": false
      },
      "abilities": [],
      "spells": ["Summon Monster", "Contact Mythos"],
      "description": "Human servants of the Mythos",
      "tactics": "Use cover, cast spells, fight to the death"
    },
    {
      "id": "dimensional_shambler",
      "name": "Dimensional Shambler",
      "name_cn": "维度行者",
      "category": "mythos",
      "size": "large",
      "attributes": {
        "str": 100,
        "con": 80,
        "siz": 80,
        "dex": 50,
        "int": 60,
        "pow": 100
      },
      "hp": 16,
      "mov": 7,
      "fighting": 50,
      "dodge": 25,
      "armor": 4,
      "damage_bonus": "+1d6",
      "attacks": [
        {"name": "Claw", "damage": "1d6+DB", "skill": "fighting"}
      ],
      "san_loss": {
        "first_encounter": 8,
        "subsequent": 2,
        "indefinite": true
      },
      "abilities": [
        {
          "name": "Dimension Walk",
          "name_cn": "维度行走",
          "description": "Can teleport short distances",
          "effect": "Teleport up to 30m once per round"
        }
      ],
      "description": "Interdimensional predators",
      "tactics": "Teleport to flank, grab victims"
    },
    {
      "id": "hunting_horror",
      "name": "Hunting Horror",
      "name_cn": "猎食恐怖",
      "category": "mythos",
      "size": "huge",
      "attributes": {
        "str": 120,
        "con": 80,
        "siz": 100,
        "dex": 80,
        "int": 40,
        "pow": 80
      },
      "hp": 18,
      "mov": 15,
      "fighting": 60,
      "dodge": 40,
      "armor": 4,
      "damage_bonus": "+1d6",
      "attacks": [
        {"name": "Bite", "damage": "2d6", "skill": "fighting"}
      ],
      "san_loss": {
        "first_encounter": 8,
        "subsequent": 2,
        "indefinite": true
      },
      "abilities": [
        {
          "name": "Flight",
          "name_cn": "飞行",
          "description": "Can fly at great speed",
          "effect": "Flying speed 20"
        },
        {
          "name": "Sunlight Vulnerability",
          "name_cn": "畏光",
          "description": "Takes damage in sunlight",
          "effect": "1 HP per round in direct sunlight"
        }
      ],
      "description": "Flying serpentine horrors",
      "tactics": "Swoop attacks, chase fleeing prey"
    },
    {
      "id": "mi_go",
      "name": "Mi-Go",
      "name_cn": "米·戈",
      "category": "mythos",
      "size": "medium",
      "attributes": {
        "str": 50,
        "con": 60,
        "siz": 40,
        "dex": 80,
        "int": 100,
        "pow": 80
      },
      "hp": 10,
      "mov": 7,
      "fighting": 40,
      "shooting": 50,
      "dodge": 40,
      "armor": 4,
      "damage_bonus": "+0",
      "attacks": [
        {"name": "Claw", "damage": "1d4", "skill": "fighting"},
        {"name": "Lightning Gun", "damage": "2d8", "skill": "shooting"}
      ],
      "san_loss": {
        "first_encounter": 5,
        "subsequent": 1,
        "indefinite": false
      },
      "abilities": [
        {
          "name": "Technological",
          "name_cn": "科技",
          "description": "Uses advanced technology",
          "effect": "Has lightning guns and other tech"
        }
      ],
      "description": "Fungoid aliens from Yuggoth",
      "tactics": "Use technology, capture not kill"
    },
    {
      "id": "nightgaunt",
      "name": "Nightgaunt",
      "name_cn": "夜魇",
      "category": "mythos",
      "size": "large",
      "attributes": {
        "str": 70,
        "con": 60,
        "siz": 70,
        "dex": 90,
        "int": 40,
        "pow": 60
      },
      "hp": 13,
      "mov": 5,
      "fighting": 45,
      "dodge": 45,
      "armor": 2,
      "damage_bonus": "+0",
      "attacks": [
        {"name": "Claw", "damage": "1d6", "skill": "fighting"}
      ],
      "san_loss": {
        "first_encounter": 6,
        "subsequent": 1,
        "indefinite": false
      },
      "abilities": [
        {
          "name": "Flight",
          "name_cn": "飞行",
          "description": "Can fly silently",
          "effect": "Flying speed 12, silent"
        },
        {
          "name": "Tickle",
          "name_cn": "挠痒",
          "description": "Tickles causing helplessness",
          "effect": "DEX save or drop items"
        }
      ],
      "description": "Faceless flying servants of Nodens",
      "tactics": "Grab and drop victims, tickle to disarm"
    }
  ]
}
```
  </action>
  <verify>
    <automated>python -c "import json; json.load(open('data/bestiary/creatures.json')); print('JSON valid')"</automated>
  </verify>
  <done>creatures.json with 10 COC creatures</done>
</task>

<task type="auto">
  <name>Task 4: Add combat integration</name>
  <files>src/dm_bot/rules/coc/combat.py</files>
  <action>
Add creature combat integration:

```python
# Add to combat.py imports
from dm_bot.coc.creature import CreatureInstance

# Add function to convert creature to combatant
def creature_to_combatant(creature: CreatureInstance) -> CombatantStats:
    """Convert a creature instance to CombatantStats.
    
    Args:
        creature: The creature instance
        
    Returns:
        CombatantStats for combat resolution
    """
    return CombatantStats(
        name=creature.name,
        dex=creature.attributes.get("dex", 50),
        fighting=creature.attributes.get("fighting", 25),
        dodge=creature.attributes.get("dodge", 25),
        hp=creature.hp,
        hp_max=creature.hp_max,
        armor=creature.attributes.get("armor", 0),
        # ... other fields from creature
    )

# Add to CombatEncounter class
def add_creature(self, creature: CreatureInstance) -> None:
    """Add a creature to combat.
    
    Args:
        creature: The creature instance to add
    """
    combatant = creature_to_combatant(creature)
    self.combatants[creature.instance_id] = combatant
    if creature.instance_id not in self.order:
        self.order.append(creature.instance_id)
```

Also add helper for creature attacks:
```python
def resolve_creature_attack(
    creature: CreatureInstance,
    target: CombatantStats,
    attack_index: int = 0,
) -> CombatCheckResult:
    """Resolve a creature's attack.
    
    Args:
        creature: The attacking creature
        target: The target combatant
        attack_index: Which attack to use (from creature's attacks list)
        
    Returns:
        CombatCheckResult
    """
    # Get attack from creature template
    # Roll attack
    # Apply damage
    # Return result
    pass
```
  </action>
  <verify>
    <automated>grep -n "creature_to_combatant\|add_creature" src/dm_bot/rules/coc/combat.py</automated>
  </verify>
  <done>Combat integration for creatures</done>
</task>

<task type="auto">
  <name>Task 5: Add sanity integration</name>
  <files>src/dm_bot/rules/coc/sanity.py</files>
  <action>
Add creature encounter sanity loss:

```python
# Add to sanity.py

from dm_bot.coc.bestiary import CreatureTemplate

def resolve_creature_encounter_sanity(
    creature_template: CreatureTemplate,
    investigator_san: int,
    has_seen_before: bool = False,
) -> SanityCheckResult:
    """Resolve SAN loss from encountering a creature.
    
    Args:
        creature_template: The creature's template
        investigator_san: Current SAN of the investigator
        has_seen_before: Whether they've seen this creature type before
        
    Returns:
        SanityCheckResult with loss amount
    """
    san_loss = creature_template.san_loss.get_loss(not has_seen_before)
    
    # Check for indefinite insanity
    indefinite = creature_template.san_loss.indefinite and not has_seen_before
    
    # Apply SAN loss
    new_san = max(0, investigator_san - san_loss)
    
    # Determine if insanity occurs
    insanity_type = None
    if san_loss >= 5:
        insanity_type = "temporary"
    if indefinite:
        insanity_type = "indefinite"
    
    return SanityCheckResult(
        san_loss=san_loss,
        new_san=new_san,
        insanity=insanity_type is not None,
        insanity_type=insanity_type,
        # ... other fields
    )
```
  </action>
  <verify>
    <automated>grep -n "resolve_creature_encounter_sanity" src/dm_bot/rules/coc/sanity.py</automated>
  </verify>
  <done>Sanity integration for creature encounters</done>
</task>

<task type="auto">
  <name>Task 6: Create unit tests</name>
  <files>tests/rules/coc/test_bestiary.py</files>
  <action>
Create comprehensive bestiary tests:

```python
"""Tests for bestiary and creature system."""

import pytest

from dm_bot.coc.bestiary import (
    Bestiary,
    CreatureTemplate,
    CreatureCategory,
    SanLoss,
    CreatureAttributes,
)
from dm_bot.coc.creature import CreatureInstance, CreatureManager


class TestSanLoss:
    """Test SAN loss mechanics."""
    
    def test_first_encounter_loss(self):
        """Test SAN loss on first encounter."""
        san_loss = SanLoss(first_encounter=5, subsequent=1)
        assert san_loss.get_loss(is_first=True) == 5
        assert san_loss.get_loss(is_first=False) == 1
    
    def test_indefinite_insanity(self):
        """Test indefinite insanity flag."""
        san_loss = SanLoss(first_encounter=10, indefinite=True)
        assert san_loss.indefinite is True


class TestCreatureAttributes:
    """Test creature attribute handling."""
    
    def test_fixed_attributes(self):
        """Test fixed attribute values."""
        attrs = CreatureAttributes(str=100, con=80, siz=70)
        fixed = attrs.get_fixed()
        assert fixed["str"] == 100
        assert fixed["con"] == 80
    
    def test_ranged_attributes(self):
        """Test ranged attribute values."""
        attrs = CreatureAttributes(str=(80, 120), con=80)
        fixed = attrs.get_fixed()
        assert fixed["str"] == 100  # Average
        assert fixed["con"] == 80


class TestCreatureTemplate:
    """Test creature template functionality."""
    
    def test_calculate_hp(self):
        """Test HP calculation from attributes."""
        template = CreatureTemplate(
            id="test",
            name="Test",
            name_cn="测试",
            category=CreatureCategory.MONSTER,
            attributes=CreatureAttributes(con=80, siz=70),
        )
        assert template.calculate_hp() == 15  # (80+70)//10
    
    def test_to_combatant_stats(self):
        """Test conversion to combatant stats."""
        template = CreatureTemplate(
            id="test",
            name="Test",
            name_cn="测试",
            category=CreatureCategory.MONSTER,
            attributes=CreatureAttributes(dex=60),
            fighting=50,
        )
        stats = template.to_combatant_stats()
        assert stats["name"] == "测试"
        assert stats["dex"] == 60
        assert stats["fighting"] == 50


class TestBestiary:
    """Test bestiary management."""
    
    @pytest.fixture
    def bestiary(self):
        """Create test bestiary."""
        b = Bestiary()
        b.add(CreatureTemplate(
            id="ghoul",
            name="Ghoul",
            name_cn="食尸鬼",
            category=CreatureCategory.MONSTER,
            attributes=CreatureAttributes(),
        ))
        return b
    
    def test_get_creature(self, bestiary):
        """Test retrieving creature by ID."""
        creature = bestiary.get("ghoul")
        assert creature is not None
        assert creature.name_cn == "食尸鬼"
    
    def test_list_by_category(self, bestiary):
        """Test listing creatures by category."""
        monsters = bestiary.list_by_category(CreatureCategory.MONSTER)
        assert len(monsters) == 1
        assert monsters[0].id == "ghoul"


class TestCreatureManager:
    """Test creature instance management."""
    
    @pytest.fixture
    def manager(self):
        """Create creature manager with test bestiary."""
        bestiary = Bestiary()
        bestiary.add(CreatureTemplate(
            id="ghoul",
            name="Ghoul",
            name_cn="食尸鬼",
            category=CreatureCategory.MONSTER,
            attributes=CreatureAttributes(),
            hp=10,
        ))
        return CreatureManager(bestiary)
    
    def test_spawn_creature(self, manager):
        """Test spawning a creature instance."""
        instance = manager.spawn("ghoul")
        assert instance.template_id == "ghoul"
        assert instance.hp == 10
        assert instance.is_alive()
    
    def test_take_damage(self, manager):
        """Test creature taking damage."""
        instance = manager.spawn("ghoul")
        damage = instance.take_damage(5)
        assert damage == 5
        assert instance.hp == 5
    
    def test_creature_death(self, manager):
        """Test creature death."""
        instance = manager.spawn("ghoul")
        instance.take_damage(20)
        assert not instance.is_alive()
    
    def test_mark_seen(self, manager):
        """Test marking creature as seen."""
        instance = manager.spawn("ghoul")
        is_first = instance.mark_seen_by("player1")
        assert is_first is True
        
        is_first_again = instance.mark_seen_by("player1")
        assert is_first_again is False


class TestCreatureCombat:
    """Test creature combat integration."""
    
    def test_creature_to_combatant(self):
        """Test converting creature to combatant."""
        from dm_bot.rules.coc.combat import creature_to_combatant
        
        instance = CreatureInstance(
            instance_id="test",
            template_id="ghoul",
            name="Test Ghoul",
            hp=10,
            hp_max=10,
            attributes={"dex": 70, "fighting": 40, "dodge": 35},
        )
        
        combatant = creature_to_combatant(instance)
        assert combatant.name == "Test Ghoul"
        assert combatant.dex == 70
```
  </action>
  <verify>
    <automated>uv run pytest tests/rules/coc/test_bestiary.py -v</automated>
  </verify>
  <done>Unit tests for bestiary and creatures</done>
</task>

<task type="auto">
  <name>Task 7: Create E2E creature encounter scenario</name>
  <files>tests/scenarios/acceptance/scen_creature_encounter.yaml</files>
  <action>
Create E2E scenario:

```yaml
# Creature Encounter E2E Scenario
# Validates: creature spawning → combat → sanity loss

scenario:
  id: scen_creature_encounter
  name: "Creature Encounter"
  description: "Validates creature encounter with combat and sanity"
  
actors:
  - id: kp
    role: keeper
  - id: p1
    role: player
    name: "调查员"

initial_state:
  dice_mode: seeded
  dice_seed: 12345
  
steps:
  # Setup
  - actor: kp
    action: command
    name: bind_campaign
    args:
      campaign_id: "creature_test"
      
  - actor: p1
    action: command
    name: join
    args: {}
    
  - actor: p1
    action: command
    name: ready
    args: {}
    
  - actor: kp
    action: command
    name: start_session
    args: {}
    
  # Spawn creature
  - actor: kp
    action: command
    name: spawn_creature
    args:
      template_id: "ghoul"
      name: "饥饿的食尸鬼"
      
  # Player sees creature (SAN loss)
  - actor: p1
    action: message
    text: "我看看前面是什么"
    
  # Assertions: SAN loss recorded
  - actor: system
    action: assert
    assertions:
      san_loss:
        p1:
          amount: 6  # Ghoul first encounter
          type: "creature_encounter"
          
  # Combat
  - actor: p1
    action: message
    text: "我用格斗攻击食尸鬼"
    
  # Assertions: Combat resolved
  - actor: system
    action: assert
    assertions:
      combat:
        active: true
        round: 1
        combatants:
          contains: ["p1", "ghoul"]
          
      skill_usage:
        p1:
          fighting: ">= 1"

expected_outcomes:
  - creature_spawned: true
  - san_loss_applied: true
  - combat_initiated: true
  - skill_tracked: true
```
  </action>
  <verify>
    <automated>cat tests/scenarios/acceptance/scen_creature_encounter.yaml | head -30</automated>
  </verify>
  <done>E2E creature encounter scenario</done>
</task>

</tasks>

<verification>
Run verification:
1. `uv run pytest tests/rules/coc/test_bestiary.py -v`
2. `uv run pytest tests/rules/coc/test_combat_and_insanity.py -v`
3. `uv run python -m dm_bot.main smoke-check`
</verification>

<success_criteria>
- CreatureTemplate model with all COC stats
- 10+ creatures defined in creatures.json
- CreatureInstance for runtime state
- CreatureManager for instance lifecycle
- Combat integration (creature_to_combatant)
- Sanity integration (creature encounter SAN loss)
- Unit tests for all components
- E2E scenario validates encounter flow
- All existing tests pass
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-e/phases/81-creature-bestiary/E81-01-SUMMARY.md`
</output>
