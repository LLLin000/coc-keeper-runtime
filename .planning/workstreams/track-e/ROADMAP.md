# Roadmap: Track E - 运行控制与运维面板层

## Milestones

- ✅ **vE.1.1** — Runtime Control Panel Foundations (completed)
- 🔄 **vE.2.1** — 全流程交互验证框架 (in progress)

---

## vE.1.1 Summary

**Goal:** Create a unified operations layer for runtime lifecycle control and expose it through a local web panel plus CLI fallback.

**Planned Phases:**
- Phase E40: Runtime Control Contracts
- Phase E41: CLI Control Surface
- Phase E42: Web Control Panel
- Phase E43: Runtime Integration And Reliability

**Contract Focus:**
- `ControlState`
- `ControlActionResult`
- `ProcessStatus`
- `ModelStatus`
- operator-facing health summary contract

---

## vE.1.1 Phases

- [x] **Phase 40: Runtime Control Contracts** - Define state/action contracts and shared runtime control service
- [x] **Phase 41: CLI Control Surface** - Expose a terminal control surface on top of the shared service
- [x] **Phase 42: Web Control Panel** - Build the first local polling-based web operations panel
- [x] **Phase 43: Runtime Integration And Reliability** - Connect restart/bootstrap/sync/logging into one reliable operator workflow

### Phase 40: Runtime Control Contracts

**Goal:** Define the shared runtime control contracts and service boundary so both CLI and web operations surfaces can consume one consistent source of truth.

**Depends on:** Nothing (first phase of vE.1.1)

**Plans:** `40-01`

---

## vE.2.1 Summary

**Goal:** Build a scenario-based process reliability test suite that validates end-to-end workflows across all layers without requiring a live Discord connection.

**Planned Phases:**
- Phase E60: Test Infrastructure & Process Health
- Phase E61: Discord Command/Adapter Layer
- Phase E62: Session / Orchestrator Layer
- Phase E63: Adventure Runtime (trigger, room, reveal)
- Phase E64: Rules Engine Flow
- Phase E65: Character / Archive Flow
- Phase E66: Model / Router Flow
- Phase E67: Narration Pipeline Flow
- Phase E68: Persistence + End-to-End Integration

**Test Fixture:**
- `fuzhe_mini.json` — 4-node vertical slice of fuzhe for deterministic 15-turn scenario testing

**Scenario Coverage:**
1. 完整开团流程 — Full session lifecycle (lobby → ready → game start → first scene → ending)
2. 多人协作流程 — Multi-player coordination, race conditions, scene round batching
3. 边界与错误恢复 — Half-state recovery, streaming interruption, smoke-check failure recovery
4. 模组呈现流程 — Module load, room switch, trigger fire, reveal policy, multi-path branching
5. 全部都要 — All of the above

**Depends on:** vE.1.1 (E43) complete

---

## vE.2.1 Phases

- [ ] **Phase 60: Test Infrastructure & Process Health** — FakeInteraction factory, model mock fixtures, VCR.py setup, pytest-bdd scaffolding
- [x] **Phase 61: Discord Command/Adapter Layer** — Command handlers, channel enforcement, session binding gates
- [x] **Phase 62: Session / Orchestrator Layer** — Campaign lifecycle, join/ready/leave, multi-user state sync
- [ ] **Phase 63: Adventure Runtime** — fuzhe_mini load, trigger chains, room transitions, reveal gates, consequence verification
- [ ] **Phase 64: Rules Engine Flow** — COC checks, SAN rolls, combat resolution, pushed rolls
- [ ] **Phase 65: Character / Archive Flow** — Character creation, profile projection, archive persistence
- [ ] **Phase 66: Model / Router Flow** — Intent classification, turn plan generation, buffering, multi-user routing
- [ ] **Phase 67: Narration Pipeline Flow** — Prompt construction, streaming output, KP/player visibility separation
- [ ] **Phase 68: Persistence + End-to-End Integration** — DB recovery, full 15-turn scenario, Chaos lobby stress test

### Phase 60: Test Infrastructure & Process Health

**Goal:** Establish the test infrastructure foundation — FakeInteraction factory, model mock strategy, VCR.py replay fixtures, and pytest-bdd scaffolding — so all subsequent phases can build reliable scenario tests on top.

**Depends on:** Nothing (first phase of vE.2.1)

**Plans:** `60-01`

### Phase 61: Discord Command/Adapter Layer

**Goal:** Validate the Discord command layer independently using FakeInteraction — /bind_campaign, /join, /select_profile, /ready, /load_adventure command handlers and their session binding gates.

**Depends on:** E60

**Plans:** `61-01`

### Phase 62: Session / Orchestrator Layer

**Goal:** Validate campaign lifecycle flows: bind → join → select_profile → ready → load_adventure across multiple players, verifying SessionStore state transitions and phase changes.

**Depends on:** E61

**Plans:** `62-01`

### Phase 63: Adventure Runtime

**Goal:** Load fuzhe_mini.json, verify trigger chains fire correctly, room transitions update state, reveal gates enforce visibility, and consequence chains produce expected state changes.

**Depends on:** E62

**Plans:** `63-01`

### Phase 64: Rules Engine Flow

**Goal:** Validate COC rule flows — skill checks, SAN damage, combat round resolution, pushed rolls — in the context of the fuzhe_mini adventure.

**Depends on:** E63

**Plans:** `64-01`

### Phase 65: Character / Archive Flow

**Goal:** Validate character creation, profile projection into campaign, and archive persistence across session boundaries.

**Depends on:** E62

**Plans:** `65-01`

### Phase 66: Model / Router Flow

**Goal:** Validate intent classification, turn plan generation, and message buffering for single and multi-user scenarios.

**Depends on:** E60

**Plans:** `66-01`

### Phase 67: Narration Pipeline Flow

**Goal:** Validate narration prompt construction, streaming output delivery, and KP vs player visibility separation.

**Depends on:** E66

**Plans:** `67-01`

### Phase 68: Persistence + End-to-End Integration

**Goal:** Run the complete 15-turn fuzhe_mini scenario end-to-end with all layers wired, plus a Chaos lobby stress test with 5 concurrent users.

**Depends on:** E67, E65, E64, E63

**Plans:** `68-01`

## Progress Table

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| 60. Test Infrastructure & Process Health | 0/1 | Planned | — |
| 61. Discord Command/Adapter Layer | 1/1 | ✓ Complete | — |
| 62. Session / Orchestrator Layer | 1/1 | ✓ Complete | — |
| 63. Adventure Runtime | 0/1 | Planned | — |
| 64. Rules Engine Flow | 0/1 | Planned | — |
| 65. Character / Archive Flow | 0/1 | Planned | — |
| 66. Model / Router Flow | 0/1 | Planned | — |
| 67. Narration Pipeline Flow | 0/1 | Planned | — |
| 68. Persistence + End-to-End Integration | 0/1 | Planned | — |

---

*Last updated: 2026-03-29 for milestone vE.2.1*
