# Milestones

## v1.4 房间图驱动的剧本理解与运行时 (Shipped: 2026-03-28)

**Phases completed:** 3 phases total, 6 plans total, 0 tasks

**Key accomplishments:**

- Introduced room-graph support with explicit locations, adjacency, and location-aware runtime state.
- Added an AI-first, reviewable extraction draft pipeline for turning source scripts into room graphs and trigger summaries.
- Migrated `疯狂之馆` toward location-first play so portal observation, intentional entry, and room returns behave more like tabletop navigation.

---

## v1.3 剧本主持体验打磨 (Shipped: 2026-03-27)

**Phases completed:** 3 phases total, 6 plans total, 0 tasks

**Key accomplishments:**

- Added structured judgement for automatic outcomes, clarification prompts, and explicit roll-needed prompts.
- Added bounded light and rescue hint tiers driven by structured module metadata rather than only narrator improvisation.
- Improved `疯狂之馆` scene framing, pressure presentation, and return-to-choice pacing to feel more like a live Keeper.

---

## v1.2 疯狂之馆开场体验与骰子系统 (Shipped: 2026-03-27)

**Phases completed:** 11 phases total, 22 plans total, 0 tasks

**Key accomplishments:**

- Added a reusable packaged-adventure ready-up flow so `mad_mansion` can start with explicit table readiness and an automatic DM opening.
- Replaced placeholder dice behavior with a mature `d20`-backed rules layer and exposed checks, saves, attacks, damage, and raw expressions in Discord.
- Improved Discord usability through clearer blocked-input feedback, inline dice shortcuts, and more visible processing during ordinary message play.
- Added true narrator-phase streaming to Discord using rate-safe chunked message edits with fallback to finalized replies.

---

## v1.1 疯狂之馆首个正式模组 (Shipped: 2026-03-27)

**Phases completed:** 8 phases, 16 plans, 0 tasks

**Key accomplishments:**

- Formalized a reusable adventure package schema with canonical module state, reveal policy, and ending support.
- Shipped `mad_mansion` / `疯狂之馆` as the first official structured module with hall-and-wing progression and branching endings.
- Persisted campaign bindings and memberships so natural-message play survives bot restarts.
- Added adventure-aware diagnostics and operator docs centered on the formal `疯狂之馆` flow.

---
