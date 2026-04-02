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

- Most recently completed milestone: `vB.1.4`
- Active milestone: `vB.1.5`
- Primary track: `Track B - 人物构建与管理层`
- Current goal: Build the operator and player-facing governance layer so active, archived, replaced, and deleted character states are manageable, reviewable, and understandable in Discord.

## Milestone vB.1.3: B3 Interview-To-Sheet Character Creation

**Goal:** Evolve the builder from "adaptive archive interview" into a full two-stage character creation loop: first interview and shape a believable person, then summarize, map, and finalize that person into a legal COC investigator card using rule-bounded generation and dice.

**Target features:**
- Split builder into two explicit stages:
  - interview stage
  - card finalization stage
- Keep the interview stage Keeper-like and dynamic:
  - start from one-line concept
  - ask 5-7 targeted follow-up questions
  - avoid giant generic prompts
- Make interview output richer than raw archive notes:
  - produce a structured character portrait
  - capture goal, weakness, belief, past event, important ties, specialities, and other card-relevant long-lived identity
- Add a rule-mapping stage that converts interview results into:
  - occupation candidates
  - skill bias suggestions
  - age/education-aware finishing hints
  - COC-bounded adjustments and recommendations
- Add a finalization stage that uses COC rules and dice to determine the actual sheet rather than letting the model invent numbers
- Keep archive truth and sheet finalization related but distinct:
  - interview shapes the person
  - rules and dice determine the legal card

**Primary Track**
- Track B - 人物构建与管理层

**Secondary Impact**
- Track D - 游戏呈现层: builder tone and summary readability
- Track C - Discord 交互层: builder flow and archive-channel interactions

**Contracts Changed**
- `BuilderSession`
- builder interview slot coverage and completion criteria
- archive writeback staging before final sheet generation
- future card-finalization contract between Track B and Track A rule resolution

**Migration Notes**
- Preserve current builder and archive compatibility during the transition
- Treat the interview phase and the sheet-finalization phase as additive structure, not a rewrite of archive semantics
- Keep local COC rulebooks as the only source of rule truth; interview output can influence recommendations, not invent rule math

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
| Track B archive work should now be organized as persistent investigator-card evolution, not one-off archive tweaks | The project needs long-lived investigator assets that can survive across modules and collaboration sessions | `vB.1.2` focused on archive-card completion |
| Card completeness should be informed by `charSheetGenerator`, but rules truth must still come from local COC sources | The site is a useful section/layout reference, not canonical rules truth | Track B may mirror card sections while keeping COC rules local |
| Long-lived archive truth and campaign instance truth must remain separate | Richer cards create pressure to leak module state back into archives | `vB.1.4` will harden campaign instance ownership and projection boundaries |

## Evolution

This file is the workstream-level project map.

Update it when:
- the active milestone changes
- a new track is introduced or removed
- a new global rule becomes mandatory
- track selection guidance needs to become more explicit for collaborators

---
## Milestone vB.1.4: B4 Identity Projection And Character Ownership

**Goal:** Strengthen the identity chain from Discord user to archive profile to campaign member to campaign character instance so multiplayer sessions have deterministic ownership, ready gates, and admin separation.

**Target features:**
- define explicit contracts for:
  - `discord_user`
  - `archive_profile`
  - `campaign_member`
  - `campaign_character_instance`
- require an explicit selected profile/instance before a player can ready into a campaign
- prevent owner/admin fallbacks from being mistaken as player identity during onboarding or scene play
- keep one active campaign instance per player per campaign, with clear auditing and governance

**Primary Track**
- Track B - 人物构建与管理层

**Secondary Impact**
- Track C - Discord 交互层: join/ready/session flows will consume the stricter ownership model

**Contracts Changed**
- `ArchiveProfile`
- `CampaignProjection`
- campaign member/profile binding semantics
- active instance ownership rules

**Migration Notes**
- preserve existing archive records while introducing stronger campaign-instance binding
- do not allow convenience fallbacks to silently choose the wrong character for a player
- keep owner/admin governance explicit rather than overloading player identity paths

## Current Milestone: vB.1.5 Character Lifecycle And Governance Surface

**Goal:** Build the operator and player-facing governance layer on top of explicit identity ownership so active, archived, replaced, and deleted character states are manageable, reviewable, and understandable in Discord.

