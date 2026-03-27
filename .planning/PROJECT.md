# Discord AI DM

## What This Is

This project is a Discord-native Dungeons & Dragons DM system powered by local models. Multiple real players can participate in the same session, the bot acts as the DM, and the system can switch between normal DM-led play and multi-character performance scenes where the bot speaks as several NPCs or enemies.

The target is not a lightweight chat toy. It should be reliable enough to run short-to-medium campaigns with strong rules support, persistent state, and external character data connected through the simplest viable integration path.

## Core Value

Run a real multiplayer D&D session in Discord where a local AI DM can narrate, roleplay multiple characters, and enforce heavy rules flow without constant manual bookkeeping.

## Requirements

### Validated

- ✓ Discord bot can run a bound multiplayer campaign in one channel with slash-command setup and local-model orchestration — v1.0 Phases 1-5
- ✓ Router and narrator are separated so structured decisions and final prose do not share authority — v1.0 Phase 1
- ✓ Deterministic rules, combat state, persistence, diagnostics, natural message intake, and a starter packaged adventure exist as the current baseline — v1.0 Phases 2-5
- ✓ The system can load a formal structured adventure package with reusable schema, state variables, triggers, reveal policy, and branching outcomes — v1.1 Phase 6
- ✓ `疯狂之馆` is the first full-length official module, playable end-to-end with room logic, countdown pressure, hidden information, and multiple endings — v1.1 Phase 7
- ✓ The AI can act as an omniscient DM for packaged modules while reveal-safe state stays gated by current discoveries and canonical module state — v1.1 Phases 6-7
- ✓ Discord play survives restarts through durable campaign bindings, restored natural-message intake, and clearer packaged-adventure status guidance — v1.1 Phase 8

### Active

- [ ] The module system supports a second formal adventure package without adding one-off runtime code for that script.
- [ ] The operator can selectively reveal secret or private information to subsets of players instead of only table-wide narration.
- [ ] The DM runtime can surface richer structured progression controls for module-specific triggers, puzzle states, and branching overrides.

### Out of Scope

- Building every D&D subsystem from scratch when stable mature projects or datasets already exist — this is explicitly excluded to reduce debugging cost and delivery time.
- Telegram support in v1 — Discord is the chosen primary runtime environment.
- Full product-grade parity with mature ecosystem bots on day one — v1 should be campaign-usable, not feature-complete against every existing tool.
- Freeform raw-document prompting as the canonical adventure runtime — structured module data is required so the DM does not drift on hidden state and branching rules.
- A full visual adventure authoring tool in this milestone — this round is about one formal module plus reusable schema, not a general editor UI.
- NSFW-specific behavior in this milestone — module and runtime quality take precedence.

## Current State

`v1.1` shipped the first formal packaged adventure milestone. The runtime now supports structured modules with canonical state, reveal-safe narration context, and a fully encoded `疯狂之馆` package that survives bot restarts and can continue through ordinary Discord channel play.

## Context

The system will run on Discord and use a dual-model architecture on local inference. The finalized default model split is:

- `qwen3:1.7b` for fast routing, structured intent classification, and tool decision output
- `qwen3:4b-instruct-2507-q4_K_M` for Chinese DM narration, NPC voice, and multi-character roleplay with lower latency on 8GB-class local GPUs

This model split is chosen for local hardware fit and reliability on a machine in the class of `RTX 5060 8GB VRAM + 32GB RAM`. Larger narration models remain possible later, but are not the default because they raise latency and deployment friction on the target setup.

The project should preferentially reuse mature external components instead of inventing custom equivalents. Current candidate references include `DND5E-MCP` as an AI-facing rules/lookup skill, `5e-srd-api` as a stable SRD-backed rules data source, and `Avrae` as a reference implementation for interaction patterns and D&D automation design rather than as the core embedded runtime.

The first release proved the core Discord gameplay loop end-to-end: player input, orchestration, rule/tool invocation, state updates, and narrated DM output. The new milestone shifts focus from runtime foundation to formal adventure packaging. `疯狂之馆` is the first target because it has strong room logic, hidden information, trigger-driven reveals, and branching endings that can force the schema to be real instead of decorative.

## Constraints

- **Platform**: Discord-first — the system must work naturally in Discord channels or threads because that is the chosen runtime surface.
- **Inference**: Local models — narration and control should run through local model infrastructure rather than a hosted LLM dependency.
- **Target Hardware**: Consumer local machine — the default stack should remain practical on `8GB`-class consumer GPUs with `32GB` system RAM.
- **Architecture**: Reuse mature projects first — stable existing tools, APIs, and datasets should be integrated before writing custom subsystems.
- **Rules Scope**: Heavy rules support in v1 — combat, initiative, HP, conditions, spells, and resource tracking are not optional side features.
- **Delivery**: First release should optimize for campaign-usable reliability over maximal scope — reducing integration and debugging cost is a priority.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Discord is the primary platform | It supports the desired multiplayer session format better than Telegram for this project | — Pending |
| The gameplay style is hybrid DM + multi-character performance | The desired experience is DM-led play with scene-based switching into NPC ensemble dialogue | — Pending |
| Multiple real players and bot-played roles are both required | The system must support real group play while also animating the world through NPCs and enemies | — Pending |
| Rules support should be heavy rather than lightweight | The goal is to reduce manual bookkeeping and allow campaign-grade play | — Pending |
| v1 should prioritize end-to-end gameplay over perfect character integration | A playable Discord session loop matters more than building an elaborate character platform first | — Pending |
| Mature external projects should be reused wherever practical | This reduces implementation risk and debugging cost | — Pending |
| The default narrator should fit 8GB-class local GPUs | Lower deployment friction matters more than marginal prose quality gains from larger local models | `qwen3:4b-instruct-2507-q4_K_M` selected |
| Router and narrator should remain separate | Roleplay-tuned narration models are not trusted as the sole authority for structured tool routing | `qwen3:1.7b` router retained |
| Formal adventures must be structured data, not raw uploaded prose | Hidden-state modules need deterministic triggers, reveal control, and reusable runtime hooks | ✓ Good |
| `疯狂之馆` is the first official module target | It is rich enough to force a real schema while still being a bounded first module | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-27 after v1.1 milestone*
