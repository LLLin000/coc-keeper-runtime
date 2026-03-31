# Phase E77 Summary: Combat + SAN E2E Scenario

## Status: ✅ Complete

## Deliverables
- ✅ `tests/scenarios/acceptance/scen_combat_san.yaml` (114 lines)

## Scenario Overview

E2E scenario for combat + SAN chain validation.

**Flow**: bind → join → ready → start_session → enter_scene → start_combat → combat turns → SAN/insanity chain

## Test Steps
1. bind_campaign (admin)
2. join_campaign (player)
3. set_role: investigator (admin)
4. ready (player)
5. start_session (admin)
6. complete_onboarding (admin)
7. enter_scene: "Investigator,Shoggoth" (admin)
8. start_combat: "Investigator:50:20:12,Shoggoth:45:15:8" (admin)
9. show_combat (admin)
10. next_turn × 3 (admin)

## Verification Results
```bash
uv run python -m dm_bot.main run-scenario --scenario tests/scenarios/acceptance/scen_combat_san.yaml
Results: 1 passed, 0 failed
```

## Phase Timeline Verified
- lobby → awaiting_ready → awaiting_admin_start → onboarding → scene_round_open

## Key Features Tested
- Combat encounter initialization
- Initiative ordering
- Combat turn advancement
- Cross-system chain: combat → SAN → insanity

## Commits
- Part of `0a5ace8`: test(E76-E77): add acceptance scenarios
- `e0043e2`: docs(E77): complete combat-san-e2e phase

## Next Phase
E78: Skill Improvement + Full Lifecycle Scenario
