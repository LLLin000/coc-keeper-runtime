---
gsd_state_version: 1.0
milestone: v2.2
milestone_name: GSD Track 化治理重构
status: planning
active_track: governance
stopped_at: Defining track-aware planning structure so future milestones can be chosen by layer without losing GSD continuity
last_updated: "2026-03-28T18:30:00.000Z"
last_activity: 2026-03-28 - Reframed project planning around persistent tracks and global rules
progress:
  total_phases: 39
  completed_phases: 39
  total_plans: 59
  completed_plans: 59
  percent: 100
---

# Project State

## Current Position

- Active milestone: `v2.2`
- Active track: `Governance`
- Current mode: restructure planning so any GSD agent can understand the project by reading `.planning`

## What Just Completed

`v2.1` completed the operational baseline for:
- local smoke-check delivery gating
- single-active archive profile lifecycle
- first-pass admin profile governance

That means the next step is not another feature by default. The next step is making the repository structure legible enough that collaborators can safely pick the next milestone by track.

## Active Tracks

- `Track A`: 模组与规则运行层
- `Track B`: 人物构建与管理层
- `Track C`: Discord 交互层
- `Track D`: 游戏呈现层

## Current Governance Priorities

1. Make tracks explicit in `PROJECT.md`.
2. Move future planning into track-aware `ROADMAP.md`.
3. Add track labels to milestone history in `MILESTONES.md`.
4. Keep README aligned so GitHub collaborators can follow the same structure.

## Next Candidate Milestones By Track

- `Track A`: `A1 Complex COC Module Runtime Stabilization`
- `Track B`: `B1 Archive And Builder Normalization`
- `Track C`: `C1 Channel Governance And Command Discipline Hardening`
- `Track D`: `D1 Keeper Presentation And Guidance Pass`

## Global Rules Reminder

All active and future work should respect these repository-level rules:

1. Each milestone must have one primary track.
2. Rule and state truth must come from deterministic code, local rulebooks, or explicit module rules.
3. Critical state must be durable and auditable.
4. Delivery claims require local smoke-check verification.
5. Planning docs must remain sufficient for AI handoff after a fresh fork.

## Open Local-Only Files

These files currently exist locally and are not formal project artifacts:

- `.planning/config.json`
- `bot.smoke.log`
- `run-bot-bg.cmd`
- `tmp_mansion.md`

## Resume Guidance

When resuming:

1. Read `PROJECT.md` for track definitions and global rules.
2. Read `ROADMAP.md` for the next milestone choices by track.
3. Use `MILESTONES.md` for historical context.
4. If starting a new milestone, choose one primary track before defining scope.
5. If other tracks will be touched, declare secondary impact and affected contracts explicitly.
6. Keep `v2.2` focused on governance/document structure only.

---
*Last updated: 2026-03-28 for milestone v2.2 planning restructure*
