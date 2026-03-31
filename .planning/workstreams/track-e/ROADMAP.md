# Roadmap: Track E - 运行控制与运维面板层

## Milestones

- ✅ **vE.1.1** — Runtime Control Panel Foundations (completed)
- ✅ **vE.2.1** — 全流程交互验证框架 (completed)
- ✅ **vE.2.2** — 统一 Scenario-Driven E2E 验证框架 (complete)
- ✅ **vE.3.1** — Character Lifecycle E2E (complete)
- ✅ **vE.3.2** — Gap Closure & Integration (completed)
- 🆕 **vE.3.3** — Scenario Runner Reliability (planned)

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

- [x] **Phase 69: Scenario Runner + RuntimeTestDriver** — Unified driver interface, SeededDiceRoller (source), fake_clock, fuzhe_mini.json creation, StepResult contracts
 (completed 2026-03-30)
- [x] **Phase 70: Scenario DSL + Artifact Writer** — YAML DSL, run-scenario CLI, model_mode strategy, artifact writer (json/md), scenario registry
 (completed 2026-03-30)
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

## vE.3.1 Summary

**Goal:** 构建角色生命周期端到端测试，覆盖角色创建 → COC 战斗/SAN/技能检定 → 技能提升 → 下一轮的完整流程。整合新合入的 COC 规则引擎（Track A）与现有 RuntimeTestDriver 测试基础设施。

**Planned Phases:**
- Phase E73: COC Derived Attributes 单元测试
- Phase E74: COC Combat + Insanity 集成测试
- Phase E75: COC Experience + Skill Catalog 单元测试
- Phase E76: 角色创建端到端 Scenario
- Phase E77: 战斗 + SAN 端到端 Scenario
- Phase E78: 技能提升 + 跨系统 Scenario

**Depends on:** vE.2.2 (E69-E72) complete

---

## vE.3.1 Phases

- [x] **Phase E73: COC Derived Attributes 单元测试** — test_derived_attributes.py (75 tests): MOV/Build/DB lookup, age modifiers, sanity functions
  (completed 2026-03-30)
- [x] **Phase E74: COC Combat + Insanity 集成测试** — test_combat_and_insanity.py (56 tests): initiative, fighting, shooting, brawl, grapple, armor, sanity triggers
  (completed 2026-03-30)
- [x] **Phase E75: COC Experience + Skill Catalog 单元测试** — test_experience_and_skill_catalog.py (91 tests): skill improvement, point allocation, COC_SKILLS/COC_SPELLS catalog validation
  (completed 2026-03-30)
- [x] **Phase E76: 角色创建端到端 Scenario** — scen_character_creation.yaml: campaign bind → join → ready → start_session lifecycle
  (completed 2026-03-30)
- [x] **Phase E77: 战斗 + SAN 端到端 Scenario** — scen_combat_san.yaml: combat encounter → SAN loss → insanity triggers (TEMPORARY/INDEFINITE)
  (completed 2026-03-31)
- [x] **Phase E78: 技能提升 + 跨系统 Scenario** — skill improvement + full character lifecycle integration
  (completed 2026-03-31)

### Phase E73: COC Derived Attributes 单元测试

**Goal:** Write unit tests for COC derived attributes — MOV, Build, DB lookup tables, age modifiers, sanity system functions.

**Depends on:** E72

**Plans:** E73-01

**Critical deliverables (explicit):**
- `tests/rules/coc/test_derived_attributes.py` — 75 tests covering:
  - MOV: 3 base cases × 5 age bands = 15 combinations + minimum floor
  - Build: 6 lookup bands (-2 to +3)
  - DB: 6 lookup bands with numeric/string tuple output
  - Age modifiers: 9 age bands with min(1) enforcement
  - Sanity functions: critical(1), fumble(100), 3 insanity types

### Phase E74: COC Combat + Insanity 集成测试

**Goal:** Write integration tests for COC combat system and insanity mechanics.

**Depends on:** E73

