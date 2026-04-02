# Phase 58: Instance Management - Discussion Log

**Date:** 2026-03-31
**Phase:** 58
**Participants:** User, Sisyphus

## Agenda

Identify implementation decisions for Phase 58: Instance Management
Requirements: ILC-02 (retire instance), ILC-03 (select archive profile for instance)

## Discussion

### G-01: Retire Instance Behavior

**Question:** Retire 实例时应该如何处理？

**Options:**
- A: 清空字段（变成空壳状态，可重新选择 archive profile 投影）
- B: 完全删除 instance
- C: 标记 status='retired'，保留记录用于审计

**Decision:** **C** - 标记为 retired，添加 status='retired' 字段，保留记录用于审计

**Rationale:** 保留审计追踪，instance 可以后续恢复或查看历史

---

### G-02: Archive Profile as Name Source

**Question:** Archive profile 的 name 字段应该作为 character_name 吗？

**Options:**
- A: 是的，使用 archive_profile.name 作为 character_name
- B: 需要额外选择（分开两步）

**Decision:** **A** - 使用 archive_profile.name 作为 character_name

**Rationale:** 简化 UX，archive profile 的 name 已经是用户创建的角色名

---

### G-03: Profile Status Validation

**Question:** 重新选择 archive profile 时，是否需要验证 profile 状态？

**Options:**
- A: 必须是 active（只允许选择 status='active' 的 archive profile）
- B: 可以是任何存在的（允许选择 archived）

**Decision:** **A** - 必须是 active

**Rationale:** 只有 active 状态的 profile 才能在战役中使用，防止使用已归档的 profile

---

### G-04: Operation Scope

**Question:** Instance 操作的作用域？

**Options:**
- A: 当前 campaign（操作默认作用于当前频道绑定的 campaign）
- B: 指定 campaign（需要额外参数指定 campaign_id）

**Decision:** **A** - 当前 campaign

**Rationale:** 与 ILC-01 的模式保持一致，简化命令设计

---

### G-05: Governance Event Names

**Question:** Instance 操作的 governance event 操作名？

**Options:**
- A: instance_retire / instance_select
- B: instance_retire 保留，但 instance_select 复用 profile_activate

**Decision:** **A** - instance_retire / instance_select

**Rationale:** 清晰的 instance 级别操作，便于审计追踪

---

## Summary of Decisions

| ID | Decision | Choice |
|----|----------|--------|
| G-01 | Retire 行为 | C: 标记 status='retired' |
| G-02 | Name 来源 | A: archive_profile.name |
| G-03 | Profile 验证 | A: 必须是 active |
| G-04 | 操作作用域 | A: 当前 campaign |
| G-05 | Event 操作名 | A: instance_retire / instance_select |

## Next Steps

1. Create 58-CONTEXT.md with decisions
2. Run `/gsd-plan-phase 58` to create implementation plan
3. Execute plan: add status field, implement retire_instance, implement select_instance_profile
