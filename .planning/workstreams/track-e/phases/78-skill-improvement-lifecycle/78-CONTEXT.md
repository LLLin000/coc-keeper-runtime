# Phase E78 Context

## Phase Boundary

Create an end-to-end scenario that validates the complete character lifecycle: character creation → combat → SAN loss → skill improvement → next round. Integrates all previous COC tests (attributes, combat, SAN, skills) into one comprehensive scenario.

## Implementation Decisions

### Scenario Design
- **Full lifecycle flow**: bind → join → ready → start → enter_scene → combat → SAN check → skill_improvement → next_round
- **Deterministic testing**: Use dice_seed=78 for reproducible rolls
- **Cross-system validation**: Verify skills used in combat are eligible for improvement

### Skill Improvement Integration
- Skills used during combat scenario: fighting, shooting, dodge, spot_hidden
- Improvement rolls: 1d100 < current_skill → +1d10 improvement
- Must verify improvement results are persisted and visible in next session

### Test Fixtures
- dice_seed: 78 (deterministic)
- model_mode: fake_contract
- db_mode: temp_sqlite
- adventure: null (combat-only scenario)

### Dependencies
- RuntimeTestDriver with combat support
- Skill improvement functions from dm_bot.rules.coc.experience
- Character state persistence across session boundaries

## Canonical References

### Previous Phases
- `tests/scenarios/acceptance/scen_character_creation.yaml` — Character creation E2E
- `tests/scenarios/acceptance/scen_combat_san.yaml` — Combat + SAN E2E
- `tests/rules/coc/test_experience_and_skill_catalog.py` — Skill improvement unit tests

### Source Code
- `src/dm_bot/rules/coc/experience.py` — Skill improvement functions
- `src/dm_bot/testing/runtime_driver.py` — RuntimeTestDriver
- `tests/scenarios/acceptance/scen_combat_san.yaml` — Combat scenario reference

## Specific Ideas

### Scenario Flow
1. **Setup**: KP binds campaign, player joins and readies
2. **Session Start**: Start session, complete onboarding
3. **Combat**: Enter scene with combatants, run combat rounds
4. **SAN Loss**: Trigger SAN check from combat/horror
5. **Skill Improvement**: Roll improvements for skills used
6. **Next Round**: Verify improved skills in next session round

### Skills to Track
- fighting (used in combat)
- shooting (used in combat)
- dodge (used in combat)
- spot_hidden (used in investigation)

### Assertions
- Phase timeline: lobby → awaiting_ready → awaiting_admin_start → onboarding → scene_round_open → (combat) → scene_round_open
- State: combat completed, SAN changed, skills improved
- Visible: combat results, skill improvement messages

## Deferred Ideas

- Full character builder integration (requires archive_repository wiring)
- Multi-session persistence testing (requires Phase 76 driver enhancement)
- Experience point tracking across multiple adventures
