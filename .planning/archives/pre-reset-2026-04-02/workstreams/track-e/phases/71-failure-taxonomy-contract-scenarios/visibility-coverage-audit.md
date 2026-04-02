## Already Covered
- `test_build_visibility_snapshot_onboarding`: ONBOARDING phase, WaitingReasonCode.ONBOARDING_IN_PROGRESS, RoutingOutcome.BUFFERED, player onboarding_complete field
- `test_build_visibility_snapshot_scene_round`: SCENE_ROUND_OPEN phase, WaitingReasonCode.WAITING_FOR_PLAYER_ACTIONS, has_submitted_action tracking, RoutingOutcome.PROCESSED

## Coverage Gaps (needs scenario coverage)
1. **WAITING_FOR_READY (AWAITING_READY phase)**: No test covers the `waiting.reason_code == WaitingReasonCode.WAITING_FOR_READY` state or the `ready_count`/`player_ready` visibility tracking
2. **RoutingOutcome.DEFERRED and IGNORED**: The routing outcome enum has DEFERRED and IGNORED variants but no test exercises them — only BUFFERED and PROCESSED are covered
3. **routing_history field**: VisibilitySnapshot carries a `routing_history: list[RoutingHistoryEntry]` field but no test passes or asserts it