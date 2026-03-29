# Remaining Work Analysis: Track A - 模组与规则运行层

## 1. Track A Milestone Status

Based on `.planning/workstreams/track-a/ROADMAP.md` and `STATE.md`, the current status of Track A is as follows:

- **vA.1.1 - 模组结构化基础**: ✅ **COMPLETE**
    - **Phases Completed**: 
        - Phase 1: 凄夜的游乐场迁移 (Structured new module)
        - Phase 2: 疯狂之馆增强 (Trigger extension + endings)
        - Phase 3: 覆辙模组完善 (Structure expansion, 3 -> 9 locations, 1 -> 14 triggers)
    - **Outcome**: Established base JSON schema for modules, including room graphs, trigger systems, and ending conditions.

- **vA.1.2 - Group Action Resolution And Shared Scene Consequences**: ⏳ **PLANNED**
    - **Goal**: Add scene-round batching and shared consequence resolution for multiplayer play.
    - **Status**: Ready to start.
    - **Key Focus**: Scene round action batching, multi-actor resolution, shared reveal summaries.

- **vA.1.3 - Closed-Loop Event Graph Runtime**: 📋 **QUEUED**
    - **Goal**: Generalize action-to-event-to-consequence flow into a reusable runtime.
    - **Status**: Queued after vA.1.2.
    - **Key Focus**: Action intent and event entry contracts, spine-branch-ending runtime model.

- **vA.1.4 - COC Core Rules Authority**: 📋 **QUEUED**
    - **Goal**: Promote local COC rulebooks into canonical runtime truth.
    - **Status**: Queued after vA.1.3.
    - **Key Focus**: Strict attribute/SAN rules, combat/injury state machine.

---

## 2. Incomplete / Not-Started Items (from ROADMAP)

| Item | Milestone | Description | Priority |
|---|---|---|---|
| **Multiplayer Action Batching** | vA.1.2 | Collecting actions from multiple players before resolving a scene round. | High |
| **Shared Reveal Summaries** | vA.1.2 | Generating consequences that affect and are visible to the whole group. | High |
| **Closed-Loop Event Graph** | vA.1.3 | Moving from scene-by-scene patching to a generalized graph-based runtime. | Medium |
| **Spine-Branch-Ending Model** | vA.1.3 | Formalizing the narrative structure within the code runtime. | Medium |
| **Module Extraction Contract** | vA.1.3 | Standardizing how raw text is extracted into the event graph structure. | Medium |
| **Canonical COC Rulebook** | vA.1.4 | Moving COC rules from simple dice rollers to authoritative state management. | High |
| **SAN/Insanity State Machine** | vA.1.4 | Managing long-term mental health state in accordance with 7th Ed rules. | High |

---

## 3. Relationship: Track A Runtime vs. vE.2.1 Scenario Testing

Track A components directly support the scenario testing requirements for vE.2.1 (Delivery & Governance):

- **Trigger Engine**: The `TriggerEngine` (`src/dm_bot/adventures/trigger_engine.py`) is the primary driver for state changes. Testing scenarios requires validating that specific player actions reliably trigger the correct effects (e.g., `set_module_state`, `move_story_node`).
- **Room/Scene/Event Graph**: The `AdventurePackage` model manages the connections between locations. Scenario testing verifies that the pathfinding and "travel" logic correctly update `location_id` and `scene_id`.
- **Reveal Policy**: Although `models.py` defines `Visibility` (public, secret, etc.), the enforcement of "who knows what" (Reveal Policy) is critical for multi-role testing in `fuzhe` (Investigator vs. Magical Girl).
- **vE.2.1 Needs**: To achieve "Campaign-usable reliability," we need deterministic verification that Track A's runtime doesn't "hallucinate" state transitions. The `fuzhe.json` module serves as the primary complex test case for this.

---

## 4. Test-Friendly Fuzhe Extraction: Advancement of Track A Goals

Would a **"test-friendly fuzhe extraction"** advance Track A goals? **Yes**, specifically for vA.1.3:

1. **Generalizing Extraction**: Track A vA.1.3 calls for a "Module extraction contract for event graphs." Implementing a cleaner extraction for `fuzhe` (using the current `extraction.py` or an improved version) provides a real-world pattern for this contract.
2. **Testing Runtime Logic**: By extracting `fuzhe` into a more granular structure (e.g., breaking large scenes into smaller story nodes), we can test the `TriggerEngine`'s ability to handle complex chains without manual patching.
3. **Bridge to vA.1.2**: A more structured `fuzhe` makes it easier to test "Group Action Resolution" because we can clearly define which triggers are "shared" vs. "individual."

**Conclusion**: Extracting `fuzhe` in a way that prioritizes **testability** (clear inputs/outputs for triggers) is a prerequisite for graduating from "patched scenes" (vA.1.1) to a "generalized runtime" (vA.1.3).

---

## 5. Overlaps and Gaps (Current vs. Goal)

- **Overlap**: The `fuzhe.json` already uses the `AdventurePackage` model and `TriggerEngine`. Most "location-first" features are implemented.
- **Gap (Rules)**: The rules in `rules/engine.py` are still largely decoupled from the `TriggerEngine`. Triggers check `roll_total` but don't yet enforce COC "Hard/Extreme" success requirements authoritatively (vA.1.4 goal).
- **Gap (Batching)**: The `TriggerEngine.execute` currently processes events one-by-one. It lacks the "Round Batching" logic needed for vA.1.2.
- **Gap (State)**: `AdventureStateField` exists but is not yet used to enforce strict COC character state during runtime execution.
