# Roadmap: Track E - 运行控制与运维面板层

## Milestones

- ✅ **vE.1.1** — Runtime Control Panel Foundations (completed)
- ✅ **vE.2.1** — 全流程交互验证框架 (completed)
- ✅ **vE.2.2** — 统一 Scenario-Driven E2E 验证框架 (complete)

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

## vE.2.1 Phases (All Complete)

- [x] **Phase 60: Test Infrastructure & Process Health** — FakeInteraction factory, model mock fixtures, VCR.py setup, pytest-bdd scaffolding
- [x] **Phase 61: Discord Command/Adapter Layer** — Command handlers, channel enforcement, session binding gates
- [x] **Phase 62: Session / Orchestrator Layer** — Campaign lifecycle, join/ready/leave, multi-user state sync
- [x] **Phase 63: Adventure Runtime** — fuzhe_mini load, trigger chains, room transitions, reveal gates, consequence verification
- [x] **Phase 64: Rules Engine Flow** — COC checks, SAN rolls, combat resolution, pushed rolls
- [x] **Phase 65: Character / Archive Flow** — Character creation, profile projection, archive persistence
- [x] **Phase 66: Model / Router Flow** — Intent classification, turn plan generation, buffering, multi-user routing
- [x] **Phase 67: Narration Pipeline Flow** — Prompt construction, streaming output, KP/player visibility separation
- [x] **Phase 68: Persistence + End-to-End Integration** — DB recovery, full 15-turn scenario, Chaos lobby stress test

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
| **vE.2.1** | | | |
| 60. Test Infrastructure & Process Health | 1/1 | ✓ Complete | 2026-03-30 |
| 61. Discord Command/Adapter Layer | 1/1 | ✓ Complete | — |
| 62. Session / Orchestrator Layer | 1/1 | ✓ Complete | — |
| 63. Adventure Runtime | 1/1 | ✓ Complete | — |
| 64. Rules Engine Flow | 1/1 | ✓ Complete | — |
| 65. Character / Archive Flow | 1/1 | ✓ Complete | 2026-03-29 |
| 66. Model / Router Flow | 1/1 | ✓ Complete | — |
| 67. Narration Pipeline Flow | 1/1 | ✓ Complete | — |
| 68. Persistence + End-to-End Integration | 1/1 | ✓ Complete | — |
| **vE.2.2** | | | |
| 69. Scenario Runner + RuntimeTestDriver | 1/1 | Complete    | 2026-03-30 |
| 70. Scenario DSL + Artifact Writer | 1/1 | Complete    | 2026-03-30 |
| 71. Failure Taxonomy + Contract Scenarios | 1/1 | Complete    | 2026-03-30 |
| 72. Acceptance Scenarios (Happy Path + Chaos) | 1/1 | Complete    | 2026-03-30 |

---

## Research Findings

**Confidence:** 5/10 (before fixes)

**Critical gaps identified:**
1. `fuzhe_mini.json` does not exist → fixed: create in E69
2. `deterministic_dice` requires source change → fixed: add SeededDiceRoller to E69
3. `fake_clock` not explicit → fixed: named in E69
4. `run-scenario` CLI not explicit → fixed: named in E70
5. `model_mode` strategy not defined → fixed: named in E70
6. VCR cassettes never recorded → fixed: named in E71
7. CI execution not planned → fixed: named in E72

**Research files:**
- `.planning/research/vE-2-2-milestone-review.md` — milestone design completeness audit
- `.planning/research/TESTING_GAP_ANALYSIS.md` — codebase gap audit (gap analysis)

---

## vE.2.2 Summary

**Goal:** Build a unified scenario-driven E2E verification framework with replayable artifacts and standardized failure taxonomy.

**Planned Phases:**
- Phase E69: Scenario Runner + RuntimeTestDriver (+ SeededDiceRoller, fake_clock, fuzhe_mini.json)
- Phase E70: Scenario DSL + Artifact Writer (+ run-scenario CLI, model_mode strategy)
- Phase E71: Failure Taxonomy + Contract Scenarios (+ VCR cassettes, visibility/reveal/AI contract scenarios)
- Phase E72: Acceptance Scenarios (+ happy path, fuzhe_15turn, crash recovery, chaos lobby, CI)

**Scenario Suites:**
- `acceptance/` — full session lifecycle, crash recovery, chaos lobby
- `contract/` — router/narrator AI contracts, visibility leak, reveal policy
- `chaos/` — concurrency stress, duplicate members, mid-session crash
- `recovery/` — stream interrupt resume, restart recovery

**Critical Cross-Phase Concerns (resolved):**
- `SeededDiceRoller` → added to E69 (requires source change to `rules/dice.py`)
- `fuzhe_mini.json` → created in E69 (4-node subset of `fuzhe.json`)
- `fake_clock` → explicit in E69
- `run-scenario` CLI → explicit in E70
- `model_mode` (fake_contract/recorded/live) → explicit in E70
- VCR cassettes → explicit in E71
- CI execution → explicit in E72

**Depends on:** vE.2.1 (E60-E68) complete

---

## vE.2.2 Phases

- [x] **Phase 69: Scenario Runner + RuntimeTestDriver** — Unified driver interface, SeededDiceRoller (source), fake_clock, fuzhe_mini.json creation, StepResult contracts (completed 2026-03-30)
- [x] **Phase 70: Scenario DSL + Artifact Writer** — YAML DSL, run-scenario CLI, model_mode strategy, artifact writer (json/md), scenario registry (completed 2026-03-30)
- [x] **Phase 71: Failure Taxonomy + Contract Scenarios** — FailureCode enum, visibility/reveal/AI contract scenarios, VCR cassettes, api model mode
  (completed 2026-03-30)
