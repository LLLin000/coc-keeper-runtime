# Roadmap: Track A - 模组与规则运行层

## Active Milestone

**vA.1.1** - 模组结构化基础
- **Primary Track:** Track A - 模组与规则运行层
- **Goal:** 完善现有模组结构，迁移新模组，建立触发器系统基础
- **Status:** ✅ COMPLETE (via PR #1)

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