**Plans:** E74-01

**Critical deliverables (explicit):**
- `tests/rules/coc/test_combat_and_insanity.py` — 56 tests covering:
  - Initiative rolls and turn order
  - Fighting attack (opposed check, critical/fumble, damage, impale)
  - Shooting attack (skill check, range/recoil modifiers)
  - Brawl & Grapple (unarmed damage, self-damage fumble)
  - DB & Armor integration
  - Insanity triggers (TEMPORARY/INDEFINITE)
  - Sanity recovery mechanics

### Phase E75: COC Experience + Skill Catalog 单元测试

**Goal:** Write unit tests for COC experience/skill system and validate skill/spell catalogs.

**Depends on:** E74

**Plans:** E75-01

**Critical deliverables (explicit):**
- `tests/rules/coc/test_experience_and_skill_catalog.py` — 91 tests covering:
  - Skill improvement roll (1d100 < skill → +1d10)
  - Occupational/Interest skill point allocation
  - Credit Rating & INT tables
  - 80+ skills in COC_SKILLS catalog validation
  - 20+ spells in COC_SPELLS catalog validation
  - Spell MP cost validation

### Phase E76: 角色创建端到端 Scenario

**Goal:** Write E2E scenario validating full character creation lifecycle using RuntimeTestDriver.

**Depends on:** E75

**Plans:** E76-01

**Critical deliverables (explicit):**
- `tests/scenarios/acceptance/scen_character_creation.yaml` — campaign bind → join → ready → start_session flow

### Phase E77: 战斗 + SAN 端到端 Scenario

**Goal:** Write E2E scenario validating combat → SAN → insanity chain.

**Depends on:** E76

**Plans:** E77-01

**Critical deliverables (explicit):**
- `tests/scenarios/acceptance/scen_combat_san.yaml` — combat encounter → SAN loss → insanity triggers (TEMPORARY/INDEFINITE)

### Phase E78: 技能提升 + 跨系统 Scenario

**Goal:** Write E2E scenario validating skill improvement and full character lifecycle.

**Depends on:** E77

**Plans:** E78-01

**Critical deliverables (explicit):**
- Skill improvement + full character lifecycle integration scenario

---

*Last updated: 2026-03-31 for milestone vE.3.1*


---

## vE.3.2 Summary

**Goal:** Fill critical gaps in COC integration and Discord bot functionality identified in codebase mapping.

**Planned Phases:**
- Phase E79: Skill Usage Tracking & Combat Integration
- Phase E80: Visibility Dispatcher Completion
- Phase E81: Creature Bestiary & Stats
- Phase E82: Chase Rules Implementation
- Phase E83: Archive Repository Completion
- Phase E84: Character Builder Integration
- Phase E85: Equipment System (optional)

**Gaps from Codebase Mapping:**
1. **Skill Usage Tracking** - Track skills used during combat for post-session improvement
2. **Visibility Dispatcher** - Complete Discord channel/DM sending (3 TODOs)
3. **Creature Stats/Bestiary** - Add monster stats for common COC creatures
4. **Chase Rules** - COC 7e chase mechanics
5. **Archive Repository** - Complete CRUD operations
6. **Character Builder** - Wire into RuntimeTestDriver
7. **Equipment System** - Weapon/armor database

**Depends on:** vE.3.1 (E73-E78) complete

---

## vE.3.2 Phases

- [x] **Phase E79: Skill Usage Tracking & Combat Integration** — Track skills used during combat for post-session improvement
  (completed 2026-03-31)
- [x] **Phase E80: Visibility Dispatcher Completion** — Complete Discord channel/DM sending (resolve 3 TODOs)
  (completed 2026-03-31)
- [x] **Phase E81: Creature Bestiary & Stats** — Add monster stats for common COC creatures
  (completed 2026-03-31)
- [x] **Phase E82: Chase Rules Implementation** — COC 7e chase mechanics
  (completed 2026-03-31)
