# Discord AI Keeper - Track C

## Track C: Discord 交互层

Owns the runtime surface:
- slash commands
- natural message intake
- channel roles and binding
- thread/ephemeral/DM usage
- startup and delivery checks
- future Activity integration boundaries

### Typical Work
- archive/game/admin/trace channel discipline
- command visibility and guidance
- smoke checks and startup reliability

### Out of Scope
- canonical rules truth
- archive semantics as the main goal

## Active Milestone

- Most recently completed milestone: `vC.1.1`
- Active milestone: `vC.1.2`
- Primary track: `Track C - Discord 交互层`
- Goal: Govern multiplayer session flow, message intake, and campaign/adventure visibility so Discord behavior is explicit instead of implicit

## Milestone vC.1.1: C1 Channel Governance And Command Discipline Hardening

**Goal:** Make channel responsibilities obvious and enforceable for players, operators, and admins.

**Target features:**
- archive/admin/trace/game channel guidance
- better wrong-channel redirects
- less command clutter in game halls

## Milestone vC.1.2: C2 Multiplayer Session Governance

**Goal:** Make multiplayer session flow explicit in Discord by adding ready-check plus admin-start, per-scene action collection and resolve stages, and clearer message-intent routing and campaign/adventure status surfaces.

**Target features:**
- session phases:
  - onboarding
  - lobby
  - awaiting_ready
  - awaiting_admin_start
  - scene_round_open
  - scene_round_resolving
  - combat
  - paused
- admin-controlled session start after all required players are ready
- structured pre-play onboarding so the table can understand:
  - what this game is
  - today's module theme
  - recommended creation scope
  - the minimum rules needed for this session
- scene-round collection so all players can submit actions before one KP resolve pass
- clearer intent routing for natural messages instead of one broad process/ignore split
- clearer visibility into current campaigns, selected adventures, ready state, and active scene

**Primary Track**
- Track C - Discord 交互层

**Secondary Impact**
- Track A - 模组与规则运行层: scene-round action batches and shared resolution contracts
- Track D - 游戏呈现层: player-facing prompts and KP output timing

**Contracts Changed**
- `ChannelRoleConfig`
- command/session routing contracts
- natural message intake classification contract
- campaign/adventure status surface

**Migration Notes**
- preserve existing single-message gameplay as a temporary fallback while session phases are introduced
- keep Discord interaction policy separate from canonical runtime truth
- stage the rollout so wrong-channel guidance and session governance stay readable to players

## Queued Milestone vC.1.3: C3 Campaign Surfaces And Intent Clarity

**Goal:** Make campaign/adventure/session state easy to understand from Discord and make message handling explainable enough that players know why a message was ignored, buffered, treated as action, or treated as rules input.

**Target features:**
- campaign and adventure listing surfaces
- current campaign/adventure/member/ready/scene visibility
- clearer intake explanations for natural messages
- more explicit user-facing feedback around why the bot did or did not react

**Primary Track**
- Track C - Discord 交互层

**Secondary Impact**
- Track A - 模组与规则运行层: current scene/location and state summaries
- Track D - 游戏呈现层: player-facing wording and summary clarity

**Contracts Changed**
- campaign/adventure status surface
- message-intent explanation surface
- operator/player feedback contracts

**Migration Notes**
- queue this after vC.1.2 so state visibility is built on top of real multiplayer session phases
- preserve wrong-channel and admin guidance from vC.1.1
- do not let UX explanations redefine canonical runtime state

---
*Last updated: 2026-03-28 for milestone vC.1.2 C2 Multiplayer Session Governance*
