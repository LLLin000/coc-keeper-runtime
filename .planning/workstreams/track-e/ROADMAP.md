# Roadmap: Track E - 运行控制与运维面板层

## Milestones

- ✅ **vE.1.1** — Runtime Control Panel Foundations (completed)

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

## Progress Table

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| 40. Runtime Control Contracts | 1/1 | Completed | 2026-03-28 |
| 41. CLI Control Surface | 1/1 | Completed | 2026-03-28 |
| 42. Web Control Panel | 1/1 | Completed | 2026-03-28 |
| 43. Runtime Integration And Reliability | 1/1 | Completed | 2026-03-28 |

---

*Last updated: 2026-03-28 for milestone vE.1.1*
