# Phase 13-01 Summary: Integration & Testing

## Goal
Add comprehensive test coverage for all 6 COC handlers (fighting, shooting, brawl, dodge, grapple, cast_spell) and fix pre-existing `san_loss` → `sanity_loss` bug.

## What Was Built

### 1. Test Infrastructure: `StubPercentileRollerForCombat`

```python
class StubPercentileRollerForCombat:
    """Returns deterministic rolls for combat tests - handles opposed checks."""
    def __init__(self, attacker_roll: int, defender_roll: int):
        self._attacker_roll = attacker_roll
        self._defender_roll = defender_roll
        self._call_count = 0
```

**Roll behavior:**
- 1st call: returns `_attacker_roll`
- 2nd call: returns `_defender_roll`
- 3rd+ calls: return 50 (neutral)

**Stub usage by handler:**
| Handler | Stub Usage | Notes |
|---------|------------|-------|
| Fighting | `(attacker, defender)` | 2 calls needed |
| Shooting | `(roll, 0)` | 2 calls, second ignored |
| Brawl | `(attacker, defender)` | 2 calls needed |
| Dodge | `(defender, attacker)` | **Swapped!** |
| Grapple | `(attacker, defender)` | 2 calls needed |

### 2. Test Coverage: 32 Tests Total

| Category | Success | Failure | Critical | Fumble | Subtotal |
|----------|---------|---------|----------|--------|----------|
| Fighting | ✅ | ✅ | ✅ | ✅ | 4 |
| Shooting | ✅ | ✅ | ✅ | ✅ | 4 |
| Brawl | ✅ | ✅ | ✅ | ✅ | 4 |
| Dodge | ✅ | ✅ | ✅ | ✅ | 4 |
| Grapple | ✅ | ✅ | ✅ | ✅ | 4 |
| Cast Spell | ✅ | ✅ | ✅ | ✅ | 4 |
| Sanity | - | - | - | - | 1 |
| Stub Tests | - | - | - | - | 7 |
| **Total** | | | | | | **32** |

### 3. Bug Fix: `san_loss` → `sanity_loss`

**File:** `tests/test_rules_engine.py` line 188
```python
# Before (broken):
assert san_loss == 1

# After (fixed):
assert sanity_loss == 1
```

### 4. Combat Resolution Rules Verified

| Outcome | Condition |
|---------|-----------|
| **Critical** | Attacker roll = 1 (fumble on 96-100, critical on 1-5) |
| **Success** | `attacker_roll < defender_roll` (strict, not ≤) |
| **Failure** | `attacker_roll >= defender_roll` |
| **Fumble** | Attacker roll = 96-100 |

**Note:** Opposed check uses strict `<` not `≤` for success.

## Key Test Examples

### Fighting: Critical Success
```python
result = resolve_fighting_attack(target, actor,
    StubPercentileRollerForCombat(1, 50))
assert result.outcome == CombatOutcome.CRITICAL
assert result.damage == 20  # 2d6=12 * 2
```

### Dodge: Success (swapped rolls)
```python
result = resolve_fighting_attack(target, actor,
    StubPercentileRollerForCombat(50, 30))  # defender=30, attacker=50
assert result.outcome == CombatOutcome.SUCCESS
```

### Shooting: Single Roll (second ignored)
```python
result = resolve_shooting_attack(target, actor,
    StubPercentileRollerForCombat(10, 0))
assert result.outcome == CombatOutcome.SUCCESS
```

## Verification

```bash
uv run pytest tests/test_rules_engine.py -v
# Result: 32 passed ✅

# Smoke-check (shows pre-existing failures unrelated to Phase 13):
uv run pytest -x --tb=no -q
# Note: ~14 pre-existing failures from Phase 09 skills migration
```

## Decisions Made (D-01 to D-04)

| Decision | Option | Description |
|----------|--------|-------------|
| D-01 Coverage | B (Extended) | All 4 test types per handler (success/failure/critical/fumble) |
| D-02 Parameters | B (Full) | All parameters including optional ones |
| D-03 Bug Fix | A (Fix existing) | Fix pre-existing `san_loss` → `sanity_loss` |
| D-04 Smoke-check | B (Full) | Run full smoke-check after tests |

## Files Changed

| File | Change |
|------|--------|
| `tests/test_rules_engine.py` | +826 lines (32 tests, stub infrastructure) |
| `.planning/workstreams/track-a/phases/13-integration-testing/13-CONTEXT.md` | Updated with decisions |
| `.planning/workstreams/track-a/phases/13-integration-testing/13-01-PLAN.md` | Phase plan |
| `.planning/workstreams/track-a/phases/13-integration-testing/13-01-SUMMARY.md` | This summary |

## Pre-existing Failures (Not Phase 13 Scope)

~14 tests fail due to `skills` field expecting `list[SkillEntry]` but receiving `dict[str, int]`. Root cause: Phase 09 skill migration changed schema. Affected files:
- `test_character_import.py`
- `test_coc_assets.py`
- `test_diagnostics.py`
- `test_investigator_panels.py`
- `test_persistence_store.py`
- `test_phase2_integration.py`
- `test_v18_archive_builder.py`

## Next Steps

- **vA.1.4 milestone complete** - all 6 COC handlers have test coverage
- Ready for Phase 14 or vA.1.5 planning
