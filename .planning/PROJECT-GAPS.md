# Discord AI Keeper - Project Gaps Analysis

**Research Date:** 2026-03-31
**Project:** Discord AI Keeper - Local Model-Driven Call of Cthulhu Campaign System
**Confidence:** HIGH (based on ROADMAP.md, STATE.md, test results, source code)

---

## Executive Summary

The Discord AI Keeper project has achieved significant momentum across all tracks with **808 passing tests** and **51 phases completed**. However, the project shows clear imbalances:

- **Track E (Runtime Control)**: Most mature - 51 phases, comprehensive testing infrastructure
- **Track B (Character Management)**: Near-complete foundation - 15 phases, vB.1.4 just finished
- **Track C (Discord Interaction)**: Complete through vC.1.3 - no future milestones planned
- **Track A (Module/Rules Runtime)**: Foundation done, multiplayer features queued
- **Track D (Game Presentation)**: **Not started** - 0 phases executed, entirely planned

**Critical gaps**: Track D has no execution, Track A multiplayer features (vA.1.2) are essential for the core value proposition, and Track C appears abandoned with no future roadmap.

---

## 1. Track Status Summary

### Track A - 模组与规则运行层 (Module & Rules Runtime)

| Milestone | Status | Phases | Notes |
|-----------|--------|--------|-------|
| vA.1.1 | ✅ COMPLETE | 3/3 | Module structuring, trigger system, 3 modules migrated |
| vA.1.2 | 📋 PLANNED | 0/0 | Group Action Resolution And Shared Scene Consequences |
| vA.1.3 | 📋 QUEUED | 0/0 | Closed-Loop Event Graph Runtime |
| vA.1.4 | 📋 QUEUED | 0/0 | COC Core Rules Authority And Module Onboarding |

**Completed Modules:**
- `sad_carnival.json` - 凄夜的游乐场 (702 lines)
- `mad_mansion.json` - 疯狂之馆 (26579 lines, 13 triggers, 6 endings)
- `fuzhe.json` - 覆辙 (35388 lines, 9 locations, 14 triggers)
- `fuzhe_mini.json` - 4-node vertical slice for testing

**vA.1.2 Gaps (Planned):**
- Scene round action batch contract
- Multi-actor resolution against shared state
- Shared reveal and consequence summaries
- Compatibility pass for existing complex modules

**Unplanned in Track A:**
- Strict COC rules enforcement (attribute/age/derived-stat rules)
- Combat and injury state machine
- SAN loss and insanity state handling
- Module onboarding metadata for new-player-friendly starts

---

### Track B - 人物构建与管理层 (Character Building & Management)

| Milestone | Status | Phases | Notes |
|-----------|--------|--------|-------|
| vB.1.1 | ✅ COMPLETE | 4/4 | Archive and Builder Normalization |
| vB.1.2 | ✅ COMPLETE | 4/4 | Archive Card Schema Expansion |
| vB.1.3 | ✅ COMPLETE | 4/4 | Interview Planner, Portrait Synthesis |
| vB.1.4 | ✅ COMPLETE | 3/3 | Identity Projection And Character Ownership |
| vB.1.5 | 📋 QUEUED | 0/0 | Character Lifecycle And Governance Surface |
| vB.1.6 | 📋 QUEUED | 0/0 | COC-Legal Character Finalization |

**vB.1.5 Gaps (Queued):**
- Profile lifecycle clarity
- Admin governance surfaces
- Ownership visibility and auditability
- Archive/campaign instance management UX

**vB.1.6 Gaps (Queued):**
- Standard canonical character finalization
- Quick-start/new-player creation mode
- Profession/skill/item recommendation consumption
- Provenance and explanation of where card values came from

---

### Track C - Discord 交互层 (Discord Interaction)

