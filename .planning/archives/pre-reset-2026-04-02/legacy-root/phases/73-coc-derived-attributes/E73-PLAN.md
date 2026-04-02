# Phase E73: COC Derived Attributes Unit Tests

## Goal
Create comprehensive unit tests for COC 7th Edition derived attribute calculations.

## Success Criteria
- [x] 75+ tests covering all derived attribute functions
- [x] All tests passing
- [x] Coverage for edge cases (age modifiers, luck spending, etc.)

## Test Targets

### Module: `derived.py`
- `calculate_luck()` - POW × 5
- `calculate_hp()` - (SIZ + CON) / 10 (rounded down)
- `calculate_mp()` - POW / 5 (rounded down)
- `calculate_sanity()` - POW × 5
- `calculate_move_rate()` - Based on STR/DEX/SIZ with age modifiers
- `calculate_build()` - STR + SIZ lookup table
- `calculate_damage_bonus()` - STR + SIZ lookup table
- `get_damage_bonus_dice_expression()` - Convert DB to dice notation
- `calculate_all_derived_attributes()` - Combined calculation
- `get_age_modifiers()` - Age band modifiers
- `apply_age_modifiers()` - Apply age effects to characteristics
- `roll_characteristic()` - Roll 3d6 or 2d6+6
- `generate_characteristics()` - Generate all 7 characteristics
- `spend_luck()` - Deduct luck points
- `recover_luck()` - Restore luck points

### Module: `sanity.py`
- `get_mythos_gain_for_encounter()` - Mythos knowledge gain
- `get_sanity_loss_for_encounter()` - SAN loss calculation
- `roll_insanity_break()` - Insanity type determination
- `resolve_sanity_check()` - SAN check resolution
- `calculate_sanity_recovery()` - SAN recovery mechanics
- `spend_luck_for_sanity()` - Luck for SAN protection

## Test Breakdown

| Category | Tests | Description |
|----------|-------|-------------|
| Luck | 5 | Standard, zero, edge cases |
| HP | 5 | Normal, minimum, edge cases |
| MP | 5 | Normal, minimum, edge cases |
| SAN | 5 | Normal calculation |
| MOV | 15 | 3 base cases × 5 age bands |
| Build | 6 | All lookup bands (-2 to +3) |
| DB | 6 | All lookup bands with dice expressions |
| Combined | 3 | Full derived calculation |
| Age Modifiers | 9 | 9 age bands with min(1) enforcement |
| Characteristics | 8 | Rolling and generation |
| Luck System | 8 | Spending and recovery |
| Sanity System | 6 | Core sanity functions |
| **Total** | **75** | |

## Edge Cases
- MOV minimum floor (regardless of age)
- Age modifier minimum enforcement (min 1)
- Damage Bonus dice expression conversion
- Characteristic generation with different age bands
- Luck spending/recovery bounds

## Dependencies
- `src/dm_bot/rules/coc/derived.py`
- `src/dm_bot/rules/coc/sanity.py`
- `src/dm_bot/characters/models.py`

## Files Created
- `tests/rules/coc/__init__.py`
- `tests/rules/coc/test_derived_attributes.py` (515 lines, 75 tests)

## Bugs Found & Fixed
1. `apply_age_modifiers()` missing `siz` field in return value
2. `generate_characteristics()` missing `random` import

## Verification
```bash
uv run pytest tests/rules/coc/test_derived_attributes.py -q
# 75 passed
```
