---
gsd_state_version: 1.0
milestone: vB.1.1
milestone_name: B1 Archive And Builder Normalization
status: planning
active_track: track-b
stopped_at: Starting milestone vB.1.1 - archive and builder normalization with better AI summarization
last_updated: "2026-03-28T11:08:00.000Z"
last_activity: 2026-03-28 - Started milestone vB.1.1 B1 Archive And Builder Normalization
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Current Position

- Active milestone: `v2.3`
- Active track: `Track B - 人物构建与管理层`
- Current mode: Defining requirements for archive-builder normalization

## What Just Completed

`v2.2` (governance restructure) was superseded by user request to focus on Track B work.

## Milestone Context

`v2.3` focuses on:
- Tightening archive-builder mapping
- Fixing AI summarization in builder flow (AI currently just copies user input)
- Referencing standard COC character sheet sections from https://www.cthulhuclub.com/charSheetGenerator/
- Using local COC rules (C:\Users\Lin\Downloads\COC) for proper semantics

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

## Current Milestone

**vB.1.1: B1 Archive And Builder Normalization** (Active Now)
- Goal: Tighten archive-builder mapping with better AI summarization
- Reference: COC character sheet sections, local COC rules

## Next Candidate Milestones By Track

- `Track A`: `A1 Complex COC Module Runtime Stabilization`
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
*Last updated: 2026-03-28 for milestone vB.1.1 B1 Archive And Builder Normalization*
