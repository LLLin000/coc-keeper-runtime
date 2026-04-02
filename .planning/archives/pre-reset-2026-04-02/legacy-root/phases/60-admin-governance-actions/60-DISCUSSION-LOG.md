# Phase 60: Admin Governance Actions - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-01
**Phase:** 60-admin-governance-actions
**Areas discussed:** Force-archive behavior, Reason requirement, Ownership reassignment, Debug status

---

## Force-Archive Behavior (AV-05, AV-06)

| Option | Description | Selected |
|--------|-------------|----------|
| 复用现有方法 | 管理员调用 archive_profile()/retire_instance()，reason 字段必填 | ✓ |
| 管理员专用方法 | 创建 admin_force_archive_profile() / admin_force_archive_instance()，独立逻辑 | |

**User's choice:** 复用现有方法
**Notes:** Admin path identified by operator_id != user_id in governance event

---

## Reason Field Requirement (AV-08)

| Option | Description | Selected |
|--------|-------------|----------|
| 必填（推荐） | reason 最少 10 字符，确保审计有实际内容 | ✓ |
| 可选但鼓励 | reason 可留空，但 bot 会提示建议填写 | |
| 自由格式 | reason 可任意长度和格式，不做限制 | |

**User's choice:** 必填（推荐）
**Notes:** Minimum 10 characters required

---

## Ownership Reassignment (AV-07)

| Option | Description | Selected |
|--------|-------------|----------|
| 变成 ADMIN（推荐） | 原 owner 保留部分权限，变成 ADMIN，防止权限真空 | ✓ |
| 变成 MEMBER | 原 owner 完全降级为普通成员 | |
| 只有 ADMIN 可转让 | Owner 不可转让，只有 ADMIN 可以发起转让，原 owner 保持 OWNER 角色 | |

**User's choice:** 变成 ADMIN（推荐）
**Notes:** Old owner becomes ADMIN, new owner receives OWNER role

---

## Debug Status (AUD-03)

| Option | Description | Selected |
|--------|-------------|----------|
| 所有事件（推荐） | 包括用户和管理员操作，便于完整审计 | ✓ |
| 仅治理事件 | 只看 lifecycle + admin 操作，过滤普通对话事件 | |
| 仅管理员操作 | 只显示 force-archive, reassign 等管理员操作 | |

**User's choice:** 所有事件（推荐）
**Notes:** Default limit 20 events, uses get_recent_events()

---

## Agent Discretion

The following decisions were left to agent discretion (user said "you decide"):
- Command naming conventions
- Error message wording
- Discord interaction flow details

## Deferred Ideas

None — discussion stayed within phase scope
