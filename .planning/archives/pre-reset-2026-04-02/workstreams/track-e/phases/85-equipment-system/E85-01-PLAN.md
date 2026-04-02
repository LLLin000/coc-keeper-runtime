---
phase: E85-equipment-system
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/coc/equipment.py
  - data/equipment/weapons.json
  - data/equipment/armor.json
  - src/dm_bot/coc/inventory.py
  - src/dm_bot/rules/coc/combat.py
  - tests/coc/test_equipment.py
  - tests/scenarios/acceptance/scen_equipment_combat.yaml
autonomous: true
requirements:
  - EQUIP-01
  - EQUIP-02
  - EQUIP-03
  - EQUIP-04
  - EQUIP-05

must_haves:
  truths:
    - "Weapon database includes COC 7e weapon stats (damage, range, ammo)"
    - "Armor database includes protection values"
    - "Equipment effects are applied in combat resolution"
    - "Basic inventory management tracks equipped items"
    - "Equipment can be used in scenario tests"
  artifacts:
    - path: "src/dm_bot/coc/equipment.py"
      provides: "Weapon, Armor models and EquipmentDatabase"
      min_lines: 100
    - path: "data/equipment/weapons.json"
      provides: "10+ weapon definitions"
      min_lines: 150
    - path: "data/equipment/armor.json"
      provides: "4+ armor definitions"
      min_lines: 50
    - path: "src/dm_bot/coc/inventory.py"
      provides: "Inventory model with equip/unequip"
      min_lines: 80
  key_links:
    - from: "Weapon.damage"
      to: "combat.py resolve_attack"
      via: "damage expression evaluation"
    - from: "Armor.protection"
      to: "combat.py"
      via: "damage reduction"
---

<objective>
Create equipment database with weapons and armor for COC 7e combat.

Purpose: Enable equipment-based combat with weapons and armor.
Output: Equipment database, inventory system, combat integration.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@src/dm_bot/rules/coc/combat.py
@src/dm_bot/rules/coc/skills.py

## Key Types from Existing Code

