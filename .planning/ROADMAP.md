# Roadmap: Discord AI Keeper

## Overview

Milestone `v1.0` established the Discord-first local-DM runtime with deterministic rules, persistence, diagnostics, and a starter packaged adventure. Milestone `v1.1` introduced a formal module runtime and shipped `疯狂之馆` as the first structured full-length module. Milestone `v1.2` added ready-gated startup, mature dice integration, and true Discord streaming. Milestone `v1.3` polished live-play feel through structured judgement, bounded guidance, and keeper-style scene framing. Milestone `v1.4` introduced room graphs, AI-first extraction drafts, and location-driven play. Milestone `v1.5` completed the missing execution layer with a reusable trigger tree and consequence engine. Milestone `v1.6` pivots that foundation into a COC/Keeper-first runtime using local rulebooks, investigator assets, and COC module semantics.

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
- [x] **Phase 16: Room Graph Runtime Foundations** - Introduce location graphs, adjacency, and location-aware runtime state.
- [x] **Phase 17: AI Extraction For Room Graphs And Trigger Trees** - Add AI-first, reviewable extraction drafts for room graphs and trigger trees.
- [x] **Phase 18: 疯狂之馆 Room-Graph Migration** - Migrate `疯狂之馆` into room-graph-driven play behavior.
- [x] **Phase 19: Generic Trigger And Consequence Schema** - Introduce a reusable trigger tree schema with declarative conditions, effects, and hook boundaries.
- [x] **Phase 20: Runtime Trigger Engine** - Execute trigger trees into persisted consequence chains and event logs.
- [x] **Phase 21: 疯狂之馆 Trigger Migration** - Migrate key `疯狂之馆` beats onto the generic trigger engine.
- [ ] **Phase 22: COC Runtime Foundations** - Add COC 7th keeper-facing checks, SAN-aware resolution, and non-D&D runtime semantics on top of the existing engine.
- [ ] **Phase 23: COC Asset And Character Intake** - Build reviewable knowledge and investigator intake paths from local rulebooks, pregens, templates, and curated COC references.
- [ ] **Phase 24: COC Module And Keeper Experience Migration** - Reframe prompts, diagnostics, and module extraction around COC investigation flow and reusable keeper-style play.

## Milestone v1.6 Delivery Plan

### Phase 22: COC Runtime Foundations
**Delivered**:
- Added COC-first percentile checks with regular, hard, and extreme success tiers on top of the existing rules engine.
- Added COC-specific roll actions and Discord command paths for skill checks and sanity checks without breaking the earlier runtime.
- Introduced a structured investigator profile for COC state such as SAN, luck, movement, build, and skill values.

### Phase 23: COC Asset And Character Intake
**Delivered**:
- Added a reviewable COC asset library that discovers local rulebooks, pregenerated-investigator files, and curated community references.
- Added a COC investigator source and data model to support pregen-oriented imports alongside the older source path.
- Added runtime configuration and a Discord command for inspecting discovered local COC assets.

### Phase 24: COC Module And Keeper Experience Migration
**Delivered**:
- Reworked router, narrator, and extraction prompts to frame play as a Keeper-led COC investigation rather than a D&D-first session.
- Preserved the room-graph and trigger runtime while migrating prompts, rule actions, and diagnostics toward reusable COC semantics.
- Expanded operator visibility with COC-relevant diagnostics such as SAN pressure, danger level, and pending push state.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15 -> 16 -> 17 -> 18 -> 19 -> 20 -> 21 -> 22 -> 23 -> 24

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
| 16. Room Graph Runtime Foundations | 2/2 | Completed | 2026-03-28 |
| 17. AI Extraction For Room Graphs And Trigger Trees | 2/2 | Completed | 2026-03-28 |
| 18. 疯狂之馆 Room-Graph Migration | 2/2 | Completed | 2026-03-28 |
| 19. Generic Trigger And Consequence Schema | 2/2 | Completed | 2026-03-28 |
| 20. Runtime Trigger Engine | 2/2 | Completed | 2026-03-28 |
| 21. 疯狂之馆 Trigger Migration | 2/2 | Completed | 2026-03-28 |
| 22. COC Runtime Foundations | 1/1 | Completed | 2026-03-28 |
| 23. COC Asset And Character Intake | 1/1 | Completed | 2026-03-28 |
| 24. COC Module And Keeper Experience Migration | 1/1 | Completed | 2026-03-28 |
