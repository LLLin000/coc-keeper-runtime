# Phase E76: Character Creation E2E Scenario

## Goal
Create an end-to-end scenario for the character creation lifecycle.

## Success Criteria
- [x] E2E scenario file created
- [x] Scenario documents character creation flow
- [x] Session join + ready flow tested

## Test Flow

### Scenario: Character Creation Lifecycle
1. **Setup**: Campaign binding
2. **Join**: Player joins campaign
3. **Role**: Admin sets player role to investigator
4. **Ready**: Player indicates ready
5. **Start**: Admin starts session
6. **Onboard**: Complete onboarding phase
7. **Next**: Advance to first round
8. **Message**: Player sends in-character message
9. **Resolve**: Resolve the round

## Limitations

**Known Issue**: Full character builder flow (`start_character_builder` + `builder_reply`) requires `archive_repository` and `character_builder` to be wired in `RuntimeTestDriver`, which is not currently available.

**Workaround**: This scenario tests session join + ready flow with the `ready` command instead of `ready_for_adventure`.

**Future Enhancement**: Phase 76 driver enhancement would enable full character creation E2E.

## Assertions

### Phase Timeline
- lobby → awaiting_ready → awaiting_admin_start → onboarding → scene_round_open → scene_round_resolving → scene_round_open

### State
- campaign_members: 1
- no_duplicate_members: true

### Visible Messages
- Must include: "就位", "游戏开始"

## Dependencies
- `tests/scenarios/acceptance/scen_character_creation.yaml`
- RuntimeTestDriver with session orchestrator

## Files Created
- `tests/scenarios/acceptance/scen_character_creation.yaml` (96 lines)

## Verification
```bash
uv run pytest tests/scenarios/acceptance/scen_character_creation.yaml -q
# Note: Scenario is documented but not fully testable due to driver limitations
```
