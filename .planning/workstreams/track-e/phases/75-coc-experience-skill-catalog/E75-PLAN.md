# Phase E75: COC Experience + Skill Catalog Tests

## Goal
Create tests for COC 7th Edition experience, skill improvement, and skill/spell catalog.

## Success Criteria
- [x] 90+ tests covering experience and skill systems
- [x] All tests passing
- [x] Skill catalog validation complete

## Test Targets

### Experience System (`experience.py`)
- `roll_skill_improvement()` - 1d100 < skill → +1d10
- `roll_all_skill_improvements()` - Batch improvement
- `calculate_new_session_skill_points()` - Credit Rating + INT based
- `get_occupational_skill_points()` - Occupational points table
- `get_interest_skill_points()` - Interest points table
- `spend_occupational_point()` - Spend occupational points
- `spend_interest_point()` - Spend interest points

### Skill Catalog (`skills.py`)
- `COC_SKILLS` - 80+ skill definitions
- `resolve_skill_check()` - Skill check with success ranks
- `get_skills_by_category()` - Filter by category
- `get_skill_categories()` - List categories

### Spell Catalog (`magic.py`)
- `COC_SPELLS` - 20+ spell definitions
- `calculate_mp()` - Spell MP cost
- `resolve_spell_cast()` - Spell casting resolution

## Test Breakdown

| Task | Tests | Description |
|------|-------|-------------|
| Skill Improvement | 9 | Roll mechanics, success/failure |
| Skill Points | 16 | Allocation and spending |
| Skill Catalog | 13 | 80+ skills validation |
| Spell Catalog | 15 | 20+ spells validation |
| Skill Resolution | 8 | Check resolution |
| **Total** | **91** | |

## Key Test Scenarios
- Skill improvement: 1d100 roll < current skill
- Credit Rating table lookup
- INT-based interest points
- Skill catalog: base points, categories, eras
- Spell catalog: MP costs, schools, types
- Success ranks: critical, success, failure, fumble

## Dependencies
- `src/dm_bot/rules/coc/experience.py`
- `src/dm_bot/rules/coc/skills.py`
- `src/dm_bot/rules/coc/magic.py`

## Files Created
- `tests/rules/coc/test_experience_and_skill_catalog.py` (638 lines, 91 tests)

## Bugs Found & Fixed
1. `resolve_spell_cast()` missing `mp_cost` field in insufficient MP return

## Verification
```bash
uv run pytest tests/rules/coc/test_experience_and_skill_catalog.py -q
# 91 passed
```
