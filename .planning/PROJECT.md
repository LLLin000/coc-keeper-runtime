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

## Active Milestones By Workstream

- `track-a`: `vA.1.2` — Group Action Resolution And Shared Scene Consequences
- `track-b`: `vB.1.4` — Identity Projection And Character Ownership
- `track-c`: `vC.1.2` — Multiplayer Session Governance
- `track-d`: `vD.1.1` — Keeper-Guided Archive Experience
- `track-e`: `vE.1.1` — Runtime Control Panel Foundations (completed foundation; follow-up milestone not yet opened)

Use each workstream's own `PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, and `STATE.md` as the source of truth for that lane. The repository-level project map describes long-lived tracks and governance, not one single active milestone.

## Current State

The project has already completed:
- a Discord-first runtime
- local dual-model orchestration
- structured COC module support
- room graphs, trigger trees, and consequence chains
- persistent investigator archives and campaign projections
- adaptive conversational builder flow
- startup smoke checks and initial profile governance

The next priority is not a single feature. It is letting collaborators and GSD-driven agents pick the right workstream and advance the next milestone without flattening the architecture.

## Constraints

- Platform: Discord-first
- Inference: local models first
- Rules source of truth: local COC rulebooks and explicit module rules
- Delivery: campaign-usable reliability matters more than speculative breadth
- Collaboration: repository-local planning must be sufficient for AI handoff

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Work should now be organized by persistent tracks rather than only by sequential feature bundles | The system is large enough that archive, runtime, Discord surface, and presentation need separate strategic lanes | `v2.2` formalized tracks in planning docs |
| Infrastructure and collaboration concerns should be global rules, not a separate product track | Smoke checks, auditability, and documentation quality apply everywhere and should not be treated as optional feature work | Global Rules added to `PROJECT.md` |
| Each workstream should carry its own active milestone and state | A repository-level single active milestone became misleading once tracks began to move independently | Repository-level planning now points contributors into per-workstream docs |

## Evolution

This file is the repository-level project map.

Update it when:
- the active milestone changes
- a new track is introduced or removed
- a new global rule becomes mandatory
- track selection guidance needs to become more explicit for collaborators

---
*Last updated: 2026-03-28 for workstream-aligned milestone governance*
