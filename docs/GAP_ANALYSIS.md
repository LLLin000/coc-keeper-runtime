# Gap Analysis

**Analysis Date:** 2026-03-31

## Critical Missing Tests (Track A COC Rules)

### 1. COC Derived Attributes (`rules/coc/derived.py`)

**Status:** ⚠️ No direct unit tests

**Functions needing tests:**
- `calculate_luck(pow_value)` - POW × 5
- `calculate_hp(con_value, siz_value)` - (CON + SIZ) / 10
- `calculate_mp(pow_value)` - POW / 5
- `calculate_sanity(pow_value)` - POW × 5
- `calculate_move_rate(str_value, dex_value, siz_value, age)` - MOV calculation with age
- `calculate_build(str_value, siz_value)` - Build from STR + SIZ
- `calculate_damage_bonus(build)` - DB from build rating
- `get_damage_bonus_string(build)` - DB string formatting
- `calculate_all_derived_attributes(attrs, age)` - Full derived calculation
- `get_age_modifiers(age)` - Age-based MOV reduction
- `apply_age_modifiers(derived, age)` - Apply age to derived
- `roll_characteristic()` - 3d6 rolling
- `generate_characteristics()` - Full characteristic generation
- `spend_luck(luck, amount)` - Spend luck points
- `recover_luck(luck, amount)` - Recover luck points

**Gap Severity:** HIGH

**Why it matters:** Derived attributes are fundamental to COC characters. Any error in these calculations affects every character in every session.

**Recommended test file:** `tests/test_coc_derived.py`

---

### 2. COC Experience System (`rules/coc/experience.py`)

**Status:** ⚠️ No direct unit tests

**Functions needing tests:**
- `get_occupational_skill_points(credit_rating)` - Credit → occupational points
- `get_interest_skill_points(int_value)` - INT → interest points
- `roll_skill_improvement(current_value, improvement_roll, die_roll)` - Improvement roll
- `roll_all_skill_improvements(skills, roll_fn)` - Multiple skill improvements
- `calculate_new_session_skill_points(credit_rating, int_value)` - Session point calculation
- `spend_occupational_point(skill, points, amount)` - Occupational point spending
- `spend_interest_point(skill, points, amount)` - Interest point spending
- `calculate_build_points_spent(points_spent)` - Track build points
- `generate_standard_characteristics()` - Standard 3d6 generation
- `get_occupation_skills(occupation)` - Get suggested skills
- `OCCUPATION_SKILL_SUGGESTIONS` - 20+ occupations defined

**Gap Severity:** HIGH

**Why it matters:** Experience and skill improvement are core to COC character progression across sessions.

**Recommended test file:** `tests/test_coc_experience.py`

---

### 3. COC Skill Definitions (`rules/coc/skills.py`)

**Status:** ⚠️ No direct unit tests for the skill catalog

**What needs tests:**
- `COC_SKILLS` dict completeness (80+ skills defined)
- `SkillDefinition` model validation
- `get_skills_by_category(category)` - Category filtering
- `get_skill_categories()` - List all categories
- `is_specialized_skill(skill_name)` - Specialization detection
- `expand_specialized_skill(skill_name, subtype)` - Full skill name
- `get_skill_display_name(skill_name, language)` - i18n display
- `OCCUPATIONAL_SKILL_POINTS` - Occupational point table
- `INTEREST_SKILL_POINTS` - Interest point table
- `IMPROVEMENT_SKILL_POINTS` - Improvement point table

**Gap Severity:** MEDIUM

**Why it matters:** Skills are the primary resolution mechanism. Wrong skill values break the game.

**Recommended test file:** `tests/test_coc_skills_catalog.py`

---

### 4. COC Sanity System - Insanity Break (`rules/coc/sanity.py`)

**Status:** ⚠️ Partial coverage via sanity check tests

**Functions needing direct tests:**
- `roll_insanity_break(actor_name, current_san, max_san, context)` - Direct test
  - Temporary insanity (acute response)
  - Indefinite insanity (phobia/mania acquisition)
- `COMMON_PHOBIAS` - 30+ phobia definitions
- `COMMON_MANIAS` - 30+ mania definitions
- `get_mythos_gain_for_encounter(encounter_type)` - Mythos knowledge gain
- `calculate_sanity_recovery(current_san, rest_days, therapy, real_world)` - Recovery calculation

**Gap Severity:** HIGH

**Why it matters:** Insanity breaks are dramatic moments that need reliable behavior.

**Recommended test file:** `tests/test_coc_insanity.py`

---

### 5. COC Magic System (`rules/coc/magic.py`)

**Status:** ⚠️ Partial coverage via spell casting tests

**Functions needing direct tests:**
- `COC_SPELLS` dict completeness (10+ spells defined)
- `SpellDefinition` model validation
- `Spellbook` and `SpellbookEntry` management
- `calculate_mp(pow_value)` - Already in derived, but needs explicit magic test
- `get_mp_for_level(caster_level)` - MP calculation
- Individual spell-specific behaviors (Contact Ghoul cost, Elder Sign requirements, etc.)

