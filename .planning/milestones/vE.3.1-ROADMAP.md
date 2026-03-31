# Milestone vE.3.1: Character Lifecycle E2E

**Status:** Planning
**Primary Track:** Track E - 运行控制与运维面板层
**Phases:** E73-E78
**Total Plans:** 6

---

## Overview

Goal: 构建角色生命周期端到端测试，覆盖角色创建 → COC 战斗/SAN/技能检定 → 技能提升 → 下一轮的完整流程。整合新合入的 COC 规则引擎（Track A）与现有 RuntimeTestDriver 测试基础设施。

## Phases

### Phase 73: COC Derived Attributes 单元测试

**Goal:** 为 `rules/coc/derived.py` 中的 15+ 派生属性函数编写单元测试。

**Depends on:** Nothing (first phase of vE.3.1)

**Requirements:** E2E-01

**Plans:** 1 plan

- [ ] 73-01 — COC Derived Attributes 单元测试

**Details:**
- `calculate_luck(pow)` — POW × 5
- `calculate_hp(con, siz)` — (CON + SIZ) / 10
- `calculate_mp(pow)` — POW / 5
- `calculate_sanity(pow)` — POW × 5
- `calculate_move_rate(str, dex, siz, age)` — MOV 计算含年龄修正
- `calculate_build(str, siz)` — Build 评级
- `get_damage_bonus_string(build)` — DB 字符串
- `get_age_modifiers(age)` — 年龄 MOV 修正表
- `roll_characteristic()` — 3d6 rolling
- `spend_luck()` / `recover_luck()`

---

### Phase 74: COC Combat + Insanity 集成测试

**Goal:** 为战斗结算和狂气触发编写集成测试，验证伤害计算、护甲吸收、狂气后果。

**Depends on:** E73

**Requirements:** E2E-02, E2E-06

**Plans:** 2 plans

- [ ] 74-01 — COC Combat Resolution 单元测试
- [ ] 74-02 — COC Insanity 触发测试

**Details (74-01):**
- `calculate_build(str, siz)` — Build 评级验证
- `get_damage_bonus_string(build)` — DB 字符串格式
- `get_range_modifier(range)` — 距离修正表
- Major wound threshold 计算
- Armor 吸收计算
- Critical hit damage multiplier (×2 for impales)

**Details (74-02):**
- `roll_insanity_break()` — 临时狂气（Acute response）
- `roll_insanity_break()` — 无限狂气（Phobia/Mania acquisition）
- `COMMON_PHOBIAS` / `COMMON_MANIAS` 表验证
- Mythos gain 计算
- Sanity recovery 计算

---

### Phase 75: COC Experience + Skill Catalog 单元测试

**Goal:** 为技能提升系统和技能定义编写单元测试。

**Depends on:** E74

**Requirements:** E2E-04

**Plans:** 2 plans

- [ ] 75-01 — COC Experience 单元测试
- [ ] 75-02 — COC Skills + Magic Catalog 验证

**Details (75-01):**
- `get_occupational_skill_points(credit_rating)` — Credit → occupational points
- `get_interest_skill_points(int_value)` — INT → interest points
- `roll_skill_improvement(current, improvement_roll, die_roll)` — 技能提升检定
- `roll_all_skill_improvements()` — 多人技能提升
- `calculate_new_session_skill_points()` — 每回合技能点
- `OCCUPATION_SKILL_SUGGESTIONS` — 20+ 职业表验证

**Details (75-02):**
- `COC_SKILLS` dict 完整性（80+ 技能）
- `get_skills_by_category(category)` — 分类过滤
- `is_specialized_skill(skill_name)` — 专业技能检测
- `COC_SPELLS` dict 完整性（10+ 咒语）
- `Spellbook` 管理验证

---

### Phase 76: 角色创建端到端 Scenario

**Goal:** 用 scenario DSL 编写角色创建完整流程的端到端测试。

**Depends on:** E75

**Requirements:** E2E-01

**Plans:** 1 plan

- [ ] 76-01 — 角色创建 E2E Scenario

**Details:**
- Rolling characteristics（STR/DEX/CON/APP/POW/SIZ/INT/EDU）
- 派生属性计算（HP/MP/SAN/LUCK/MOV/Build/DB）
- 技能分配（occupational + interest points）
- 职业选择和技能建议
- 最终 investigator profile 就绪验证
- 断言：profile 字段完整性、值范围合法性

---

### Phase 77: 战斗 + SAN 端到端 Scenario

**Goal:** 用 scenario DSL 编写 COC 战斗和 SAN 检定的端到端测试。

**Depends on:** E76

**Requirements:** E2E-02, E2E-03, E2E-05

**Plans:** 1 plan

- [ ] 77-01 — 战斗 + SAN E2E Scenario

**Details:**
- Initiative roll（DEX×2 + 1d100）
- Fighting attack vs Dodge（opposed check）
- 伤害结算（damage + DB + armor absorption）
- Major wound threshold 验证
- SAN 检定（loss_on_success / loss_on_failure）
- 跨系统：战斗伤害 → SAN 损失 → 狂气检定链

---

### Phase 78: 技能提升 + 跨系统 Scenario

**Goal:** 用 scenario DSL 编写技能提升和完整角色生命周期的端到端测试。

**Depends on:** E77

**Requirements:** E2E-04, E2E-05

**Plans:** 1 plan

- [ ] 78-01 — 技能提升 + 完整生命周期 Scenario

**Details:**
- Post-session skill improvement roll（1d100 < skill → +1d10）
- Occupational + interest points 分配
- Credit Rating 变化
- 下一轮 investigator 更新验证
- 完整链条：session end → skill improvement → next session → combat → SAN damage

---

## Progress Table

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| **vE.3.1** | | | |
| 73. COC Derived Attributes | 1/1 | Planned | — |
| 74. COC Combat + Insanity | 2/2 | Planned | — |
| 75. COC Experience + Skill Catalog | 2/2 | Planned | — |
| 76. Character Creation E2E | 1/1 | Planned | — |
| 77. Combat + SAN E2E | 1/1 | Planned | — |
| 78. Skill Improvement + Lifecycle | 1/1 | Planned | — |

---

## Requirements Coverage

| Requirement | Phase | Status |
|------------|-------|--------|
| E2E-01: 角色创建端到端 | 73, 76 | Planned |
| E2E-02: COC 战斗端到端 | 74, 77 | Planned |
| E2E-03: COC SAN 端到端 | 74, 77 | Planned |
| E2E-04: COC 技能提升端到端 | 75, 78 | Planned |
| E2E-05: 跨系统集成 | 77, 78 | Planned |
| E2E-06: 疯狂系统端到端 | 74 | Planned |

---

## Key Accomplishments (planned)

1. 15+ 派生属性函数有单元测试覆盖
2. 10+ 经验/技能提升函数有单元测试覆盖
3. 战斗结算和狂气触发有集成测试覆盖
4. 角色创建全流程端到端场景可运行
5. 战斗 + SAN 跨系统场景可运行
6. 完整角色生命周期端到端可运行

---

*For current project status, see .planning/workstreams/track-e/ROADMAP.md*
