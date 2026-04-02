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

- Most recently completed milestone: `vC.1.2`
- Active milestone: `vC.1.3`
- Primary track: `Track C - Discord 交互层`
- Goal: Make campaign/adventure/session state legible in Discord and make message handling reasons explicit to players and operators through logic-first visibility contracts and reusable surfaces


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
- logic-first canonical visibility state for campaign, adventure, session, waiting reasons, routing outcomes, and existing player state snapshots
- player-facing shared status surfaces in play contexts
- short player-facing handling reasons when messages are ignored, buffered, or handled differently
- separate KP/operator operational visibility surface with session ops, adventure state, player status, and routing diagnostics
- activity-ready core contracts so future Discord Activity UI can reuse the same visibility model
- current-only campaign/adventure identity visibility rather than broad cross-campaign browsing

**Primary Track**
- Track C - Discord 交互层

**Secondary Impact**
- Track A - 模组与规则运行层: current scene/location, waiting state, and canonical runtime summaries exposed for visibility surfaces
- Track B - 人物构建与管理层: existing canonical player sheet state surfaced in Discord without redefining character semantics
- Track D - 游戏呈现层: player-facing wording, explanation brevity, and presentation clarity

**Contracts Changed**
- campaign/adventure/session visibility contract
- waiting/blocker reason contract
- message routing outcome + short explanation contract
- player snapshot visibility contract
- operator/player feedback surface contract

**Migration Notes**
- build canonical visibility state first, then attach chat surfaces as one renderer
- keep the design compatible with future Discord Activity UI, but do not build Activity UI in this milestone
- surface existing HP/SAN/attribute truth only; do not turn this milestone into a character-system redesign
- keep broader listing/browsing and deep debug-only internals out of scope for this milestone


---
*Last updated: 2026-03-29 for milestone vC.1.3 C3 Campaign Surfaces And Intent Clarity*