**Gap Severity:** MEDIUM

**Recommended test file:** `tests/test_coc_magic_catalog.py`

---

### 6. COC Combat - Damage Resolution (`rules/coc/combat.py`)

**Status:** ⚠️ Partial coverage via attack tests

**Functions needing direct tests:**
- `calculate_build(str_value, siz_value)` - Build rating calculation
- `calculate_damage_bonus(build)` - Damage bonus from build
- `get_damage_bonus_string(build)` - DB string formatting
- `get_damage_bonus_dice_expression(build)` - Dice expression
- `get_range_modifier(range_category)` - Range modifier lookup
- `RANGE_MODIFIERS` dict - Range categories and modifiers
- Major wound threshold calculation
- Armor absorption calculation
- Critical hit damage multiplier (×2 for impales)

**Gap Severity:** MEDIUM

**Recommended test file:** `tests/test_coc_combat_resolution.py`

---

### 7. Skill Triggers & Point Allocation (`rules/`)

**Status:** ⚠️ Not directly tested

**Files needing tests:**
- `rules/skill_points.py` - Skill point allocation logic
- `rules/skill_resolution.py` - Skill check resolution helpers
- `rules/skill_triggers.py` - Skill trigger system

**Gap Severity:** MEDIUM

---

## Medium Priority Gaps

### 8. COC Skill Check - Bonus/Penalty Dice (`rules/engine.py`)

**Current:** `test_coc_skill_check_success_regular/hard/extreme` test basic difficulty

**Missing:**
- Bonus dice selection (minimum of tens pool when bonus dice)
- Penalty dice selection (maximum of tens pool when penalty dice)
- Combined bonus+penalty dice (uses first die)
- Pushed roll re-roll behavior

**Gap Severity:** MEDIUM

---

### 9. Turn Plan Resolution (`orchestrator/gameplay.py`)

**File:** `src/dm_bot/orchestrator/gameplay.py`

**Methods needing tests:**
- `resolve_plan()` - TurnPlan tool call execution
- `_apply_roll_consequences()` - Trigger consequences from roll results
- `_current_story_node()` - Story node retrieval

**Gap Severity:** MEDIUM

---

### 10. Scene Evaluation (`orchestrator/gameplay.py`)

**Methods needing tests:**
- `evaluate_scene_action()` - Scene action resolution
- `_evaluate_location_connections()` - Location transition evaluation
- `_record_scene_miss_and_hint()` - Hint generation

**Gap Severity:** LOW-MEDIUM

---

## Lower Priority Gaps

### 11. Message Buffer (`router/message_buffer.py`)

**File:** `router/message_buffer.py`

**Functions needing tests:**
- `MessageBuffer.buffer_message()`
- `MessageBuffer.release_buffered_messages()`
- `MessageBuffer.has_buffered_messages()`

**Gap Severity:** LOW (covered by integration tests)

---

### 12. Trigger Engine (`adventures/trigger_engine.py`)

**File:** `adventures/trigger_engine.py`

**Functions needing tests:**
- `TriggerEngine.execute()` - Trigger execution
- Event consequence merging

**Gap Severity:** LOW (covered by adventure integration tests)

---

## Summary: Test Gaps by COC Subsystem

| Subsystem | Functions | Direct Tests | Gap Severity |
|-----------|-----------|--------------|--------------|
| **derived.py** | 15+ | 0 | 🔴 HIGH |
| **experience.py** | 10+ | 0 | 🔴 HIGH |
| **sanity.py (insanity)** | 5+ | 0 | 🔴 HIGH |
| **skills.py (catalog)** | 10+ | 0 | 🟡 MEDIUM |
| **magic.py (catalog)** | 5+ | 0 | 🟡 MEDIUM |
| **combat.py (damage)** | 6+ | 0 | 🟡 MEDIUM |
| **skill_triggers.py** | 3+ | 0 | 🟡 MEDIUM |
| **skill_points.py** | 3+ | 0 | 🟡 MEDIUM |
| **skill_resolution.py** | 3+ | 0 | 🟡 MEDIUM |

---

## Recommended Test File Structure

```
tests/
├── test_coc_derived.py              # NEW - derived attributes
├── test_coc_experience.py           # NEW - experience system  
├── test_coc_insanity.py             # NEW - insanity breaks
├── test_coc_skills_catalog.py      # NEW - skill definitions
├── test_coc_magic_catalog.py       # NEW - spell definitions
├── test_coc_combat_resolution.py   # NEW - damage calculations
├── test_rules_engine.py             # EXISTS - engine integration
└── test_coc_rules_flow.py          # EXISTS - skill check flow
```

---

## Priority Recommendations

1. **Immediate:** Add `test_coc_derived.py` - these are pure functions with deterministic output
2. **Immediate:** Add `test_coc_experience.py` - character progression depends on this
3. **High:** Add insanity break tests - dramatic game moments need reliability
4. **Medium:** Add skill/magic catalog tests - catch data definition errors
5. **Medium:** Add combat damage tests - DB and armor calculations

---

*Gap analysis: 2026-03-31*
