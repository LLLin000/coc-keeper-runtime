# Phase 55: Profile List And Event Logging Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-31
**Phase:** 55-profile-list-and-event-logging-foundation
**Mode:** discuss
**Areas discussed:** Event Log Schema, Admin Listing Scope, Profile Listing Format, One-Instance Enforcement

---

## Event Log Schema

| Option | Description | Selected |
|--------|-------------|----------|
| 基础字段 | 时间戳、操作类型、user_id、profile_id、campaign_id — 最少信息满足审计需求 | |
| 完整字段 | 基础字段 + 操作者ID、目标详情，前后状态快照、原因/备注 | ✓ |

**User's choice:** 完整字段
**Notes:** 需要记录操作者ID（admin actions）、前后状态快照、原因备注

---

## Admin Listing Scope

| Option | Description | Selected |
|--------|-------------|----------|
| 当前战役 | 仅显示当前绑定战役中的成员档案 — 与 campaign member 关联 | ✓ |
| 全局 | 显示所有用户的档案 — 无范围限制 | |

**User's choice:** 当前战役范围
**Notes:** 管理员档案列表需要与战役成员关联

---

## Profile Listing Display Format

| Option | Description | Selected |
|--------|-------------|----------|
| 简洁摘要行 | 每行一个档案：名称 + 状态 + 简要信息 — 现有 summary_line() 模式 | |
| 完整卡片 | 每个档案完整展示 — 包含更多数值和技能信息 | ✓ |
| 混合模式 | 先显示摘要列表，详细信息需要单独命令查看 | |

**User's choice:** 完整卡片
**Notes:** 复用现有的 `detail_view()` 方法

---

## One-Instance Enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| 已是单一键 | character_instances[user_id] 已经是单一键，无需额外强制 | ✓ |
| 需要显式检查 | 在创建新实例前显式检查并拒绝，而不是直接覆盖 | |

**User's choice:** 已是单一键
**Notes:** vB.1.4 已建立单键模式

---

## Deferred Ideas

None — discussion stayed within phase scope
