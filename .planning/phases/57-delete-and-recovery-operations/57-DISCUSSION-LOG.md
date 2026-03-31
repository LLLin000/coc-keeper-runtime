# Phase 57: Delete And Recovery Operations - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-31
**Phase:** 57-delete-and-recovery-operations
**Areas discussed:** Replace behavior, Grace period duration, Deleted profile visibility, Permanent delete trigger

---

## Replace Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Archived (推荐) | Consistent with archive operation — user action moves to archived state | ✓ |
| Replaced | Distinct semantic — auto-superseded by new profile, not manually archived | |

**User's choice:** 已归档（推荐）
**Notes:** 用户选择了与归档操作一致的语义

---

## Grace Period Duration

| Option | Description | Selected |
|--------|-------------|----------|
| 7天（推荐） | Standard grace period — users have enough time to recover, storage impact manageable | ✓ |
| 24小时 | Quick cleanup — suitable for testing or short events | |
| 30天 | Long retention — meets some compliance standards | |
| Never auto-purge | Admin manually triggers permanent delete — more control | |

**User's choice:** 7天（推荐）
**Notes:** 

---

## Deleted Profile Visibility

| Option | Description | Selected |
|--------|-------------|----------|
| 宽限期内显示（推荐） | Show in /profiles with "deleted" status — users can see recoverable profiles | ✓ |
| 完全隐藏 | Cleaner UX — users only see active/archived | |
| 始终显示 | Even after grace period show "deleted" — users know remnants exist | |

**User's choice:** 宽限期内显示（推荐）
**Notes:** 

---

## Permanent Delete Trigger

| Option | Description | Selected |
|--------|-------------|----------|
| 自动执行（推荐） | Auto-permanent delete after grace period expires — self-service, no admin overhead | ✓ |
| 管理员手动 | Admin manually permanent delete — more control, audit trail | |
| 用户确认 | User explicitly confirms permanent delete — clear action, less surprising | |

**User's choice:** 自动执行（推荐）
**Notes:** 

---

## Decisions Captured

1. **Replace → Archived**: Replacing an active profile moves the old one to "archived" state (D-05)
2. **Grace Period 7 days**: Deleted profiles remain recoverable for 7 days (D-06)
3. **Deleted Visible in Grace**: Deleted profiles show in /profiles with "deleted" status during grace period (D-07)
4. **Auto Purge**: Grace period expiration triggers automatic permanent deletion (D-08)

