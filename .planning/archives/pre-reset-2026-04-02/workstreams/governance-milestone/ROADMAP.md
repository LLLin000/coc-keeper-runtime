# Roadmap: Discord AI Keeper

## Overview

This roadmap is now organized by persistent product tracks, not only by historical phase order. GSD agents should first choose the relevant track, then choose the next milestone inside that track.

Historical phase execution still matters and remains recorded in `MILESTONES.md`, but future planning should use the track structure below.

## Track Planning Policy

Future milestone planning should follow this policy:

1. Choose one primary track.
2. Define scope in that track first.
3. If other tracks are affected, declare them as secondary impact instead of widening the milestone's primary ownership.
4. When a shared contract changes, document the affected contract and migration note in the milestone or PR summary.

This keeps the system compatible with GSD's linear milestone history while still allowing four parallel product lanes.

## Active Milestone

**vB.1.1** - B1 Archive And Builder Normalization
- **Primary Track:** Track B - 人物构建与管理层
- **Goal:** Tighten archive-builder mapping with better AI summarization during builder flow, aligned with standard COC character sheet sections

---

## vB.1.1 Phases

- [ ] **Phase 40: Foundation** - Pydantic contracts, AnswerNormalizer, schema versioning
- [ ] **Phase 41: Core Synthesis** - CharacterSheetSynthesizer, SectionNormalizer
- [ ] **Phase 42: Integration** - Connect to builder, backward compatibility, archive-projection sync
- [ ] **Phase 43: Polish** - Expand COC 7e sections, validation, playtest

### Phase 40: Foundation

**Goal:** Establish Pydantic contracts and schema versioning before building synthesis logic to prevent integration breakage later.

**Depends on:** Nothing (first phase of vB.1.1)

**Requirements:** BC-01, BC-02, FN-05

**Success Criteria** (what must be TRUE):
  1. Developer can import synthesis contracts and see clear Pydantic schemas for builder-to-archive communication
  2. AnswerNormalizer component can clean raw user input (Chinese variations) to canonical slot format
  3. New archive schema fields are nullable with defaults, preserving backward compatibility with existing profiles
  4. Existing profile queries continue to work without modification after schema changes

**Plans:** TBD

### Phase 41: Core Synthesis

**Goal:** Build the core AI summarization that transforms raw builder answers into cohesive COC character profiles instead of copying verbatim.

**Depends on:** Phase 40

**Requirements:** AI-01, BC-03, BC-04, BC-05

**Success Criteria** (what must be TRUE):
  1. User completing builder interview receives a synthesized character profile that reads as cohesive narrative, not copied input
  2. CharacterSheetSynthesizer uses structured output (instructor + Pydantic) to generate narrative from normalized answers
  3. SectionNormalizer maps synthesis output to standard COC 7e character sheet sections
  4. ArchiveProfileFactory creates valid ArchiveProfile instances from synthesis output
  5. Synthesis respects COC 7e rules - no invented skills or occupations appear in output

**Plans:** TBD

**UI hint:** yes

### Phase 42: Integration

**Goal:** Connect new synthesis components to existing builder flow with backward compatibility and archive-projection synchronization.

**Depends on:** Phase 41

**Requirements:** AI-02, AI-03, AI-04, FN-01, FN-02, FN-03, FN-04, BC-06, PS-01, PS-02, PS-03

**Success Criteria** (what must be TRUE):
  1. ConversationalCharacterBuilder uses new synthesis flow end-to-end without breaking existing users
  2. Fallback from synthesis to heuristic extraction works when synthesis produces invalid output
  3. Existing "life_goal", "weakness", "key_past_event" fields map to standard COC backstory sections
  4. New COC 7e fields (Birthplace, Residence, Family, Education) are added and populated
  5. Archive normalization updates automatically propagate to campaign projections
  6. Diagnostic command shows sync status between archive and projection
  7. Single active profile governance continues to work after normalization changes
  8. User sees confirmation step before AI overwrites their explicit character choices

**Plans:** TBD

### Phase 43: Polish

**Goal:** Validate with real playtest data and expand COC 7e section coverage before declaring milestone complete.

**Depends on:** Phase 42

**Requirements:** (validation-focused - all vB.1.1 requirements should be tested)

**Success Criteria** (what must be TRUE):
  1. At least one playtest session creates characters using the new synthesis flow
  2. Created characters display correctly in /profile_detail with all COC 7e sections
  3. Archive-to-projection sync works correctly for playtest characters
  4. No synthesis failures that crash the builder flow - fallback handles edge cases gracefully
  5. Validation rules confirm occupation skills match COC 7e allowed lists

