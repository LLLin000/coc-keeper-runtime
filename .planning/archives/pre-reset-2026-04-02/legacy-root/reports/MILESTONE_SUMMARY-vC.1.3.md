# Milestone vC.1.3 — 项目总结

**生成时间**: 2026-03-29
**用途**: 团队 onboarding 和项目回顾

---

## 1. 项目概述

**Discord AI DM** 是一个运行在 Discord 里的、本地模型驱动的 **Call of Cthulhu (COC) Keeper 系统**。它把 Discord、COC 规则、结构化模组运行时、长期角色档案和 AI 叙事层整合在一起，形成一个多人跑团框架。

### 核心目标
- 多个真人玩家在 Discord 里直接跑团
- AI 负责 Keeper 叙事、NPC 扮演、场景推进
- 规则、模组状态、线索揭露、后果链尽量由系统托管
- 本地模型部署，确保数据隐私和可控性

### 当前 Milestone 状态
vC.1.3 (Campaign Surfaces And Intent Clarity) 已于 **2026-03-29** 完成交付。所有 5 个阶段 (51-55) 均已实现、验证并通过审计。

---

## 2. 架构与技术决策

### 关键技术选型

| 技术选型 | 说明 | 阶段 |
|---------|------|------|
| **VisibilitySnapshot 统一可见性模型** | 定义战役/冒险/会话状态的结构化表示，与 Discord 解耦 | 51 |
| **PlayerStatusRenderer 玩家状态渲染器** | 将 VisibilitySnapshot 转换为玩家可读的状态展示 | 52 |
| **DiscordFeedbackService 临时反馈服务** | 通过 Discord DM 发送路由处理原因的临时消息 | 53 |
| **KPOpsRenderer KP 运维渲染器** | 为 KP/运营者提供高密度运维信息面板 | 54 |
| **Renderer 接口模式** | 清晰的规范状态层与渲染层分离，便于未来 Discord Activity 复用 | 55 |

### 关键设计模式

- **规范状态与渲染分离**: `VisibilitySnapshot` (纯数据) → `Renderer` (平台特定输出)
- **无 Discord 依赖的可见性层**: 所有可见性模型位于 `orchestrator/visibility.py`，零 Discord 导入
- **临时消息反馈**: 使用 Discord DM 发送处理原因，而非频道临时消息
- **路由历史追踪**: 记录最近 10 条路由决策供 KP 审查

---

## 3. 交付的阶段

| 阶段 | 名称 | 状态 | 一句话总结 |
|-----|------|------|-----------|
| 51 | Campaign Status Visibility | ✅ Complete | 定义 VisibilitySnapshot 统一模型，6 个子块 (campaign/adventure/session/waiting/players/routing) |
| 52 | Player Status Surfaces | ✅ Complete | 实现 `/status_overview`、`/status_me` 命令，玩家可见当前战役/冒险身份和等待状态 |
| 53 | Handling Reason Surfaces | ✅ Complete | 通过 Discord DM 发送简短处理原因 (≤50 字符)，支持 BUFFERED/IGNORED/DEFERRED |
| 54 | KP Ops Surfaces | ✅ Complete | 实现 `/ops_status` 命令，提供阶段/轮次/阻塞/路由历史等运维信息 |
| 55 | Activity-Ready Boundary Polish | ✅ Complete | 清理可见性层与渲染层边界，移除 Discord 导入，确保可复用性 |

---

## 4. 需求覆盖

| 需求 | 阶段 | 状态 |
|-----|------|------|
| **SURF-01**: Discord 表面读取统一可见性模型 | 51 | ✅ 已实现 |
| **SURF-02**: 显式等待/阻塞原因 | 51 | ✅ 已实现 |
| **SURF-03**: 路由结果 + 简短说明 | 51 | ✅ 已实现 |
| **SURF-04**: 暴露现有玩家快照状态 | 51 | ✅ 已实现 |
| **PLAY-01**: 玩家可见当前战役/冒险/会话身份 | 52 | ✅ 已实现 |
| **PLAY-02**: 玩家可见等待原因和待处理玩家 | 52 | ✅ 已实现 |
| **CURR-01**: 仅当前可见性，无需浏览 UI | 52 | ✅ 已实现 |
| **CURR-02**: 显式说明未激活/未加载状态 | 52 | ✅ 已实现 |
| **PLAY-03**: 简短实用的处理说明 | 53 | ✅ 已实现 |
| **PLAY-04**: 适合游戏频道的简洁内容 | 53 | ✅ 已实现 |
| **OPS-01**: KP 可见阶段/轮次/阻塞/运行时状态 | 54 | ✅ 已实现 |
| **OPS-02**: KP 可见每个玩家的 ready/submitted/pending 状态 | 54 | ✅ 已实现 |
| **OPS-03**: KP 可见路由结果，无需查看原始日志 | 54 | ✅ 已实现 |
| **ACT-01**: 可见性合约可复用 (不止 Discord) | 55 | ✅ 已实现 |
| **ACT-02**: 规范状态与渲染逻辑清晰分离 | 55 | ✅ 已实现 |

### 审计结果

| 检查项 | 状态 |
|-------|------|
| 所有阶段成功标准达成 | ✅ 通过 |
| 所有需求已处理 | ✅ 通过 |
| 无回归问题 | ✅ 通过 |
| 测试通过 | ✅ 通过 (216 测试) |
| Smoke check 通过 | ✅ 通过 |

