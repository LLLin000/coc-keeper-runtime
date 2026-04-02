# Phase 64: Rules Engine Flow - Context

## Overview
- **Phase**: 64-rules-engine
- **Goal**: Validate COC rule flows — skill checks, SAN damage, combat round resolution, pushed rolls — in the context of the fuzhe adventure.
- **Depends on**: Phase 63 (Adventure Runtime)
- **Requirements**: RULES-01, RULES-02, RULES-03

## What Exists

### Source Files
| File | Purpose |
|------|---------|
| `src/dm_bot/rules/engine.py` | RulesEngine with `execute(action)` for attack_roll, coc_skill_check, coc_sanity_check, damage_roll |
| `src/dm_bot/rules/dice.py` | D20DiceRoller, PercentileOutcome, success level computation |
| `src/dm_bot/rules/actions.py` | RuleAction, StatBlock, LookupAction Pydantic models |
| `src/dm_bot/rules/compendium.py` | FixtureCompendium for rules lookups |

### Key Methods in RulesEngine
```python
execute(action: RuleAction) -> dict
  - "coc_skill_check" → returns {success_level, roll, threshold, damage_or_healing}
  - "coc_sanity_check" → returns {san_loss, success_level, roll, threshold, sanity_damage}
  - "attack_roll" → returns {hit, damage, roll, ac}
  - "damage_roll" → returns {total, breakdown}
  - "saving_throw" → returns {success, DC, roll}

# Success levels: "critical" (01), "extreme" (≤5%), "hard" (≤20%), "success" (≤50%), "failure" (>50%), "fumble" (96-100)
```

### Existing Tests
| File | Coverage |
|------|----------|
| `tests/test_rules_engine.py` | 188 lines — coc_skill_check, sanity check, attack roll, compendium lookup |
| `tests/test_combat_loop.py` | Combat round resolution, HP tracking |

## Gap Analysis

Per test-coverage-survey.md:
> "Rules Engine: Strong unit coverage for deterministic COC checks (188 lines)"

**Existing gap**: Unit tests verify dice outcomes in isolation. Missing:
1. **RULES-01**: Skill check success levels in a gameplay context (not just engine unit)
2. **RULES-02**: SAN damage with 7th ed rulebook values (not just engine-level)
3. **RULES-03**: Combat round resolution with HP tracking and defeated state — full flow test
4. **Pushed roll** behavior — when a player chooses to push a failed check

## Requirements Coverage

| Requirement | What to Test |
|-------------|--------------|
| RULES-01 | `coc_skill_check` with various roll totals returns correct success level; critical (01), extreme (≤5%), hard (≤20%), success (≤50%), failure (>50%), fumble (96-100) |
| RULES-02 | SAN damage: real SAN loss from investigator's current sanity vs. breakdown threshold; temporary vs. indefinite insanity triggers |
| RULES-03 | Combat round: apply damage to HP, detect defeated (HP≤0), remove from combat order |
| (implied) | Pushed roll: player can push a failed check, re-roll, and face consequences on second failure |

## Approach

1. Create `tests/test_coc_rules_flow.py` — COC skill checks and SAN damage in gameplay context
2. Create `tests/test_combat_resolution_flow.py` — HP tracking, defeated state, combat round resolution
3. Create `tests/test_pushed_roll_flow.py` — pushed roll re-roll and consequence on second failure

All tests use the FastMock model fixture from E60 infrastructure.
