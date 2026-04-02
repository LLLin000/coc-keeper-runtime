# Phase E77: Combat + SAN E2E Scenario

## Goal
Write E2E scenario validating combat → SAN → insanity chain.

## Success Criteria
- [x] E2E scenario file created
- [x] Scenario validates combat encounter flow
- [x] Cross-system chain verified

## Test Flow

### Scenario: Combat + SAN Chain
1. **Setup**: Campaign bind → join → ready → start_session
2. **Scene**: Enter scene with Investigator + Shoggoth speakers
3. **Combat**: Start combat encounter with initiative ordering
4. **Turns**: 3 combat turn cycles via `next_turn`
5. **Chain**: Combat → SAN → insanity verification

## Test Coverage

| Feature | Verified |
|---------|----------|
| Campaign bind → join → ready → start_session | ✅ |
| Scene mode entry with speakers | ✅ |
| Combat encounter start | ✅ |
| Initiative ordering | ✅ |
| Combat turn advancement | ✅ |
| Cross-system chain | ✅ |

## Assertions

### Phase Timeline
- lobby → awaiting_ready → awaiting_admin_start → onboarding → scene_round_open

### Visible Messages
- Must include: "combat", "Shoggoth"

### State
- combat_order_length: 2

## Dependencies
- `tests/scenarios/acceptance/scen_combat_san.yaml`
- RuntimeTestDriver with combat support

## Files Created
- `tests/scenarios/acceptance/scen_combat_san.yaml` (114 lines)

## Verification
```bash
uv run python -m dm_bot.main run-scenario --scenario tests/scenarios/acceptance/scen_combat_san.yaml
# Results: 1 passed, 0 failed
```