| Milestone | Status | Phases | Notes |
|-----------|--------|--------|-------|
| vC.1.1 | ✅ SHIPPED | 3/3 | Channel Governance |
| vC.1.2 | ✅ SHIPPED | 4/4 | Multiplayer Session Governance |
| vC.1.3 | ✅ SHIPPED | 5/5 | Campaign Surfaces And Intent Clarity |
| Future | ❌ **NOT PLANNED** | 0/0 | No roadmap beyond vC.1.3 |

**⚠️ CONCERN: Track C has no future milestones planned.**

**Post-vC.1.3 ideas (from ROADMAP.md) but NOT planned:**
- Broader campaign/adventure browsing beyond current runtime context
- Richer historical operator visibility
- Discord Activity UI implementation
- Character semantics redesign outside Track C

**Completed Features:**
- `/bind_campaign`, `/join`, `/select_profile`, `/ready` commands
- Channel enforcement (`channel_enforcer.py`)
- Session phases, ready-check, admin-start discipline
- Pre-play onboarding with Discord buttons
- Visibility contracts (VisibilitySnapshot)
- Player status surfaces, KP/operator dashboard
- Handling reason surfaces (buffered/ignored/deferred explanations)

---

### Track D - 游戏呈现层 (Game Presentation)

| Milestone | Status | Phases | Notes |
|-----------|--------|--------|-------|
| vD.1.1 | 📋 PLANNED | 0/4 | Keeper-Guided Archive Experience |
| vD.1.2 | 📋 QUEUED | 0/0 | Session Boards And Keeper Scene Presentation |
| vD.1.3 | 📋 QUEUED | 0/0 | New-Player Start Pack And Rules Boards |

**⚠️ CRITICAL: Track D has 0 phases executed - entirely not started.**

**vD.1.1 Planned Focus (0/4 complete):**
- Private-first builder experience
- Archive channel role redesign
- Richer card boards and summaries
- Activity-ready presentation contracts

**vD.1.2 Planned Focus:**
- Session boards
- Scene framing and consequence presentation
- Clue/history/current-state summaries
- Newcomer-friendly minimum-rules and flow boards
- Activity-ready session presentation contracts

**vD.1.3 Planned Focus:**
- What-is-COC and today's-module start packs
- Recommended profession/skill/item presentation
- Combat/injury/SAN flow boards
- Explanation density by mode (new-player/standard/veteran)

---

### Track E - 运行控制与运维面板层 (Runtime Control & Operations)

| Milestone | Status | Phases | Tests | Notes |
|-----------|--------|--------|-------|-------|
| vE.1.1 | ✅ COMPLETE | 4/4 | - | Runtime Control Contracts |
| vE.2.1 | ✅ COMPLETE | 9/9 | - | Full Process Validation Framework |
| vE.2.2 | ✅ COMPLETE | 4/4 | - | Unified Scenario-Driven E2E |
| vE.3.1 | ✅ COMPLETE | 6/6 | 222 | COC Rules Unit Tests |
| vE.3.2 | ✅ COMPLETE | 7/7 | - | Gap Closure & Integration |
| **Total** | | **51** | **808** | |

**vE.3.2 Completed Gaps:**
- ✅ Skill Usage Tracking (E79)
- ✅ Visibility Dispatcher Completion (E80)
- ✅ Creature Bestiary & Stats (E81)
- ✅ Chase Rules Implementation (E82)
- ✅ Archive Repository Completion (E83)
- ✅ Character Builder Integration (E84)
- ✅ Equipment System (E85)

**Remaining TODOs in Track E:**
- `gameplay/chase.py:39` - "TODO: Get actual stats from character registry"
- `gameplay/chase.py:42` - "TODO: Get actual name"
- `orchestrator/consequence_aggregator.py:144` - "TODO: Integrate with Ollama for LLM summarization"

**No future milestones planned for Track E.**

---

## 2. Test Coverage Analysis

### Test Inventory

| Category | Files | Tests | Status |
|----------|-------|-------|--------|
| COC Rules Unit Tests | 3 | 222 | ✅ Complete |
| Integration Tests | 60+ | ~400+ | ✅ Good |
| E2E Scenarios | 14 | 14 | ✅ Complete |
| BDD Tests | 5 | 5 | ✅ Complete |
| **Total** | **80+** | **808** | ✅ All Passing |