- [x] **Phase E83: Archive Repository Completion** — Complete CRUD operations
  (completed 2026-03-31)
- [x] **Phase E84: Character Builder Integration** — Wire into RuntimeTestDriver
  (completed 2026-03-31)
- [x] **Phase E85: Equipment System** — Weapon/armor database (optional)
  (completed 2026-03-31)

### Phase E79: Skill Usage Tracking & Combat Integration

**Goal:** Implement skill usage tracking during combat encounters so skills used can feed into post-session improvement.

**Depends on:** E78 (vE.3.1 complete)

**Requirements:** SKILL-TRACK-01, SKILL-TRACK-02, SKILL-TRACK-03, SKILL-TRACK-04

**Success Criteria** (what must be TRUE):
1. Combat system records each skill check attempt with skill name and result
2. Session state maintains skill usage history per character per encounter
3. Post-session improvement phase can query which skills were used (and succeeded)
4. E2E scenario validates combat → skill tracking → improvement flow

**Plans:** 1 plan created
- [ ] **E79-01-PLAN.md** — Core skill tracking integration (SkillUsageTracker + combat hooks + tests)
  - Files: `src/dm_bot/orchestrator/skill_tracker.py`, `src/dm_bot/rules/coc/combat.py`, `tests/rules/coc/test_skill_tracking.py`
  - Tasks: 6 (tracker, session integration, combat hooks, RuntimeTestDriver, unit tests, E2E scenario)

### Phase E80: Visibility Dispatcher Completion

**Goal:** Complete the visibility dispatcher to actually send messages to Discord channels and DMs, resolving the 3 TODOs in visibility_dispatcher.py.

**Depends on:** E79

**Requirements:** VIS-DISP-01, VIS-DISP-02, VIS-DISP-03, VIS-DISP-04, VIS-DISP-05

**Success Criteria** (what must be TRUE):
1. Messages sent to Discord channels appear in the correct channels
2. Private messages (DMs) reach individual players
3. Group DMs work for KP-to-party communications
4. gm_only content never leaks to player channels (enforced + tested)
5. All 3 TODOs from visibility_dispatcher.py are resolved and tested

**Plans:** 1 plan created
- [ ] **E80-01-PLAN.md** — Complete visibility dispatcher with Discord integration
  - Files: `src/dm_bot/discord_bot/visibility_dispatcher.py`, `tests/discord_bot/test_visibility_dispatcher.py`
  - Tasks: 6 (public messages, private DMs, group DMs, FakeDiscordClient, unit tests, contract tests)

### Phase E81: Creature Bestiary & Stats

**Goal:** Create a bestiary system with stats for common COC creatures that integrates with combat and sanity systems.

**Depends on:** E80

**Requirements:** BESTIARY-01, BESTIARY-02, BESTIARY-03, BESTIARY-04, BESTIARY-05

**Success Criteria** (what must be TRUE):
1. Bestiary data structure supports COC creature stats (STR, CON, SIZ, etc.)
2. At least 10 common creatures defined (ghouls, deep ones, zombies, cultists, etc.)
3. Creature stats integrate with combat system (can be targets/attackers)
4. Sanity loss values are linked to creature encounters
5. Creatures can be used in fuzhe_mini adventure scenarios

**Plans:** 1 plan created
- [ ] **E81-01-PLAN.md** — Bestiary system with 10+ COC creatures
  - Files: `src/dm_bot/coc/bestiary.py`, `src/dm_bot/coc/creature.py`, `data/bestiary/creatures.json`
  - Tasks: 7 (models, instance manager, creatures.json, combat integration, sanity integration, unit tests, E2E scenario)

### Phase E82: Chase Rules Implementation

**Goal:** Implement COC 7e chase mechanics including pursuer/fleeer roles, CON rolls, and obstacle resolution.

**Depends on:** E81

**Requirements:** CHASE-01, CHASE-02, CHASE-03, CHASE-04, CHASE-05

