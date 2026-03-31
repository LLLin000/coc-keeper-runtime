# Test Coverage Map

**Analysis Date:** 2026-03-31

## Test Infrastructure

### Framework
- **Runner:** pytest
- **Assertion Library:** pytest assertions
- **Test Files Location:** `tests/`
- **Scenario Tests:** YAML-based scenario DSL in `tests/scenarios/`
- **Test Driver:** `RuntimeTestDriver` in `testing/runtime_driver.py`

### Running Tests
```bash
uv run pytest -q                           # Run all tests
uv run pytest tests/test_rules_engine.py    # Run rules engine tests
uv run python -m dm_bot.main smoke-check   # Smoke check
```

---

## Coverage by Subsystem

### ✅ COC Rules Engine (`rules/engine.py`)

**Test File:** `tests/test_rules_engine.py` (1000 lines)

| Action Type | Test Status | Test Functions |
|-------------|-------------|----------------|
| `coc_skill_check` | ✅ Covered | `test_coc_skill_check_*` (difficulty, bonus/penalty dice, pushed rolls) |
| `coc_sanity_check` | ✅ Covered | `test_coc_sanity_check_*` (loss application, Mythos gain) |
| `coc_fighting_attack` | ✅ Covered | `test_coc_fighting_attack_*` (success, failure, critical, fumble) |
| `coc_shooting_attack` | ✅ Covered | `test_coc_shooting_attack_*` (success, failure, critical, fumble) |
| `coc_brawl_attack` | ✅ Covered | `test_coc_brawl_attack_*` (success, failure, critical, fumble) |
| `coc_dodge` | ✅ Covered | `test_coc_dodge_*` (success, failure, critical, fumble) |
| `coc_grapple_attack` | ✅ Covered | `test_coc_grapple_attack_*` (success, failure, critical, fumble) |
| `coc_cast_spell` | ✅ Covered | `test_coc_cast_spell_*` (success, failure, critical, fumble) |
| `attack_roll` (D&D) | ✅ Covered | `test_rules_engine_executes_attack_*` |
| `ability_check` | ✅ Covered | `test_rules_engine_executes_ability_check_*` |
| `damage_roll` | ✅ Covered | `test_rules_engine_executes_damage_roll_*` |
| `raw_roll` | ✅ Covered | `test_rules_engine_executes_raw_roll_*` |
| `lookup` | ✅ Covered | `test_compendium_returns_2014_srd_*` |

**Coverage:** ~95% of `RulesEngine` action types tested

---

### ✅ COC Skill Check Flow (`rules/coc/skills.py`)

**Test File:** `tests/test_coc_rules_flow.py` (264 lines)

| Test | What It Covers |
|------|----------------|
| `test_coc_skill_check_critical_on_01` | Roll of 01 = automatic success |
| `test_coc_skill_check_fumble_on_96_plus` | Roll ≥ 96 = fumble |
| `test_coc_skill_check_fumble_on_100` | Roll of 100 = fumble regardless of skill |
| `test_coc_skill_check_success_regular` | Regular difficulty threshold |
| `test_coc_skill_check_success_hard` | Hard (÷2) threshold |
| `test_coc_skill_check_success_extreme` | Extreme (÷5) threshold |
| `test_coc_skill_check_failure` | Failure when roll > threshold |
| `test_coc_skill_check_zero_value_raises` | Error on value ≤ 0 |
| `test_coc_skill_check_negative_value_raises` | Error on negative value |

**Coverage:** Skill check resolution (difficulty, critical, fumble) ✅

---

### ✅ Dice Rolling (`rules/dice.py`)

**Test Coverage:** Via `test_rules_engine.py` with `StubPercentileRoller` and `StubPercentileRollerForCombat`

| Dice Roller | Status |
|-------------|--------|
| `D20DiceRoller` | ✅ Used in actual engine (real dice) |
| `SeededDiceRoller` | ✅ Available for deterministic tests |
| `_LegacyDiceRoller` | ✅ Covered (backward compat tests) |

---

### ✅ Router & Intent Classification (`router/`)

**Test Files:**
- `tests/test_intent_routing.py`
- `tests/test_intent_classification_flow.py`
- `tests/test_router_service_flow.py`

| Component | Status |
|-----------|--------|
| `MessageIntent` types | ✅ Tested |
| `IntentHandlerRegistry` | ✅ Tested |
| Phase-dependent priorities | ✅ Tested |
| Message buffering | ✅ Tested |

---

### ✅ Session Phase Transitions (`orchestrator/`)

