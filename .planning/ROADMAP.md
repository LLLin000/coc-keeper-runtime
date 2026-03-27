# Roadmap: Discord AI DM

## Overview

This roadmap now has two milestones in sequence. Milestone `v1.0` established a Discord-first local-DM runtime with deterministic rules, persistence, diagnostics, and a starter packaged adventure. Milestone `v1.1` builds on that base by introducing a formal structured module runtime, making `疯狂之馆` the first full official module, and hardening Discord interaction so packaged adventures can survive restarts and remain campaign-usable.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Discord Runtime & Dual-Model Control** - Establish the Discord session surface, async interaction flow, and local dual-model orchestration.
- [x] **Phase 2: Character Import & Rules Authority** - Add one low-friction character path and a deterministic 2014 SRD rules backbone.
- [x] **Phase 3: Gameplay Loop & Combat Play** - Deliver DM narration, multi-character scenes, and heavy-rules combat inside Discord.
- [x] **Phase 4: Persistence, Recovery & Diagnostics** - Harden the runtime for campaign reuse, replayability, and operator visibility.

## Phase Details

### Phase 1: Discord Runtime & Dual-Model Control
**Goal**: Players and operators can run a responsive Discord session through a local dual-model control loop on target consumer hardware.
**Depends on**: Nothing (first phase)
**Requirements**: DISC-01, DISC-02, DISC-03, DISC-04, ORCH-01, ORCH-02, ORCH-03, ORCH-04, OPS-03
**Success Criteria** (what must be TRUE):
  1. Operators can run a setup and health workflow that verifies Discord permissions, local model availability, and service connectivity before live play.
  2. Players can create or join a campaign session tied to a Discord channel or thread, and multiple players can participate in the same session without overlapping turn handling.
  3. Discord interactions are acknowledged quickly and longer model or tool work completes through follow-up responses instead of timing out.
  4. On hardware in the class of 8GB VRAM and 32GB RAM, routing uses the small router for structured mode and tool decisions while the narrator separately produces final prose.
**Plans**: 3 plans
Plans:
- [x] 01-01-PLAN.md - Bootstrap the Python runtime shell, typed config, and setup or health workflow.
- [x] 01-02-PLAN.md - Implement Discord session binding, deferred interactions, and campaign-scoped turn serialization.
- [x] 01-03-PLAN.md - Implement dual-model router and narrator orchestration with model health checks.

### Phase 2: Character Import & Rules Authority
**Goal**: The system has one mature character onboarding path and an authoritative deterministic rules layer grounded in the 2014 SRD.
**Depends on**: Phase 1
**Requirements**: CHAR-01, CHAR-02, CHAR-03, CHAR-04, RULE-01, RULE-04, RULE-05, RULE-06
**Success Criteria** (what must be TRUE):
  1. A player can import or link a character through one clearly defined mature v1 path without using a custom Discord sheet editor.
  2. Imported character data is normalized into a local gameplay model that can support later rolls, attacks, saves, spells, and resource usage, and the system clearly labels whether the source is snapshot-based or live-sync.
  3. Players or operators can look up rules, spells, monsters, classes, and equipment from a structured compendium source constrained to 2014 SRD content.
  4. State-changing mechanics are applied by deterministic rules logic, and malformed model actions are rejected or flagged instead of mutating canonical state silently.
**Plans**: 3 plans
Plans:
- [x] 02-01-PLAN.md - Add one snapshot character import path and normalize imported gameplay models.
- [x] 02-02-PLAN.md - Build the 2014 SRD compendium adapter and deterministic rules engine.
- [x] 02-03-PLAN.md - Integrate character and rules foundations into the existing turn/runtime pipeline.

### Phase 3: Gameplay Loop & Combat Play
**Goal**: A live Discord session can run normal DM narration, multi-character performance scenes, and heavy-rules combat without losing context.
**Depends on**: Phase 2
**Requirements**: PLAY-01, PLAY-02, PLAY-03, PLAY-04, RULE-02, RULE-03
**Success Criteria** (what must be TRUE):
  1. Players can trigger checks, saves, attacks, and damage resolution from Discord and receive results in the active session.
  2. Combat can track initiative, turn order, HP changes, conditions, concentration, death saves, and basic resource counters without corrupting state.
  3. The DM can switch from normal narration into scene-based multi-character performance with explicit speaker attribution and return to DM-led play without losing scene, combat, or actor context.
  4. Final DM and NPC output is Chinese-first and suitable for scene framing, storytelling, and dialogue during active play.
**Plans**: 3 plans
Plans:
- [x] 03-01-PLAN.md - Add gameplay mode state and scene speaker formatting.
- [x] 03-02-PLAN.md - Build initiative-driven combat state and deterministic combat flow.
- [x] 03-03-PLAN.md - Integrate scene and combat play into the existing runtime.