- [x] **Phase 72: Acceptance Scenarios** — Happy path session, fuzhe_15turn, crash recovery, chaos lobby, CI execution
  (completed 2026-03-30)

### Phase 69: Scenario Runner + RuntimeTestDriver

**Goal:** Create `RuntimeTestDriver` — a unified, Discord-free interface for driving runtime scenarios — and `ScenarioRunner` that executes YAML scenario scripts against it. Also add `SeededDiceRoller` (seeded deterministic dice) to `rules/dice.py`, add `fake_clock`, and create `fuzhe_mini.json` as a 4-node deterministic vertical slice fixture.

**Depends on:** Nothing (first phase of vE.2.2)

**Plans:** 1/1 plans complete

**Critical deliverables (explicit — not implied):**
- `RuntimeTestDriver` with methods: `run_command`, `send_message`, `snapshot_state`, `snapshot_db`, `get_outputs`, `restart_runtime`, `simulate_crash`, `simulate_stream_interrupt`
- `ScenarioRunner` — executes YAML scenario scripts
- `SeededDiceRoller` in `src/dm_bot/rules/dice.py` — accepts seed, deterministic `random.Random` for reproducible rolls
- `fake_clock` — controllable time for testing time-dependent triggers
- `fuzhe_mini.json` — 4-node subset of `fuzhe.json` for deterministic 15-turn testing
- `StepResult` contract — phase_before/after, emitted_outputs, state_diff, persistence_events

---

### Phase 70: Scenario DSL + Artifact Writer

**Goal:** Define structured YAML scenario format and implement `ArtifactWriter` that produces human-readable + machine-parseable run records. Define `run-scenario` CLI command. Define `model_mode` parameter (fake_contract | recorded | live) integration strategy.

**Depends on:** E69

**Plans:** 1/1 plans complete

**Critical deliverables (explicit):**
- Scenario DSL — YAML format for actors, steps, assertions, phase_timeline, visibility, dice_mode, model_mode, db_mode
- `run-scenario` CLI command: `uv run python -m dm_bot.main run-scenario --scenario <path> --suite <name> --all`
- `ArtifactWriter` — outputs: `run.json`, `summary.md`, `timeline.json`, `outputs_by_actor/`, `state_before.json`, `state_after.json`, `failure.json`
- Scenario registry — auto-discovers scenarios in `tests/scenarios/`
- `model_mode` strategy: `fake_contract` (FastMock), `recorded` (VCR cassettes — record first), `live` (Ollama)
- Initial state setup mechanism: each scenario gets fresh in-memory SQLite + optional seeded dice

---

### Phase 71: Failure Taxonomy + Contract Scenarios

**Goal:** Establish `FailureCode` taxonomy and write contract-level scenarios for visibility, reveal policy, and AI packet structure. Integrate VCR.py for `recorded` mode cassettes. Verify no redundancy with existing `tests/orchestrator/test_visibility.py`.

**Depends on:** E70

**Plans:** `71-01`

**Critical deliverables (explicit):**
- `FailureCode` enum: PHASE_TRANSITION_MISMATCH, COMMAND_GATE_FAILURE, REVEAL_POLICY_VIOLATION, VISIBILITY_LEAK, RULE_RESOLUTION_MISMATCH, SESSION_STATE_MISMATCH, PERSISTENCE_RECOVERY_FAILURE, STREAM_RECOVERY_FAILURE, INTENT_ROUTING_MISMATCH, NARRATION_CONTRACT_VIOLATION, CONCURRENCY_INVARIANT_FAILURE, SCENARIO_TIMEOUT, UNSUPPORTED_TEST_CONTRACT
- Visibility leak scenarios — verify gm_only state never reaches player output
- Reveal policy scenarios — verify clue reveal gates enforced correctly
- AI contract scenarios (fake_contract mode): router input packet structure, narrator prompt isolation, audience split correctness
- VCR cassette recording: record at least one real router + narrator response for `recorded` mode
- `tests/orchestrator/test_visibility.py` coverage audit — avoid duplicate work

---

### Phase 72: Acceptance Scenarios

**Goal:** Write and run acceptance scenarios that prove the system can complete a full session lifecycle, recover from crashes, and handle chaos load. Ensure scenarios run in CI (headless, no Discord, no live AI).

**Depends on:** E71

**Plans:** `72-01`

**Critical deliverables (explicit):**
- `acceptance/scen_session_happy_path.yaml` — full session lifecycle: bind→join→ready→start_session→onboarding→round→resolve→next_round
- `acceptance/scen_fuzhe_15turn.yaml` — 15-turn run using `fuzhe_mini.json` with seeded dice
- `recovery/scen_crash_recovery.yaml` — mid-scenario crash + restart, verify state recovered
- `recovery/scen_stream_interrupt.yaml` — streaming interruption + resume contract
- `chaos/scen_chaos_lobby.yaml` — 5 concurrent users, no duplicate members, correct phase transitions
- CI execution: `uv run pytest tests/scenarios/` runs all suites; `run-scenario --all` for local dev
- All artifacts written to `artifacts/scenarios/<scenario-id>/` (gitignored)

---

*Last updated: 2026-03-30 for milestone vE.2.2*
