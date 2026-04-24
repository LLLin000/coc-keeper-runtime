# Roadmap: `track-surface`

## Status

Standardized on `2026-04-09` for GSD phase parsing.

**Ownership**
- Discord command UX
- channel discipline
- DM / ephemeral / public presentation behavior
- readable cards and boards
- keeper-feel player-facing output

## v1.0 Session Boards And Runtime-Aware Presentation

**Goal:** Build session boards and scene-facing presentation on top of canonical runtime truth once runtime contracts become stable enough to consume.

### Phase 30: Session Board Core

**Goal:** Render current session identity, phase, pending participants, and blocker summaries from canonical runtime state.
**Depends on:** Phase 13
**Requirements:** SUR-01
**Plans:** 1 plan

### Phase 31: Scene Framing Surface

**Goal:** Present focused scene context, cross-cut transitions, and waiting reasons in a keeper-readable format.
**Depends on:** Phase 30
**Requirements:** SUR-02
**Plans:** 0 plans

### Phase 32: Consequence Publication Surface

**Goal:** Render public/shared/private consequence outputs without re-owning runtime publication semantics.
**Depends on:** Phase 30, Phase 31
**Requirements:** SUR-03
**Plans:** 0 plans

### Phase 33: Clue And History Boards

**Goal:** Present shared clue/history boards built only from runtime-approved shared knowledge.
**Depends on:** Phase 12, Phase 32
**Requirements:** SUR-04
**Plans:** 0 plans

### Phase 34: Activity-Ready View Contracts

**Goal:** Separate view payloads from Discord formatting so later richer UI can reuse them.
**Depends on:** Phase 30, Phase 31, Phase 32, Phase 33
**Requirements:** SUR-05
**Plans:** 0 plans

## v1.1 Identity And Onboarding Surface Integration

**Goal:** Make archive, builder, campaign, and onboarding surfaces coherent without taking ownership of identity logic.

### Phase 35: Archive Card Contracts

**Goal:** Standardize archive detail rendering and card sections for identity-owned profile truth.
**Depends on:** Phase 24
**Requirements:** SUR-06
**Plans:** 0 plans

### Phase 36: Builder And DM Flow Polish

**Goal:** Refine DM-first builder and related archive guidance around the finalized identity flow.
**Depends on:** Phase 20, Phase 21, Phase 35
**Requirements:** SUR-07
**Plans:** 0 plans

### Phase 37: Campaign And Roster Surfaces

**Goal:** Show campaign binding, roster state, and selected identity in a player-readable way.
**Depends on:** Phase 25, Phase 30
**Requirements:** SUR-08
**Plans:** 0 plans

### Phase 38: New-Player Start Pack

**Goal:** Present module intro, flow guidance, and minimum COC concepts for first-session usability.
**Depends on:** Phase 34, Phase 37
**Requirements:** SUR-09
**Plans:** 0 plans

### Phase 39: Command Information Architecture

**Goal:** Align help copy, command naming, and channel guidance with the new workstream boundaries.
**Depends on:** Phase 35, Phase 36, Phase 37, Phase 38
**Requirements:** SUR-10
**Plans:** 0 plans

## v1.2 Interactive Discord Surface And Activity Bridge

**Goal:** Move beyond static boards into interaction patterns that still preserve runtime and identity ownership boundaries.

### Phase 40: Stateful Views And Pagination

**Goal:** Add stateful view handling for longer cards and boards within Discord constraints.
**Depends on:** Phase 34, Phase 39
**Requirements:** SUR-11
**Plans:** 0 plans

### Phase 41: Component-Driven Actions

**Goal:** Add button/select-driven flows on top of existing command and runtime contracts.
**Depends on:** Phase 40
**Requirements:** SUR-12
**Plans:** 0 plans

### Phase 42: Delivery Reliability

**Goal:** Make DM, ephemeral, and public delivery semantics explicit and testable across common UX flows.
**Depends on:** Phase 39, Phase 41
**Requirements:** SUR-13
**Plans:** 0 plans

### Phase 43: Activity Bridge Schema

**Goal:** Define a future-facing surface schema that Activity UI can consume without re-deriving meaning.
**Depends on:** Phase 34, Phase 40, Phase 41
**Requirements:** SUR-14
**Plans:** 0 plans

### Phase 44: Surface QA And Localization

**Goal:** Finish the track with consistency, readability, and Chinese-first copy validation.
**Depends on:** Phase 42, Phase 43
**Requirements:** SUR-15
**Plans:** 0 plans
