# Phase 51: Visibility Core Contracts - Summary

## Work Completed
1. **Defined `VisibilitySnapshot`**: Created the canonical representation of campaign status in `src/dm_bot/orchestrator/visibility.py` with six strictly defined blocks: `campaign`, `adventure`, `session`, `waiting`, `players`, and `routing`.
2. **Implemented Sub-blocks**:
   - `CampaignVisibility` and `SessionVisibility` correctly mirror the canonical fields from `CampaignSession`.
   - `WaitingVisibility` categorizes wait states with a stable `WaitingReasonCode`, a user-friendly message, and structured metadata based on session phases (e.g., waiting for players during `SCENE_ROUND_OPEN`).
   - `PlayerVisibility` extracts read-only canonical data from `InvestigatorPanel` combined with current session flags (ready, onboarding, submitted action).
   - `RoutingVisibility` extracts outcome types from `IntentHandlingResult`.
3. **State Aggregation Builder**: Provided a pure functional builder `build_visibility_snapshot()` that derives the snapshot from existing runtime classes without mutating them.
4. **Testing**: Implemented exhaustive snapshot compilation tests validating metadata generation and block formatting in `tests/orchestrator/test_visibility.py`.

## Verification
- Run `uv run pytest -q tests/orchestrator/test_visibility.py`. Both tests (onboarding mock and scene round mock) pass. 

## Requirements Satisfied
- **SURF-01**: Discord-facing surfaces read from a canonical visibility model (achieved via the `VisibilitySnapshot` model).
- **SURF-02**: Included explicit waiting/blocker reasons (`WaitingVisibility`).
- **SURF-03**: Included routing outcome plus short explanation (`RoutingVisibility`).
- **SURF-04**: Surfaced existing canonical player snapshot state (`PlayerSnapshot` fields mirroring existing structures).

## Next Steps
- This canonical core paves the way for Phase 52 ("Player Status Surfaces") where Discord commands/UI will directly query this snapshot instead of ad hoc logic, fulfilling the visual representation rules.
