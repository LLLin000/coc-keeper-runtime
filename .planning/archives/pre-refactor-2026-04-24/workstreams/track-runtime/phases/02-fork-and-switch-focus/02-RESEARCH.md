# Phase 2: Fork And Switch Focus - Research

## Research Summary

Phase 1 delivered explicit `SceneLifecycle` and `PlayerFocusScope` enums on `CampaignSession`. Phase 2 must now implement the `fork()` and `switch_focus()` runtime operations that decouple scene creation from focus switching.

## Findings

### 1. Phase 1 Foundation

Phase 1 added to `CampaignSession`:
- `scene_lifecycle: SceneLifecycle` — COLLECTING, LOCKED, RESOLVING, PUBLISHED
- `player_focus: PlayerFocusScope` — SINGLE, SHARED, KEEPER_ONLY

These are scalar fields on a single campaign session. The v1.0 spec calls for a `scene_graph: Dict[scene_id, Scene]` but Phase 1 deferred multi-scene data structures to focus on the lifecycle/focus separation.

### 2. Fork Mechanics (what Phase 2 must add)

The v1.0-SCENE-FORK-SPEC.md defines:
```
fork()
├── Validate: max 2 OPEN scenes across all
├── Validate: initiating_player not already in OPEN scene
├── Create new Scene with:
│   ├── participants = {initiating_player}
│   ├── lifecycle = OPEN (or COLLECTING)
│   ├── entry_trigger, exit_trigger
├── DO NOT change focus automatically
└── Return (new_scene_id, fork_status)
```

**Key:** fork() is IMMEDIATE — focus change requires separate switch_focus() call.

### 3. Switch Focus Mechanics

```
switch_focus()
├── Validate: player belongs to source scene (if any)
├── Validate: player belongs to target_scene_id
├── Update WorldState.focus_scope[player_id] = target_scene_id
└── Return (previous_scene_id, new_scene_id)
```

**Cross-cut:** When a scene is RESOLVED and player switches to another OPEN scene, a "cutaway" is triggered in the narrator.

### 4. Scene Data Structure Gap

The spec envisions a `WorldState.scene_graph` with `Scene` objects. Phase 1 did not implement this — it only added lifecycle and focus enum fields to CampaignSession.

For Phase 2, we need to decide:
- Does fork() create a new "scene" as a first-class object, or just track additional lifecycle/focus state on CampaignSession?
- The spec says "max 2 OPEN scenes" — this implies we need scene-level tracking beyond scalar lifecycle

**Recommended approach:** Add a lightweight `OpenScene` tracking structure (scene_id -> scene metadata) alongside the existing CampaignSession fields. Do NOT over-engineer a full WorldState model yet — that belongs to later phases.

### 5. Integration Points

- `session_store.py` — fork() and switch_focus() methods on CampaignSession
- `gameplay.py` — cross-cut notification via GameModeState  
- Narration service — receives cross-cut signal for cutaway narrative

### 6. RTR-03 (Deterministic Resolution Order)

This requirement is about the resolution phase, not fork/switch. The deterministic ordering applies when multiple actors submit actions in a shared scene. This is a cross-cutting concern that affects the batch/merge phase (Phase 3), not Phase 2 directly.

However, Phase 2 should ensure that the fork/switch operations produce traceable events that a later resolution system can order deterministically.

## Risks

1. **Over-engineering scene graph** — Resist building a full WorldState with scene_graph until Phase 3. Keep fork/switch lightweight.
2. **Blurring with Phase 3** — fork/switch establishes the structure; batch/merge uses it. Don't implement merge behavior here.
3. **Concurrency not fully solved** — Phase 1 noted turn coordination is campaign-serialized. fork/switch operations should be atomic but don't need to solve the full concurrency problem yet.

## Recommended Planning Direction

1. Add lightweight open_scene tracking to CampaignSession
2. Implement fork() with validation rules
3. Implement switch_focus() with cross-cut signaling
4. Update GameModeState to expose focus-switch context
5. Add persistence for fork/switch events
6. Regression tests for fork, switch, and cross-cut behavior
