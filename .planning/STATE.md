---
gsd_state_version: 1.0
milestone: v1.6
milestone_name: COC/KP 基础运行时与模组资产接入
status: defining requirements
stopped_at: Started milestone v1.6 from local COC rulebooks, pregens, templates, and curated COC references
last_updated: "2026-03-28T15:05:00.000Z"
last_activity: 2026-03-28 - Milestone v1.6 started
progress:
  total_phases: 24
  completed_phases: 21
  total_plans: 53
  completed_plans: 47
  percent: 88
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-27)

**Core value:** Run a real multiplayer Call of Cthulhu session in Discord where a local AI Keeper can narrate, roleplay multiple characters, and enforce investigation-heavy rules flow without constant manual bookkeeping.
**Current focus:** Defining v1.6 to pivot the runtime into a COC/Keeper-first system based on local rulebooks, pregens, templates, and reusable module semantics

## Current Position

Phase: Not started (defining requirements)
Plan: -
Status: Defining requirements
Last activity: 2026-03-28 - Milestone v1.6 started

Progress: [████████░░] 88%

## Performance Metrics

**Velocity:**

- Total plans completed: 17
- Average duration: -
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 3 | - | - |
| 2 | 3 | - | - |
| 3 | 3 | - | - |
| 4 | 2 | - | - |
| 5 | 2 | - | - |
| 19 | 2 | - | - |
| 20 | 2 | - | - |
| 21 | 2 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: Stable

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Phase 1: Discord-first runtime remains the primary execution surface for v1.
- Phase 2: One mature low-friction character import path is preferred over a custom sheet platform.
- Phase 2: Deterministic rules authority and 2014 SRD-only scope are fixed v1 guardrails.
- Phase 4: Campaign usability depends on persistence, replayability, and recovery rather than feature breadth.
- Phase 9 target: adventure loading should become a guided ready-up and DM opening flow.
- Phase 10 target: placeholder rolls should be replaced with a mature dice engine, not a custom parser.
- Phase 11 target: Discord should show progress during long DM turns and ordinary message handling should be more transparent.
- Phase 12 target: Ollama narrator output should stream live into Discord through chunked edits with safe fallback.
- Phase 13 delivered structured runtime judgements for direct scene interactions, including automatic outcomes, clarification prompts, and explicit roll-needed prompts.
- Phase 14 delivered reusable light/rescue hint tiers and stall recovery driven by module metadata rather than freeform narrator guesswork.
- Phase 15 delivered stronger scene entry framing, pressure presentation, and return-to-choice pacing for `疯狂之馆`, with reusable hooks for later modules.
- Phase 16 target: adventure runtime should become location-first through room graphs, local interactables, and explicit adjacency.
- Phase 17 target: source scripts should be AI-extracted into room graphs, trigger trees, and reveal-safe runtime drafts.
- Phase 18 target: `疯狂之馆` should migrate into the new room-graph format and improve live navigation and consequence flow.
- Phase 16 delivered location-aware runtime state, adjacency, and room-graph schema support.
- Phase 17 delivered reviewable AI extraction drafts for room graphs and trigger summaries.
- Phase 18 delivered the first location-first migration of `疯狂之馆`, including natural portal observation and room returns.
- Phase 19 delivered a generic chain-capable trigger schema with mostly declarative nodes and limited hook escape hatches.
- Phase 20 delivered runtime trigger execution so actions and rolls now cause auditable consequence chains.
- Phase 21 migrated `疯狂之馆` key progress beats onto the generic trigger engine and verified reusable consequence flow.

### Pending Todos

None yet.

### Roadmap Evolution

- Roadmap now extends through Phases 22-24 for milestone v1.6.

### Blockers/Concerns

- Character import source must stay low-friction and mature; do not expand into a sheet platform.
- Rules and narration boundaries must stay strict so models never become the source of truth for state mutations.
- Dice parsing should be integrated from a mature external library to reduce debugging cost.
- Streaming transport must not become the source of truth for canonical state.
- Discord message edit frequency must stay rate-safe when true streaming is added.
- Presentation polish should stay grounded in structured module logic rather than freeform narrator improvisation as new modules are added.
- AI-first extraction must stay reviewable; the system should not silently turn source scripts into opaque runtime blobs.
- Location graphs should preserve the original script topology and not flatten everything into unordered node soup.
- Trigger execution must stay reusable across future adventures and cannot collapse into `疯狂之馆`-specific imperative code.
- The COC pivot must reuse the current Discord, room-graph, persistence, trigger, and streaming foundations instead of starting over.
- Dynamic-form investigator PDFs may need a non-text-extraction intake path.
- Community COC sites are useful ecosystem references, but canonical runtime truth should stay local and reviewable.

## Session Continuity

Last session: 2026-03-28T15:05:00.000Z
Stopped at: Started milestone v1.6 from local COC rulebooks, pregens, templates, and curated COC references
Resume file: .planning/PROJECT.md