**Plans:** TBD

---

## Track A Roadmap: 模组与规则运行层

Owns canonical module truth, rules truth, structured state, trigger execution, and reusable authoring/runtime contracts.

### Completed Foundation

- `v1.1` formal structured module runtime and `疯狂之馆`
- `v1.4` room-graph runtime and AI-first extraction draft
- `v1.5` trigger tree and consequence engine
- `v1.6` COC/Keeper-first runtime pivot
- `v1.7` mixed room/scene/event graph and `覆辙` complex-module baseline

### Completed Phases

- Phase 6: Structured Module Runtime
- Phase 7: 疯狂之馆 Formal Module
- Phase 16: Room Graph Runtime Foundations
- Phase 17: AI Extraction For Room Graphs And Trigger Trees
- Phase 18: 疯狂之馆 Room-Graph Migration
- Phase 19: Generic Trigger And Consequence Schema
- Phase 20: Runtime Trigger Engine
- Phase 21: 疯狂之馆 Trigger Migration
- Phase 22: COC Runtime Foundations
- Phase 23: COC Asset And Character Intake
- Phase 24: COC Module And Keeper Experience Migration
- Phase 25: Investigator Panel Runtime
- Phase 26: Private Knowledge And Complex Module Graphs
- Phase 27: 覆辙 Complex Module Migration

### Next Milestones

#### `A1` Complex COC Module Runtime Stabilization
Goal:
- Harden mixed room/scene/event graph play for long, asymmetrical, private-information COC modules.

Includes:
- stronger module-state contracts
- clearer scene/event gating
- less module-specific glue in `覆辙`

Does not include:
- Discord command redesign as the main goal
- archive UI redesign as the main goal

#### `A2` Trigger/Consequence Deepening
Goal:
- Improve chained consequence handling so rolls, clues, statuses, and branching conditions propagate more naturally.

Includes:
- deeper post-roll consequence chains
- better event-log semantics
- cleaner module hook boundaries

#### `A3` COC Rules Authority Deepening
Goal:
- Expand deterministic COC coverage while keeping all mechanics grounded in local rulebooks or explicit module rules.

Includes:
- success tiers
- opposed/group/pushed checks
- SAN and long-form state interactions

#### `A4` Module Author Workflow
Goal:
- Make new structured module creation repeatable for collaborators.

Includes:
- extraction drafts
- module review flow
- package conventions

Recommended contract focus:
- `AdventureSchema`
- `ModuleState`
- `TriggerExecutionResult`

## Track B Roadmap: 人物构建与管理层

Owns long-lived character truth, archive lifecycles, builder flows, and campaign projection.

### Completed Foundation

- `v1.8` archive-vs-campaign projection split
- `v1.9` adaptive builder interviews and richer identity
- `v2.0` richer archive schema, archive details, AI writeback
- `v2.1` smoke-check-adjacent governance basics, one-active-profile baseline, initial admin visibility

### Completed Phases

- Phase 25: Investigator Panel Runtime
- Phase 28: Discord Channel Roles And Command Discipline
- Phase 29: COC Conversational Character Builder
- Phase 30: Profile Archive And Campaign Projection
- Phase 31: Dynamic Builder Interview Engine
- Phase 32: Narrative Character Shaping And Fun Builder UX
- Phase 33: COC-Legal Character Projection And Archive Writeback
- Phase 34: Rich Archive Schema And Normalization
- Phase 35: Archive Presentation And Detail Views
- Phase 36: COC-Bounded Archive Finishing And Module Reuse
- Phase 38: Single Active Profile Lifecycle
- Phase 39: Admin Character Governance

### Next Milestones

#### `B1` Archive And Builder Normalization (ACTIVE)
Goal:
- Tighten the mapping from conversational answers into clean, reusable archive fields.

Includes:
- richer semantic normalization
- better builder-to-archive contracts
- fewer fallback heuristics

#### `B2` Character Lifecycle And Admin Governance
Goal:
- Finish profile lifecycle, admin control, archive replacement, and auditability.

Includes:
- admin detail views
- force-activate/archive/delete flows
- clearer player/admin separation

#### `B3` Character Finishing And COC-Bounded Projection
Goal:
- Let interviews shape legal finishing choices and campaign projections without inventing house rules.

Includes:
- bounded finishing recommendations
- transparent projection logic

#### `B4` Advanced Character Assets
Goal:
- Support richer long-term identity surfaces and future non-bot UI.

Includes:
- panel-ready data groupings
- richer role overlays for complex modules

