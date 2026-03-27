# Discord AI Keeper

## What This Is

This project is a Discord-native Call of Cthulhu keeper system powered by local models. Multiple real players can participate in the same session, the bot acts as the Keeper, and the runtime manages investigation flow, hidden information, scene pressure, consequence chains, and multi-character performance inside Discord.

The target is not a lightweight chat toy. It should be reliable enough to run short-to-medium COC modules with strong rules support, persistent state, reusable structured module data, and operator-facing control surfaces that keep the Keeper logic deterministic.

## Core Value

Run a real multiplayer Call of Cthulhu session in Discord where a local AI Keeper can narrate, roleplay multiple characters, enforce COC-style investigation and sanity pressure, and keep canonical module state without constant manual bookkeeping.

## Requirements

### Validated

- ✓ Discord bot can run a bound multiplayer campaign in one channel with slash-command setup and local-model orchestration — v1.0 Phases 1-5
- ✓ Router and narrator are separated so structured decisions and final prose do not share authority — v1.0 Phase 1
- ✓ Deterministic rules, combat state, persistence, diagnostics, natural message intake, and a starter packaged adventure exist as the current baseline — v1.0 Phases 2-5
- ✓ The system can load a formal structured adventure package with reusable schema, state variables, triggers, reveal policy, and branching outcomes — v1.1 Phase 6
- ✓ `疯狂之馆` is the first full-length official module, playable end-to-end with room logic, countdown pressure, hidden information, and multiple endings — v1.1 Phase 7
- ✓ The AI can act as an omniscient DM for packaged modules while reveal-safe state stays gated by current discoveries and canonical module state — v1.1 Phases 6-7
- ✓ Discord play survives restarts through durable campaign bindings, restored natural-message intake, and clearer packaged-adventure status guidance — v1.1 Phase 8
- ✓ Loading a packaged adventure now drives a visible ready-up flow and can auto-open the first scene once the table is ready — v1.2 Phase 9
- ✓ Dice and roll resolution now reuse a mature external engine instead of placeholder values, with command-path support for checks, saves, attacks, damage, and raw expressions — v1.2 Phase 10
- ✓ Discord play now gives clearer pending and blocked feedback through setup guidance, ready gating, and ordinary-message responsiveness improvements — v1.2 Phase 11
- ✓ Narrator output can now stream live into Discord through rate-safe chunked message edits, with fallback to finalized non-streamed replies if streaming fails — v1.2 Phase 12
- ✓ `疯狂之馆` now uses structured runtime judgement to distinguish automatic outcomes, clarification prompts, and explicit roll-needed moments before generic narration takes over — v1.3 Phase 13
- ✓ Light guidance, rescue hints, and stall recovery now come from reusable schema and runtime contracts so players get oriented without being spoon-fed solutions — v1.3 Phase 14
- ✓ Scene entry framing, pressure presentation, and consequence-facing prompts now feel more like a human Keeper while staying grounded in reusable prompt and module structures — v1.3 Phase 15
- ✓ Adventures can now be represented as room graphs with explicit locations, adjacency, and local transition text instead of only sequence-first scene chunks — v1.4 Phase 16
- ✓ The codebase now includes an AI-first, reviewable room-graph extraction draft pipeline for source scripts — v1.4 Phase 17
- ✓ `疯狂之馆` now ships with explicit location graph data and location-driven play behavior such as observing portals without forced entry and natural room returns — v1.4 Phase 18
- ✓ The runtime now includes a reusable trigger tree schema with declarative conditions, effects, and limited hook boundaries for future adventures — v1.5 Phase 19
- ✓ Trigger execution now produces persisted consequence chains, event-log entries, and table-facing summaries instead of stopping at shallow prompt text — v1.5 Phase 20
- ✓ `疯狂之馆` now migrates key investigation beats and roll outcomes through the generic trigger engine rather than only bespoke prompt logic — v1.5 Phase 21

### Active

- [ ] The next milestone should pivot the runtime from D&D-first assumptions to a COC/Keeper-first rules and asset model built around local rulebooks, pregens, and module-heavy play.

### Out of Scope

- Building every D&D subsystem from scratch when stable mature projects or datasets already exist — this is explicitly excluded to reduce debugging cost and delivery time.
- Telegram support in v1 — Discord is the chosen primary runtime environment.
- Full product-grade parity with mature ecosystem bots on day one — v1 should be campaign-usable, not feature-complete against every existing tool.
- Freeform raw-document prompting as the canonical adventure runtime — structured module data is required so the DM does not drift on hidden state and branching rules.
- A full visual adventure authoring tool in this milestone — this round is about one formal module plus reusable schema, not a general editor UI.
- NSFW-specific behavior in this milestone — module and runtime quality take precedence.

## Current State

`v1.5` completed the missing execution layer after room graphs. The runtime now supports declarative trigger definitions, consequence effects, pending-roll handoff into consequence resolution, trigger event logging, and trigger-aware extraction drafts. `疯狂之馆` uses the new engine for some of its key investigation beats so roll outcomes and actions can now unlock clues and structured aftermath instead of only producing prose.

## Current Milestone: v1.6 COC/KP 基础运行时与模组资产接入

**Goal:** Pivot the project into a COC/Keeper-first runtime that can load COC rules knowledge, investigator assets, and module-facing structures while preserving the existing Discord, room-graph, and trigger-engine foundations.

**Target features:**
- Add a reusable COC 7th runtime layer with SAN, difficulty tiers, opposed/combined checks, bonus and penalty dice, pushed rolls, and keeper-facing consequence handling.
- Build intake paths for COC assets from local rulebooks, pregenerated investigators, blank templates, and curated community references so the bot can operate on stable structured data.
- Rework prompts, schemas, and module extraction to favor Keeper-style investigation pacing, hidden truth control, and COC module portability over D&D-first assumptions.

