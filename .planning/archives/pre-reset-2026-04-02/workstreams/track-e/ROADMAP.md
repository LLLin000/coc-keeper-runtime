# Roadmap: Track E - 运行控制与验证层

## Current Status

- **Latest milestone:** `vE.3.4` — Runtime Phase Transition Wiring
- **Status:** Completed 2026-04-02
- **Archive readiness:** ready to archive/reclassify after repository-level planning cleanup

Track E owns runtime control, scenario infrastructure, smoke-check reliability, and operator-facing verification. It does not own gameplay semantics or character lifecycle truth; it owns the surfaces that prove those systems can run and recover reliably.

---

## Completed Milestones

- ✅ **vE.3.4** — Runtime Phase Transition Wiring (completed 2026-04-02)
- ✅ **vE.3.3** — Scenario Runner Reliability
- ✅ **vE.3.2** — Gap Closure & Integration
- ✅ **vE.3.1** — Character Lifecycle E2E
- ✅ **vE.2.2** — 统一 Scenario-Driven E2E 验证框架
- ✅ **vE.2.1** — 全流程交互验证框架
- ✅ **vE.1.1** — Runtime Control Panel Foundations

---

## vE.3.4 Summary

**Goal:** Fix runtime phase transition wiring so scenario-driven verification reflects the real session lifecycle instead of getting stuck in `lobby`.

**Completed phases:**
- [x] Phase E90: Auto-Advance Lobby → Awaiting Ready
- [x] Phase E91: Ready Command Phase Transitions
- [x] Phase E92: Admin Start → Onboarding → Scene Round
- [x] Phase E93: Scenario Precondition Alignment

**Delivered outcomes:**
- session lifecycle now advances through `lobby → awaiting_ready → awaiting_admin_start → onboarding → scene_round_open`
- scenario YAML preconditions were aligned with the actual ready/onboarding contracts
- scenario verification became trustworthy enough to catch later regressions instead of masking them

Detailed plans and summaries are archived under `.planning/milestones/vE.3.4-phases/`.

---

## Next Step

Archive `vE.3.4`, then decide during workstream reclassification whether Track E should remain a standalone verification/operations lane or be split into narrower reliability and operator tracks.

---

*Last updated: 2026-04-02 after roadmap/state reconciliation*