Recommended contract focus:
- `ArchiveProfile`
- `CampaignProjection`
- `AdminProfileOps`

## Track C Roadmap: Discord 交互层

Owns how users and operators interact with the runtime inside Discord.

### Completed Foundation

- `v1.0` Discord runtime and dual-model control
- `v1.2` true Discord streaming and reliability improvements
- `v1.8` archive/game channel discipline
- `v2.1` local smoke-check gate and first admin channel binding

### Completed Phases

- Phase 1: Discord Runtime & Dual-Model Control
- Phase 4: Persistence, Recovery & Diagnostics
- Phase 5: Multiplayer usability, natural message intake, and starter adventure
- Phase 9: Adventure Onboarding And Auto-Opening
- Phase 11: Streaming Responses And Message Reliability
- Phase 12: True Streaming Discord Output
- Phase 28: Discord Channel Roles And Command Discipline
- Phase 37: Local Delivery Smoke Check
- Phase 39: Admin Character Governance

### Next Milestones

#### `C1` Channel Governance And Command Discipline Hardening
Goal:
- Make channel responsibilities obvious and enforceable for players, operators, and admins.

Includes:
- archive/admin/trace/game guidance
- better wrong-channel redirects
- less command clutter in game halls

#### `C2` Builder And Archive Interaction Flow Polish
Goal:
- Make builder and archive interactions feel reliable and intentional inside Discord constraints.

Includes:
- clearer continuation behavior
- less confusion around ephemeral vs channel flows
- improved feedback on blocked states

#### `C3` Operational Reliability Surface
Goal:
- Reduce Discord-side confusion when the bot is down, starting, or misconfigured.

Includes:
- clearer startup diagnostics
- more explicit operator guidance
- stable command sync expectations

#### `C4` Activity Preparation Layer
Goal:
- Prepare data shapes and boundaries for a later Discord Activity UI without requiring it yet.

Includes:
- UI-ready payloads
- boundaries between bot-native and Activity-only features

Recommended contract focus:
- `ChannelRoleConfig`
- `InteractionRouting`
- `OperationalHealth`

## Track D Roadmap: 游戏呈现层

Owns table feel, Keeper presentation, clue visibility, and the readable player-facing shape of the experience.

### Completed Foundation

- `v1.3` structured judgement, bounded hints, keeper-style framing
- `v1.7` player panel baseline
- `v2.0` archive detail view improvements

### Completed Phases

- Phase 13: Structured Judgement And Roll Prompting
- Phase 14: Hint Timing, Clue Flow, And Stall Recovery
- Phase 15: Keeper-Style Scene Framing And Consequence Presentation
- Phase 32: Narrative Character Shaping And Fun Builder UX
- Phase 35: Archive Presentation And Detail Views

### Next Milestones

#### `D1` Keeper Presentation And Guidance Pass
Goal:
- Improve the feel of investigation play without over-guiding or breaking module truth.

Includes:
- scene presentation
- clue pacing
- consequence wording

#### `D2` Player-Facing Boards And Summaries
Goal:
- Make clues, history, and character state easier to read in Discord-native surfaces.

Includes:
- better summaries
- clearer panel layouts
- board-like presentation patterns

#### `D3` Failure, Fear, And Consequence Presentation
Goal:
- Present SAN loss, setbacks, and discovery consequences in a more tabletop-authentic way.

Includes:
- success/failure framing
- escalation tone
- emotional readability

#### `D4` Rich UI Surfaces
Goal:
- Move beyond bot-native presentation where needed.

Includes:
- future Activity-backed character/clue/map panels

Recommended contract focus:
- `NarratorInput`
- `GuidanceContract`
- `PanelSummaryContract`

---

## v2.2 Governance Milestone

**Primary purpose:** Formalize track-based project governance so any GSD-driven collaborator can recover the product structure, global rules, and next-milestone choices directly from repository planning docs.

**Planned phases:** Phase 44-46 (deferred - waiting for vB.1.1 completion)

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 40. Foundation | 0/1 | Not started | - |
| 41. Core Synthesis | 0/1 | Not started | - |
| 42. Integration | 0/1 | Not started | - |
| 43. Polish | 0/1 | Not started | - |

---

## Current Recommendation

If a new collaborator needs to choose what to work on next:

1. Pick a track.
2. Confirm the track choice against `PROJECT.md`.
3. Use this roadmap to choose the next milestone in that track.
4. Check `STATE.md` to avoid conflicting with the currently active milestone.

---
*Last updated: 2026-03-28 for milestone vB.1.1*
