# Milestone vE.3.1: Character Lifecycle E2E

**Status:** Planning
**Primary Track:** Track E - 运行控制与运维面板层
**Goal:** 覆盖角色构建到跑团全流程的端到端测试，整合 COC 规则引擎与现有测试基础设施。
**Depends on:** vE.2.2 (E69-E72) complete

---

## Background

vE.2.2 合入了 tanlearner123 的 COC 规则引擎（`rules/coc/skills.py`、`rules/coc/combat.py`、`rules/coc/sanity.py`、`rules/coc/magic.py`、`rules/coc/derived.py`、`rules/coc/experience.py`），但这批代码只有部分集成测试。`GAP_ANALYSIS.md` 识别出以下 HIGH 严重度缺口：

| 模块 | 缺口 |
|------|------|
| `rules/coc/derived.py` | 15+ 派生属性函数无单元测试 |
| `rules/coc/experience.py` | 10+ 经验/技能提升函数无单元测试 |
| `rules/coc/sanity.py` | 狂气触发（临时/无限狂气）无测试 |

---

## Scope

### In Scope
1. **角色创建流程** — 从 rolling characteristics 到 investigator 就绪
2. **跑团流程** — 战斗 + 调查 + SAN 检定的端到端
3. **技能提升流程** — post-session 技能提升 + 下一轮
4. **跨系统集成** — 战斗伤害 → SAN 损失 → 技能提升的完整链条

### Out of Scope
- 实际 Discord 交互（全部用 RuntimeTestDriver + fake_contract）
- 实际 LLM 调用（全部用 FastMock）
- D&D 规则相关（D&D 战斗已经在 tests/test_rules_engine.py 中覆盖）

---

## Requirements

### E2E-01: 角色创建端到端
- 角色创建 → 派生属性计算（HP/MP/SAN/LUCK/MOV/Build/Damage Bonus）
- 验证 `COCInvestigatorProfile` 与 `CharacterRecord.coc` 的一致性

### E2E-02: COC 战斗端到端
- initiative → Fighting/Shooting/Brawl 检定 → 伤害结算 → DB 计算 → 护甲吸收
- 验证 damage bonus 字符串生成正确

### E2E-03: COC SAN 端到端
- SAN 检定 → 成功/失败 → SAN 损失应用 → Mythos gain
- 验证 sanity_loss 返回值与规则一致

### E2E-04: COC 技能提升端到端
- 技能检定成功 → improvement roll → 技能值增加
- 验证 Credit Rating → occupational points → interest points 的完整链条

### E2E-05: 跨系统集成
- 战斗伤害触发 SAN 损失
- SAN 损失触发狂气检定
- 狂气检定触发临时/无限狂气后果

### E2E-06: 疯狂系统端到端
- 临时狂气（Acute）和无限狂气（Indefinite）的触发与后果

---

## Test Architecture

### 纯函数单元测试（pytest）
用于：`derived.py`、`experience.py`、`magic.py`、`skill catalog`

这些是纯函数，有确定性输出，适合用 `SeededDiceRoller` 做精确断言。

### 端到端场景测试（scenario DSL + pytest）
用于：角色创建流程、战斗流程、技能提升流程

用 `RuntimeTestDriver` + `fake_contract` 模式驱动，模拟真人跑团的完整流程。

### 集成测试（pytest）
用于：跨系统交互、疯狂触发后果

用 `RuntimeTestDriver` 端到端跑，验证系统间的数据流正确。

---

## Test Files to Create

| 文件 | 类型 | 内容 |
|------|------|------|
| `tests/test_coc_derived.py` | pytest | 15+ 派生属性函数单元测试 |
| `tests/test_coc_experience.py` | pytest | 10+ 经验/技能提升函数单元测试 |
| `tests/test_coc_insanity.py` | pytest | 狂气触发后果测试 |
| `tests/test_coc_skills_catalog.py` | pytest | 80+ 技能定义验证 |
| `tests/test_coc_magic_catalog.py` | pytest | 10+ 咒语定义验证 |
| `tests/test_coc_combat_resolution.py` | pytest | DB 计算、护甲吸收测试 |
| `tests/scenarios/lifecycle/scen_character_creation.yaml` | DSL | 角色创建 E2E |
| `tests/scenarios/lifecycle/scen_combat_flow.yaml` | DSL | 战斗流程 E2E |
| `tests/scenarios/lifecycle/scen_skill_improvement.yaml` | DSL | 技能提升 E2E |

---

## Dependency Chain

```
E73 (derived tests)
    ↓
E74 (combat + insanity tests)    ← E73 产出被使用
    ↓
E75 (experience tests)
    ↓
E76 (character creation scenario)
    ↓
E77 (combat E2E scenario)
    ↓
E78 (skill improvement + cross-system scenario)
```

---

## Key Technical Constraints

- **SeededDiceRoller**: 所有 dice 相关测试必须使用 seeded roller，保证可复现性
- **fake_contract 模式**: 所有端到端场景使用 FastMock，不调用真实 LLM
- **无 Discord 依赖**: 全部通过 RuntimeTestDriver 的命令接口驱动
- **无网络依赖**: 全部本地运行
