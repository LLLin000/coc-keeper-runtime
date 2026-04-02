# Milestone vC.1.3: Campaign Surfaces And Intent Clarity

**Status:** ✅ SHIPPED 2026-03-29
**Primary Track:** Track C - Discord 交互层
**Phases:** 51-55
**Total Plans:** 5

## Overview

Goal: Make campaign/adventure/session state legible in Discord and make message handling reasons explicit to players and operators through logic-first visibility contracts and reusable surfaces.

## Phases

### Phase 51: Visibility Core Contracts

**Goal:** Define canonical visibility state for campaign, adventure, session, waiting reasons, routing outcomes, and existing player snapshot state.

**Depends on:** Nothing (first phase of vC.1.3)

**Requirements:** SURF-01, SURF-02, SURF-03, SURF-04

**Plans:** 1 plan

- [x] 51-01-PLAN.md — Visibility core contracts

**Details:**
- Created VisibilitySnapshot with canonical campaign/adventure/session state
- Waiting/blocker reasons are now explicit and queryable
- Routing outcomes carry a short explanation contract
- Existing player snapshot state can be exposed without redefining character semantics

---

### Phase 52: Player Status Surfaces

**Goal:** Add player-facing shared status surfaces for current campaign/adventure/session identity and waiting state.

**Depends on:** Phase 51

**Requirements:** PLAY-01, PLAY-02, CURR-01, CURR-02

**Plans:** 1 plan

- [x] 52-01-PLAN.md — Player status surfaces

**Details:**
- Players can see current campaign/adventure/session identity from Discord
- Players can see what the table is waiting on and who is pending
- Current-only visibility works without requiring broad browsing UI
- Inactive or unloaded states are explained explicitly instead of failing silently

---

### Phase 53: Handling Reason Surfaces

**Goal:** Add concise player-facing explanations for why messages were ignored, buffered, deferred, or otherwise routed differently.

**Depends on:** Phase 52

**Requirements:** PLAY-03, PLAY-04

**Plans:** 1 plan

- [x] 53-01-PLAN.md — Handling reason surfaces

**Details:**
- Players receive short practical handling explanations at the right moments
- Explanations are phase-aware and routing-aware
- Explanations stay concise enough for ordinary play channels

---

### Phase 54: KP Ops Surfaces

**Goal:** Add a separate KP/operator operational surface showing session ops, runtime state, player participation, and routing diagnostics.

**Depends on:** Phase 53

**Requirements:** OPS-01, OPS-02, OPS-03

**Plans:** 1 plan

- [x] 54-01-PLAN.md — KP ops surfaces

**Details:**
- KP/operators can see phase, round state, blockers, and current runtime state in one place
- KP/operators can inspect per-player ready/submitted/pending style state
- KP/operators can inspect routing outcomes without digging through raw logs

---

### Phase 55: Activity-Ready Boundary Polish

**Goal:** Consolidate the visibility contracts and surfaces so future Discord Activity UI can reuse the same business logic without rewriting the model.

**Depends on:** Phase 54

**Requirements:** ACT-01, ACT-02

**Plans:** 1 plan

- [x] 55-01-PLAN.md — Activity-ready boundary polish

**Details:**
- Visibility contracts are reusable beyond chat-only rendering
- Surface implementations clearly separate canonical state from renderer logic
- Milestone remains Activity-ready without implementing Activity UI itself

---

## Requirements Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| SURF-01 | 51 | ✅ Implemented |
| SURF-02 | 51 | ✅ Implemented |
| SURF-03 | 51 | ✅ Implemented |
| SURF-04 | 51 | ✅ Implemented |
| PLAY-01 | 52 | ✅ Implemented |
| PLAY-02 | 52 | ✅ Implemented |
| CURR-01 | 52 | ✅ Implemented |
| CURR-02 | 52 | ✅ Implemented |
| PLAY-03 | 53 | ✅ Implemented |
| PLAY-04 | 53 | ✅ Implemented |
| OPS-01 | 54 | ✅ Implemented |
| OPS-02 | 54 | ✅ Implemented |
| OPS-03 | 54 | ✅ Implemented |
| ACT-01 | 55 | ✅ Implemented |
| ACT-02 | 55 | ✅ Implemented |

**Requirements shipped:** 15/15

---

## Key Accomplishments

1. Created VisibilitySnapshot with canonical campaign/adventure/session state
2. Implemented player-facing status surfaces with current context visibility
3. Added handling reason surfaces for buffered/ignored/deferred messages
4. Built KP/operator operational dashboard with session diagnostics
5. Established Activity-ready boundary with clear separation of concerns

---

_For current project status, see .planning/ROADMAP.md_
