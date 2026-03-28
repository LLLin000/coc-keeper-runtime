# Requirements: Discord AI Keeper - Track A

**Core Value:** Owns canonical play truth - COC rules authority, module schema, room/scene/event graphs, trigger trees and consequence chains, reveal policy, private knowledge, endings.

## vA.1.1 Requirements (Track A)

Milestone: 模组结构化基础

### Module Structure (模组结构)

- [ ] **MOD-01**: 凄夜的游乐场模组包含完整的 room graph
- [ ] **MOD-02**: 凄夜的游乐场模组支持触发器系统
- [ ] **MOD-03**: 凄夜的游乐场模组定义结局条件

### Trigger System (触发器系统)

- [ ] **MOD-04**: 疯狂之馆触发器数量扩展 (5→13)
- [ ] **MOD-05**: 疯狂之馆结局数量扩展 (3→6)

### Module Expansion (模组扩展)

- [ ] **MOD-06**: 覆辙模组地点扩展 (3→9)
- [ ] **MOD-07**: 覆辙模组触发器扩展 (1→14)
- [ ] **MOD-08**: 覆辙模组结局添加 (0→3)

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| MOD-01 | 1 | Pending |
| MOD-02 | 1 | Pending |
| MOD-03 | 1 | Pending |
| MOD-04 | 2 | Pending |
| MOD-05 | 2 | Pending |
| MOD-06 | 3 | Pending |
| MOD-07 | 3 | Pending |
| MOD-08 | 3 | Pending |

**Coverage:**
- vA.1.1 requirements: 8 total
- Mapped to phases: 3
- Unmapped: 0 ✓

---

*Requirements updated: 2026-03-28 - Initial vA.1.1 requirements from PR #1*

---

## vA.1.2 Requirements (Track A)

Milestone: Group Action Resolution And Shared Scene Consequences

### Group Action Contracts

- [ ] **GROUP-01**: Runtime accepts a structured scene-round action batch instead of only one immediate actor input
- [ ] **GROUP-02**: Action batch contract preserves actor identity and ordering metadata without letting collection logic redefine rules truth
- [ ] **GROUP-03**: Single-actor flows remain supported as a compatible fallback during migration

### Shared Resolution

- [ ] **RESOLVE-01**: Multiple player actions can be resolved against one shared scene state in a single deterministic pass
- [ ] **RESOLVE-02**: Shared resolution can emit one coherent consequence bundle for Track D narration instead of contradictory per-message outputs
- [ ] **RESOLVE-03**: Trigger chains and rule results remain auditable after multi-actor resolution

### Reveal And Module Compatibility

- [ ] **REVEAL-01**: Public, player, and group-scoped reveals can all be emitted from one shared scene resolution
- [ ] **REVEAL-02**: Existing structured modules continue to run without requiring one-off multiplayer hacks

## Traceability (vA.1.2)

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GROUP-01 | TBD | Planned |
| GROUP-02 | TBD | Planned |
| GROUP-03 | TBD | Planned |
| RESOLVE-01 | TBD | Planned |
| RESOLVE-02 | TBD | Planned |
| RESOLVE-03 | TBD | Planned |
| REVEAL-01 | TBD | Planned |
| REVEAL-02 | TBD | Planned |

---

## vA.1.3 Requirements (Track A)

Milestone: Closed-Loop Event Graph Runtime

### Action Intent And Event Entry

- [ ] **EVENT-01**: Player language can be normalized into reusable action-intent categories without hardcoding each module around freeform wording
- [ ] **EVENT-02**: Action-intent routing produces stable event-entry contracts that later runtime layers can resolve deterministically
- [ ] **EVENT-03**: Event-entry contracts stay generic enough to support future modules instead of only current sample modules

### Event Reaction Nodes

- [ ] **REACT-01**: A resolved event can yield direct feedback, clarification, roll requests, state changes, clue changes, and follow-on events as first-class structured outcomes
- [ ] **REACT-02**: Event reactions can respond to non-mainline actions without breaking mainline progression
- [ ] **REACT-03**: Structured event reactions remain auditable and reusable by Track D presentation logic

### Spine / Branch / Ending Runtime

