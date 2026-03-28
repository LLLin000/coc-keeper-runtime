# Discord AI Keeper - Track D

## Track D: 游戏呈现层

Owns perceived table experience:
- Keeper-style narration boundaries
- guidance and stall recovery tone
- clue/history/panel presentation
- consequence framing
- player-facing readability and immersion

### Typical Work
- prompt shaping
- player-facing boards and summaries
- archive/game presentation contracts
- keeper-feel polish

### Out of Scope
- canonical rules truth
- archive persistence semantics as the main goal
- Discord command governance as the main goal

## Active Milestone

- Active milestone: `vD.1.1`
- Primary track: `Track D - 游戏呈现层`
- Goal: Redesign archive and builder presentation so character creation feels like a private Keeper-guided interview and player-facing archive output feels like a readable investigator board instead of a plain command transcript

## Milestone vD.1.1: D1 Keeper-Guided Archive Experience

**Goal:** Improve how archive and builder interactions feel to the player, with private-first character creation, clearer archive-channel purpose, and richer player-facing card presentation that prepares for future Discord Activity surfaces.

**Target features:**
- private-first builder experience with archive channels acting as entry and management surfaces rather than the only interview stage
- clearer archive channel role and player guidance
- richer archive/player-facing card summaries and section boards
- presentation contracts that later Activity work can reuse

**Primary Track**
- Track D - 游戏呈现层

**Secondary Impact**
- Track B - 人物构建与管理层: richer card sections and builder staging
- Track C - Discord 交互层: archive-channel flow and private/ephemeral routing

**Contracts Changed**
- `NarratorInput` (archive-facing builder guidance usage)
- player-facing archive/panel summary contract
- private-first builder presentation contract

**Migration Notes**
- do not reintroduce rules truth into presentation logic
- preserve existing archive operations while shifting the perceived experience toward a one-to-one Keeper interview
- keep the design compatible with future Discord Activity surfaces rather than hardcoding one Discord-message-only presentation forever

## Queued Milestone vD.1.2: D2 Session Boards And Keeper Scene Presentation

**Goal:** Extend presentation work beyond archive channels into live play so players can read current scene, current pressure, recent history, and clue/state summaries as coherent session boards instead of piecemeal bot messages.

**Target features:**
- player-facing campaign/adventure/session boards
- clearer scene framing and consequence summaries
- structured history/clue/current-state boards suitable for future Activity surfaces
- newcomer-friendly rules boards for:
  - minimum rules
  - combat flow
  - injury flow
  - SAN flow
- presentation contracts for multiplayer scene rounds and shared KP resolution

**Primary Track**
- Track D - 游戏呈现层

**Secondary Impact**
- Track C - Discord 交互层: command/status surfaces and where boards appear
- Track A - 模组与规则运行层: structured scene and consequence summaries

**Contracts Changed**
- player-facing session board contract
- scene summary and consequence summary presentation contract
- clue/history/current-state board layout contract

**Migration Notes**
- queue this after vD.1.1 so archive presentation and private-first builder experience are settled first
- build on structured state from Tracks A/C rather than inventing presentation-only truth
- keep all board structures Activity-ready

## Queued Milestone vD.1.3: D3 New-Player Start Pack And Rules Boards

**Goal:** Turn module intro, minimum-rules explanation, and key COC flowcharts into reusable player-facing start packs so new players can begin quickly without reading a full rulebook.

**Target features:**
- build reusable start-pack sections for:
  - what COC play is
  - today's module theme
  - recommended professions / skills / items
  - minimum rules the table needs right now
- build digestible boards/cards for:
  - attribute meaning
  - skill allocation guidance
  - combat flow
  - damage / injury flow
  - SAN and insanity flow
- support different explanation density for:
  - new-player mode
  - standard mode
  - veteran mode

**Primary Track**
- Track D - 游戏呈现层

**Secondary Impact**
- Track A - 模组与规则运行层: start packs consume canonical rules summaries and module onboarding metadata
- Track B - 人物构建与管理层: builder/finalization flows consume profession and skill guidance surfaces
- Track C - Discord 交互层: onboarding stage and where these boards are surfaced

**Contracts Changed**
- player-facing onboarding pack contract
- rules board / flowchart summary contract
- explanation-density presentation contract

**Migration Notes**
- start packs summarize canonical rules; they must not become a second source of rules truth
- prefer reusable presentation sections over module-specific narrated tutorials
- build for Discord now, but keep all sections Activity-ready

---
*Last updated: 2026-03-28 for milestone vD.1.1 D1 Keeper-Guided Archive Experience*
