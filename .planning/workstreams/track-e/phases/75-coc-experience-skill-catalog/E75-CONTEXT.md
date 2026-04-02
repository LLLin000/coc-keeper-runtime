# Phase E75 Context

## Source Code Analysis

### `src/dm_bot/rules/coc/experience.py`
- **Lines**: ~150
- **Purpose**: Experience and skill improvement
- **Key Concepts**:
  - Skill improvement: roll 1d100 < skill to gain +1d10
  - Occupational points based on Credit Rating
  - Interest points based on INT
  - Immutable spending functions

### `src/dm_bot/rules/coc/skills.py`
- **Lines**: ~400
- **Purpose**: Skill catalog and resolution
- **Key Concepts**:
  - 80+ skills with base points and categories
  - Success ranks: critical, success, failure, fumble
  - Category-based filtering

### `src/dm_bot/rules/coc/magic.py`
- **Lines**: ~300
- **Purpose**: Spell catalog and casting
- **Key Concepts**:
  - 20+ spells with MP costs
  - Spell schools and types
  - Casting resolution with MP check

## Test Conventions
- Validate catalog completeness
- Test table lookups
- Mock dice for deterministic tests
- Verify immutable operations

## Reference
- Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 4 (Skills) and Chapter 10 (Magic)
