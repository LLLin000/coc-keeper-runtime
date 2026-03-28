# Discord AI Keeper

## What This Is

This project is a Discord-native, local-model-first Call of Cthulhu Keeper runtime. It is not a freeform chat toy. The goal is to run real multiplayer COC sessions in Discord with structured module state, reusable rules logic, long-lived investigator archives, and AI narration that stays subordinate to canonical runtime truth.

## Core Value

Run a real multiplayer Call of Cthulhu session in Discord where a local AI Keeper can narrate, roleplay multiple characters, enforce investigation-heavy rules flow, and keep canonical module state without constant manual bookkeeping.

## Track Model

All new work must belong to exactly one primary track. Cross-track effects are allowed, but each milestone needs one clear home so GSD agents can reason about scope without mixing unrelated concerns.

### Track A: 模组与规则运行层

Owns canonical play truth:
- COC rules authority
- module schema
- room/scene/event graphs
- trigger trees and consequence chains
- reveal policy, private knowledge, endings

Typical work:
- complex module runtime
- reusable module authoring contracts
- rule resolution and state mutation

Out of scope for this track:
- Discord UX polish as the main goal
- archive UI as the main goal
- prose quality polish as the main goal

### Track B: 人物构建与管理层

Owns long-lived identity truth:
- conversational builder
- archive schema
- profile lifecycle
- campaign projection
- admin role/profile governance

Typical work:
- richer archive fields
- builder interviews
- one-active-profile rules
- profile detail surfaces and archive operations

Out of scope for this track:
- adventure runtime mechanics as the main goal
- channel routing as the main goal

### Track C: Discord 交互层

Owns the runtime surface:
- slash commands
- natural message intake
- channel roles and binding
- thread/ephemeral/DM usage
- startup and delivery checks
- future Activity integration boundaries

Typical work:
- archive/game/admin/trace channel discipline
- command visibility and guidance
- smoke checks and startup reliability

Out of scope for this track:
- canonical rules truth
- archive semantics as the main goal

### Track D: 游戏呈现层

Owns perceived table experience:
- Keeper-style narration boundaries
- guidance and stall recovery tone
- clue/history/panel presentation
- consequence framing
- player-facing readability and immersion

Typical work:
- prompt shaping
- table summaries
- presentation layouts
- keeper-feel polish

Out of scope for this track:
- canonical rules mutations
- persistence/governance mechanics as the main goal

## Global Rules

These rules apply to every track and every milestone.

1. Every milestone must declare one primary track.
2. Cross-track effects must be documented, but the milestone should still have one clear center of gravity.
3. Numeric truth, rule truth, and state truth must come from local COC rulebooks, deterministic code, or explicit module-specific rules. Prompt output is never canonical truth by itself.
4. Critical state changes must be durable and auditable. Hidden state may be selectively revealed, but it cannot exist only inside model context.
5. Delivery claims must pass local verification, including `uv run pytest -q` and `uv run python -m dm_bot.main smoke-check`.
6. New features should prefer reusable runtime primitives over one-off module hacks.
7. Planning docs and README must stay understandable to a fresh GSD agent working from the repository alone.

## Cross-Track Change Declaration

Shared contracts are stable by default, but this project still allows controlled cross-track evolution when integration work requires it.

If a milestone, implementation, or PR changes another track's interface or assumptions, it must explicitly declare:

- `Primary Track`
- `Secondary Impact`
- `Contracts Changed`
- `Migration Notes`

This means cross-track modification is allowed for integration, experimentation, or debugging, but silent breakage is not allowed.

Preferred policy:
- preserve backward compatibility where practical
- extend before replacing when practical
- if a breaking change is necessary, document the affected tracks and update planning/docs in the same change

## Track Selection Guidance

When starting a new milestone:

1. Identify the primary question being solved.
2. Map that question to one track.
3. Record any secondary impact in milestone notes instead of broadening the milestone scope.

Use these heuristics:
- If the work changes what is legally true in play, it belongs to Track A.
- If the work changes who a player is across sessions, it belongs to Track B.
- If the work changes how people operate the bot in Discord, it belongs to Track C.
- If the work changes how the table perceives the experience, it belongs to Track D.

When work genuinely spans multiple tracks:
- pick the track with the strongest ownership over the canonical behavior being changed
- record all secondary impacts explicitly
- avoid turning one milestone into a broad multi-track rewrite

## Active Milestone

- Current milestone: `vB.1.2`
- Primary track: `Track B - 人物构建与管理层`
- Goal: Expand archive and profile presentation toward a fuller COC investigator card, aligned with the sections exposed by `charSheetGenerator`

## Milestone vB.1.2: B2 Investigator Archive Card Completion

**Goal:** Upgrade long-lived investigator archives from usable profiles into fuller COC investigator cards with clearer sections, richer writeback, and cleaner long-lived identity boundaries.

**Target features:**
- Reference [COC第七版调查员人物卡生成器](https://www.cthulhuclub.com/charSheetGenerator/) for card sections worth mirroring in Discord form
- Continue treating local COC rulebooks as the rules source of truth; new card sections extend character representation, not rule truth
- Fill out richer archive sections:
  - 基础身份
  - 人物塑造
  - 经历与状态
  - 资源与装备
  - 技能与规则建议
- Improve builder writeback so interview answers land in specific character-card sections instead of only background summaries
- Strengthen archive detail and `/sheet` presentation so archives feel like persistent investigator assets rather than thin lists
- Preserve strict separation between long-lived archive truth and campaign/module instance state

## Current State

Track B has already completed:
- archive-builder normalization (`vB.1.1`)
- adaptive conversational builder flow
- archive/projection sync basics
- single-active-profile governance

The next priority is making long-lived archives feel like complete investigator cards rather than thin archive records.

## Constraints

- Platform: Discord-first
- Inference: local models first
- Rules source of truth: local COC rulebooks and explicit module rules
- Delivery: campaign-usable reliability matters more than speculative breadth
- Collaboration: repository-local planning must be sufficient for AI handoff

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Track B archive work should now be organized as persistent investigator-card evolution, not one-off archive tweaks | The project needs long-lived investigator assets that can survive across modules and collaboration sessions | `vB.1.2` focuses on archive-card completion |
| Card completeness should be informed by `charSheetGenerator`, but rules truth must still come from local COC sources | The site is a useful section/layout reference, not canonical rules truth | Track B may mirror card sections while keeping COC rules local |
| Long-lived archive truth and campaign instance truth must remain separate | Richer cards create pressure to leak module state back into archives | Track B milestones must keep projection boundaries explicit |

## Evolution

This file is the repository-level project map.

Update it when:
- the active milestone changes
- a new track is introduced or removed
- a new global rule becomes mandatory
- track selection guidance needs to become more explicit for collaborators

---
*Last updated: 2026-03-28 for milestone vB.1.2 B2 Investigator Archive Card Completion*
