# Roadmap: Discord AI DM

## Overview

Milestone `v1.0` established the Discord-first local-DM runtime with deterministic rules, persistence, diagnostics, and a starter packaged adventure. Milestone `v1.1` introduced a formal module runtime and shipped `疯狂之馆` as the first structured full-length module. Milestone `v1.2` added ready-gated startup, mature dice integration, and true Discord streaming. Milestone `v1.3` polished live-play feel through structured judgement, bounded guidance, and keeper-style scene framing. Milestone `v1.4` now changes the underlying module representation: adventures should be understood and run as room graphs with local triggers and branching state, extracted AI-first from source scripts and then refined into reusable runtime data.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Discord Runtime & Dual-Model Control** - Establish the Discord session surface, async interaction flow, and local dual-model orchestration.
- [x] **Phase 2: Character Import & Rules Authority** - Add one low-friction character path and a deterministic 2014 SRD rules backbone.
- [x] **Phase 3: Gameplay Loop & Combat Play** - Deliver DM narration, multi-character scenes, and heavy-rules combat inside Discord.
- [x] **Phase 4: Persistence, Recovery & Diagnostics** - Harden the runtime for campaign reuse, replayability, and operator visibility.
- [x] **Phase 5: Multiplayer usability, natural message intake, and starter adventure** - Make the bot runnable by a small group through natural channel input and a packaged one-shot.
- [x] **Phase 6: Structured Module Runtime** - Introduce reusable formal adventure packages with canonical state and reveal policy.
- [x] **Phase 7: 疯狂之馆 Formal Module** - Encode `疯狂之馆` as the first official structured module.
- [x] **Phase 8: Module UX, Session Continuity, and Operator Guidance** - Persist packaged-adventure sessions and improve operator visibility.
- [x] **Phase 9: Adventure Onboarding And Auto-Opening** - Make packaged-adventure startup feel like a real game session.
- [x] **Phase 10: Mature Dice Engine And Deterministic Roll Resolution** - Replace placeholder rolls with a mature dice engine.
- [x] **Phase 11: Streaming Responses And Message Reliability** - Make Discord play feel responsive with clearer processing feedback.
- [x] **Phase 12: True Streaming Discord Output** - Stream narrator output live into Discord through chunked edits with fallback.
- [x] **Phase 13: Structured Judgement And Roll Prompting** - Add keeper-style action judgement and explicit roll prompting.
- [x] **Phase 14: Hint Timing, Clue Flow, And Stall Recovery** - Add bounded guidance tiers and stall recovery.
- [x] **Phase 15: Keeper-Style Scene Framing And Consequence Presentation** - Strengthen room introductions, pressure, and return-to-choice rhythm.

## Milestone v1.4 Planned Work

### Phase 16: Room Graph Runtime Foundations
**Goal**: Replace sequence-first adventure representation with explicit room or location graphs that carry local state, reachable transitions, and runtime-ready place data.
**Depends on**: Phase 15
**Requirements**: GRAPH-01, GRAPH-02, GRAPH-03, GRAPH-04
**Success Criteria** (what must be TRUE):
  1. Formal adventures can define rooms or locations, explicit edges between them, and local interactables without being reduced to ordered scene lists.
  2. Runtime decisions can key off current location plus reachable nodes rather than script-order progression.
  3. Existing narration, persistence, and judgement layers can consume the new room-graph state without a parallel stack being invented.
  4. The new schema is general enough for future adventures and not tailored only to `疯狂之馆`.
**Plans**: 2 plans
Plans:
- [ ] 16-01-PLAN.md - Introduce room-graph schema, local interactable containers, and adjacency-aware runtime state.
- [ ] 16-02-PLAN.md - Adapt runtime loading, persistence, and location-aware judgement to consume room graphs cleanly.

