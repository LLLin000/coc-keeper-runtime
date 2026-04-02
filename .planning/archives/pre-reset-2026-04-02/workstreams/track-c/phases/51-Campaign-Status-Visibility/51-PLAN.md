# Phase 51: Visibility Core Contracts - Execution Plan

## 1. Goal
Define the canonical visibility state for campaign, adventure, session, waiting reasons, routing outcomes, and player snapshots so Discord surfaces can render from a shared, logic-first model.

## 2. Requirements Tracking
- **SURF-01**: Discord-facing surfaces read from a canonical visibility model rather than assembling ad hoc text independently.
- **SURF-02**: The visibility model includes explicit waiting/blocker reasons.
- **SURF-03**: The visibility model includes routing outcome plus a short explanation contract.
- **SURF-04**: The visibility model surfaces existing canonical player snapshot state without redefining character semantics.

## 3. Task Breakdown

### Task 1: Top-Level Visibility Contracts
- **Goal:** Create the core Pydantic structure for the `VisibilitySnapshot`.
- **Files to Edit:** `src/dm_bot/orchestrator/visibility.py` (new)
- **Steps:**
  1. Define `VisibilitySnapshot` as a Pydantic model.
  2. Implement explicit nested blocks: `CampaignVisibility`, `AdventureVisibility`, `SessionVisibility`, `WaitingVisibility`, `PlayerVisibility`, `RoutingVisibility`.
- **Acceptance:** Pydantic definitions strictly map to the D-01 and D-02 constraints from `51-CONTEXT.md`.

### Task 2: Sub-block Implementations
- **Goal:** Implement the logic and fields for each sub-block based on existing canonical state.
- **Files to Edit:** `src/dm_bot/orchestrator/visibility.py`
- **Steps:**
  1. `WaitingVisibility`: Model as `reason_code` (enum), `message` (short string), and `metadata` (dict, e.g., pending user IDs).
  2. `PlayerVisibility`: Surface existing canonical state from `InvestigatorPanel` (HP, SAN, MP, LUCK, bound character identity, participation status).
  3. `RoutingVisibility`: Map routing outcome and short explanation from `IntentHandlingResult`.
  4. `CampaignVisibility` / `AdventureVisibility`: Expose active campaign ID, channel ID, and current adventure reference.
  5. `SessionVisibility`: Expose `SessionPhase`, ready count, and admin start status.
- **Acceptance:** Matches decisions D-04/05/06 for waiting, D-07/08 for player snapshot, and D-10/11 for routing.

### Task 3: State Aggregation Builder
- **Goal:** Implement a builder that synthesizes the `VisibilitySnapshot` from existing runtime classes without mutating them.
- **Files to Edit:** `src/dm_bot/orchestrator/visibility.py` or a dedicated builder module.
- **Steps:**
  1. Create a factory method or class (e.g., `build_visibility_snapshot`).
  2. Inject `CampaignSession` and loaded `InvestigatorPanel`s.
  3. Extract pending actions to populate the `waiting` block intelligently (e.g., waiting on specific user ids during `scene_round_open`).
  4. Add routing context if processing a specific message.
- **Acceptance:** A single function call produces the complete, fully formed 6-block `VisibilitySnapshot`.

### Task 4: Testing & Verification
- **Goal:** Prove the data structures work and aggregate correctly from running sessions.
- **Files to Edit:** `tests/orchestrator/test_visibility.py` (new)
- **Steps:**
  1. Construct mock `CampaignSession` data with pending actions.
  2. Construct mock `InvestigatorPanel` data.
  3. Generate a `VisibilitySnapshot` and assert block presence and field correctness.
- **Acceptance:** `uv run pytest -q tests/orchestrator/test_visibility.py` passes 100%.

## 4. Out of Scope (Phase Boundaries)
- Do not build player-facing Discord commands (e.g., `/status`, `/waiting`). This belongs to Phase 52.
- Do not implement KP ops channels or UI updates. This belongs to Phase 54.
- Do not redesign or expand `InvestigatorPanel` character data semantics.
- Do not implement Discord Activity UI logic.

## 5. Success Criteria Confirmation
1. `VisibilitySnapshot` defined with exactly six specified partitions.
2. Waiting state structured with reason code, message, and metadata.
3. Routing outcomes feature concise explanations.
4. Player snapshots expose HP/SAN/attributes read-only without feature creep.
