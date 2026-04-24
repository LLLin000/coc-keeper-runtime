# Phase 2: Fork And Switch Focus - Context

**Gathered:** 2026-04-11
**Status:** Ready for planning
**Source:** Phase 1 artifacts + v1.0-SCENE-FORK-SPEC.md

<domain>
## Phase Boundary

Implement the fork() and switch_focus() runtime operations that decouple scene creation from focus switching. This establishes the multi-scene structure that batch/merge (Phase 3) will use for collection and resolution.
</domain>

<decisions>
## Implementation Decisions

### Fork Is Decoupled from Focus
- fork() creates a new scene immediately
- fork() does NOT automatically switch any player's focus
- Focus change requires an explicit switch_focus() call

### Max Open Scenes Policy
- Maximum 2 OPEN scenes allowed at any time (per v1.0 spec)
- Validation in fork() rejects exceeding this limit

### Player Scene Membership
- A player can only belong to one OPEN scene at a time (per v1.0 spec key invariant)
- fork() validates the initiating player is not already in an OPEN scene

### Lightweight Scene Tracking
- Do NOT build a full WorldState/scene_graph yet — that is later-phase work
- Track open scenes with a lightweight dict[str, OpenScene] structure on CampaignSession
- Each OpenScene tracks: scene_id, initiating_player, lifecycle

### Cross-Cut Is a Signal, Not a Behavior
- When a player switches focus from a RESOLVED scene to an OPEN scene, this is a "cross-cut" signal
- The narrator runtime consumes this signal to produce cutaway narration
- Phase 2 does NOT implement the narration itself — only the signal

### the agent's Discretion
- Exact class/struct name for open scene tracking (OpenScene vs SceneContext vs SceneRecord)
- Whether fork/switch validation lives on CampaignSession or a helper
- How to serialize fork/switch events for persistence
</decisions>

<canonical_refs>
## Canonical References

### Planning Truth
- `.planning/workstreams/track-runtime/ROADMAP.md` — Phase 2 goal, dependencies, requirements
- `.planning/workstreams/track-runtime/REQUIREMENTS.md` — RTR-01, RTR-02, RTR-03
- `.planning/workstreams/track-runtime/STATE.md` — active milestone and phase position
- `.planning/workstreams/track-runtime/v1.0-SCENE-FORK-SPEC.md` — fork/switch design contract

### Phase 1 Artifacts
- `.planning/workstreams/track-runtime/phases/01-scene-lifecycle/01-CONTEXT.md` — scene lifecycle/focus separation decision
- `.planning/workstreams/track-runtime/phases/01-scene-lifecycle/01-RESEARCH.md` — session_store.py integration findings
- `.planning/workstreams/track-runtime/phases/01-scene-lifecycle/01-01-PLAN.md` — implementation approach
- `.planning/workstreams/track-runtime/phases/01-scene-lifecycle/01-01-SUMMARY.md` — what was delivered

### Existing Runtime Code
- `src/dm_bot/orchestrator/session_store.py` — SceneLifecycle, PlayerFocusScope enums, CampaignSession model
- `src/dm_bot/orchestrator/gameplay.py` — GameModeState integration
- `src/dm_bot/gameplay/modes.py` — GameModeState with scene_lifecycle and player_focus fields
</canonical_refs>

<specifics>
## Specific Ideas

- fork() creates scene_id = str(uuid4()), participants = {initiating_player}, lifecycle = COLLECTING
- switch_focus() updates player_focus_scope to track focused scene_id
- Cross-cut signal: when switch_focus() moves from RESOLVED to OPEN scene, emit cross_cut_signal event
- Fork validation error if player already in OPEN scene
</specifics>

<deferred>
## Deferred Ideas

- Full WorldState with scene_graph — belongs to later phases when more scene data needs tracking
- Merge behavior (merge_propose, merge_confirm) — Phase 3
- Multi-player shared scenes (SHARED focus scope) — Phase 3+
- Scene-to-scene dependencies — deferred
- Trigger authoring workflow — deferred
- Scene state persistence across restarts — deferred
</deferred>
