# Phase E77 Context

## Scenario Design

The scenario tests the cross-system chain:
1. **Session Flow**: Standard bind → join → ready → start
2. **Scene Entry**: Enter scene with multiple speakers
3. **Combat Start**: Initialize combat with combatants
4. **Combat Turns**: Advance through multiple turns
5. **Chain Verification**: Combat state affects SAN/insanity

## Combatant Format
```yaml
combatants: "Investigator:50:20:12,Shoggoth:45:15:8"
# Format: name:initiative:hp:armor
```

## Test Fixtures
- dice_seed: 77 (deterministic)
- model_mode: fake_contract
- db_mode: temp_sqlite

## Dependencies
- Combat commands: start_combat, show_combat, next_turn
- Scene commands: enter_scene
- Session commands: bind_campaign, join_campaign, etc.

## Reference
- `tests/scenarios/acceptance/scen_combat_san.yaml`
- `src/dm_bot/test_helpers/runtime_driver.py`
