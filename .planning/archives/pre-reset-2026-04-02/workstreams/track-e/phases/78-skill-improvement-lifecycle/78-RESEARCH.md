# Phase E78 Research: Skill Improvement + Full Lifecycle Scenario

**Gathered:** 2026-03-31
**Status:** Ready for planning

## Phase Boundary

Create an end-to-end scenario that validates the complete character lifecycle: character creation → combat → SAN loss → skill improvement → next round. Integrates all previous COC tests (attributes, combat, SAN, skills) into one comprehensive scenario.

## Technical Analysis

### Existing Test Infrastructure

1. **RuntimeTestDriver** (`src/dm_bot/testing/runtime_driver.py`)
   - Provides Discord-free testing interface
   - Supports commands: bind_campaign, join_campaign, ready, start_session, complete_onboarding, enter_scene, start_combat, show_combat, next_turn, next_round, resolve_round
   - Uses FakeInteraction for mocking Discord interactions
   - Supports dice_seed for deterministic testing
   - Tracks outputs by audience (public/kp)

2. **Scenario DSL** (from E70)
   - YAML-based scenario format
   - Actors: kp (admin), p1 (player)
   - Fixtures: dice_seed, model_mode, db_mode
   - Steps: command actions with args, message actions with text
   - Assertions: phase_timeline, visible content, state checks

3. **Skill Improvement System** (`src/dm_bot/rules/coc/experience.py`)
   - `roll_skill_improvement(skill_key, current_value, improvement_roll)` → SkillImprovementResult
   - `roll_all_skill_improvements(skills_used, current_skills, improvement_rolls)` → list[SkillImprovementResult]
   - Improvement rule: 1d100 < current_skill → +1d10 improvement
   - Functions are pure/deterministic when improvement_roll provided

4. **Previous Scenarios**
   - `scen_character_creation.yaml`: bind → join → ready → start → complete_onboarding → next_round
   - `scen_combat_san.yaml`: bind → join → ready → start → complete_onboarding → enter_scene → start_combat → show_combat → next_turn (×3)

### Integration Points

**What's Missing for Full Lifecycle:**
1. No direct skill improvement command in RuntimeTestDriver
2. No skill tracking during combat (which skills were used)
3. No session-end skill improvement phase
4. No persistence of improved skills across rounds

**Recommended Approach:**
1. Create scenario YAML that simulates full lifecycle using existing commands
2. Add skill improvement verification via assertions on state
3. Use deterministic dice (seed=78) for reproducible improvement rolls
4. Verify skills used in combat are tracked and eligible for improvement

### Scenario Flow Design

```
Phase 1: Setup
- bind_campaign (KP)
- join_campaign (Player)
- set_role (KP sets player as investigator)
- ready (Player)
- start_session (KP)
- complete_onboarding (KP)

Phase 2: Combat & SAN
- enter_scene with speakers (KP)
- start_combat with combatants (KP)
- next_turn × N (advance combat)
- Skills used: fighting, shooting, dodge tracked

Phase 3: Skill Improvement
- resolve_round (KP) - ends combat/scene
- next_round (KP) - starts new round
- Implicit: skill improvement check for used skills

Phase 4: Verification
- Assert phase timeline includes all phases
- Assert skills improved (via state inspection)
- Assert visible output includes improvement messages
```

### Critical Implementation Notes

1. **Skill Tracking**: RuntimeTestDriver doesn't currently track which skills are used during combat. Need to either:
   - Add skill tracking to combat resolution
   - Or simulate skill usage via direct state manipulation in scenario

2. **Improvement Rolls**: Use deterministic rolls (seed=78) with pre-rolled values:
   - fighting: 45 (improves if current < 45)
   - shooting: 30 (improves if current < 30)
   - dodge: 25 (improves if current < 25)

3. **State Assertions**: Need to verify:
   - `combat_completed: true`
   - `skills_improved: [...]`
   - `phase_timeline` includes expected phases

4. **Visible Assertions**: Check that public output includes:
   - Combat results
   - Skill improvement messages ("成功！技能提升")

## Validation Architecture (Dimension 8)

**Test Approach:**
- **Type:** E2E Scenario Test
- **Mocking:** RuntimeTestDriver with fake_contract model mode
- **Determinism:** dice_seed=78, pre-rolled improvement rolls
- **Coverage:** Full lifecycle from session start to skill improvement

**Success Criteria:**
1. Scenario runs without errors
2. Phase timeline matches expected sequence
3. Skills used in combat are eligible for improvement
4. Improvement rolls produce deterministic results
5. State changes are persisted and visible

## Dependencies

- E76: Character creation scenario (completed)
- E77: Combat + SAN scenario (completed)
- E75: Experience + skill catalog tests (completed)
- RuntimeTestDriver with combat support

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| RuntimeTestDriver lacks skill tracking | Medium | Add skill_used tracking to combat resolution or simulate via state |
| No explicit skill improvement command | Low | Use resolve_round/next_round to trigger end-of-session improvement |
| Cross-system integration complexity | Medium | Build on proven patterns from E76/E77 |

## References

- `tests/scenarios/acceptance/scen_character_creation.yaml`
- `tests/scenarios/acceptance/scen_combat_san.yaml`
- `src/dm_bot/rules/coc/experience.py`
- `src/dm_bot/testing/runtime_driver.py`
- `tests/rules/coc/test_experience_and_skill_catalog.py`