**Test Files:**
- `tests/test_session_phase_transitions.py`
- `tests/test_lobby_flow.py`
- `tests/test_ready_commands.py`
- `tests/test_ready_gate.py`

| Phase | Status |
|-------|--------|
| `onboarding` | ✅ Tested |
| `lobby` | ✅ Tested |
| `awaiting_ready` | ✅ Tested |
| `scene_round_open` | ✅ Tested |
| `scene_round_resolving` | ✅ Tested |
| `combat` | ✅ Tested |
| `paused` | ✅ Tested |

---

### ✅ Combat System (`gameplay/combat.py`)

**Test Files:**
- `tests/test_combat_resolution_flow.py`
- `tests/test_combat_loop.py`
- `tests/bdd/test_combat_round_bdd.py`

| Feature | Status |
|---------|--------|
| Initiative rolling | ✅ Tested |
| Turn advancement | ✅ Tested |
| Combatant tracking | ✅ Tested |
| Combat summary | ✅ Tested |

---

### ✅ Character System (`characters/`)

**Test Files:**
- `tests/test_character_import.py`
- `tests/test_character_profile_projection.py`
- `tests/test_character_archive_flow.py`

| Component | Status |
|-----------|--------|
| `CharacterRecord` model | ✅ Tested |
| `COCInvestigatorProfile` | ✅ Tested |
| Character import | ✅ Tested |
| Panel sync | ✅ Tested |

---

### ✅ Investigator Panels (`coc/panels.py`)

**Test File:** `tests/test_investigator_panels.py`

| Feature | Status |
|---------|--------|
| Panel creation | ✅ Tested |
| SAN/HP/MP tracking | ✅ Tested |
| Skill display | ✅ Tested |
| Journal entries | ✅ Tested |

---

### ✅ Scenario DSL & Runtime (`testing/`)

**Test Files:**
- `tests/test_scenario_runner.py`
- `tests/test_scenarios.py`

| Component | Status |
|-----------|--------|
| `ScenarioParser` | ✅ Tested |
| `ScenarioRegistry` | ✅ Tested |
| `RuntimeTestDriver` | ✅ Tested |
| Scenario execution | ✅ Tested |

---

### ✅ Narrative Service (`narration/`)

**Test Files:**
- `tests/test_narration_service.py`
- `tests/test_narration_pipeline_flow.py`
- `tests/test_narration_streaming_flow.py`

| Feature | Status |
|---------|--------|
| Narration generation | ✅ Tested |
| Streaming output | ✅ Tested |
| Scene formatting | ✅ Tested |

---

### ✅ Persistence & Recovery

**Test Files:**
- `tests/test_persistence_store.py`
- `tests/test_restart_system.py`
- `tests/scenarios/recovery/` (scenario directory)

| Feature | Status |
|---------|--------|
| Session save/load | ✅ Tested |
| Event persistence | ✅ Tested |
| Restart recovery | ✅ Tested |

---

## Scenario Directories

| Directory | Purpose | Scenario Count |
|-----------|---------|----------------|
| `tests/scenarios/acceptance/` | Standard acceptance tests | Unknown |
| `tests/scenarios/contract/` | Model contract tests | Unknown |
| `tests/scenarios/chaos/` | Chaos/stress tests | Unknown |
| `tests/scenarios/recovery/` | Persistence recovery tests | Unknown |

---

## NOT Directly Tested (but may be via integration)

| Subsystem | Test File | Coverage |
|-----------|-----------|----------|
| `rules/coc/skills.py` - `COC_SKILLS` dict | Not directly unit-tested | Integration only |
| `rules/coc/derived.py` - All functions | Not directly unit-tested | Integration only |
| `rules/coc/experience.py` - All functions | Not directly unit-tested | Integration only |
| `rules/coc/sanity.py` - `roll_insanity_break` | Not directly unit-tested | Via sanity check |
| `rules/coc/magic.py` - `COC_SPELLS` dict | Not directly unit-tested | Via spell cast |
| `rules/coc/combat.py` - `calculate_damage_bonus` | Not directly unit-tested | Via combat |
| `rules/coc/combat.py` - `get_range_modifier` | Not directly unit-tested | Via shooting |

---

## Summary by Track

| Track | Subsystem | Unit Test Coverage | Integration Coverage |
|-------|-----------|-------------------|---------------------|
| **Track A** | COC Rules (skills, combat, sanity, magic, derived, experience) | ~70% (via engine) | ~90% |
| **Track B** | Characters & Archive | ~80% | ~85% |
| **Track C** | Discord Interaction | ~75% | ~80% |
| **Track E** | Runtime & Orchestration | ~80% | ~85% |

---

*Test coverage map: 2026-03-31*