### Phase 4: Persistence, Recovery & Diagnostics
**Goal**: Sessions become campaign-usable through durable state, replayable history, resumability, and operator diagnostics.
**Depends on**: Phase 3
**Requirements**: PERS-01, PERS-02, PERS-03, PERS-04, OPS-01, OPS-02
**Success Criteria** (what must be TRUE):
  1. Campaign state survives restarts and can be reloaded so scenes, combat, resources, and party context resume without manual reconstruction.
  2. Every turn records a replayable event trail linking the user action, router decision, tool execution, state mutations, and outbound Discord response.
  3. Operators can inspect Discord, model, tool, and recent rules failures from a compact debug surface or command and trace a player action end-to-end with stable identifiers.
  4. The system can generate prompt-ready summaries or projections from canonical stored state rather than relying on raw Discord history as the only source of truth.
**Plans**: 2 plans
Plans:
- [x] 04-01-PLAN.md - Add durable campaign state storage and append-only turn events.
- [x] 04-02-PLAN.md - Expose compact diagnostics and trace inspection through the runtime.

## Milestone v1.0 Progress

### Phase 5: Multiplayer usability, natural message intake, and starter adventure
**Goal**: Make the bot genuinely runnable by a small group through natural channel input, cleaner multiplayer flow, Chinese DM voice refinement, and a packaged starter one-shot.
**Depends on**: Phase 4
**Requirements**: DISC-01, DISC-02, PLAY-01, PLAY-02, PLAY-03, PLAY-04, RULE-03
**Success Criteria** (what must be TRUE):
  1. Joined players in a bound campaign channel can play through ordinary channel messages without using `/turn` for every action.
  2. The runtime ignores obvious OOC and player-to-player social chatter while still accepting action declarations that mention teammates.
  3. Combat communicates the active actor clearly and rejects natural-message turns from non-active combatants.
  4. Operators can load a packaged starter adventure and follow updated docs to run a real multiplayer test session quickly.
**Plans**: 2 plans
Plans:
- [x] 05-01-PLAN.md - Add multiplayer runtime helpers, natural message intake, and combat gating.
- [x] 05-02-PLAN.md - Improve DM narration, ship a starter adventure, and rewrite operator docs.

## Milestone v1.1 Planned Work

### Phase 6: Structured Module Runtime
**Goal**: Introduce a reusable formal adventure package model with canonical state, reveal policy, and deterministic trigger handling that can power full modules.
**Depends on**: Phase 5
**Requirements**: MOD-01, MOD-02, MOD-03, MOD-04
**Success Criteria** (what must be TRUE):
  1. Operators can load a formally structured adventure package whose scenes, state variables, reveal tiers, and ending paths are validated before play begins.
  2. The runtime stores module state separately from Discord history and can answer what room, clues, triggers, timers, and hidden flags are currently active.
  3. Narration can consume omniscient module data without leaking hidden information that is still gated by the package's reveal policy.
  4. Invalid or incomplete package data fails closed with actionable diagnostics instead of silently degrading into freeform DM improvisation.
**Plans**: 1 plan
Plans:
- [x] 06-01-PLAN.md - Formalize adventure schema, loader validation, and canonical module state runtime.

### Phase 7: 疯狂之馆 Formal Module
**Goal**: Encode `疯狂之馆` as the first full-length structured module with its room logic, hidden-status mechanics, and branching endings.
**Depends on**: Phase 6
**Requirements**: MANS-01, MANS-02, MANS-03, MANS-04
**Success Criteria** (what must be TRUE):
  1. A group can enter `疯狂之馆`, move through the hall and branch wings, and have room progression driven by structured data instead of ad hoc prompt text.
  2. Countdown pressure, room-specific costs, blood progression, sensory loss, saint-state style transformations, and similar script mechanics mutate canonical module state deterministically.
  3. The DM reveals clues and hidden information according to scripted triggers and discoveries, while still retaining full module knowledge internally.
  4. The run can conclude through multiple endings that depend on accumulated state and choices rather than a single scripted exit.
**Plans**: 1 plan
Plans:
- [x] 07-01-PLAN.md - Encode 疯狂之馆 as a formal package and add thin progression helpers.

### Phase 8: Module UX, Session Continuity, and Operator Guidance
**Goal**: Make packaged adventure play reliable after restarts and understandable to a small real group using ordinary Discord messages.
**Depends on**: Phase 7
**Requirements**: UX-01, UX-02, UX-03, UX-04, PACK-01, PACK-02
**Success Criteria** (what must be TRUE):
  1. Campaign/channel binding, joined-member state, and packaged-adventure context survive bot restarts well enough that natural-message play resumes without manual re-setup.
  2. Joined players can play packaged adventures through ordinary channel messages with clear OOC filtering, combat gating, and feedback when input is ignored or blocked.
  3. Commands or debug surfaces clearly report the current room, objectives, known clues, pressure, and blocked progression so the operator does not have to inspect raw state files.
  4. The repository contains docs and examples that let an operator load `疯狂之馆`, understand the gameplay loop, and author the next structured module without reverse-engineering the code.
**Plans**: 1 plan
Plans:
- [x] 08-01-PLAN.md - Persist sessions, restore packaged-adventure runtime state, and update operator guidance.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8

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