**最终状态: PASSED**

---

## 5. 关键决策记录

| ID | 描述 | 阶段 | 理由 |
|----|------|------|------|
| D-01 | 路由反馈通过 Discord DM 发送临时消息 | 53 | 比频道临时消息更简单的集成方式 |
| D-02 | 反馈在 buffered/ignored/deferred 时立即发送 | 53 | 让玩家立即知道消息处理状态 |
| D-03 | 反馈内容 ≤50 字符 | 53 | 保持简洁，不干扰游戏流程 |
| D-04 | 每个路由结果对应不同反馈内容 | 53 | 提供具体、可操作的信息 |
| D-05 | 专用 KP/运营 ops 频道 | 54 | 与玩家信息分离，避免刷屏 |
| D-06 | 从现有 VisibilitySnapshot 渲染 | 54 | 不创建新数据结构，复用现有模型 |
| D-07 | 路由历史显示最近 10 条 | 54 | 提供足够上下文但不冗余 |

---

## 6. 技术债务与延期项目

### 本里程碑无技术债务
- 所有阶段完成时均保持清洁测试覆盖
- 无已知 bug
- 维护了适当的关注点分离

### 未来/延期想法
- 超越当前运行时上下文的战役/冒险浏览
- 更丰富的历史运营者可见性
- Discord Activity UI 实现
- 角色语义重新设计 (Track B)

---

## 7. 快速上手

### 运行项目

```powershell
# 前置检查
uv run python -m dm_bot.main preflight
uv run python -m dm_bot.main smoke-check

# 启动 bot
uv run python -m dm_bot.main run-bot

# 启动本地控制面板 (可选)
uv run python -m dm_bot.main run-control-panel
```

控制面板地址: http://127.0.0.1:8001/control-panel

### 关键目录

| 目录 | 用途 |
|------|------|
| `src/dm_bot/orchestrator/` | 核心运行时、会话编排、可见性模型 |
| `src/dm_bot/discord_bot/` | Discord 客户端、命令、消息传输 |
| `src/dm_bot/rules/` | COC 骰子、规则判定 |
| `src/dm_bot/adventures/` | 结构化模组、图结构、触发器 |

### 测试

```powershell
uv run pytest -q
```

### 首先看哪里

**新贡献者推荐顺序:**
1. 先读 `.planning/PROJECT.md` 了解 Track 和 Global Rules
2. 再读 `.planning/ROADMAP.md` 选择该 Track 的下一个 milestone
3. 用 `.planning/STATE.md` 判断当前激活的是哪条 Track

**Track C 核心入口:**
- `src/dm_bot/orchestrator/visibility.py` — 统一可见性模型
- `src/dm_bot/discord_bot/commands.py` — Discord 命令实现

---

## 8. 新增命令一览

| 命令 | 描述 | 频道 |
|------|------|------|
| `/bind_player_status_channel` | 绑定当前频道为玩家状态频道 | 任意 |
| `/status_overview` | 显示玩家状态概览 | 玩家状态 / 游戏 |
| `/status_me` | 显示个人角色状态 (私密) | 玩家状态 / 游戏 |
| `/bind_ops_channel` | 绑定当前频道为 KP 运维频道 | 任意 |
| `/ops_status` | 显示 KP 运维状态 | 运维频道 |

---

## 9. 创建的文件

### Phase 51: Visibility Core Contracts
- `src/dm_bot/orchestrator/visibility.py` — VisibilitySnapshot 及子模型
- `tests/orchestrator/test_visibility.py` — 可见性测试

### Phase 52: Player Status Surfaces
- `src/dm_bot/orchestrator/player_status_renderer.py` — PlayerStatusRenderer
- `src/dm_bot/discord_bot/commands.py` — status_overview, status_me 命令
- `src/dm_bot/discord_bot/channel_enforcer.py` — PLAYER_STATUS 频道类型

### Phase 53: Handling Reason Surfaces
- `src/dm_bot/discord_bot/feedback.py` — DiscordFeedbackService
- `tests/test_feedback_delivery.py` — 反馈投递测试

### Phase 54: KP Ops Surfaces
- `src/dm_bot/orchestrator/kp_ops_renderer.py` — KPOpsRenderer
- `src/dm_bot/orchestrator/routing_history.py` — RoutingHistoryStore
- `src/dm_bot/discord_bot/commands.py` — bind_ops_channel, ops_status 命令
- `tests/orchestrator/test_kp_ops_renderer.py` — 15 个测试

### Phase 55: Activity-Ready Boundary Polish
- `.planning/workstreams/track-c/phases/55-Activity-Ready-Boundary-Polish/RENDERER_INTERFACE.md` — 渲染器接口模式文档

---

## Stats

- **时间线**: 2026-03-29 (单日完成)
- **阶段**: 5/5 完成
- **测试**: 216 passed, 3 warnings
- **提交**: 14+ commits (详见 git log)
- **主要提交**:
  - `973b53d` — docs(vC.1.3): add milestone planning artifacts
  - `b3145c7` — feat(track-c): implement Phase 51 Visibility Core Contracts
  - `ff00851` — feat(track-c): implement player status surfaces (Phase 52)
  - `91cf223` — feat(phase-53): Create DiscordFeedbackService
  - `cb24b63` — feat(ops): create KPOpsRenderer

---

*本文档由 GSD 自动化生成*
