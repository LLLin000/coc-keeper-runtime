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

## Traceability

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

---
*Last updated: 2026-03-28 for vE.1.1*
