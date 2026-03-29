# Roadmap: Track C - Discord 交互层

## Milestones

- ✅ **vC.1.1** — Channel Governance (Phases 44-46) — SHIPPED 2026-03-28
- ✅ **vC.1.2** — Multiplayer Session Governance (Phases 47-50) — SHIPPED 2026-03-29
- ✅ **vC.1.3** — Campaign Surfaces And Intent Clarity (Phases 51-55) — SHIPPED 2026-03-29

---

## vC.1.1 Phases (COMPLETE)

<details>
<summary>✅ vC.1.1 Channel Governance (Phases 44-46) — SHIPPED 2026-03-28</summary>

- [x] Phase 44: Channel Structure (1/1 plan) — 2026-03-28
- [x] Phase 45: Command Routing (1/1 plan) — 2026-03-28
- [x] Phase 46: Guidance & Polish (1/1 plan) — 2026-03-28

</details>

---

## vC.1.2 Phases (COMPLETE)

<details>
<summary>✅ vC.1.2 Multiplayer Session Governance (Phases 47-50) — SHIPPED 2026-03-29</summary>

**Goal:** Add explicit multiplayer session phases, structured onboarding, admin-start flow, scene-round collection/resolution, and clearer message-intent routing.

- [x] Phase 47: Session Phases (1/1 plan) — 2026-03-28 ✅
- [x] Phase 48: Pre-Play Onboarding (1/1 plan) — 2026-03-28 ✅
- [x] Phase 49: Scene Round Collection (1/1 plan) — 2026-03-28 ✅
- [x] Phase 50: Message Intent Routing (1/1 plan) — 2026-03-28 ✅

**Completed focus:**
- ✅ ready-check plus admin-start discipline
- ✅ pre-play onboarding with interactive Discord buttons
- ✅ scene round collection/resolution flow
- ✅ phase-aware intent routing and buffering

</details>

---

## vC.1.3 Phases (COMPLETE)

**Goal:** Make campaign/adventure/session state legible in Discord and make message handling reasons explicit to players and operators through logic-first visibility contracts and reusable surfaces.

### Phase 51: Visibility Core Contracts
- Status: Complete
- Plans: 1/1
- Completed: 2026-03-29
- Goal: Define canonical visibility state for campaign, adventure, session, waiting reasons, routing outcomes, and existing player snapshot state.
- Requirements: SURF-01, SURF-02, SURF-03, SURF-04
- Success Criteria:
  1. Discord surfaces read from a shared visibility model instead of ad hoc string assembly
  2. Waiting/blocker reasons are explicit and queryable
  3. Routing outcomes carry a short explanation contract
  4. Existing player snapshot state can be exposed without redefining character semantics

### Phase 52: Player Status Surfaces
- Status: Complete
- Plans: 1/1
- Completed: 2026-03-29
- Goal: Add player-facing shared status surfaces for current campaign/adventure/session identity and waiting state.
- Requirements: PLAY-01, PLAY-02, CURR-01, CURR-02
- Success Criteria:
  1. Players can see current campaign/adventure/session identity from Discord
  2. Players can see what the table is waiting on and who is pending when relevant
  3. Current-only visibility works without requiring broad browsing UI
  4. Inactive or unloaded states are explained explicitly instead of failing silently

### Phase 53: Handling Reason Surfaces
- Status: Complete
- Plans: 1/1
- Completed: 2026-03-29
- Goal: Add concise player-facing explanations for why messages were ignored, buffered, deferred, or otherwise routed differently.
- Requirements: PLAY-03, PLAY-04
- Success Criteria:
  1. Players receive short practical handling explanations at the right moments
  2. Explanations are phase-aware and routing-aware
  3. Explanations stay concise enough for ordinary play channels

### Phase 54: KP Ops Surfaces
- Status: Complete
- Plans: 1/1
- Completed: 2026-03-29
- Goal: Add a separate KP/operator operational surface showing session ops, runtime state, player participation, and routing diagnostics.
- Requirements: OPS-01, OPS-02, OPS-03
- Success Criteria:
  1. KP/operators can see phase, round state, blockers, and current runtime state in one place
  2. KP/operators can inspect per-player ready/submitted/pending style state
  3. KP/operators can inspect routing outcomes without digging through raw logs

### Phase 55: Activity-Ready Boundary Polish
- Status: Complete
- Plans: 1/1
- Completed: 2026-03-29
- Goal: Consolidate the visibility contracts and surfaces so future Discord Activity UI can reuse the same business logic without rewriting the model.
- Requirements: ACT-01, ACT-02
- Success Criteria:
  1. Visibility contracts are reusable beyond chat-only rendering
  2. Surface implementations clearly separate canonical state from renderer logic
  3. This milestone remains Activity-ready without implementing Activity UI itself

---

## Future / Deferred

**Post-vC.1.3 ideas:**
- broader campaign/adventure browsing beyond current runtime context
- richer historical operator visibility
- Discord Activity UI implementation
- character semantics redesign outside Track C

---

## Progress Table

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| 44. Channel Structure | 1/1 | ✅ Complete | 2026-03-28 |
| 45. Command Routing | 1/1 | ✅ Complete | 2026-03-28 |
| 46. Guidance & Polish | 1/1 | ✅ Complete | 2026-03-28 |
| 47. Session Phases | 1/1 | ✅ Complete | 2026-03-28 |
| 48. Pre-Play Onboarding | 1/1 | ✅ Complete | 2026-03-28 |
| 49. Scene Round Collection | 1/1 | ✅ Complete | 2026-03-28 |
| 50. Message Intent Routing | 1/1 | ✅ Complete | 2026-03-28 |
| 51. Visibility Core Contracts | 1/1 | ✅ Complete | 2026-03-29 |
| 52. Player Status Surfaces | 1/1 | ✅ Complete | 2026-03-29 |
| 53. Handling Reason Surfaces | - | ✅ Complete | 2026-03-29 |
| 54. KP Ops Surfaces | - | ✅ Complete | 2026-03-29 |
| 55. Activity-Ready Boundary Polish | - | ✅ Complete | 2026-03-29 |

---

*Last updated: 2026-03-29 — vC.1.3 SHIPPED*