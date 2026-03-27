# Project Summary (v1.0 -> v2.1)

## 1. Overview

This project started as a Discord-native local AI DM runtime and gradually evolved into a Discord-native local **Call of Cthulhu Keeper system**. The original goal was to let multiple real players run TRPG sessions in Discord while a local AI handled narration, NPC performance, scene control, and part of the bookkeeping. Over time, the project moved away from a generic "AI storyteller bot" and toward a more deterministic, reusable runtime built around structured module state, trigger execution, investigator data, and COC-first rules.

The key product direction is now clear: this is not a freeform chatbot pretending to be a Keeper. It is a **local multiplayer COC runtime** with a bot interface, a structured adventure engine, long-lived investigator archives, and a growing set of operator controls.

## 2. Architecture

The runtime is organized into a few major layers.

- **Discord interface**: slash commands, ordinary message intake, streaming replies, channel-role discipline, and future admin/archive channel separation.
- **Session orchestration**: campaign binding, turn coordination, player membership, role selection, archive projection, and gameplay mode routing.
- **Adventure runtime**: room graphs, mixed room/scene/event graph support, trigger trees, reveal policy, module state, and consequence chains.
- **Rules layer**: deterministic dice and COC-first checks, including percentile skill checks, success tiers, bonus/penalty dice, and sanity handling.
- **Character/archive layer**: long-lived archive profiles, conversational character creation, investigator panels, and campaign-specific projections.
- **Model layer**: a small routing model for structured decisions and a larger narrator model for Keeper prose and NPC performance.
- **Persistence/diagnostics**: SQLite-backed session state, campaign state, archive state, event logs, and runtime diagnostics.

The system intentionally keeps **narrative authority** and **state authority** separate. Models generate prose and some structured suggestions, but the canonical truth lives in rules, archive data, module state, and trigger execution.

## 3. Phases And Milestones

### v1.0 Foundations

- Built the Discord runtime, dual-model orchestration, deterministic rules baseline, persistence, diagnostics, and natural-message multiplayer flow.
- Added the first starter adventure and made Discord play feel like a real game loop instead of a pure slash-command demo.

### v1.1 Formal Module Runtime

- Introduced structured module packages.
- Shipped `mad_mansion` / `疯狂之馆` as the first official formal module.
- Made packaged-adventure state persistent and reveal-safe.

### v1.2 Playability Polish

- Added startup/ready flow, mature dice integration, and true streaming Discord output.
- Moved the system from "functional" toward "usable by real players."

### v1.3 Keeper Experience

- Added structured judgement, bounded hints, stall recovery, and stronger scene framing.
- Shifted away from generic AI narration toward more Keeper-like pacing.

### v1.4 Location-First Modeling

- Introduced room graphs and AI-first extraction drafts.
- Moved adventures away from sequence-first script order toward location-first runtime logic.

### v1.5 Trigger Engine

- Built a reusable trigger tree and consequence engine.
- Added event-log style execution traces and deterministic state updates for rolls and actions.

### v1.6 COC Pivot

- Reframed the whole project around COC/Keeper semantics.
- Added COC rule intake, local rulebook awareness, and COC-first prompts and diagnostics.

### v1.7 Complex COC Runtime

- Added investigator panels, private knowledge flow, mixed room/scene/event graphs, and the first `覆辙` sample module.
- Validated that the runtime could support asymmetrical information and more complex COC structure.

### v1.8- v1.9 Character Identity Layer

- Separated archive channels from live-play channels.
- Added a conversational COC builder.
- Split long-lived archive identities from campaign-specific projections.
- Upgraded character creation from a fixed script to an adaptive interview with richer roleplay anchors like life goal, weakness, and key past event.

### v2.0 Archive Deepening

- Began turning thin archive entries into real investigator-card-like identities.
- Added richer archive schema and stronger AI-assisted writeback for traits like specialty, career arc, and core belief.
- Added detailed archive views in Discord.

### v2.1 Delivery And Governance

- Added a local smoke-check command so "ready" means more than "tests passed."
- Began enforcing single-active-profile governance and admin-facing profile control.
- Tightened the project toward a more maintainable, shareable system.

## 4. Important Decisions

- Discord is the primary runtime surface.
- Local models remain the default inference path.
- The project prefers mature libraries and existing prior art over reinventing whole subsystems.
- Structured runtime state always wins over narrator improvisation.
- COC/Keeper semantics, not D&D semantics, are now the canonical core.
- Archive identities and campaign instances must stay separate.
- Character creation may be conversational, but numeric truth must remain bounded by explicit COC rules.
- Operational readiness must include a startup smoke check, not just unit tests.

## 5. What Has Been Built

At this point the codebase already includes:

- Discord bot runtime with slash commands and ordinary-message play
- local Ollama model split (`router` + `narrator`)
- packaged-adventure loading
- room-graph and mixed graph runtime
- trigger tree and consequence execution
- streaming narration in Discord
- COC dice and sanity checks
- persistent campaign state
- persistent archive profiles
- adaptive conversational character building
- private knowledge and role-based onboarding hooks
- two sample adventures/modules:
  - `mad_mansion`
  - `fuzhe`

## 6. Current Gaps / Tech Debt

The system is already substantial, but it is not "finished." The biggest remaining gaps are:

- Discord runtime reliability still needs stricter handoff discipline in day-to-day workflow.
- Archive/profile governance has started but is not yet complete from a user-experience perspective.
- Admin controls are still basic and need fuller auditability and clearer channel-level UX.
- Archive detail and builder writeback are improving, but not all rich answers are normalized equally well yet.
- Module authoring and extraction still need a stronger path if multiple collaborators will add new COC modules at scale.
- UI is still bot-native. If the project eventually wants truly rich per-player panels, Discord Activity is the next ceiling.

## 7. Getting Started

For a new contributor, the fastest mental model is:

1. Read `README.md`
2. Understand the split between:
   - `discord_bot`
   - `orchestrator`
   - `adventures`
   - `rules`
   - `coc`
3. Run tests with `uv run pytest -q`
4. Run the local startup gate with `uv run python -m dm_bot.main smoke-check`
5. Then inspect:
   - adventure schema in `src/dm_bot/adventures/models.py`
   - archive/builder flow in `src/dm_bot/coc/`
   - Discord command surface in `src/dm_bot/discord_bot/`

This project is already beyond "prototype chatbot" territory. It is now a layered runtime whose next challenges are collaboration, module scale, governance, and operator polish.