### Phase 17: AI Extraction For Room Graphs And Trigger Trees
**Goal**: Build an AI-first extraction pipeline that reads source scripts and emits draft room graphs, trigger trees, reveal gates, and editable runtime data.
**Depends on**: Phase 16
**Requirements**: TREE-01, TREE-02, TREE-03, TREE-04, EXTRACT-01, EXTRACT-02, EXTRACT-03, EXTRACT-04
**Success Criteria** (what must be TRUE):
  1. Source scripts can be transformed into draft maps of locations, triggers, and local state with limited manual bootstrapping.
  2. Trigger trees attach to places, objects, NPCs, and roll outcomes rather than only to prose sequence.
  3. Extracted output stays reviewable and editable so humans can correct AI mistakes without rebuilding everything by hand.
  4. Player intent like observing, approaching, entering, leaving, and activating can be mapped onto the room graph in a reusable way.
**Plans**: 2 plans
Plans:
- [ ] 17-01-PLAN.md - Build AI-assisted extraction artifacts for room topology, trigger trees, and reveal-safe state metadata.
- [ ] 17-02-PLAN.md - Add reviewable module draft outputs and integrate trigger-tree concepts into runtime intent handling.

### Phase 18: 疯狂之馆 Room-Graph Migration
**Goal**: Migrate `疯狂之馆` into the new room-graph format and use it to improve actual session feel in navigation, consequences, and location-driven play.
**Depends on**: Phase 17
**Requirements**: MANSION-01, MANSION-02, MANSION-03, MANSION-04
**Success Criteria** (what must be TRUE):
  1. `疯狂之馆` is modeled as a room graph with the central hall, branch halls, key landmarks, and their real movement relationships.
  2. Room entry, observation, movement, return paths, and local interactions behave more like tabletop play than script playback.
  3. Roll results and trigger outcomes update local room state and future options in ways players can feel.
  4. The migrated module remains faithful to the original script while allowing varied player phrasing and DM improvisational tolerance.
**Plans**: 2 plans
Plans:
- [ ] 18-01-PLAN.md - Port `疯狂之馆` data into room-graph nodes, edges, landmarks, and trigger trees.
- [ ] 18-02-PLAN.md - Tune live play around movement, inspection, room exits, and consequence flow using the migrated module.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15 -> 16 -> 17 -> 18

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Discord Runtime & Dual-Model Control | 3/3 | Completed | 2026-03-27 |
| 2. Character Import & Rules Authority | 3/3 | Completed | 2026-03-27 |
| 3. Gameplay Loop & Combat Play | 3/3 | Completed | 2026-03-27 |
| 4. Persistence, Recovery & Diagnostics | 2/2 | Completed | 2026-03-27 |
| 5. Multiplayer usability, natural message intake, and starter adventure | 2/2 | Completed | 2026-03-27 |
| 6. Structured Module Runtime | 1/1 | Completed | 2026-03-27 |
| 7. 疯狂之馆 Formal Module | 1/1 | Completed | 2026-03-27 |
| 8. Module UX, Session Continuity, and Operator Guidance | 1/1 | Completed | 2026-03-27 |
| 9. Adventure Onboarding And Auto-Opening | 2/2 | Completed | 2026-03-27 |
| 10. Mature Dice Engine And Deterministic Roll Resolution | 2/2 | Completed | 2026-03-27 |
| 11. Streaming Responses And Message Reliability | 2/2 | Completed | 2026-03-27 |
| 12. True Streaming Discord Output | 1/1 | Completed | 2026-03-27 |
| 13. Structured Judgement And Roll Prompting | 2/2 | Completed | 2026-03-27 |
| 14. Hint Timing, Clue Flow, And Stall Recovery | 2/2 | Completed | 2026-03-27 |
| 15. Keeper-Style Scene Framing And Consequence Presentation | 2/2 | Completed | 2026-03-27 |
| 16. Room Graph Runtime Foundations | 0/2 | Planned | - |
| 17. AI Extraction For Room Graphs And Trigger Trees | 0/2 | Planned | - |
| 18. 疯狂之馆 Room-Graph Migration | 0/2 | Planned | - |
