# Phase E74: COC Combat + Insanity Integration Tests

## Goal
Create integration tests for COC 7th Edition combat resolution and insanity mechanics.

## Success Criteria
- [x] 56+ tests covering combat and insanity
- [x] All tests passing
- [x] Cross-system chain verified (combat → SAN → insanity)

## Test Targets

### Combat System (`combat.py`)
- `roll_initiative()` - DEX-based initiative
- `get_initiative_order()` - Sort combatants by initiative
- `resolve_fighting_attack()` - Melee attack resolution
- `resolve_shooting_attack()` - Ranged attack resolution
- `resolve_brawl_attack()` - Unarmed combat
- `resolve_grapple_attack()` - Grappling mechanics
- `calculate_build()` - Build from STR+SIZ
- `calculate_damage_bonus()` - DB calculation
- `get_damage_bonus_string()` - DB as string

### Insanity System (`sanity.py`)
- `roll_insanity_break()` - Determine insanity type
- `resolve_sanity_check()` - SAN check with consequences
- Insanity types: TEMPORARY, INDEFINITE, PERMANENT

## Test Breakdown

| Category | Tests | Description |
|----------|-------|-------------|
| Initiative | 6 | Rolling, sorting, tie-breaking |
| Build/DB | 8 | Calculations and string formatting |
| Fighting | 10 | Attack resolution, damage, impale |
| Shooting | 8 | Range modifiers, recoil, ammo |
| Brawl/Grapple | 6 | Unarmed damage, self-damage |
| Armor | 6 | Penetration, damage reduction |
| Insanity | 12 | Triggers, types, recovery |
| **Total** | **56** | |

## Key Test Scenarios
- Critical hits (01) and fumbles (100)
- Impale mechanic for piercing weapons
- Armor piercing bypass
- Combat → SAN loss → insanity chain
- Temporary vs indefinite insanity triggers

## Dependencies
- `src/dm_bot/rules/coc/combat.py`
- `src/dm_bot/rules/coc/sanity.py`
- `src/dm_bot/rules/coc/derived.py`

## Files Created
- `tests/rules/coc/test_combat_and_insanity.py` (800 lines, 56 tests)

## Bugs Found & Fixed
1. Armor piercing logic inverted in `combat.py:265`

## Verification
```bash
uv run pytest tests/rules/coc/test_combat_and_insanity.py -q
# 56 passed
```
