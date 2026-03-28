# Milestones

Historical milestones remain linear for GSD continuity. Each milestone now includes a primary track label so collaborators can understand where it belongs in the long-term product map.

## vB.1.1 [Track B] B1 Archive And Builder Normalization (Planned: 2026-03-28)

**Goal:**

- Tighten archive-builder mapping with better AI summarization during builder flow, aligned with standard COC character sheet sections.

**Planned phases:** 4 phases total

**Planned focus:**

- Fix AI summarization in builder flow (currently copies user input verbatim)
- Add Pydantic contracts for builder-to-archive communication
- Normalize archive fields to COC 7e character sheet structure
- Ensure archive-projection sync works automatically

---

## v2.2 [Governance] GSD Track 化治理重构 (Shipped: 2026-03-28)

**Goal:**

- Formalize track-based project governance so any GSD-driven collaborator can recover the product structure, global rules, and next-milestone choices directly from repository planning docs.

**Phases completed:** 3 phases total

**Key accomplishments:**

- Defined four persistent product tracks (A/B/C/D) with clear ownership boundaries
- Added global rules to PROJECT.md for smoke-check, canonical truth, auditability
- Restructured ROADMAP.md to organize by track for future milestone selection
- Added track labels to MILESTONES.md for historical context
- Updated collaboration notes with track guidance

---

## v2.1 [Track B / Track C] 交付检查与角色治理 (Shipped: 2026-03-28)

**Goal:**

- Add a hard local smoke-check gate before delivery, enforce a single active long-lived character per account by default, and introduce administrator-facing role management with a preferred admin channel.

**Planned phases:** 3 phases total

**Planned focus:**

- Add a repeatable local startup smoke check that must pass before work is declared ready.
- Reshape archive identity rules so each account has one active profile by default, with explicit archive/replace flows.
- Add admin-role character visibility and management commands, with defaults that guide usage into a dedicated management channel.

---

## v2.0 [Track B] Archive 系统与人物卡面板完善 (Shipped: 2026-03-28)

**Goal:**

- Turn the current archive from a thin profile store into a richer, investigator-card-like long-lived identity system with clearer schema, better Discord presentation, and explicit COC-bounded finishing logic.

**Planned phases:** 3 phases total

**Planned focus:**

- Expand archive schema and normalize builder output into more specific structured fields.
- Improve archive presentation so players can actually read and use their long-lived profiles in Discord.
- Let interview output influence finishing choices only through explicit, reviewable COC-compatible rules.

---

## v1.9 [Track B] 沉浸式人物构建层 (Shipped: 2026-03-28)

**Goal:**

- Turn investigator creation into a more game-like, immersive character-shaping experience while preserving canonical COC sheet legality and archive/campaign separation.

**Phases completed:** 3 phases total

**Key accomplishments:**

- Replaced the fixed builder script with a concept-first interview flow that can adapt the next question to the current character premise.
- Added richer archive identity fields such as life goal, weakness, and key past event so long-lived investigators feel like people, not just sheets.
- Kept numeric truth grounded in canonical COC generation while writing the richer interview output back into archive-ready profiles.

---

## v1.8 [Track B / Track C] 角色档案分层与 COC 对话建卡系统 (Shipped: 2026-03-28)

**Goal:**

- Separate Discord archive and live-play channel responsibilities, add a conversational but rules-grounded COC investigator builder, and split long-lived archive identities from campaign-specific role instances.

**Phases completed:** 3 phases total

**Key accomplishments:**

- Added archive-channel and trace-channel bindings so profile/archive operations can be redirected away from live-play halls.
- Added a private-first conversational investigator builder that generates canonical COC attributes and turns player answers into occupation/background/persona summaries.
- Added long-lived investigator archive profiles and per-campaign profile selection so module play can project mutable instances without mutating the archive base.

---

## v1.7 [Track A / Track B] 调查员面板与复杂 COC 模组运行时 (Shipped: 2026-03-28)

**Goal:**

