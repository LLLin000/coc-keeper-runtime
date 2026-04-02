---
phase: E85-equipment-system
plan: 01
subsystem: coc-equipment
tags:
  - equipment
  - weapons
  - armor
  - inventory
  - combat
dependency_graph:
  requires: []
  provides:
    - EQUIP-01
    - EQUIP-02
    - EQUIP-03
    - EQUIP-04
    - EQUIP-05
  affects:
    - combat.py
    - rules/coc
tech_stack:
  added:
    - pydantic
    - d20
  patterns:
    - equipment-database
    - inventory-management
key_files:
  created:
    - src/dm_bot/coc/equipment.py
    - src/dm_bot/coc/inventory.py
    - data/equipment/weapons.json
    - data/equipment/armor.json
    - tests/coc/test_equipment.py
    - tests/scenarios/acceptance/scen_equipment_combat.yaml
  modified:
    - src/dm_bot/rules/coc/combat.py
decisions:
  - "Equipment database uses JSON files for weapon/armor definitions"
  - "Inventory validates weapons against equipment database when equipped"
  - "Combat integration uses equipment_db for weapon damage and armor protection"
metrics:
  duration_minutes: 5
  completed_date: "2026-03-31T12:48:00.000Z"
  tasks_completed: 7
  tests_passed: 12
  files_created: 6
  files_modified: 1
---

# Phase E85 Plan 01: Equipment System Summary

## One-liner

Weapon/armor database with 13 weapons and 5 armor types, inventory management, and combat integration for COC 7e.

## Completed Tasks

| Task | Name | Status | Commit |
|------|------|--------|--------|
| 1 | Create equipment models | ✅ | 3f2f3c9 |
| 2 | Create weapons.json | ✅ | 3f2f3c9 |
| 3 | Create armor.json | ✅ | 3f2f3c9 |
| 4 | Create inventory system | ✅ | 3f2f3c9 |
| 5 | Integrate equipment into combat | ✅ | 3f2f3c9 |
| 6 | Create unit tests | ✅ | 3f2f3c9 |
| 7 | Create E2E scenario | ✅ | 3f2f3c9 |

## Artifacts Created

### Equipment Models (`src/dm_bot/coc/equipment.py`)
- `Weapon` model with id, name, name_cn, category, damage, range, ammo_capacity, malfunction, skill
- `Armor` model with id, name, name_cn, protection, coverage, bulky
- `EquipmentDatabase` class with load_from_files, add/get/list methods
- 13 weapons: unarmed, knife, club, sword, axe, pistol_light, pistol_heavy, rifle, shotgun, submachine_gun, rifle_assault, thrown_knife, thrown_rock
- 5 armor types: none, leather_jacket, heavy_leather, riot_gear, plate_mail

### Inventory System (`src/dm_bot/coc/inventory.py`)
- `Inventory` model with weapons list, equipped_weapon, armor, items, cash, assets
- `InventoryManager` class for managing multiple character inventories
- equip_weapon validates against equipment database
- get_weapon_damage and get_armor_protection helper methods

### Combat Integration (`src/dm_bot/rules/coc/combat.py`)
- `resolve_fighting_attack_with_equipment()` - looks up weapon/armor from database
- `resolve_shooting_attack_with_equipment()` - looks up weapon/armor from database

### Unit Tests (`tests/coc/test_equipment.py`)
- 12 tests covering Weapon, Armor, EquipmentDatabase, Inventory, InventoryManager
- All tests pass

### E2E Scenario (`tests/scenarios/acceptance/scen_equipment_combat.yaml`)
- Validates weapon damage and armor protection in combat

## Deviations from Plan

None - plan executed exactly as written.

## Verification

- `uv run pytest tests/coc/test_equipment.py -v` → 12 passed
- Equipment module imports correctly
- Inventory system integrates with equipment database

## Requirements Satisfied

- ✅ EQUIP-01: Weapon database with 13 COC 7e weapon definitions
- ✅ EQUIP-02: Armor database with 5 protection levels
- ✅ EQUIP-03: Combat integration for weapon damage
- ✅ EQUIP-04: Inventory system with equip/unequip
- ✅ EQUIP-05: E2E scenario for equipment combat