### COC Rules Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| Derived Attributes | 75 | MOV, Build, DB, HP, MP, SAN, LUCK, age modifiers |
| Combat + Insanity | 56 | Initiative, fighting, shooting, brawl, grapple, armor, insanity |
| Experience + Skills | 91 | Skill improvement, COC_SKILLS (80+), COC_SPELLS (20+) |

### E2E Scenarios (14 Total)

**Acceptance (9):**
- `scen_character_creation.yaml` - Campaign bind → join → ready
- `scen_combat_san.yaml` - Combat → SAN → insanity chain
- `scen_skill_improvement_lifecycle.yaml` - Skill improvement flow
- `scen_fuzhe_15turn.yaml` - 15-turn fuzhe_mini adventure
- `scen_session_happy_path.yaml` - Full session lifecycle
- `scen_smoke.yaml` - Smoke check
- `scen_equipment_combat.yaml` - Equipment combat
- `scen_character_builder.yaml` - Builder flow
- `scen_chase.yaml` - Chase mechanics

**Contract (5):**
- `scen_awaiting_ready_visibility.yaml`
- `scen_gmonly_reaches_kp.yaml`
- `scen_no_gmonly_to_player.yaml`
- `scen_investigation_before_reveal.yaml`
- `scen_wrong_path_no_premature_reveal.yaml`

**Chaos (1):**
- `scen_chaos_lobby.yaml` - 5 concurrent users

**Recovery (2):**
- `scen_crash_recovery.yaml`
- `scen_stream_interrupt.yaml`

### Tested Systems

✅ **Discord Commands** - `/bind_campaign`, `/join`, `/select_profile`, `/ready`, `/start_session`
✅ **Session/Orchestrator** - Phase transitions, multi-user state sync
✅ **Adventure Runtime** - Trigger chains, room transitions, reveal gates
✅ **COC Rules** - Skills, combat, sanity, magic, derived attributes, experience
✅ **Narration Pipeline** - Streaming output, KP/player visibility separation
✅ **Model/Router** - Intent classification, turn plan generation
✅ **Persistence** - SQLite recovery, state restoration
✅ **Visibility Dispatcher** - Public/private/group messages, gm_only leak prevention

### Untested/Unverified Systems

⚠️ **Real Discord Integration** - All tests use FakeInteraction
⚠️ **Live Ollama Model** - Tests use fake_contract or recorded cassettes
⚠️ **VCR Cassettes** - Limited real recordings for api model mode
⚠️ **Chase Rules** - Implemented but `gameplay/chase.py` has TODOs for character registry integration
⚠️ **Equipment System** - E85 scenario exists but integration with combat needs runtime verification

---

## 3. Planned vs Unplanned Gaps

### Planned Gaps (In Roadmap)

| Track | Gap | Milestone | Status |
|-------|-----|-----------|--------|
| A | Group Action Resolution | vA.1.2 | Planned |
| A | Closed-Loop Event Graph | vA.1.3 | Queued |
| A | COC Core Rules Authority | vA.1.4 | Queued |
| B | Character Lifecycle Governance | vB.1.5 | Queued |
| B | COC-Legal Finalization | vB.1.6 | Queued |
| D | Keeper-Guided Archive | vD.1.1 | Planned (0%) |
| D | Session Boards | vD.1.2 | Queued |
| D | New-Player Start Pack | vD.1.3 | Queued |

### Unplanned Gaps (Not in Roadmap)

| Gap | Severity | Notes |
|-----|----------|-------|
| Track C has no future roadmap | HIGH | vC.1.3 shipped, nothing after |
| Track D entirely not started | HIGH | 0 phases executed |
| Multiplayer shared scene resolution | HIGH | Core value proposition gap |
| Discord Activity UI preparation | MEDIUM | Mentioned but not planned |
| Real Discord integration testing | MEDIUM | Only FakeInteraction used |
| Live Ollama model verification | LOW | Rely on fake_contract/recorded |

