# Phase 61: Integration And Polish - Discussion Log

> **Audit trail only.** Do not use as input to planning or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-01
**Phase:** 61-integration-and-polish
**Areas discussed:** Ready Gate Validation, Profile Detail Status, Test Scope

---

## Ready Gate Validation

| Option | Description | Selected |
|-------|-------------|----------|
| 更新为实例模型 (推荐) | 检查 character_instances[user_id].status == 'active' — 与Phase 58架构一致 | ✓ |
| 保留旧检查 | 继续检查 selected_profile_id OR active_character_name — 兼容旧逻辑 | |

**User's choice:** 更新为实例模型 (推荐)
**Notes:** 用中文回复

---

## Profile Detail Status

| Option | Description | Selected |
|-------|-------------|----------|
| 保持纯档案视图 | detail_view() 只显示档案内容，不显示战役上下文（当前行为） | |
| 显示实例上下文 | 同时显示该档案是否在某个战役中激活、激活状态是什么 | ✓ |

**User's choice:** 显示实例上下文
**Notes:** 用中文回复

---

## Test Scope

| Option | Description | Selected |
|-------|-------------|----------|
| E2E生命周期测试 (推荐) | 完整流程 create → archive → activate → select → ready | ✓ |
| 缺口聚焦测试 | 只测试未被现有测试覆盖的部分 | |
| 验证全部24个需求 | 确保vB.1.5所有需求都有通过的测试 | |

**User's choice:** E2E生命周期测试 (推荐)
**Notes:** 用中文回复

---

## Summary

All three gray areas discussed and resolved:
1. Ready validation → use instance model
2. Profile detail → show instance context
3. Testing → E2E lifecycle test
