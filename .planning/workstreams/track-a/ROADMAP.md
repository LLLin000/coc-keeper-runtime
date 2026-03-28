# Roadmap: Track A - 模组与规则运行层

## Active Milestone

**vA.1.1** - 模组结构化基础
- **Primary Track:** Track A - 模组与规则运行层
- **Goal:** 完善现有模组结构，迁移新模组，建立触发器系统基础
- **Status:** ✅ COMPLETE (via PR #1)

---

## Next Milestone

**vA.1.2** - Group Action Resolution And Shared Scene Consequences
- **Primary Track:** Track A - 模组与规则运行层
- **Goal:** Add scene-round batching and shared consequence resolution for multiplayer play while preserving canonical module truth
- **Status:** Planned

**Planned focus:**
- scene round action batch contract
- multi-actor resolution against shared state
- shared reveal and consequence summaries
- compatibility pass for existing complex modules

---

## Queued Milestone

**vA.1.3** - Closed-Loop Event Graph Runtime
- **Primary Track:** Track A - 模组与规则运行层
- **Goal:** Generalize action-to-event-to-consequence flow into a reusable closed-loop event graph runtime so future modules can be extracted into one framework instead of patched scene by scene
- **Status:** Queued after vA.1.2

**Planned focus:**
- action intent and event entry contracts
- event reaction and consequence nodes
- spine-branch-ending runtime model
- module extraction contract for event graphs

**vA.1.4** - COC Core Rules Authority And Module Onboarding Metadata
- **Primary Track:** Track A - 模组与规则运行层
- **Goal:** Promote local COC rulebooks into canonical runtime truth for character generation, skill allocation, combat, injury, SAN, and module onboarding metadata
- **Status:** Queued after vA.1.3

**Planned focus:**
- strict attribute / age / derived-stat rules
- strict occupation + interest skill allocation rules
- combat and injury state machine
- SAN loss and insanity state handling
- module onboarding metadata for new-player-friendly session starts

---

## vA.1.1 Phases (COMPLETE)

- [x] **Phase 1: 凄夜的游乐场迁移** - 结构化新模组 ✅
- [x] **Phase 2: 疯狂之馆增强** - 触发器扩展 + 结局增加 ✅
- [x] **Phase 3: 覆辙模组完善** - 结构扩展 ✅

### Phase 1: 凄夜的游乐场迁移

**Goal:** 将「凄夜的游乐场」模组迁移为结构化格式

**Depends on:** Nothing (first phase of vA.1.1)

**Requirements:** MOD-01, MOD-02, MOD-03

**Plans:** 1 plan
- [x] 1-01-PLAN.md — 凄夜的游乐场迁移

**Details:**
- 创建 sad_carnival.json (+702 行)
- 包含 room graph, 触发器系统, 结局条件

---

### Phase 2: 疯狂之馆增强

**Goal:** 扩展疯狂之馆的触发器系统，增加更多结局分支

**Depends on:** Phase 1

**Requirements:** MOD-04, MOD-05

**Plans:** 1 plan
- [x] 2-01-PLAN.md — 疯狂之馆增强

**Details:**
- 触发器扩展: 5 → 13
- 结局扩展: 3 → 6

---

### Phase 3: 覆辙模组完善

**Goal:** 扩展覆辙模组的结构，支持更复杂的场景图

**Depends on:** Phase 2

**Requirements:** MOD-06, MOD-07, MOD-08

**Plans:** 1 plan
- [x] 3-01-PLAN.md — 覆辙模组完善

**Details:**
- 地点扩展: 3 → 9
- 触发器扩展: 1 → 14
- 结局添加: 0 → 3

---

## Progress Table

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| 1. 凄夜的游乐场迁移 | 1/1 | ✅ Complete | 2026-03-28 |
| 2. 疯狂之馆增强 | 1/1 | ✅ Complete | 2026-03-28 |
| 3. 覆辙模组完善 | 1/1 | ✅ Complete | 2026-03-28 |

---

*Last updated: 2026-03-28 - vA.1.1 complete via PR #1*
