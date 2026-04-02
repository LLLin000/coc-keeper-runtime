# Phase 59: Admin Visibility Surfaces - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-31
**Phase:** 59-admin-visibility-surfaces
**Areas discussed:** AV-02 Detail View, AV-03 Ownership Chain, AV-04 Instance List, Admin Output Visibility

---

## AV-02: Admin Profile Detail View (AV-02)

| Option | Description | Selected |
|--------|-------------|----------|
| A: 用户目标命令 | /admin_profile_detail <用户ID> — 直接指定目标用户，简洁明确 | |
| B: 交互式选择 | /admin_profiles 显示列表后，点选查看详情 — 适合大量成员 | ✓ |
| C: 混合模式 | 有参数则直接查，无参数则交互选择 | |

**User's choice:** B - 交互式选择
**Notes:** 从 admin_profiles 列表点选查看详情，适合成员较多的场景

---

## AV-03: Ownership Chain Display Format (AV-03)

| Option | Description | Selected |
|--------|-------------|----------|
| A: 紧凑单行 | 一行显示：用户 → 档案名 [状态] → 成员角色 → 实例角色名 | ✓ |
| B: 展开多行 | 每个节点一行，带标签和详情，类似家谱结构 | |
| C: 可折叠块 | 紧凑摘要 + 可展开详情，平衡信息密度和深度 | |

**User's choice:** A - 紧凑单行
**Notes:** 格式：`Discord_user → ArchiveProfile_name [status] → Member_role → Instance_character`

---

## AV-04: Cross-Campaign Instance List (AV-04)

| Option | Description | Selected |
|--------|-------------|----------|
| A: 按战役分组 | 按 campaign 分组显示，每个战役下列出所有成员和实例 | ✓ |
| B: 扁平列表 | 简单列表：(用户, 战役, 角色名, 状态) 表格 | |
| C: 地图视图 | 以玩家为中心，列出每个玩家参与的所有战役和实例 | |

**User's choice:** A - 按战役分组
**Notes:** 每个战役下显示所有成员和活跃实例

---

## Admin Output Visibility

| Option | Description | Selected |
|--------|-------------|----------|
| A: 临时消息 | ephemeral — 只有管理员自己看到，不污染频道 | |
| B: 频道可见 | 所有成员可见，方便协作讨论 | |
| C: 混合 | 列表默认临时，详情可设置可见性 | ✓ |

**User's choice:** C - 混合
**Notes:** 列表默认临时，详情可设置可见性

---

## Decisions Summary

| ID | Decision |
|----|----------|
| G-01 | 交互式选择 - 从列表点选 |
| G-02 | 紧凑单行格式 |
| G-03 | 按战役分组 |
| G-04 | 混合可见性 |
