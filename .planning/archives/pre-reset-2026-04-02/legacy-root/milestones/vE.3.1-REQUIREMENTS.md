# Requirements Archive: vE.3.1 Character Lifecycle E2E

**Archived:** 2026-03-31
**Status:** SHIPPED

For current requirements, see `.planning/REQUIREMENTS.md`.

---

# Requirements: Discord AI Keeper - Track E

**Defined:** 2026-03-28
**Core Value:** Give operators one reliable place to see whether bot, API, models, sync, and smoke-check are healthy and to restart the system without guessing from Discord behavior.

## vE.1.1 Requirements (Track E)

Milestone: E1 Runtime Control Panel Foundations

### Unified Runtime State

- [ ] **CTRL-01**: System exposes one aggregated runtime state object for bot, API, model checks, sync, and smoke-check status
- [ ] **CTRL-02**: Runtime state distinguishes "process exists" from "runtime is actually ready"
- [ ] **CTRL-03**: Runtime state includes recent READY/SYNC evidence and recent failure summaries

### Unified Actions

- [ ] **ACT-01**: Operators can start, stop, and restart bot from one control layer
- [ ] **ACT-02**: Operators can start, stop, and restart API from one control layer
- [ ] **ACT-03**: Operators can restart the whole system from one control layer
- [ ] **ACT-04**: Operators can trigger smoke-check and command sync from the same control layer

### Panel Surface

- [ ] **PANEL-01**: A local web panel shows the aggregated runtime state
- [ ] **PANEL-02**: A CLI fallback exists for environments where the web panel is not being used
- [ ] **PANEL-03**: The panel shows recent log excerpts for startup/restart failures

### Reliability

- [ ] **REL-01**: Existing `smoke-check` behavior remains valid
- [ ] **REL-02**: Existing `restart-system` behavior remains valid
- [ ] **REL-03**: Actions return structured success/failure results instead of only shell output

## vE.2.1 Requirements (Track E)

Milestone: E2 全流程交互验证框架

### Test Infrastructure

- [ ] **TEST-01**: FakeInteraction factory produces fully-formed discord.Interaction/Context with nested mocks (Guild, Member, Channel)
- [ ] **TEST-02**: Model mock fixture supports Instant/Delay/Error modes, switchable per test
- [ ] **TEST-03**: VCR.py cassette recordings exist for all narration output patterns
- [ ] **TEST-04**: pytest-bdd Gherkin feature files cover combat and investigation flows

### Layer Coverage

- [ ] **DISC-01**: /bind_campaign, /join, /select_profile, /ready, /load_adventure all return correct session state changes
- [ ] **DISC-02**: Channel enforcement gates reject unauthorized commands
- [ ] **SESS-01**: Campaign lifecycle bind→join→ready→load_adventure completes without error across 3 players
- [ ] **SESS-02**: SessionPhase transitions (LOBBY→SCENE_ROUND_OPEN→COMBAT) correct under multi-user load
- [ ] **ADV-01**: fuzhe_mini.json loads and returns valid AdventurePackage
- [ ] **ADV-02**: Trigger chains fire on correct conditions and produce expected state changes
- [ ] **ADV-03**: Reveal gates correctly hide/show content based on investigation progress
- [ ] **ADV-04**: Room transitions update location_id and scene_id correctly
- [ ] **RULES-01**: COC skill checks return correct success levels (critical/success/failure/fumble)
- [ ] **RULES-02**: SAN damage applies correctly per 7th ed rules
- [ ] **RULES-03**: Combat round resolution updates HP and handles defeated state
- [ ] **CHAR-01**: Character creation flow produces valid archive profile
- [ ] **CHAR-02**: Profile projection into campaign maintains correct visibility
- [ ] **CHAR-03**: Archive persists across session boundaries
- [ ] **ROUTER-01**: Intent classification returns correct TurnMode (dm/scene/combat)
- [ ] **ROUTER-02**: Turn plan generation includes required tool_calls
- [ ] **ROUTER-03**: Message buffering handles out-of-order delivery correctly
- [ ] **NARR-01**: Narration prompts contain correct context (scene, characters, state)
- [ ] **NARR-02**: KP vs player visibility separation is enforced in output
- [ ] **PERSIST-01**: Session state survives process restart
- [ ] **PERSIST-02**: Full 15-turn scenario completes with all state persisted correctly

### Scenario Coverage

- [ ] **SCEN-01**: 完整开团流程 — lobby → ready → first scene → ending, all layers wired
- [ ] **SCEN-02**: 多人协作流程 — 5 concurrent users, race condition handling verified
- [ ] **SCEN-03**: 边界与错误恢复 — streaming interruption recovery, half-state restart
- [ ] **SCEN-04**: 模组呈现流程 — multi-path branching, consequence chains, reveal policy

## Traceability

### vE.1.1

| Requirement | Phase | Status |
|-------------|-------|--------|
| CTRL-01 | E40 | Done |
| CTRL-02 | E40 | Done |
| CTRL-03 | E40 | Done |
| ACT-01 | E41 | Done |
| ACT-02 | E41 | Done |
| ACT-03 | E43 | Done |
| ACT-04 | E43 | Done |
| PANEL-01 | E42 | Done |
| PANEL-02 | E41 | Done |
| PANEL-03 | E42 | Done |
| REL-01 | E43 | Done |
| REL-02 | E43 | Done |
| REL-03 | E40 | Done |

### vE.2.1

| Requirement | Phase | Status |
|-------------|-------|--------|
| TEST-01 | E60 | Planned |
| TEST-02 | E60 | Planned |
| TEST-03 | E60 | Planned |
| TEST-04 | E60 | Planned |
| DISC-01 | E61 | Planned |
| DISC-02 | E61 | Planned |
| SESS-01 | E62 | Planned |
| SESS-02 | E62 | Planned |
| ADV-01 | E63 | Planned |
| ADV-02 | E63 | Planned |
| ADV-03 | E63 | Planned |
| ADV-04 | E63 | Planned |
| RULES-01 | E64 | Planned |
| RULES-02 | E64 | Planned |
| RULES-03 | E64 | Planned |
| CHAR-01 | E65 | Planned |
| CHAR-02 | E65 | Planned |
| CHAR-03 | E65 | Planned |
| ROUTER-01 | E66 | Planned |
| ROUTER-02 | E66 | Planned |
| ROUTER-03 | E66 | Planned |
| NARR-01 | E67 | Planned |
| NARR-02 | E67 | Planned |
| PERSIST-01 | E68 | Planned |
| PERSIST-02 | E68 | Planned |
| SCEN-01 | E68 | Planned |
| SCEN-02 | E68 | Planned |
| SCEN-03 | E68 | Planned |
| SCEN-04 | E68 | Planned |

---
*Last updated: 2026-03-29 for vE.2.1*
