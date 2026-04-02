# Phase E73 Context

## Source Code Analysis

### `src/dm_bot/rules/coc/derived.py`
- **Lines**: ~400
- **Purpose**: Calculate COC 7e derived attributes from characteristics
- **Key Functions**:
  - All calculation functions are pure (input → output)
  - Age modifiers apply characteristic penalties
  - Build/DB use lookup tables based on STR+SIZ
  - MOV has complex age-based reduction logic

### `src/dm_bot/rules/coc/sanity.py`
- **Lines**: ~200
- **Purpose**: Sanity system mechanics
- **Key Functions**:
  - Encounter-based SAN loss
  - Insanity break determination
  - Recovery mechanics

## Test Conventions
- Use `pytest` with descriptive class names
- Mock random rolls with `@patch`
- Test edge cases (0, minimums, maximums)
- Validate return types and field presence

## Reference
- Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 2
