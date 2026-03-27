# Discord AI DM

## What This Is

This project is a Discord-native Dungeons & Dragons DM system powered by local models. Multiple real players can participate in the same session, the bot acts as the DM, and the system can switch between normal DM-led play and multi-character performance scenes where the bot speaks as several NPCs or enemies.

The target is not a lightweight chat toy. It should be reliable enough to run short-to-medium campaigns with strong rules support, persistent state, and external character data connected through the simplest viable integration path.

## Core Value

Run a real multiplayer D&D session in Discord where a local AI DM can narrate, roleplay multiple characters, and enforce heavy rules flow without constant manual bookkeeping.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Multiplayer Discord sessions support multiple human players in the same campaign channel or thread.
- [ ] The DM flow supports two modes: normal DM-led narration and scene-based multi-character performance.
- [ ] The system can play multiple NPCs, enemies, or companions as distinct speaking roles in the same session.
- [ ] The rules layer supports heavy D&D flow including combat, initiative, HP, conditions, spell/rule lookup, and resource tracking.
- [ ] Character data comes from an external or importable source using the simplest viable mature integration path rather than a large custom character platform.
- [ ] The first usable release can reliably run a one-shot or short campaign with persistent game state and recoverable session context.

### Out of Scope

- Building every D&D subsystem from scratch when stable mature projects or datasets already exist — this is explicitly excluded to reduce debugging cost and delivery time.
- Telegram support in v1 — Discord is the chosen primary runtime environment.
- Full product-grade parity with mature ecosystem bots on day one — v1 should be campaign-usable, not feature-complete against every existing tool.

## Context

The system will run on Discord and use a dual-model architecture on local inference. The finalized default model split is:

- `qwen3:1.7b` for fast routing, structured intent classification, and tool decision output
- `collective-v0.1-chinese-roleplay-8b` for Chinese DM narration, NPC voice, and multi-character roleplay

This model split is chosen for local hardware fit and reliability on a machine in the class of `RTX 5060 8GB VRAM + 32GB RAM`. Larger 14B narration models remain possible later, but are not the default v1 choice because they raise latency and deployment friction on the target setup.

The project should preferentially reuse mature external components instead of inventing custom equivalents. Current candidate references include `DND5E-MCP` as an AI-facing rules/lookup skill, `5e-srd-api` as a stable SRD-backed rules data source, and `Avrae` as a reference implementation for interaction patterns and D&D automation design rather than as the core embedded runtime.

The first release should prioritize running the full Discord gameplay loop end-to-end: player input, orchestration, rule/tool invocation, state updates, and narrated DM output. External character integration should be chosen based on the lowest-friction mature option, not on brand preference.

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
| The default narrator should fit 8GB-class local GPUs | Lower deployment friction matters more than marginal prose quality gains from larger local models | `collective-v0.1-chinese-roleplay-8b` selected |
| Router and narrator should remain separate | Roleplay-tuned narration models are not trusted as the sole authority for structured tool routing | `qwen3:1.7b` router retained |

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
*Last updated: 2026-03-27 after initialization*