**Success Criteria** (what must be TRUE):
1. Chase mechanics support pursuer/fleeer roles with CON-based rolls
2. Chase state tracks locations and relative positions
3. Obstacles require appropriate skill checks to overcome
4. Chase ends correctly on escape, capture, or transition to combat
5. E2E scenario validates a complete chase flow

**Plans:** 1 plan created
- [ ] **E82-01-PLAN.md** — COC 7e chase mechanics
  - Files: `src/dm_bot/rules/coc/chase.py`, `src/dm_bot/gameplay/chase.py`
  - Tasks: 5 (chase models, gameplay integration, RuntimeTestDriver, unit tests, E2E scenario)

### Phase E83: Archive Repository Completion

**Goal:** Complete the archive repository with full CRUD operations and integrate it with RuntimeTestDriver.

**Depends on:** E82

**Requirements:** ARCHIVE-01, ARCHIVE-02, ARCHIVE-03, ARCHIVE-04, ARCHIVE-05

**Success Criteria** (what must be TRUE):
1. Archive repository supports Create, Read, Update, Delete operations
2. Character profiles can be stored and retrieved
3. Campaign state can be persisted across sessions
4. Archive is fully wired into RuntimeTestDriver
5. E2E tests validate archive CRUD operations

**Plans:** 1 plan created
- [ ] **E83-01-PLAN.md** — Complete archive CRUD with persistence
  - Files: `src/dm_bot/coc/archive.py`, `src/dm_bot/persistence/store.py`
  - Tasks: 6 (update_profile, persistence methods, integration, RuntimeTestDriver, unit tests, E2E scenario)

### Phase E84: Character Builder Integration

**Goal:** Wire the character builder into RuntimeTestDriver and validate the full builder flow with E2E tests.

**Depends on:** E83

**Requirements:** BUILDER-01, BUILDER-02, BUILDER-03, BUILDER-04

**Success Criteria** (what must be TRUE):
1. Character builder is accessible through RuntimeTestDriver
2. Builder produces valid archive-compatible profiles
3. Builder validates against COC rules (point totals, skill limits)
4. E2E scenario validates full builder → archive → projection flow

**Plans:** 1 plan created
- [ ] **E84-01-PLAN.md** — Character builder RuntimeTestDriver integration
  - Files: `src/dm_bot/testing/runtime_driver.py`, `src/dm_bot/orchestrator/gameplay.py`
  - Tasks: 4 (gameplay integration, RuntimeTestDriver methods, unit tests, E2E scenario)

### Phase E85: Equipment System

**Goal:** Create an equipment database with weapons and armor that affect combat resolution.

**Depends on:** E84

**Requirements:** EQUIP-01, EQUIP-02, EQUIP-03, EQUIP-04, EQUIP-05

**Success Criteria** (what must be TRUE):
1. Weapon database includes COC 7e weapon stats (damage, range, ammo)
2. Armor database includes protection values
3. Equipment effects are applied in combat resolution
4. Basic inventory management tracks equipped items
5. Equipment can be used in scenario tests

**Plans:** 1 plan created
- [ ] **E85-01-PLAN.md** — Equipment database with weapons and armor
  - Files: `src/dm_bot/coc/equipment.py`, `data/equipment/weapons.json`, `data/equipment/armor.json`
  - Tasks: 7 (equipment models, weapons.json, armor.json, inventory system, combat integration, unit tests, E2E scenario)

---

## vE.3.3 Summary

**Goal:** Fix critical reliability issues in the scenario runner and test infrastructure so scenarios actually validate what they claim to test.

**Problems Discovered:**
1. **False-positive assertions** — 14/14 scenarios PASS despite step errors; phase_timeline never advances past `lobby`
2. **API signature mismatches** — `join_campaign(campaign_id)`, `load_adventure(adventure_slug)`, unknown commands (`get_phase`, `advance_story`, etc.)
3. **Persistence not initialized** — `no such table: campaign_sessions`, `no such table: campaign_state` in temp_sqlite mode
4. **Duration always 0ms** — timing measurement not working
5. **Output records not isolated per step** — cumulative outputs make debugging hard