- Add per-player investigator panels, private knowledge handling, and reusable runtime support for more complex COC modules such as `覆辙`, while keeping all new mechanics grounded in local COC rulebooks or explicit module rules.

**Phases completed:** 3 phases total

**Key accomplishments:**

- Added persistent investigator panels with bot-native `/sheet` and role-aware panel seeding for standard investigators and alternate templates such as `magical_girl`.
- Extended the runtime with player-private and group-scoped knowledge, plus mixed room/scene/event graph primitives and story-node tracking.
- Shipped the first structured `覆辙` sample module to validate dual onboarding tracks, asymmetrical truths, and reusable complex-module abstractions.

---

## v1.6 [Track A] COC/KP 基础运行时与模组资产接入 (Shipped: 2026-03-28)

**Phases completed:** 3 phases total

**Key accomplishments:**

- Pivoted the runtime from D&D-first assumptions to COC/Keeper-first percentile checks, sanity handling, and investigator state.
- Added a reviewable local COC asset layer for rulebooks, pregenerated investigators, templates, and curated community references.
- Reframed prompts, extraction, commands, and diagnostics around keeper-style investigation flow while preserving the existing Discord, room-graph, trigger, persistence, and streaming foundations.

---

## v1.5 [Track A] 通用 Trigger Tree 与后果引擎 (Shipped: 2026-03-28)

**Phases completed:** 3 phases total, 6 plans total, 0 tasks

**Key accomplishments:**

- Added a reusable declarative trigger schema with conditions, effects, and constrained hook boundaries.
- Added runtime trigger execution so actions and rolls now produce persisted consequence chains and auditable event-log entries.
- Migrated key `疯狂之馆` investigation beats onto the generic trigger engine, including pending-roll consequence flow and clearer diagnostics.

---

## v1.4 [Track A] 房间图驱动的剧本理解与运行时 (Shipped: 2026-03-28)

**Phases completed:** 3 phases total, 6 plans total, 0 tasks

**Key accomplishments:**

- Introduced room-graph support with explicit locations, adjacency, and location-aware runtime state.
- Added an AI-first, reviewable extraction draft pipeline for turning source scripts into room graphs and trigger summaries.
- Migrated `疯狂之馆` toward location-first play so portal observation, intentional entry, and room returns behave more like tabletop navigation.

---

## v1.3 [Track D] 剧本主持体验打磨 (Shipped: 2026-03-27)

**Phases completed:** 3 phases total, 6 plans total, 0 tasks

**Key accomplishments:**

- Added structured judgement for automatic outcomes, clarification prompts, and explicit roll-needed prompts.
- Added bounded light and rescue hint tiers driven by structured module metadata rather than only narrator improvisation.
- Improved `疯狂之馆` scene framing, pressure presentation, and return-to-choice pacing to feel more like a live Keeper.

---

## v1.2 [Track A / Track C / Track D] 疯狂之馆开场体验与骰子系统 (Shipped: 2026-03-27)

**Phases completed:** 11 phases total, 22 plans total, 0 tasks

**Key accomplishments:**

- Added a reusable packaged-adventure ready-up flow so `mad_mansion` can start with explicit table readiness and an automatic DM opening.
- Replaced placeholder dice behavior with a mature `d20`-backed rules layer and exposed checks, saves, attacks, damage, and raw expressions in Discord.
- Improved Discord usability through clearer blocked-input feedback, inline dice shortcuts, and more visible processing during ordinary message play.
- Added true narrator-phase streaming to Discord using rate-safe chunked message edits with fallback to finalized replies.

---

## v1.1 [Track A] 疯狂之馆首个正式模组 (Shipped: 2026-03-27)

**Phases completed:** 8 phases, 16 plans, 0 tasks

**Key accomplishments:**

- Formalized a reusable adventure package schema with canonical module state, reveal policy, and ending support.
- Shipped `mad_mansion` / `疯狂之馆` as the first official structured module with hall-and-wing progression and branching endings.
- Persisted campaign bindings and memberships so natural-message play survives bot restarts.
- Added adventure-aware diagnostics and operator docs centered on the formal `疯狂之馆` flow.

---
