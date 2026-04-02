# Phase 51: Campaign Status Visibility - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-29
**Phase:** 51-Campaign-Status-Visibility
**Areas discussed:** Contract shape, Waiting / blocker reasons, Player snapshot boundary

---

## Contract shape

| Option | Description | Selected |
|--------|-------------|----------|
| 方案 A | 一个大而平的统一状态对象 | |
| 方案 B（推荐） | 顶层 VisibilitySnapshot + campaign/adventure/session/waiting/players/routing 六个明确子块 | ✓ |
| 方案 C | 完全拆成多个独立 contract，不做统一快照 | |
| 自定义 | 用户自定义变体 | |

**User's choice:** 方案 B（推荐）
**Notes:** 用户接受 logic-first 方向，选择统一顶层快照但内部明确分块，便于后续玩家面板、KP ops surface 和未来 Activity 复用同一逻辑层。

---

## Waiting / blocker reasons

| Option | Description | Selected |
|--------|-------------|----------|
| 方案 1 | 只存纯文本原因 | |
| 方案 2（推荐） | 保留稳定 reason code，同时带短展示文案和少量结构化字段 | ✓ |
| 方案 3 | 只存结构化字段，不带展示文案 | |
| 自定义 | 用户自定义变体 | |

**User's choice:** 方案 2（推荐）
**Notes:** 用户接受 reason code + short text + metadata 的组合，以支持后续不同 renderer 共享逻辑但保留展示灵活性。

---

## Player snapshot boundary

| Option | Description | Selected |
|--------|-------------|----------|
| 方案 1 | 只保留最小参与状态，不带 HP/SAN/属性 | |
| 方案 2（推荐） | 参与状态 + 角色名 + 现有 canonical 的 HP/SAN/少量关键属性，只读展示 | ✓ |
| 方案 3 | 把技能、日志、更多角色数据也纳入 Phase 51 visibility core | |
| 自定义 | 用户自定义变体 | |

**User's choice:** 方案 2（推荐）
**Notes:** 用户明确希望可见性层包含现有 canonical 的 HP / SAN / 少量关键属性，但不希望借此扩张成角色系统重构。

---

## the agent's Discretion

- 具体字段命名与嵌套深度
- campaign 与 adventure 的精确层级组织
- 哪些额外属性可算“少量关键属性”
- routing short text 的生成时机（存储 vs 生成）

## Deferred Ideas

- 玩家共享状态 surface 细节放到 Phase 52
- 玩家 handling reasons surface 细节放到 Phase 53
- KP/operator ops surface 细节放到 Phase 54
- Discord Activity UI 实现放到后续阶段
- 角色系统语义重构不在本 phase