- [ ] **SPINE-01**: Runtime distinguishes core spine progression from optional branches and flavor/reactive nodes
- [ ] **SPINE-02**: Optional actions can influence risk, information, and endings without making the main scenario incoherent
- [ ] **SPINE-03**: Ending conditions can be accumulated from structured state instead of only linear script order

### Extraction Contract

- [ ] **EXTRACT-01**: Future module extraction targets closed-loop event graph structures rather than module-specific scene hacks
- [ ] **EXTRACT-02**: Extraction contract covers locations, events, clue graph, main spine, optional branches, and ending conditions

## Traceability (vA.1.3)

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| EVENT-01 | TBD | Planned |
| EVENT-02 | TBD | Planned |
| EVENT-03 | TBD | Planned |
| REACT-01 | TBD | Planned |
| REACT-02 | TBD | Planned |
| REACT-03 | TBD | Planned |
| SPINE-01 | TBD | Planned |
| SPINE-02 | TBD | Planned |
| SPINE-03 | TBD | Planned |
| EXTRACT-01 | TBD | Planned |
| EXTRACT-02 | TBD | Planned |

---

## vA.1.4 Requirements (Track A)

Milestone: COC Core Rules Authority And Module Onboarding Metadata

### Character Generation Truth

- [ ] **CHAR-01**: Runtime defines canonical COC 7e attribute generation formulas, including standard rolls for core attributes and luck
- [ ] **CHAR-02**: Runtime defines canonical age adjustments, EDU improvement checks, and derived-stat calculations for HP, MP, SAN, MOV, DB, and Build
- [ ] **CHAR-03**: Character-generation truth is reusable by Track B finalization flows without moving rule authority into builder prompts

### Skill Allocation Truth

- [ ] **SKILL-01**: Runtime defines occupation skill-point formulas, interest skill-point formulas, and credit-rating range handling
- [ ] **SKILL-02**: Runtime defines specialization-dependent allocation rules for fighting/firearms and similar bounded skill families
- [ ] **SKILL-03**: Runtime distinguishes strict canonical generation from optional quick-start presets without silently replacing the canonical path

### Combat / Injury Truth

- [ ] **COMBAT-01**: Runtime codifies DEX order, prepared-firearm initiative adjustments, and cover/point-blank style modifiers as canonical combat truth
- [ ] **COMBAT-02**: Runtime codifies melee opposition truth for dodge, fight back, and fighting maneuver resolution, including Build comparisons
- [ ] **COMBAT-03**: Runtime codifies extreme-success / impale damage handling and firearm/non-firearm damage distinctions
- [ ] **COMBAT-04**: Runtime codifies injury state transitions for HP loss, major wounds, unconsciousness, dying, stabilization, and recovery

### SAN Truth

- [ ] **SAN-01**: Runtime codifies sanity-roll outcomes, including success/failure SAN loss handling
- [ ] **SAN-02**: Runtime codifies single-shock follow-up logic such as 5+ SAN loss leading to INT-based temporary insanity checks
- [ ] **SAN-03**: Runtime codifies daily cumulative SAN-loss tracking, indefinite insanity thresholds, and insanity-state boundaries

### Module Onboarding Metadata

- [ ] **ONBOARD-01**: Module contracts support onboarding metadata such as recommended professions, recommended skills, recommended items, and rules scope
- [ ] **ONBOARD-02**: Module onboarding metadata remains extraction-friendly so future scenarios can be adapted to the framework rather than hand-patched

## Traceability (vA.1.4)

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| CHAR-01 | TBD | Planned |
| CHAR-02 | TBD | Planned |
| CHAR-03 | TBD | Planned |
| SKILL-01 | TBD | Planned |
| SKILL-02 | TBD | Planned |
| SKILL-03 | TBD | Planned |
| COMBAT-01 | TBD | Planned |
| COMBAT-02 | TBD | Planned |
| COMBAT-03 | TBD | Planned |
| COMBAT-04 | TBD | Planned |
| SAN-01 | TBD | Planned |
| SAN-02 | TBD | Planned |
| SAN-03 | TBD | Planned |
| ONBOARD-01 | TBD | Planned |
| ONBOARD-02 | TBD | Planned |
