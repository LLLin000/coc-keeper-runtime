# Track A: 模组与规则运行层

## What This Is

Track A 负责 COC 规则权威和模组运行时真相。

## Core Value

Owns canonical play truth:
- COC rules authority
- module schema
- room/scene/event graphs
- trigger trees and consequence chains
- reveal policy, private knowledge, endings

## Typical Work

- complex module runtime
- reusable module authoring contracts
- rule resolution and state mutation

## Out of Scope

- Discord UX polish as the main goal
- archive UI as the main goal
- prose quality polish as the main goal

## vA.1.1 Scope

基于 PR #1 贡献者 tanlearner123 的工作：

- `sad_carnival.json` - 凄夜的游乐场结构化模组
- `mad_mansion.json` - 疯狂之馆触发器增强 + 结局扩展
- `fuzhe.json` - 覆辙模组结构化完善

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| 模组 JSON 格式 | 使用结构化 schema 包含 room graph, triggers, endings |
| 触发器系统 | 支持条件触发和后果链 |
| 地点扩展 | 支持多地点场景图 |

## Active Milestone

- Most recently completed milestone: `vA.1.1`
- Active milestone: `vA.1.2`
- Primary track: `Track A - 模组与规则运行层`
- Current goal: Add group action batching and shared scene consequence resolution so multiplayer scenes can be resolved as one coherent Keeper pass instead of one-message-at-a-time narration.

## Milestone vA.1.2: A2 Group Action Resolution And Shared Scene Consequences

**Goal:** Extend the canonical runtime so a scene round can collect multiple player actions, resolve them together, and emit one structured consequence pass for shared reveals, trigger chains, and Keeper narration.

**Target features:**
- define a scene-round action batch contract that Track C can collect against
- resolve multiple player actions against shared room/scene/event state in one pass
- emit shared consequence and reveal outputs without duplicating contradictory narration
- remain compatible with existing complex modules such as `mad_mansion` and `fuzhe`

**Primary Track**
- Track A - 模组与规则运行层

**Secondary Impact**
- Track C - Discord 交互层: scene round collection and admin-start flows will consume the new batch contract
- Track D - 游戏呈现层: player-facing summaries and KP narration will consume shared consequence outputs

**Contracts Changed**
- `ModuleState`
- `TriggerExecutionResult`
- `RuleResolutionResult`
- new scene-round group action input/output contract

**Migration Notes**
- preserve single-actor resolution as a compatible fallback while multiplayer batching is introduced
- keep canonical state truth in Track A; Track C may collect actions but must not become the rules authority
- do not force all modules to adopt special-case multiplayer hooks; prefer reusable runtime primitives

## Queued Milestone vA.1.3: A3 Closed-Loop Event Graph Runtime

**Goal:** Build a reusable closed-loop event graph runtime so future modules are extracted into the framework instead of receiving module-specific action/trigger patches.

**Target features:**
- define action intent contracts that translate player language into reusable event-entry types
- define event reaction nodes that can emit:
  - direct feedback
  - clarification
  - roll requests
  - state changes
  - clue changes
  - follow-on events
- define a spine/branch/ending runtime model so modules can support freedom of action without losing mainline progression
- define extraction contracts so future modules are adapted to the framework instead of hardcoding bespoke scene behavior

**Primary Track**
- Track A - 模组与规则运行层

**Secondary Impact**
- Track C - Discord 交互层: message intake and scene-round collection will route into the new action-entry contract
- Track D - 游戏呈现层: player-facing guidance and consequence presentation will consume structured event reactions

**Contracts Changed**
- `AdventureSchema`
- action intent / event entry contract
- event reaction / consequence node contract
- spine-branch-ending runtime contract

**Migration Notes**
- do not re-specialize around `mad_mansion` or `fuzhe`; use them only as validation cases
- keep `vA.1.2` focused on multiplayer batch resolution and let `vA.1.3` own the generalized event-graph framework
- future module extraction should target the framework rather than inventing scene-specific heuristics first

## Queued Milestone vA.1.4: A4 COC Core Rules Authority And Module Onboarding Metadata

**Goal:** Promote the local COC rulebooks into explicit runtime authority for character generation, skill allocation, combat, injury, and SAN handling, while extending module contracts with onboarding metadata that supports faster and safer new-player starts.

**Target features:**
- codify canonical COC 7e rules for:
  - attribute generation
  - age adjustments and EDU improvement
  - derived stats such as HP, MP, SAN, MOV, DB, and Build
- codify occupation skill points, interest skill points, credit-rating ranges, and specialization boundaries as reusable contracts
- codify combat truth for:
  - DEX order
  - dodge / fight back / fighting maneuvers
  - prepared firearms and cover
  - extreme-success / impale handling
  - major wounds, dying, stabilization, and recovery
- codify SAN truth for:
  - sanity rolls
  - 5+ loss follow-up
  - daily cumulative loss
  - temporary and indefinite insanity thresholds
- extend module extraction/runtime contracts with onboarding metadata:
  - recommended professions
  - recommended skills
  - recommended items
  - new-player notes
  - rules scope

**Primary Track**
- Track A - 模组与规则运行层

**Secondary Impact**
- Track B - 人物构建与管理层: legal sheet finalization must consume canonical generation/allocation rules
- Track C - Discord 交互层: session onboarding and campaign surfaces will expose module onboarding metadata
- Track D - 游戏呈现层: player-facing rules boards and minimum-rules explanations will consume codified summaries

**Contracts Changed**
- `RuleResolutionResult`
- COC character generation / derived-stat contracts
- combat, injury, and SAN state contracts
- module onboarding metadata contract

**Migration Notes**
- local COC PDFs remain the canonical rule source; helper articles may shape onboarding flow but must not override rules
- preserve simplified helpers only as temporary compatibility shims
- do not bury combat/injury/SAN truth inside presentation prompts or module-specific heuristics

---

_See main PROJECT.md for full project context._
