# Phase E81: Creature Bestiary & Stats Summary

## Phase Information

| Field | Value |
|-------|-------|
| Phase | E81-creature-bestiary |
| Plan | 01 |
| Status | **COMPLETE** |
| Started | 2026-03-31T20:15:00Z |
| Duration | ~45 minutes |
| Requirements | BESTIARY-01, BESTIARY-02, BESTIARY-03, BESTIARY-04, BESTIARY-05 |

## Objective

Create a bestiary system with stats for common COC creatures to enable creature encounters in adventures with proper combat and sanity mechanics.

## Deliverables

### Artifacts Created

| Artifact | Lines | Status |
|----------|-------|--------|
| `src/dm_bot/coc/bestiary.py` | ~230 | ✅ Complete |
| `src/dm_bot/coc/creature.py` | ~135 | ✅ Complete |
| `data/bestiary/creatures.json` | ~400 | ✅ Complete |
| `src/dm_bot/rules/coc/sanity.py` | +75 | ✅ Modified |
| `tests/rules/coc/test_bestiary.py` | ~200 | ✅ Complete |
| `tests/scenarios/acceptance/scen_creature_encounter.yaml` | ~90 | ✅ Complete |

### Creatures Added (10 total)

1. **Deep One** (深潜者) - Mythos, amphibious fish-humanoids
2. **Shoggoth** (修格斯) - Mythos, protoplasmic horror with regeneration
3. **Ghoul** (食尸鬼) - Monster, paralysis-inducing undead feeders
4. **Byakhee** (拜亚基) - Mythos, winged servants of Hastur
5. **Zombie** (僵尸) - Undead, mindless reanimated corpses
6. **Cultist** (邪教徒) - Human, spellcasting servants of Mythos
7. **Dimensional Shambler** (维度行者) - Mythos, teleporting predators
8. **Hunting Horror** (猎食恐怖) - Mythos, flying serpentine horrors
9. **Mi-Go** (米·戈) - Mythos, fungoid aliens with technology
10. **Nightgaunt** (夜魇) - Mythos, faceless flying servants

## Implementation Details

### Core Models

**CreatureTemplate** - Static bestiary data:
- Identity (id, name, name_cn, category, size)
- Attributes with support for ranges (e.g., STR: 80-120)
- Combat stats (fighting, dodge, armor, damage_bonus)
- SAN loss (first_encounter, subsequent, indefinite flag)
- Special abilities and spells

**CreatureInstance** - Runtime creature state:
- HP tracking with damage/healing
- Condition management
- Encounter tracking (which players have seen this creature)
- Attribute values (rolled or fixed)

**CreatureManager** - Session creature lifecycle:
- Spawn creatures from templates
- HP modifiers for difficulty scaling
- Instance tracking and cleanup

### Integration Points

**Combat Integration** (`src/dm_bot/rules/coc/combat.py`):
- `creature_to_combatant()` - Convert CreatureInstance to CombatantStats
- `resolve_creature_attack()` - Resolve creature attacks with damage calculation

**Sanity Integration** (`src/dm_bot/rules/coc/sanity.py`):
- `resolve_creature_encounter_sanity()` - Apply SAN loss for creature encounters
- Handles first/subsequent encounter distinction
- Triggers indefinite insanity when creature has that flag

## Test Results

```
40 passed in 0.22s
- TestSanLoss: 4 tests
- TestCreatureAttributes: 3 tests  
- TestCreatureTemplate: 5 tests
- TestBestiary: 6 tests
- TestBestiaryLoadFromFile: 1 test
- TestCreatureManager: 15 tests
- TestCreatureCombat: 2 tests
- TestCreatureSanityIntegration: 3 tests
```

## Deviation Notes

None - plan executed exactly as written.

## Known Issues

The following pre-existing test failures are unrelated to this phase:
- `test_armor_piercing_bypasses_armor` - Pre-existing bug in original combat.py
- `TestVisibilityDispatcher` tests - Pre-existing issues in visibility dispatcher
- `TestApplyAgeModifiers` tests - Pre-existing bugs in derived.py
- `TestSpellCatalogValidation` tests - Pre-existing bugs in magic.py

## Decisions Made

1. **Field naming**: Used `str_val` instead of `str` for strength attribute to avoid Python built-in shadowing issues with Pydantic
2. **Intelligence field**: Used `intel` as field name, mapped from JSON's `int` via validation alias
3. **Creature attack resolution**: Implemented `resolve_creature_attack()` that loads creature template at runtime for attack data

## Key Files Modified

| File | Change |
|------|--------|
| `src/dm_bot/coc/bestiary.py` | New - Bestiary models and Bestiary class |
| `src/dm_bot/coc/creature.py` | New - CreatureInstance and CreatureManager |
| `data/bestiary/creatures.json` | New - 10 COC creature definitions |
| `src/dm_bot/rules/coc/sanity.py` | Added `resolve_creature_encounter_sanity()` |
| `src/dm_bot/rules/coc/combat.py` | Added creature combat integration |

## Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| BESTIARY-01: Creature Data Models | ✅ Complete | CreatureTemplate, SanLoss, CreatureAbility |
| BESTIARY-02: Core Creatures | ✅ Complete | 10 creatures in creatures.json |
| BESTIARY-03: Combat Integration | ✅ Complete | creature_to_combatant, resolve_creature_attack |
| BESTIARY-04: Sanity Integration | ✅ Complete | resolve_creature_encounter_sanity |
| BESTIARY-05: Adventure Usage | ✅ Complete | Bestiary.load_from_file, CreatureManager.spawn |

---

*Phase E81 execution complete - 2026-03-31*
