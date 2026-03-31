# Phase E74 Summary: COC Combat + Insanity Integration Tests

## Status: ✅ Complete

## Deliverables
- ✅ `tests/rules/coc/test_combat_and_insanity.py` (800 lines, 56 tests)

## Test Coverage

| Category | Tests |
|----------|-------|
| Initiative | 6 |
| Build/DB | 8 |
| Fighting | 10 |
| Shooting | 8 |
| Brawl/Grapple | 6 |
| Armor | 6 |
| Insanity | 12 |
| **Total** | **56** |

## Key Features Tested
- Initiative rolls and turn order
- Combat resolution (Fighting, Shooting, Brawl, Grapple)
- Armor penetration and damage
- Insanity triggers (TEMPORARY/INDEFINITE)
- Sanity recovery mechanics
- Cross-system chain: combat → SAN → insanity

## Bugs Fixed
1. Armor piercing logic inverted at `combat.py:265`

## Verification
```bash
uv run pytest tests/rules/coc/test_combat_and_insanity.py -q
# 56 passed
```

## Commits
- Part of `1bdb9cb`: feat(track-e): update vE.3.1 state

## Next Phase
E75: COC Experience + Skill Catalog Tests