**Target features:**
- richer lifecycle operations for long-lived archive profiles and campaign character instances
- clearer player-facing visibility into:
  - active profile
  - archived profiles
  - selected campaign instance
- clearer admin-facing visibility into all player characters and ownership state
- audit-friendly management actions for activation, archival, replacement, deletion, and recovery

**Primary Track**
- Track B - 人物构建与管理层

**Secondary Impact**
- Track C - Discord 交互层: archive/admin channel command behavior and redirects
- Track D - 游戏呈现层: player-facing summaries and ownership clarity

**Contracts Changed**
- `ArchiveProfile`
- admin lifecycle operation contracts
- archive/profile status surface

**Migration Notes**
- build lifecycle UI on a stable identity chain (vB.1.4 foundation)
- preserve one-active-profile-by-default as the baseline policy
- keep governance changes auditable and explicit rather than silent

---

## Queued Milestone vB.1.6: B6 COC-Legal Character Finalization And New-Player Modes

**Goal:** Turn builder output into a full legal investigator-sheet finalization system that supports both strict canonical COC generation and a clearly bounded quick-start mode for new players.

**Target features:**
- consume Track A's canonical generation/allocation rules instead of ad-hoc numeric finishing
- support a strict standard creation path:
  - canonical attribute generation
  - age adjustments
  - derived stats
  - occupation and interest skill allocation
- support a clearly labeled quick-start/new-player path:
  - controlled attribute arrays or KP-approved presets
  - recommended professions, skills, and starter items from module onboarding metadata
  - shorter path to a legal playable sheet without pretending to be the canonical method
- explain to players where each numeric result came from:
  - rules
  - dice
  - chosen profession
  - optional quick-start constraints

**Primary Track**
- Track B - 人物构建与管理层

**Secondary Impact**
- Track A - 模组与规则运行层: finalization consumes canonical generation/allocation contracts
- Track D - 游戏呈现层: player-facing finalization summaries and newcomer card guidance
- Track C - Discord 交互层: onboarding and builder flows may expose standard vs quick-start creation modes

**Contracts Changed**
- `BuilderSession`
- character finalization contract
- archive profile writeback for canonical vs quick-start provenance

**Migration Notes**
- quick-start must remain clearly marked as an onboarding aid, not a silent replacement of canonical rules
- preserve the interview-to-sheet flow as the narrative front-end while replacing the numeric back-end with stricter rule-bound finalization
- keep module-specific recommendations data-driven through onboarding metadata rather than hardcoding per-module builder logic

## Queued Milestone vB.1.6: B6 COC-Legal Character Finalization And New-Player Modes

**Goal:** Turn builder output into a full legal investigator-sheet finalization system that supports both strict canonical COC generation and a clearly bounded quick-start mode for new players.

**Target features:**
- consume Track A's canonical generation/allocation rules instead of ad-hoc numeric finishing
- support a strict standard creation path:
  - canonical attribute generation
  - age adjustments
  - derived stats
  - occupation and interest skill allocation
- support a clearly labeled quick-start/new-player path:
  - controlled attribute arrays or KP-approved presets
  - recommended professions, skills, and starter items from module onboarding metadata
  - shorter path to a legal playable sheet without pretending to be the canonical method
- explain to players where each numeric result came from:
  - rules
  - dice
  - chosen profession
  - optional quick-start constraints

**Primary Track**
- Track B - 人物构建与管理层

**Secondary Impact**
- Track A - 模组与规则运行层: finalization consumes canonical generation/allocation contracts
- Track D - 游戏呈现层: player-facing finalization summaries and newcomer card guidance
- Track C - Discord 交互层: onboarding and builder flows may expose standard vs quick-start creation modes

**Contracts Changed**
- `BuilderSession`
- character finalization contract
- archive profile writeback for canonical vs quick-start provenance

**Migration Notes**
- quick-start must remain clearly marked as an onboarding aid, not a silent replacement of canonical rules
- preserve the interview-to-sheet flow as the narrative front-end while replacing the numeric back-end with stricter rule-bound finalization
- keep module-specific recommendations data-driven through onboarding metadata rather than hardcoding per-module builder logic

---
*Last updated: 2026-03-28 for milestone vB.1.4 B4 Identity Projection And Character Ownership*
