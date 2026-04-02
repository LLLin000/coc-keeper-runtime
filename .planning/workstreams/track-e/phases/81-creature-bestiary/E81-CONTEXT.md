# Phase E81 Context: Creature Bestiary & Stats

## Goal
Create a bestiary system with stats for common COC creatures that integrates with combat and sanity systems.

## Background

### Current State
- Combat system exists (`combat.py`) but only supports player characters
- No creature/monster stats defined
- Sanity system exists but no creature SAN loss values
- Need stats for: Deep One, Shoggoth, Ghoul, Byakhee, Zombie, Cultist, etc.

### COC 7e Creature Stats
Creatures need:
- Attributes: STR, CON, SIZ, INT, POW, DEX
- Derived: HP, DB, Build, MOV
- Combat: Fighting, Dodge, Armor
- Sanity: SAN loss on seeing/encountering
- Special: Abilities, spells, immunities

## Design Decisions

### 1. Bestiary Data Structure

**Decision**: Pydantic models with JSON file storage

**Rationale**:
- Easy to edit and extend
- Version controlled
- Can load at runtime
- Supports localization

**Structure**:
```python
class CreatureTemplate(BaseModel):
    """Template for a COC creature."""
    id: str
    name: str
    name_cn: str
    category: CreatureCategory  # MONSTER, HUMAN, MYTHOS
    
    # Attributes (typical values or ranges)
    attributes: CreatureAttributes
    
    # Combat
    fighting: int
    dodge: int
    armor: int
    
    # Sanity
    san_loss: SanLoss  # First / Subsequent seeing
    
    # Special
    abilities: list[str]
    spells: list[str]
    immunities: list[str]
    
    # Description
    description: str
    tactics: str
```

### 2. Creature Instance vs Template

**Decision**: Separate template from instance

**Rationale**:
- Template = static data (bestiary entry)
- Instance = runtime state (current HP, conditions)
- Multiple instances from one template

### 3. Integration Points

**Combat Integration**:
- Creatures can be combatants
- Use template stats for initiative, attacks
- Track instance HP separately

**Sanity Integration**:
- Encounter triggers SAN loss
- First time vs subsequent different values
- Some creatures cause indefinite insanity

**Adventure Integration**:
- Reference creatures by ID in adventures
- Spawn instances with custom HP modifiers
- Override stats for specific scenarios

### 4. Bestiary Storage

**Decision**: JSON files in `data/bestiary/`

**Rationale**:
- Human-readable and editable
- Easy to version control
- Can add images later
- Supports modding

## Implementation Requirements

### BESTIARY-01: Creature Data Models
- CreatureTemplate Pydantic model
- CreatureInstance for runtime state
- CreatureCategory enum
- SanLoss model

### BESTIARY-02: Core Creatures
At least 10 common COC creatures:
1. Deep One
2. Shoggoth
3. Ghoul
4. Byakhee
5. Zombie
6. Cultist (human)
7. Dimensional Shambler
8. Hunting Horror
9. Mi-Go
10. Nightgaunt

### BESTIARY-03: Combat Integration
- Creatures as CombatantStats
- Initiative calculation
- Attack resolution
- HP tracking

### BESTIARY-04: Sanity Integration
- SAN loss values per creature
- First/subsequent distinction
- Indefinite insanity triggers
- Encounter logging

### BESTIARY-05: Adventure Usage
- Load creatures in adventures
- Spawn with modifiers
- Reference in fuzhe_mini

## Files to Create/Modify

- `src/dm_bot/coc/bestiary.py` - Core models and loader
- `src/dm_bot/coc/creature.py` - Creature instance management
- `data/bestiary/creatures.json` - Creature definitions
- `src/dm_bot/rules/coc/combat.py` - Combat integration
- `src/dm_bot/rules/coc/sanity.py` - Sanity integration
- `tests/rules/coc/test_bestiary.py` - Unit tests
- `tests/scenarios/acceptance/scen_creature_encounter.yaml` - E2E

## Success Criteria

- [ ] Bestiary data structure supports COC creature stats
- [ ] At least 10 common creatures defined
- [ ] Creature stats integrate with combat system
- [ ] Sanity loss values linked to creatures
- [ ] Creatures usable in fuzhe_mini adventure
- [ ] Unit tests for all creatures
- [ ] E2E scenario validates creature encounter
