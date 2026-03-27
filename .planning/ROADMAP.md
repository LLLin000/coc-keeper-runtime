# Roadmap: Discord AI DM

## Overview

This roadmap keeps v1 narrow: deliver a Discord-first D&D runtime that can run a real local-model session with deterministic rules authority, one mature character import path, Chinese-first DM narration, and enough persistence and diagnostics to recover and operate campaign play on consumer hardware.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Discord Runtime & Dual-Model Control** - Establish the Discord session surface, async interaction flow, and local dual-model orchestration.
- [x] **Phase 2: Character Import & Rules Authority** - Add one low-friction character path and a deterministic 2014 SRD rules backbone.
- [ ] **Phase 3: Gameplay Loop & Combat Play** - Deliver DM narration, multi-character scenes, and heavy-rules combat inside Discord.
- [ ] **Phase 4: Persistence, Recovery & Diagnostics** - Harden the runtime for campaign reuse, replayability, and operator visibility.

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
**Plans**: TBD

### Phase 4: Persistence, Recovery & Diagnostics
**Goal**: Sessions become campaign-usable through durable state, replayable history, resumability, and operator diagnostics.
**Depends on**: Phase 3
**Requirements**: PERS-01, PERS-02, PERS-03, PERS-04, OPS-01, OPS-02
**Success Criteria** (what must be TRUE):
  1. Campaign state survives restarts and can be reloaded so scenes, combat, resources, and party context resume without manual reconstruction.
  2. Every turn records a replayable event trail linking the user action, router decision, tool execution, state mutations, and outbound Discord response.
  3. Operators can inspect Discord, model, tool, and recent rules failures from a compact debug surface or command and trace a player action end-to-end with stable identifiers.
  4. The system can generate prompt-ready summaries or projections from canonical stored state rather than relying on raw Discord history as the only source of truth.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Discord Runtime & Dual-Model Control | 3/3 | Completed | 2026-03-27 |
| 2. Character Import & Rules Authority | 3/3 | Completed | 2026-03-27 |
| 3. Gameplay Loop & Combat Play | 0/TBD | Not started | - |
| 4. Persistence, Recovery & Diagnostics | 0/TBD | Not started | - |