**Planned Phases:**
- Phase E86: Scenario Runner Assertion Fix
- Phase E87: API Signature Alignment
- Phase E88: Persistence Initialization for Test Driver
- Phase E89: Timing + Output Isolation

**Depends on:** vE.3.2 (E79-E85) complete

---

## vE.3.3 Phases

### Phase E86: Scenario Runner Assertion Fix

**Goal:** Fix the scenario runner's assertion logic so scenarios actually fail when assertions are not met.

**Problem:** `scenario_runner.py:134-150` has assertion logic that only runs in `fail_fast` mode. Normal assertion checking is broken — phase_timeline assertions in YAML are never evaluated.

**Success Criteria:**
1. `scen_session_happy_path` FAILS until phase transitions actually happen
2. Phase timeline assertions are properly evaluated
3. State assertions (campaign_members, no_duplicate_members) are evaluated
4. Visibility assertions (public_must_include, kp_must_include) are evaluated
5. Scenarios with step errors properly report failure

**Files to modify:**
- `src/dm_bot/testing/scenario_runner.py` — assertion evaluation loop
- `tests/test_scenarios.py` — add tests for assertion behavior

### Phase E87: API Signature Alignment

**Goal:** Fix API signature mismatches between scenario YAML definitions and actual BotCommands/RuntimeTestDriver methods.

**Mismatches to fix:**
1. `join_campaign(campaign_id=...)` → actual method signature differs
2. `load_adventure(adventure_slug=...)` → actual method signature differs
3. Unknown commands: `get_phase`, `advance_story`, `move_to_location`, `interact`, `trigger_improvement_phase`

**Approach:**
- Option C: Mix — fix real bugs in API, update YAML for test-specific names

**Files to modify:**
- `src/dm_bot/discord_bot/commands.py` — add stub adventure methods
- `src/dm_bot/testing/runtime_driver.py` — resolve driver-level methods in run_command
- `tests/scenarios/**/*.yaml` — update to match actual API

**Plans:** 1 plan created
- [ ] **E87-01-PLAN.md** — API signature alignment (driver methods + YAML fixes + stubs)
  - Files: `src/dm_bot/testing/runtime_driver.py`, `src/dm_bot/discord_bot/commands.py`, `tests/scenarios/**/*.yaml`
  - Tasks: 5 (driver method resolution, YAML param fixes, stub commands, YAML cleanup, verification)

### Phase E88: Persistence Initialization for Test Driver

**Goal:** Ensure `RuntimeTestDriver` with `db_mode: temp_sqlite` creates all necessary database tables.

**Problem:** `no such table: campaign_sessions` and `no such table: campaign_state` errors in 7+ scenarios.

**Success Criteria:**
1. `temp_sqlite` mode creates all tables needed by session lifecycle
2. `campaign_sessions` table exists and is queryable
3. `campaign_state` table exists and is queryable
4. No persistence errors in any scenario run

**Files to modify:**
- `src/dm_bot/testing/runtime_driver.py` — fix `_init_temp_sqlite()` method
- `src/dm_bot/persistence/store.py` — ensure table creation is reusable

### Phase E89: Timing + Output Isolation

**Goal:** Fix duration measurement and isolate output records per step.

**Problems:**
1. All scenarios report `Duration: 0ms` — timing not working
2. Output records are cumulative across steps — step 10 contains outputs from steps 0-9

**Success Criteria:**
1. Duration accurately reflects step execution time
2. Each step's outputs only contain outputs emitted during that step
3. Artifact reports show accurate timing and isolated outputs

**Files to modify:**
- `src/dm_bot/testing/scenario_runner.py` — fix timing, isolate outputs
- `src/dm_bot/testing/runtime_driver.py` — clear output buffer per step

---

*Last updated: 2026-03-31 for milestone vE.3.3 - Scenario Runner Reliability*
