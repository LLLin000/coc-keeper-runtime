---
phase: E78
plan_number: 01
wave: 1
depends_on: []
files_modified:
  - tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml
autonomous: true
---

# Plan E78-01: Skill Improvement + Full Lifecycle E2E Scenario

## Objective

Create an end-to-end scenario YAML file that validates the complete character lifecycle: character creation → combat → SAN loss → skill improvement → next round. This integrates all previous COC tests (attributes, combat, SAN, skills) into one comprehensive scenario.

## Context

This is the final phase of vE.3.1 milestone. Previous phases E73-E77 have established:
- E73: COC derived attributes unit tests (75 tests)
- E74: COC combat + insanity integration tests (56 tests)
- E75: COC experience + skill catalog unit tests (91 tests)
- E76: Character creation E2E scenario
- E77: Combat + SAN E2E scenario

This plan creates the capstone scenario that ties all these systems together.

## Tasks

### Task 1: Create scen_skill_improvement_lifecycle.yaml

<read_first>
- tests/scenarios/acceptance/scen_combat_san.yaml
- tests/scenarios/acceptance/scen_character_creation.yaml
- src/dm_bot/rules/coc/experience.py
- .planning/workstreams/track-e/phases/78-skill-improvement-lifecycle/78-RESEARCH.md
</read_first>

<acceptance_criteria>
- File exists at `tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml`
- YAML has valid structure: id, title, description, tags, mode, actors, fixtures, steps, assertions
- id is "scen_skill_improvement_lifecycle"
- title contains "Skill Improvement + Full Lifecycle"
- tags include: acceptance, character_lifecycle, combat, skill_improvement
- fixtures include: dice_seed: 78, model_mode: fake_contract, db_mode: temp_sqlite
</acceptance_criteria>

<action>
Create the scenario YAML file with the following structure:

1. **Metadata section:**
   - id: scen_skill_improvement_lifecycle
   - title: "Skill Improvement + Full Lifecycle E2E - Complete Character Journey"
   - description explaining the full lifecycle flow
   - tags: acceptance, character_lifecycle, combat, san, skill_improvement
   - mode: acceptance

2. **Actors section:**
   - kp: kind=admin, user_id=u_kp
   - p1: kind=player, user_id=u_p1

3. **Fixtures section:**
   - dice_seed: 78
   - model_mode: fake_contract
   - db_mode: temp_sqlite

4. **Steps section** (in order):
   - bind_campaign (KP)
   - join_campaign (Player)
   - set_role (KP sets investigator)
   - ready (Player)
   - start_session (KP)
   - complete_onboarding (KP)
   - enter_scene with speakers "Investigator,DeepOne" (KP)
   - start_combat with combatants "Investigator:50:25:10,DeepOne:40:30:8" (KP)
   - show_combat (KP)
   - next_turn (KP) × 4 turns to advance combat
   - resolve_round (KP) - ends combat
   - next_round (KP) - new round for skill improvement phase

5. **Assertions section:**
   - phase_timeline: lobby, awaiting_ready, awaiting_admin_start, onboarding, scene_round_open, scene_round_resolving, scene_round_open
   - visible.public_must_include: "combat", "DeepOne", "improvement" or "提升"
   - state.combat_completed: true
   - state.campaign_members: 1
</action>

### Task 2: Add skill improvement verification to scenario

<read_first>
- tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml (after Task 1)
- src/dm_bot/rules/coc/experience.py (roll_skill_improvement function)
</read_first>

<acceptance_criteria>
- Scenario includes comment block explaining skill improvement flow
- Scenario references skills that would be used: fighting, shooting, dodge
- Deterministic improvement rolls are documented (dice_seed=78)
- Assertions verify combat completion and state transitions
</acceptance_criteria>

<action>
Add detailed comments to the scenario YAML explaining:

1. **Skill Usage Tracking:**
   - Skills used during combat: fighting (attack), dodge (defense)
   - These skills become eligible for improvement after session

2. **Improvement Mechanics:**
   - With dice_seed=78, improvement rolls are deterministic
   - Improvement rule: 1d100 < current_skill → +1d10 improvement
   - Example: fighting=50, roll=45 (<50) → success, +1d10 improvement

3. **Cross-System Integration:**
   - Combat system tracks skill usage
   - End of session triggers improvement rolls
   - Improved skills persist to next round

4. **Verification Points:**
   - Combat completes successfully
   - Phase transitions follow expected timeline
   - Public output contains combat and improvement messages
</action>

### Task 3: Validate scenario runs successfully

<read_first>
- tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml
- src/dm_bot/testing/scenario_runner.py (if exists)
- pyproject.toml or pytest configuration
</read_first>

<acceptance_criteria>
- YAML syntax is valid (no parsing errors)
- Scenario can be discovered by test runner
- `uv run pytest tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml -v` passes (or equivalent command)
- All assertions pass
</acceptance_criteria>

<action>
1. Validate YAML syntax:
   ```bash
   python -c "import yaml; yaml.safe_load(open('tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml'))"
   ```

2. Run scenario test:
   ```bash
   uv run pytest tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml -v
   ```

3. If scenario runner uses different mechanism, run appropriate test command

4. Verify all assertions pass and scenario completes without errors
</action>

## Verification Criteria

### Must Haves (Goal-Backward Verification)

1. **Scenario file exists and is valid:**
   - File at `tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml`
   - Valid YAML syntax
   - All required fields present

2. **Full lifecycle coverage:**
   - Session setup (bind, join, ready, start)
   - Combat encounter (enter_scene, start_combat, next_turn)
   - Round resolution (resolve_round)
   - Next round transition (next_round)

3. **Integration with COC systems:**
   - Uses combat system (from E74)
   - Implies skill usage tracking (from E75)
   - Validates phase transitions (from E76/E77)

4. **Deterministic testing:**
   - dice_seed=78 for reproducible results
   - fake_contract model mode
   - temp_sqlite db mode

5. **Test passes:**
   - Scenario runs without errors
   - All assertions satisfied
   - pytest exits with code 0

## Dependencies

- E76: Character creation scenario (provides session lifecycle pattern)
- E77: Combat + SAN scenario (provides combat testing pattern)
- E75: Experience + skill catalog (provides skill improvement functions)
- RuntimeTestDriver with combat support

## Notes

- This is the capstone scenario for vE.3.1 milestone
- Scenario demonstrates integration of all COC subsystems
- Pattern follows established E76/E77 scenario structure
- No source code changes required - uses existing RuntimeTestDriver