---

## 4. Cross-Track Dependencies

```
Track A (Module Runtime)
    │
    ├── vA.1.2 (Group Action) ──→ Needs Track C multiplayer governance
    ├── vA.1.3 (Event Graph) ──→ Needs Track E scenario testing
    └── vA.1.4 (COC Authority) ──→ Depends on Track B character system

Track B (Character Management)
    │
    ├── vB.1.5 (Governance) ──→ Needs Track C admin surfaces
    └── vB.1.6 (Finalization) ──→ Needs Track A COC rules

Track C (Discord Interaction)
    │
    └── Future ──→ No milestones planned ⚠️

Track D (Game Presentation)
    │
    ├── vD.1.1 ──→ Depends on Track B archive system
    ├── vD.1.2 ──→ Needs Track A session state
    └── vD.1.3 ──→ Needs Track A COC rules

Track E (Runtime Control)
    │
    └── Infrastructure complete ──→ Ready to support other tracks
```

---

## 5. Recommendations for Next Milestones

### Immediate Priority

#### 1. Track D Execution (vD.1.1)
**Reason:** Track D is completely untouched (0 phases). The game presentation layer is essential for player experience. Without it, the system lacks:
- Keeper-style scene presentation
- Clue/history boards
- New-player onboarding surfaces

**Start with:** D40 - Private-First Builder Experience

#### 2. Track A vA.1.2 (Group Action Resolution)
**Reason:** Core multiplayer value proposition. Current system handles single-player scene rounds; multiplayer shared scenes are essential for real campaign use.

**Start with:** Scene round action batch contract design

### Near-Term (After Track D begins)

#### 3. Track B vB.1.5 (Character Lifecycle Governance)
**Reason:** Identity ownership hardened in vB.1.4; next logical step to build governance surfaces.

#### 4. Track A vA.1.4 (COC Core Rules Authority)
**Reason:** Strict COC rules enforcement needed before Track D can present rules clearly to new players.

### Long-Term

#### 5. Track C Future Planning
**Reason:** Track C has no future milestones. Needs planning for:
- Campaign/adventure browsing
- Historical operator visibility
- Discord Activity UI preparation

---

## 6. Metrics Summary

| Metric | Value |
|--------|-------|
| Total Phases Completed | 51 (E40-E85 + B40-B54 + C44-C55 + A1-A3) |
| Total Tests | 808 passing |
| COC Unit Tests | 222 |
| E2E Scenarios | 14 |
| Modules Structured | 4 (sad_carnival, mad_mansion, fuzhe, fuzhe_mini) |
| COC Skills | 80+ |
| COC Spells | 20+ |
| Tracks with Future Roadmap | 3/5 (A, B, D) |
| Tracks Executing | 2/5 (B, E) |

---

## 7. Files Analyzed

**Roadmaps:**
- `.planning/workstreams/track-a/ROADMAP.md` - Track A roadmap
- `.planning/workstreams/track-b/ROADMAP.md` - Track B roadmap
- `.planning/workstreams/track-c/ROADMAP.md` - Track C roadmap
- `.planning/workstreams/track-d/ROADMAP.md` - Track D roadmap
- `.planning/workstreams/track-e/ROADMAP.md` - Track E roadmap

**States:**
- `.planning/workstreams/track-a/STATE.md`
- `.planning/workstreams/track-b/STATE.md`
- `.planning/workstreams/track-c/STATE.md`
- `.planning/workstreams/track-d/STATE.md`
- `.planning/workstreams/track-e/STATE.md`

**Research:**
- `.planning/MAP-CODEBASE-TRACK-E.md` - Comprehensive Track E analysis

**Source:**
- `src/dm_bot/` - All source modules

**Tests:**
- `tests/` - 808 passing tests

---

*Report generated: 2026-03-31*
*Next recommended milestone: vD.1.1 (Track D - Keeper-Guided Archive Experience)*