From combat.py:
```python
class CombatCheckResult(BaseModel):
    damage: int
    armor_absorbed: int
    final_damage: int
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create equipment models</name>
  <files>src/dm_bot/coc/equipment.py</files>
  <action>
Create equipment data models:

```python
"""COC 7th Edition Equipment System.

Weapons and armor for Call of Cthulhu.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class WeaponCategory(StrEnum):
    """Weapon categories."""
    MELEE = "melee"
    RANGED = "ranged"
    THROWN = "thrown"


class Weapon(BaseModel):
    """A weapon in COC 7e."""
    
    # Identity
    id: str
    name: str
    name_cn: str
    category: WeaponCategory
    
    # Combat stats
    damage: str  # Damage expression, e.g., "1d6", "1d8+DB", "2d6"
    damage_type: str = "physical"  # physical, fire, etc.
    
    # Range
    range: str = "touch"  # "touch", "2m", "10m", "50m", "100m", etc.
    
    # For ranged weapons
    ammo_capacity: int | None = None
    malfunction: int | None = None  # Malfunction number
    
    # Combat
    attacks_per_round: int = 1
    skill: str = "fighting"  # Default skill to use
    
    # Special
    two_handed: bool = False
    concealable: bool = True
    
    # Description
    description: str = ""
    
    def get_damage_expression(self, db: int = 0) -> str:
        """Get damage expression with DB substituted.
        
        Args:
            db: Damage bonus value
            
        Returns:
            Damage expression ready to roll
        """
        return self.damage.replace("DB", str(db))


class Armor(BaseModel):
    """Armor in COC 7e."""
    
    # Identity
    id: str
    name: str
    name_cn: str
    
    # Protection
    protection: int  # Armor points
    
    # Coverage
    coverage: list[str] = Field(default_factory=lambda: ["torso"])
    # body parts: head, torso, arms, legs
    
    # Properties
    bulky: bool = False  # May affect movement
    description: str = ""


class EquipmentDatabase:
    """Database of weapons and armor."""
    
    def __init__(self) -> None:
        self.weapons: dict[str, Weapon] = {}
        self.armor: dict[str, Armor] = {}
    
    def add_weapon(self, weapon: Weapon) -> None:
        """Add a weapon to the database."""
        self.weapons[weapon.id] = weapon
    
    def get_weapon(self, weapon_id: str) -> Weapon | None:
        """Get a weapon by ID."""
        return self.weapons.get(weapon_id)
    
    def list_weapons(self, category: WeaponCategory | None = None) -> list[Weapon]:
        """List weapons, optionally filtered by category."""
        weapons = list(self.weapons.values())
        if category:
            weapons = [w for w in weapons if w.category == category]
        return weapons
    
    def add_armor(self, armor: Armor) -> None:
        """Add armor to the database."""
        self.armor[armor.id] = armor
    
    def get_armor(self, armor_id: str) -> Armor | None:
        """Get armor by ID."""
        return self.armor.get(armor_id)
    
    def list_armor(self) -> list[Armor]:
        """List all armor."""
        return list(self.armor.values())
    
    @classmethod
    def load_from_files(
        cls,
        weapons_path: str | None = None,
        armor_path: str | None = None,
    ) -> "EquipmentDatabase":
        """Load equipment from JSON files.
        
        Args:
            weapons_path: Path to weapons JSON
            armor_path: Path to armor JSON
            
        Returns:
            Populated EquipmentDatabase
        """
        import json
        
        db = cls()
        
        if weapons_path:
            with open(weapons_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for weapon_data in data.get("weapons", []):
                db.add_weapon(Weapon.model_validate(weapon_data))
        
        if armor_path:
            with open(armor_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for armor_data in data.get("armor", []):
                db.add_armor(Armor.model_validate(armor_data))
        
        return db


# Common weapon IDs for convenience
COMMON_WEAPONS = {
    "unarmed": "unarmed",
    "knife": "knife",
    "club": "club",
    "pistol": "pistol_light",
    "rifle": "rifle",
    "shotgun": "shotgun",
}

# Common armor IDs
COMMON_ARMOR = {
    "none": "none",
    "leather": "leather_jacket",
    "heavy": "heavy_leather",
}
```
  </action>
  <verify>
    <automated>python -c "from dm_bot.coc.equipment import Weapon, Armor, EquipmentDatabase; print('OK')"</automated>
  </verify>
  <done>Equipment models created</done>
</task>

<task type="auto">
  <name>Task 2: Create weapons.json</name>
  <files>data/equipment/weapons.json</files>
  <action>
Create weapons database:

```json
{
  "weapons": [
    {
      "id": "unarmed",
      "name": "Unarmed",
      "name_cn": "徒手",
      "category": "melee",
      "damage": "1d3+DB",
      "range": "touch",
      "skill": "brawl",
      "description": "Fists, feet, or improvised blunt objects"
    },
    {
      "id": "knife",
      "name": "Knife",
      "name_cn": "匕首",
      "category": "melee",
      "damage": "1d4+DB",
      "range": "touch",
      "skill": "fighting",
      "concealable": true,
      "description": "Small blade weapon"
    },
    {
      "id": "club",
      "name": "Club",
      "name_cn": "棍棒",
      "category": "melee",
      "damage": "1d6+DB",
      "range": "touch",
      "skill": "fighting",
      "description": "Baseball bat, truncheon, or similar"
    },
    {
      "id": "sword",
      "name": "Sword",
      "name_cn": "剑",
      "category": "melee",
      "damage": "1d8+DB",
      "range": "touch",
      "skill": "fighting",
      "concealable": false,
      "description": "Bladed weapon"
    },
    {
      "id": "axe",
      "name": "Axe",
      "name_cn": "斧",
      "category": "melee",
      "damage": "1d8+DB",
      "range": "touch",
      "skill": "fighting",
      "description": "Hand axe or hatchet"
    },
    {
      "id": "pistol_light",
      "name": "Light Pistol",
      "name_cn": "轻型手枪",
      "category": "ranged",
      "damage": "1d6",
      "range": "15m",
      "ammo_capacity": 8,
      "malfunction": 100,
      "skill": "shooting",
      "concealable": true,
      "description": "Small handgun"
    },
    {
      "id": "pistol_heavy",
      "name": "Heavy Pistol",
      "name_cn": "重型手枪",
      "category": "ranged",
      "damage": "1d8",
      "range": "15m",
      "ammo_capacity": 7,
      "malfunction": 100,
      "skill": "shooting",
      "concealable": true,
      "description": "Large handgun"
    },
    {
      "id": "rifle",
      "name": "Rifle",
      "name_cn": "步枪",
      "category": "ranged",
      "damage": "2d6",
      "range": "110m",
      "ammo_capacity": 5,
      "malfunction": 100,
      "skill": "shooting",
      "two_handed": true,
      "concealable": false,
      "description": "Bolt-action or lever-action rifle"
    },
    {
      "id": "shotgun",
      "name": "Shotgun",
      "name_cn": "霰弹枪",
      "category": "ranged",
      "damage": "4d6",
      "range": "10m",
      "ammo_capacity": 2,
      "malfunction": 100,
      "skill": "shooting",
      "two_handed": true,
      "concealable": false,
      "description": "Double-barreled shotgun"
    },
    {
      "id": "submachine_gun",
      "name": "Submachine Gun",
      "name_cn": "冲锋枪",
      "category": "ranged",
      "damage": "1d8",
      "range": "30m",
      "ammo_capacity": 32,
      "malfunction": 96,
      "skill": "shooting",
      "attacks_per_round": 2,
      "two_handed": true,
      "concealable": false,
      "description": "Automatic weapon"
    },
    {
      "id": "rifle_assault",
      "name": "Assault Rifle",
      "name_cn": "突击步枪",
      "category": "ranged",
      "damage": "2d6",
      "range": "90m",
      "ammo_capacity": 30,
      "malfunction": 96,
      "skill": "shooting",
      "attacks_per_round": 2,
      "two_handed": true,
      "concealable": false,
      "description": "Military automatic rifle"
    },
    {
      "id": "thrown_knife",
      "name": "Thrown Knife",
      "name_cn": "飞刀",
      "category": "thrown",
      "damage": "1d4+DB",
      "range": "STR/5m",
      "skill": "throw",
      "description": "Knife thrown at target"
    },
    {
      "id": "thrown_rock",
      "name": "Thrown Rock",
      "name_cn": "投掷石块",
      "category": "thrown",
      "damage": "1d4+DB",
      "range": "STR/5m",
      "skill": "throw",
      "description": "Rock or similar object"
    }
  ]
}
```
  </action>
  <verify>
    <automated>python -c "import json; json.load(open('data/equipment/weapons.json')); print('JSON valid')"</automated>
  </verify>
  <done>weapons.json with 13 weapons</done>
</task>

<task type="auto">
  <name>Task 3: Create armor.json</name>
  <files>data/equipment/armor.json</files>
  <action>
Create armor database:

```json
{
  "armor": [
    {
      "id": "none",
      "name": "None",
      "name_cn": "无护甲",
      "protection": 0,
      "coverage": ["torso"],
      "description": "No armor protection"
    },
    {
      "id": "leather_jacket",
      "name": "Leather Jacket",
      "name_cn": "皮夹克",
      "protection": 1,
      "coverage": ["torso", "arms"],
      "description": "Thick leather jacket"
    },
    {
      "id": "heavy_leather",
      "name": "Heavy Leather",
      "name_cn": "厚皮甲",
      "protection": 2,
      "coverage": ["torso", "arms"],
      "bulky": true,
      "description": "Heavy leather armor"
    },
    {
      "id": "riot_gear",
      "name": "Riot Gear",
      "name_cn": "防暴装备",
      "protection": 4,
      "coverage": ["head", "torso", "arms", "legs"],
      "bulky": true,
      "description": "Modern police riot armor"
    },
    {
      "id": "plate_mail",
      "name": "Plate Mail",
      "name_cn": "板甲",
      "protection": 5,
      "coverage": ["torso", "arms", "legs"],
      "bulky": true,
      "description": "Medieval plate armor"
    }
  ]
}
```
  </action>
  <verify>
    <automated>python -c "import json; json.load(open('data/equipment/armor.json')); print('JSON valid')"</automated>
  </verify>
  <done>armor.json with 5 armor types</done>
</task>

<task type="auto">
  <name>Task 4: Create inventory system</name>
  <files>src/dm_bot/coc/inventory.py</files>
  <action>
Create inventory management:

```python
"""Inventory management for COC characters."""

from pydantic import BaseModel, Field

from dm_bot.coc.equipment import Weapon, Armor, EquipmentDatabase


class Inventory(BaseModel):
    """Character inventory."""
    
    # Weapons
    weapons: list[str] = Field(default_factory=list)  # Weapon IDs
    equipped_weapon: str | None = None
    
    # Armor
    armor: str | None = None  # Armor ID
    
    # Other items
    items: list[str] = Field(default_factory=list)
    
    # Money
    cash: float = 0.0
    assets: float = 0.0
    
    def equip_weapon(self, weapon_id: str) -> bool:
        """Equip a weapon.
        
        Args:
            weapon_id: The weapon ID to equip
            
        Returns:
            True if equipped, False if not in inventory
        """
        if weapon_id not in self.weapons and weapon_id != "unarmed":
            return False
        self.equipped_weapon = weapon_id
        return True
    
    def unequip_weapon(self) -> None:
        """Unequip current weapon (revert to unarmed)."""
        self.equipped_weapon = None
    
    def equip_armor(self, armor_id: str) -> bool:
        """Equip armor.
        
        Args:
            armor_id: The armor ID
            
        Returns:
            True if equipped
        """
        self.armor = armor_id
        return True
    
    def unequip_armor(self) -> None:
        """Remove armor."""
        self.armor = None
    
    def add_weapon(self, weapon_id: str) -> None:
        """Add a weapon to inventory."""
        if weapon_id not in self.weapons:
            self.weapons.append(weapon_id)
    
    def remove_weapon(self, weapon_id: str) -> bool:
        """Remove a weapon from inventory.
        
        Returns:
            True if removed, False if not found
        """
        if weapon_id in self.weapons:
            self.weapons.remove(weapon_id)
            if self.equipped_weapon == weapon_id:
                self.equipped_weapon = None
            return True
        return False
    
    def add_item(self, item: str) -> None:
        """Add an item to inventory."""
        self.items.append(item)
    
    def remove_item(self, item: str) -> bool:
        """Remove an item from inventory."""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def get_equipped_weapon(self, equipment_db: EquipmentDatabase) -> Weapon | None:
        """Get the currently equipped weapon.
        
        Args:
            equipment_db: Equipment database
            
        Returns:
            Equipped weapon or None
        """
        weapon_id = self.equipped_weapon or "unarmed"
        return equipment_db.get_weapon(weapon_id)
    
    def get_equipped_armor(self, equipment_db: EquipmentDatabase) -> Armor | None:
        """Get the currently equipped armor.
        
        Args:
            equipment_db: Equipment database
            
        Returns:
            Equipped armor or None
        """
        if not self.armor:
            return None
        return equipment_db.get_armor(self.armor)
    
    def get_protection(self, equipment_db: EquipmentDatabase) -> int:
        """Get total armor protection.
        
        Args:
            equipment_db: Equipment database
            
        Returns:
            Armor protection value
        """
        armor = self.get_equipped_armor(equipment_db)
        if armor:
            return armor.protection
        return 0


class InventoryManager:
    """Manages inventories for multiple characters."""
    
    def __init__(self, equipment_db: EquipmentDatabase) -> None:
        self.equipment_db = equipment_db
        self.inventories: dict[str, Inventory] = {}
    
    def get_inventory(self, character_id: str) -> Inventory:
        """Get or create inventory for a character."""
        if character_id not in self.inventories:
            self.inventories[character_id] = Inventory()
        return self.inventories[character_id]
    
    def set_inventory(self, character_id: str, inventory: Inventory) -> None:
        """Set inventory for a character."""
        self.inventories[character_id] = inventory
    
    def equip_weapon(self, character_id: str, weapon_id: str) -> bool:
        """Equip a weapon for a character."""
        inv = self.get_inventory(character_id)
        return inv.equip_weapon(weapon_id)
    
    def get_weapon_damage(self, character_id: str, db: int = 0) -> str:
        """Get damage expression for character's weapon.
        
        Args:
            character_id: The character ID
            db: Damage bonus
            
        Returns:
            Damage expression
        """
        inv = self.get_inventory(character_id)
        weapon = inv.get_equipped_weapon(self.equipment_db)
        if weapon:
            return weapon.get_damage_expression(db)
        return f"1d3+{db}"  # Default unarmed
    
    def get_armor_protection(self, character_id: str) -> int:
        """Get armor protection for a character."""
        inv = self.get_inventory(character_id)
        return inv.get_protection(self.equipment_db)
```
  </action>
  <verify>
    <automated>python -c "from dm_bot.coc.inventory import Inventory, InventoryManager; print('OK')"</automated>
  </verify>
  <done>Inventory system created</done>
</task>

<task type="auto">
  <name>Task 5: Integrate equipment into combat</name>
  <files>src/dm_bot/rules/coc/combat.py</files>
  <action>
Add equipment integration to combat:

```python
# Add to combat.py imports
from dm_bot.coc.equipment import EquipmentDatabase
from dm_bot.coc.inventory import Inventory

# Modify CombatantStats to include equipment
def resolve_fighting_attack_with_equipment(
    attacker: CombatantStats,
    defender: CombatantStats,
    attacker_roll: int,
    defender_roll: int,
    equipment_db: EquipmentDatabase,
    attacker_weapon: str | None = None,
    defender_armor: str | None = None,
) -> CombatCheckResult:
    """Resolve fighting attack with equipment.
    
    Args:
        # ... existing args ...
        equipment_db: Equipment database
        attacker_weapon: Attacker's weapon ID
        defender_armor: Defender's armor ID
    """
    # Get weapon damage
    weapon = equipment_db.get_weapon(attacker_weapon) if attacker_weapon else None
    if weapon:
        damage_expr = weapon.get_damage_expression(attacker.damage_bonus)
    else:
        damage_expr = f"1d3+{attacker.damage_bonus}"
    
    # Get armor protection
    armor = equipment_db.get_armor(defender_armor) if defender_armor else None
    armor_protection = armor.protection if armor else 0
    
    # Resolve attack (existing logic)
    # ...
    
    # Calculate damage with equipment
    if result.success:
        import d20
        damage_result = d20.roll(damage_expr)
        damage = damage_result.total
        
        # Apply armor
        final_damage = max(0, damage - armor_protection)
        armor_absorbed = damage - final_damage
        
        result.damage = damage
        result.armor_absorbed = armor_absorbed
        result.final_damage = final_damage
    
    return result

# Add helper to CombatEncounter
def resolve_attack_with_equipment(
    self,
    attacker_id: str,
    target_id: str,
    equipment_db: EquipmentDatabase,
    inventory_manager,  # InventoryManager
) -> dict:
    """Resolve attack with equipment consideration.
    
    Args:
        attacker_id: Attacker combatant ID
        target_id: Target combatant ID
        equipment_db: Equipment database
        inventory_manager: Inventory manager
        
    Returns:
        Combat result
    """
    # Get combatants
    attacker = self.combatants[attacker_id]
    defender = self.combatants[target_id]
    
    # Get equipment
    attacker_weapon = inventory_manager.get_inventory(attacker_id).equipped_weapon
    defender_armor = inventory_manager.get_inventory(target_id).armor
    
    # Resolve with equipment
    # ... implementation ...
    pass
```
  </action>
  <verify>
    <automated>grep -n "equipment_db\|attacker_weapon" src/dm_bot/rules/coc/combat.py | head -10</automated>
  </verify>
  <done>Equipment integrated into combat</done>
</task>

<task type="auto">
  <name>Task 6: Create unit tests</name>
  <files>tests/coc/test_equipment.py</files>
  <action>
Create equipment unit tests:

```python
"""Tests for equipment system."""

import pytest

from dm_bot.coc.equipment import (
    Weapon,
    Armor,
    EquipmentDatabase,
    WeaponCategory,
)
from dm_bot.coc.inventory import Inventory, InventoryManager


class TestWeapon:
    """Test weapon functionality."""
    
    def test_weapon_creation(self):
        """Test creating a weapon."""
        weapon = Weapon(
            id="test_knife",
            name="Test Knife",
            name_cn="测试匕首",
            category=WeaponCategory.MELEE,
            damage="1d4+DB",
        )
        assert weapon.damage == "1d4+DB"
    
    def test_damage_expression_with_db(self):
        """Test damage expression substitution."""
        weapon = Weapon(
            id="test",
            name="Test",
            name_cn="测试",
            category=WeaponCategory.MELEE,
            damage="1d6+DB",
        )
        expr = weapon.get_damage_expression(db=2)
        assert expr == "1d6+2"


class TestArmor:
    """Test armor functionality."""
    
    def test_armor_protection(self):
        """Test armor protection value."""
        armor = Armor(
            id="leather",
            name="Leather",
            name_cn="皮甲",
            protection=2,
        )
        assert armor.protection == 2


class TestEquipmentDatabase:
    """Test equipment database."""
    
    @pytest.fixture
    def db(self):
        """Create test database."""
        database = EquipmentDatabase()
        database.add_weapon(Weapon(
            id="knife",
            name="Knife",
            name_cn="匕首",
            category=WeaponCategory.MELEE,
            damage="1d4+DB",
        ))
        database.add_armor(Armor(
            id="leather",
            name="Leather",
            name_cn="皮甲",
            protection=2,
        ))
        return database
    
    def test_get_weapon(self, db):
        """Test retrieving weapon."""
        weapon = db.get_weapon("knife")
        assert weapon is not None
        assert weapon.name == "Knife"
    
    def test_get_armor(self, db):
        """Test retrieving armor."""
        armor = db.get_armor("leather")
        assert armor is not None
        assert armor.protection == 2
    
    def test_list_weapons_by_category(self, db):
        """Test listing weapons by category."""
        melee = db.list_weapons(WeaponCategory.MELEE)
        assert len(melee) == 1


class TestInventory:
    """Test inventory management."""
    
    @pytest.fixture
    def inv(self):
        """Create test inventory."""
        return Inventory()
    
    def test_add_weapon(self, inv):
        """Test adding weapon to inventory."""
        inv.add_weapon("knife")
        assert "knife" in inv.weapons
    
    def test_equip_weapon(self, inv):
        """Test equipping weapon."""
        inv.add_weapon("knife")
        result = inv.equip_weapon("knife")
        assert result is True
        assert inv.equipped_weapon == "knife"
    
    def test_equip_weapon_not_owned(self, inv):
        """Test equipping weapon not in inventory."""
        result = inv.equip_weapon("sword")
        assert result is False
    
    def test_equip_armor(self, inv):
        """Test equipping armor."""
        inv.equip_armor("leather")
        assert inv.armor == "leather"


class TestInventoryManager:
    """Test inventory manager."""
    
    @pytest.fixture
    def manager(self):
        """Create inventory manager."""
        db = EquipmentDatabase()
        db.add_weapon(Weapon(
            id="knife",
            name="Knife",
            name_cn="匕首",
            category=WeaponCategory.MELEE,
            damage="1d4+DB",
        ))
        db.add_armor(Armor(
            id="leather",
            name="Leather",
            name_cn="皮甲",
            protection=2,
        ))
        return InventoryManager(db)
    
    def test_get_weapon_damage(self, manager):
        """Test getting weapon damage."""
        manager.equip_weapon("char1", "knife")
        damage = manager.get_weapon_damage("char1", db=1)
        assert damage == "1d4+1"
    
    def test_get_armor_protection(self, manager):
        """Test getting armor protection."""
        inv = manager.get_inventory("char1")
        inv.equip_armor("leather")
        protection = manager.get_armor_protection("char1")
        assert protection == 2
```
  </action>
  <verify>
    <automated>uv run pytest tests/coc/test_equipment.py -v</automated>
  </verify>
  <done>Equipment unit tests</done>
</task>

<task type="auto">
  <name>Task 7: Create E2E equipment scenario</name>
  <files>tests/scenarios/acceptance/scen_equipment_combat.yaml</files>
  <action>
Create E2E equipment combat scenario:

```yaml
# Equipment Combat E2E Scenario
# Validates: weapon damage, armor protection in combat

scenario:
  id: scen_equipment_combat
  name: "Equipment Combat"
  description: "Validates combat with weapons and armor"
  
actors:
  - id: kp
    role: keeper
  - id: p1
    role: player
    name: "武装调查员"
  - id: enemy
    role: npc
    name: "邪教徒"

initial_state:
  dice_mode: seeded
  dice_seed: 12345
  
steps:
  # Setup
  - actor: kp
    action: command
    name: bind_campaign
    args:
      campaign_id: "equipment_test"
      
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
    
  # Equip weapon and armor
  - actor: p1
    action: command
    name: equip_weapon
    args:
      weapon_id: "pistol_light"
      
  - actor: p1
    action: command
    name: equip_armor
    args:
      armor_id: "leather_jacket"
      
  # Spawn enemy with weapon
  - actor: kp
    action: command
    name: spawn_creature
    args:
      template_id: "cultist"
      equipment:
        weapon: "knife"
        armor: "none"
        
  # Combat with equipment
  - actor: p1
    action: message
    text: "我用手枪射击邪教徒"
    
  - actor: system
    action: assert
    assertions:
      combat_resolved:
        weapon_used: "pistol_light"
        damage: "> 0"
        
  # Enemy attacks (with armor protection)
  - actor: kp
    action: command
    name: npc_attack
    args:
      attacker: "enemy"
      target: "p1"
      
  - actor: system
    action: assert
    assertions:
      damage_reduced:
        base_damage: "> 0"
        armor_absorbed: ">= 1"  # Leather jacket
        final_damage: "< base_damage"

expected_outcomes:
  - weapon_damage_applied: true
  - armor_protection_applied: true
  - combat_with_equipment: true
```
  </action>
  <verify>
    <automated>cat tests/scenarios/acceptance/scen_equipment_combat.yaml | head -30</automated>
  </verify>
  <done>E2E equipment combat scenario</done>
</task>

</tasks>

<verification>
Run verification:
1. `uv run pytest tests/coc/test_equipment.py -v`
2. `uv run python -m dm_bot.main smoke-check`
</verification>

<success_criteria>
- Equipment models (Weapon, Armor, EquipmentDatabase)
- weapons.json with 10+ weapons
- armor.json with 4+ armor types
- Inventory system with equip/unequip
- Combat integration for weapon damage
- Armor protection in damage calculation
- Unit tests for all components
- E2E scenario validates equipment combat
- All existing tests pass
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-e/phases/85-equipment-system/E85-01-SUMMARY.md`
</output>