## Context

The system will run on Discord and use a dual-model architecture on local inference. The finalized default model split is:

- `qwen3:1.7b` for fast routing, structured intent classification, and tool decision output
- `qwen3:4b-instruct-2507-q4_K_M` for Chinese DM narration, NPC voice, and multi-character roleplay with lower latency on 8GB-class local GPUs

This model split is chosen for local hardware fit and reliability on a machine in the class of `RTX 5060 8GB VRAM + 32GB RAM`. Larger narration models remain possible later, but are not the default because they raise latency and deployment friction on the target setup.

The project should preferentially reuse mature external components instead of inventing custom equivalents. Mature Discord TRPG products remain valuable references for interaction and operator design, but the new runtime should shift away from D&D-specific assumptions and toward COC/Keeper patterns grounded in the local COC rulebooks, pregenerated investigator assets, and curated reference sources such as [克苏鲁公社](https://www.cthulhuclub.com).

The first releases proved the core Discord gameplay loop end-to-end: player input, orchestration, state updates, and narrated output. The next three milestones replaced shallow prompt play with a formal module runtime, startup and streaming polish, room graphs, and a generic trigger engine. That foundation is reusable, but it still carries D&D-first language and rule assumptions. `v1.6` should turn the same architecture into a COC/Keeper runtime by centering investigation flow, hidden knowledge, sanity pressure, structured clue discovery, and COC investigator data.

## Constraints

- **Platform**: Discord-first — the system must work naturally in Discord channels or threads because that is the chosen runtime surface.
- **Inference**: Local models — narration and control should run through local model infrastructure rather than a hosted LLM dependency.
- **Target Hardware**: Consumer local machine — the default stack should remain practical on `8GB`-class consumer GPUs with `32GB` system RAM.
- **Architecture**: Reuse mature projects first — stable existing tools, APIs, and datasets should be integrated before writing custom subsystems.
- **Rules Scope**: Heavy rules support should now follow COC 7th priorities — skill checks, SAN, injuries, pressure, hidden information, and investigation consequences matter more than D&D combat breadth.
- **Delivery**: First release should optimize for campaign-usable reliability over maximal scope — reducing integration and debugging cost is a priority.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Discord is the primary platform | It supports the desired multiplayer session format better than Telegram for this project | — Pending |
| The gameplay style is hybrid Keeper + multi-character performance | The desired experience is Keeper-led play with scene-based switching into NPC ensemble dialogue | — Pending |
| Multiple real players and bot-played roles are both required | The system must support real group play while also animating the world through NPCs and enemies | — Pending |
| Rules support should be heavy rather than lightweight | The goal is to reduce manual bookkeeping and allow campaign-grade play | — Pending |
| v1 should prioritize end-to-end gameplay over perfect character integration | A playable Discord session loop matters more than building an elaborate character platform first | — Pending |
| Mature external projects and libraries should be the default implementation path | This reduces implementation risk and debugging cost; custom code should be limited to glue and small targeted optimizations | ✓ Good |
| The default narrator should fit 8GB-class local GPUs | Lower deployment friction matters more than marginal prose quality gains from larger local models | `qwen3:4b-instruct-2507-q4_K_M` selected |
| Router and narrator should remain separate | Roleplay-tuned narration models are not trusted as the sole authority for structured tool routing | `qwen3:1.7b` router retained |
| Formal adventures must be structured data, not raw uploaded prose | Hidden-state modules need deterministic triggers, reveal control, and reusable runtime hooks | ✓ Good |
| The project should now pivot to COC/Keeper-first runtime semantics | The available local rulebooks, pregens, and target module ecosystem are all COC-centric | v1.6 should replace D&D-first assumptions with COC structures |
| Local COC books and pregenerated characters are first-class project assets | They provide the canonical basis for rules, roles, and module handling | v1.6 should build extraction and intake paths around them |
| Community COC references should supplement, not replace, canonical local assets | Websites are useful for ecosystem patterns and metadata, but runtime truth must remain reviewable and local-first | v1.6 should use curated references as secondary inputs |
| `疯狂之馆` is the first official module target | It is rich enough to force a real schema while still being a bounded first module | ✓ Good |
| New runtime subsystems should reuse mature prior art where possible | This reduces debugging cost and keeps the bot aligned with proven Discord D&D workflows | `d20`-style dice integration prioritized for v1.2 |
| Live-play feel now matters more than new runtime primitives | The next milestone should polish judgement, hinting, and scene presentation before expanding breadth | `疯狂之馆` experience polish prioritized for v1.3 |
| Guidance must stay light and bounded | Players should feel oriented, not shepherded through the solution | v1.3 should add tiered hints rather than hard walkthroughs |
| Adventure runtime should be location-first, not script-order-first | Players navigate rooms and places, not paragraphs; the module model should reflect that | v1.4 should introduce room graphs and trigger trees |
| Adventure ingestion should be AI-first with human review | Manual from-scratch authoring will not scale; AI should extract structure under review | v1.4 should add room-graph extraction from source scripts |
| Room-graph migration should remain backward-compatible with the current runtime | Existing narration, persistence, and Discord flow should not be discarded to adopt location-first modeling | v1.4 integrated room graphs into the existing module runtime |
| Trigger logic should be mostly declarative with limited hook escape hatches | Pure data will not cover every module mechanic, but custom code should remain the exception | v1.5 should add a generic trigger engine with minimal hooks |
| Trigger execution should emit auditable event trails | The system needs a GM-facing control surface and reliable debugging path, not just hidden state mutation | v1.5 writes trigger effects into consequence summaries and event logs |

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
*Last updated: 2026-03-28 after milestone v1.6 kickoff*
