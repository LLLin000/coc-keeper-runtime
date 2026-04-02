# Phase E74 Context

## Source Code Analysis

### `src/dm_bot/rules/coc/combat.py`
- **Lines**: ~692
- **Purpose**: Combat resolution mechanics
- **Key Concepts**:
  - Opposed checks for combat
  - Critical (01) = max damage + impale
  - Fumble (100) = self-harm or dropped weapon
  - Armor reduces damage
  - Armor piercing ignores armor

### `src/dm_bot/rules/coc/sanity.py`
- **Lines**: ~200
- **Purpose**: Sanity and insanity mechanics
- **Key Concepts**:
  - Temporary insanity: failed POW check or severe threat
  - Indefinite insanity: SAN reaches 0
  - Recovery: rest and therapy

## Test Conventions
- Mock dice rolls for deterministic tests
- Test both success and failure paths
- Verify state changes after combat
- Test cross-system interactions

## Reference
- Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 7 (Combat) and Chapter 9 (Sanity)
