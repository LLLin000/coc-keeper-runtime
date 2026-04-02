---
phase: E93
name: Scenario Precondition Alignment
goal: Update scenario YAML files to include required preconditions (set_role, select_profile) for phase transitions
success_criteria:
  - All 13 previously failing scenarios now pass
  - "uv run python -m dm_bot.main run-scenario --all" shows all PASS
  - No regressions in existing tests
gap_closure: false
plan_id: E93-01
wave: 1
autonomous: true
files_modified:
  - src/dm_bot/testing/runtime_driver.py
  - tests/scenarios/acceptance/scen_session_happy_path.yaml
  - tests/scenarios/acceptance/scen_character_creation.yaml
  - tests/scenarios/acceptance/scen_combat_san.yaml
  - tests/scenarios/acceptance/scen_fuzhe_15turn.yaml
  - tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml
  - tests/scenarios/acceptance/scen_smoke.yaml
  - tests/scenarios/acceptance/scen_chase.yaml
  - tests/scenarios/acceptance/scen_creature_encounter.yaml
  - tests/scenarios/acceptance/scen_equipment_combat.yaml
  - tests/scenarios/acceptance/scen_character_builder.yaml
  - tests/scenarios/acceptance/scen_archive_crud.yaml
  - tests/scenarios/chaos/scen_chaos_lobby.yaml
  - tests/scenarios/contract/visibility/scen_gmonly_reaches_kp.yaml
  - tests/scenarios/contract/visibility/scen_no_gmonly_to_player.yaml
tasks:
  - id: 1
    name: Modify run_command to support driver methods without interaction
    description: >
      In runtime_driver.py run_command(), modify the driver method call to derive
      user_id from actor_id when the method signature includes 'user_id'. This allows
      create_test_profile to be called from scenario YAMLs without an interaction parameter.
    verification: grep -n "is_driver_method" src/dm_bot/testing/runtime_driver.py shows the modification
  - id: 2
    name: Update acceptance scenario YAMLs with preconditions
    description: >
      For each acceptance scenario that fails with PHASE_TRANSITION_MISMATCH:
      1. Add create_test_profile step for each player actor before join_campaign
      2. Add set_role step with role="player" after join_campaign
      3. Add select_profile step with the created profile_id after set_role
      Scenarios to update: scen_session_happy_path, scen_character_creation,
      scen_combat_san, scen_fuzhe_15turn, scen_skill_improvement_lifecycle,
      scen_chase, scen_creature_encounter, scen_equipment_combat,
      scen_character_builder, scen_archive_crud
    verification: uv run python -m dm_bot.main run-scenario --scenario scen_session_happy_path shows PASS
  - id: 3
    name: Update chaos scenario YAML with preconditions
    description: >
      Update scen_chaos_lobby.yaml to:
      1. Add create_test_profile for each of the 5 players
      2. Add set_role and select_profile steps before ready
      3. Also fix the member count expectation - KP may be counted, adjust to 6
    verification: uv run python -m dm_bot.main run-scenario --scenario scen_chaos_lobby shows PASS
  - id: 4
    name: Update contract scenario YAMLs with preconditions
    description: >
      Update scen_gmonly_reaches_kp and scen_no_gmonly_to_player to add
      preconditions for players (set_role, select_profile)
    verification: uv run python -m dm_bot.main run-scenario --scenario scen_gmonly_reaches_kp shows PASS
  - id: 5
    name: Fix scen_smoke and scen_awaiting_ready_visibility
    description: >
      scen_smoke has "Final phase mismatch" - needs investigation
      scen_awaiting_ready_visibility has "'str' object has no attribute 'get'" error
    verification: uv run python -m dm_bot.main run-scenario --scenario scen_smoke shows PASS
  - id: 6
    name: Run full scenario suite verification
    description: >
      Run "uv run python -m dm_bot.main run-scenario --all" and verify all scenarios pass
    verification: All 14 scenarios show PASS status
---

## Objective

Execute E93: Scenario Precondition Alignment - fixing 12+ failing scenarios by adding
missing preconditions (set_role, select_profile) that ready() requires.

## Technical Analysis

### Root Cause
The `validate_ready()` function in `session_store.py` (line 468-473) requires players to have
either `selected_profile_id` OR `active_character_name` before calling `ready()`:

```python
if not member.selected_profile_id and not member.active_character_name:
    return ValidationResult(
        success=False,
        error=ReadyGateError.NO_PROFILE_SELECTED.value,
        ...
    )
```

Most scenario YAMLs skip `set_role` and `select_profile` steps, causing `ready()` to fail
silently and preventing phase transitions beyond `awaiting_ready`.

### Solution
1. Modify `run_command()` in `runtime_driver.py` to support driver methods that need `user_id`
   by deriving it from `actor_id` when the method signature includes a `user_id` parameter.

2. Update scenario YAMLs to add:
   - `create_test_profile` step for each player (creates profile in archive)
   - `set_role(role="player")` step after join
   - `select_profile(profile_id=<id>)` step after set_role

## Tasks

### Task 1: Modify run_command to support driver methods
**File:** `src/dm_bot/testing/runtime_driver.py`

Modify the `is_driver_method` branch in `run_command()` to pass `user_id=actor_id`
when the driver method's signature includes a `user_id` parameter.

### Task 2-4: Update scenario YAMLs
**Files:** See files_modified list

For each failing scenario, add precondition steps:

```yaml
# Before join_campaign (create profiles)
- actor: p1
  action: command
  name: create_test_profile
  args:
    user_id: u_p1
    name: Test Investigator P1
    occupation: scholar
    age: 25

# After join_campaign (set role and select profile)
- actor: p1
  action: command
  name: set_role
  args:
    role: player

- actor: p1
  action: command
  name: select_profile
  args:
    profile_id: u_p1
```

### Task 5: Debug specific failures
**Files:** scen_smoke.yaml, scen_awaiting_ready_visibility.yaml

Investigate and fix the specific errors in these scenarios.

### Task 6: Full suite verification
Run `uv run python -m dm_bot.main run-scenario --all` and confirm all 14 scenarios pass.

## Success Criteria
- All 13+ previously failing scenarios now pass
- `uv run python -m dm_bot.main run-scenario --all` shows 14/14 PASS
- No regressions in 842+ existing tests
