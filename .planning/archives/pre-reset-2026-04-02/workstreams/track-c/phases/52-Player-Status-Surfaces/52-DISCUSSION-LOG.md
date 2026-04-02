# Phase 52: Player Status Surfaces - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-29
**Phase:** 52-Player-Status-Surfaces
**Areas discussed:** 主状态入口, 信息密度, 玩家状态频道, 可见范围, 身份呈现

---

## 主状态入口

| Option | Description | Selected |
|--------|-------------|----------|
| 方案 A | 只通过命令查看状态 | |
| 方案 B | 只维护共享持久状态消息 | |
| 方案 C（推荐） | 共享持久状态消息 + 按需查看细节 | ✓ |
| 自定义 | 用户自定义变体 | |

**User's choice:** 方案 C（推荐）
**Notes:** 玩家需要默认可见的状态 surface，同时保留按需查看细节的路径。

---

## 信息密度

| Option | Description | Selected |
|--------|-------------|----------|
| 方案 1 | 超简洁 | |
| 方案 2（推荐） | 中等密度 | ✓ |
| 方案 3 | 高密度 | |
| 自定义 | 用户自定义变体 | |

**User's choice:** 方案 2（带补充）
**Notes:** 用户补充提出可以建一个新的频道放信息查询与总 panel 呈现，因此默认共享消息保持中等密度，更完整的概览可移到状态频道。

---

## 玩家状态频道

| Option | Description | Selected |
|--------|-------------|----------|
| 要，建玩家状态频道（推荐） | 建玩家可见状态频道，用于总 panel 和查询结果，但不承载 KP 深度运维信息 | ✓ |
| 先不建频道 | 只做主游戏频道状态消息 + 查询 | |
| 自定义 | 用户自定义变体 | |

**User's choice:** 要，建玩家状态频道（推荐）
**Notes:** 状态频道被正式纳入 Phase 52 范围，但要和未来 KP ops surface 保持边界。

---

## 可见范围

| Option | Description | Selected |
|--------|-------------|----------|
| 方案 1（推荐） | 自己详细，别人摘要 | ✓ |
| 方案 2 | 玩家之间默认尽量透明 | |
| 方案 3 | 只显示整体摘要 | |
| 自定义 | 用户自定义变体 | |

**User's choice:** 方案 1（带约束修正）
**Notes:** 用户先选“自己详细，别人摘要”，随后确认普通公共频道里不能对不同玩家显示不同内容，因此落地方式改为：公共频道只显示公共摘要，个人详细状态走 ephemeral / 私人查询。

---

## 身份呈现

| Option | Description | Selected |
|--------|-------------|----------|
| 方案 1 | 只用结构化标题 | |
| 方案 2 | 更偏叙事化身份说明 | |
| 方案 3（推荐） | 顶部结构化标题 + 一句短叙事说明 | ✓ |
| 自定义 | 用户自定义变体 | |

**User's choice:** 方案 3（推荐）
**Notes:** 状态 surface 顶部应快速可扫读，同时保留一条短 narrative/status line 增强氛围和上下文清晰度。

---

## the agent's Discretion

- 具体查询命令/按钮设计
- 状态频道的创建与绑定机制
- 私人详细状态的具体字段选择
- 标题与短叙事说明的文案风格

## Deferred Ideas

- KP/operator ops surface 细节放到 Phase 54
- 深度 handling reason surface 放到 Phase 53
- Activity UI 实现继续 defer
