# Phase E75 Summary: COC Experience + Skill Catalog Tests

## Status: ✅ Complete

## Deliverables
- ✅ `tests/rules/coc/test_experience_and_skill_catalog.py` (638 lines, 91 tests)

## Test Coverage

| Task | Tests |
|------|-------|
| Skill Improvement Roll | 9 |
| Skill Point Allocation | 16 |
| Skill Point Spending | 7 |
| Skill Catalog Validation | 13 |
| Spell Catalog Validation | 15 |
| Skill Check Resolution | 8 |
| **Total** | **91** |

## Key Features Tested
- Skill improvement mechanics (1d100 < skill → +1d10)
- Credit Rating and INT-based skill points
- Occupational and interest point spending
- COC_SKILLS catalog (80+ skills)
- COC_SPELLS catalog (20+ spells)
- Skill check resolution with success ranks

## Bugs Fixed
1. `resolve_spell_cast()` missing `mp_cost` field in insufficient MP return

## Verification
```bash
uv run pytest tests/rules/coc/test_experience_and_skill_catalog.py -q
# 91 passed
```

## Commits
- Part of `1bdb9cb`: feat(track-e): update vE.3.1 state

## Next Phase
E76: Character Creation E2E Scenario
