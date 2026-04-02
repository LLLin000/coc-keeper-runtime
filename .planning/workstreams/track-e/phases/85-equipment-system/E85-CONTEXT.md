# Phase E85 Context: Equipment System

## Goal
Create an equipment database with weapons and armor that affect combat resolution.

## Background

### Current State
- Combat system exists but equipment is hardcoded
- No weapon/armor database
- No inventory management
- Damage calculated from attributes only

### COC 7e Equipment

**Weapons**:
- Melee: Knife, Club, Sword, Axe, etc.
- Ranged: Pistol, Rifle, Shotgun, etc.
- Stats: Damage, Range, Ammo, Malfunction

**Armor**:
- Types: None, Leather, Heavy Leather, Chain, Plate
- Protection: Reduces damage

**Combat Effects**:
- Weapon damage replaces base damage
- Armor reduces incoming damage
- Some weapons have special effects

## Design Decisions

### 1. Equipment Data Model

**Decision**: JSON file with Pydantic models

```python
class Weapon(BaseModel):
    id: str
    name: str
    name_cn: str
    category: WeaponCategory  # MELEE, RANGED
    damage: str  # e.g., "1d6", "1d8+DB"
    range: str  # e.g., "touch", "10m", "50m"
    ammo: int | None = None
    malfunction: int | None = None
    attacks_per_round: int = 1

class Armor(BaseModel):
    id: str
    name: str
    name_cn: str
    protection: int  # Armor points
    coverage: str  # body parts covered
```

### 2. Combat Integration

**Decision**: Equipment modifies combat resolution

- Weapon damage replaces base damage
- Armor subtracts from damage
- DB still applies

### 3. Inventory Model

**Decision**: Simple inventory per character

```python
class Inventory(BaseModel):
    weapons: list[str]  # Weapon IDs
    armor: str | None  # Armor ID
    items: list[str]  # Other items
    
    def get_equipped_weapon(self) -> Weapon | None
    def get_equipped_armor(self) -> Armor | None
```

### 4. Priority

**Decision**: Low priority, basic implementation

- Core weapons only (10-15)
- Basic armor types (4-5)
- Simple inventory
- Can extend later

## Implementation Requirements

### EQUIP-01: Weapon Database
- Weapon Pydantic model
- 10+ weapon definitions
- Melee and ranged categories
- Damage expressions

### EQUIP-02: Armor Database
- Armor Pydantic model
- 4+ armor types
- Protection values

### EQUIP-03: Combat Integration
- Weapon damage in combat
- Armor damage reduction
- Equipment selection

### EQUIP-04: Inventory Management
- Inventory model
- Equip/unequip
- Basic item tracking

### EQUIP-05: Scenario Usage
- Equipment in scenarios
- Combat with weapons
- Equipment effects verified

## Files to Create

- `src/dm_bot/coc/equipment.py` - Equipment models and loader
- `data/equipment/weapons.json` - Weapon definitions
- `data/equipment/armor.json` - Armor definitions
- `src/dm_bot/coc/inventory.py` - Inventory management
- `tests/coc/test_equipment.py` - Unit tests
- `tests/scenarios/acceptance/scen_equipment_combat.yaml` - E2E

## Success Criteria

- [ ] Weapon database includes COC 7e weapon stats
- [ ] Armor database includes protection values
- [ ] Equipment effects applied in combat resolution
- [ ] Basic inventory management tracks equipped items
- [ ] Equipment can be used in scenario tests
