# Roadmap: Discord AI DM

## Overview

Milestone `v1.0` established the Discord-first local-DM runtime with deterministic rules, persistence, diagnostics, and a starter packaged adventure. Milestone `v1.1` introduced a formal module runtime and shipped `疯狂之馆` as the first structured full-length module. Milestone `v1.2` added ready-gated startup, mature dice integration, and true Discord streaming. Milestone `v1.3` now focuses on the part players feel most directly during live play: better judgement about when rolls should happen, light guidance with clear boundaries, and scene presentation that feels closer to a real human Keeper/DM while still improving the reusable prompt, parsing, and module pipeline for future adventures.

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

## Milestone v1.3 Planned Work

### Phase 13: Structured Judgement And Roll Prompting
**Goal**: Make the runtime act more like a real Keeper by deciding when a roll is needed, when it is not, and how to prompt the table clearly, while expressing those decisions through reusable prompt and runtime structures.
**Depends on**: Phase 12
**Requirements**: JUDGE-01, JUDGE-02, JUDGE-03, JUDGE-04, GUIDE-01
**Success Criteria** (what must be TRUE):
  1. `疯狂之馆` interactions can distinguish between automatic success, blocked action, clarification-needed action, and formal roll-needed action through structured runtime logic.
  2. When a roll is needed, the bot can surface a concise DM-facing prompt that identifies the actor, the roll family, and the reason.
  3. Roll-trigger outcomes update canonical state and downstream narration rather than being treated as a purely narrative flourish.
  4. The design reuses mature tabletop and bot patterns where possible instead of inventing unnecessary new judgement semantics, and the prompt/runtime contract is reusable by later modules.
**Plans**: 2 plans
Plans:
- [ ] 13-01-PLAN.md - Add structured action judgement tiers and map roll-needed outcomes into the deterministic rules layer.
- [ ] 13-02-PLAN.md - Surface explicit DM roll prompts and reusable guidance-tier contracts through prompt and ordinary-message flow.

### Phase 14: Hint Timing, Clue Flow, And Stall Recovery
**Goal**: Improve how `疯狂之馆` reveals information, nudges players, and recovers from stalls without spoiling hidden truths, while formalizing guidance tiers that future modules can reuse.
**Depends on**: Phase 13
**Requirements**: HINT-01, HINT-02, HINT-03, HINT-04, GUIDE-02
**Success Criteria** (what must be TRUE):
  1. The module can distinguish ambient description from discoverable clues, light guidance, and explicit rescue-level hints.
  2. The runtime can detect common stall states or repeated dead-end loops and emit safe next-step guidance.
  3. Major pressure beats and critical module truths are introduced deliberately rather than accidentally drifting into view.
  4. Hints never bypass canonical reveal gates or expose protected late-stage secrets too early, and extracted module data preserves enough metadata to support the same behavior in later adventures.
**Plans**: 2 plans
Plans:
- [ ] 14-01-PLAN.md - Encode context-sensitive hint triggers, clue tiers, and stall detection into the runtime and module schema.
- [ ] 14-02-PLAN.md - Improve DM-facing recap and redirect messaging plus extraction-time clue metadata so players can recover without raw state inspection.

### Phase 15: Keeper-Style Scene Framing And Consequence Presentation
**Goal**: Make scene presentation, consequence delivery, and return-to-choice rhythm feel more like a human Keeper running the module, without turning scenes into over-guided walkthroughs.
**Depends on**: Phase 14
**Requirements**: PRESENT-01, PRESENT-02, PRESENT-03, PRESENT-04, GUIDE-03
**Success Criteria** (what must be TRUE):
  1. Central hall framing, branch-hall introductions, and major set-piece interactions have stronger module-specific DM voice and usable scene structure.
  2. The runtime can present transitions between exploration, roll prompt, consequence, and next choice cleanly enough that the session rhythm feels intentional.
  3. Scene output highlights salient props, threats, and opportunities without collapsing into either generic prose, menu spam, or over-explicit solution feeding.
  4. Failed exploration and wrong assumptions still move the table forward because the DM knows when to restate pressure, recap discoveries, and redirect attention, and the polish remains mostly reusable beyond this single module.
**Plans**: 2 plans
Plans:
- [ ] 15-01-PLAN.md - Refine `疯狂之馆` scene framing and branch introductions using structured presentation templates with bounded guidance.
- [ ] 15-02-PLAN.md - Integrate consequence narration, recap beats, return-to-choice pacing, and reusable prompt/schema hooks into live Discord output.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15

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
| 13. Structured Judgement And Roll Prompting | 0/2 | Planned | - |
| 14. Hint Timing, Clue Flow, And Stall Recovery | 0/2 | Planned | - |
| 15. Keeper-Style Scene Framing And Consequence Presentation | 0/2 | Planned | - |
