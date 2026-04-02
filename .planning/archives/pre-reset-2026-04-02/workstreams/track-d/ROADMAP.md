# Roadmap: Track D - 游戏呈现层

## Overview

Track D owns the perceived table experience — Keeper-style narration, guidance and stall recovery tone, clue/history/panel presentation, consequence framing, and player-facing readability and immersion.

**Core Principle:** Track D does NOT define canonical truth. It presents what Tracks A, B, C, E have already resolved in a Keeper-style way.

## Completed Milestones

- ✅ **vD.1.1** — Keeper-Guided Archive Experience (completed 2026-03-31)

## Latest Completed Milestone

**vD.1.1** - Keeper-Guided Archive Experience
- **Primary Track:** Track D - 游戏呈现层
- **Goal:** Make archive and builder feel like a Keeper-guided experience, not a bot interface
- **Status:** Completed

**4 Planned Phases:**
- D40: Private-First Builder Experience
- D41: Archive Card Redesign
- D42: Keeper Prompt Polish
- D43: Activity-Ready Presentation Contracts

---

## vD.1.1 Summary

**Goal:** Redesign archive and builder presentation so character creation feels like a private Keeper-guided interview and player-facing archive output feels like a readable investigator card.

**What This Consumes From Other Tracks:**
- Track B: ConversationalCharacterBuilder, InvestigatorArchiveProfile, InvestigatorPanel
- Track C: VisibilityDispatcher, slash commands, ephemeral routing
- Track E: COC rules engine (for future Keeper narration)

**What This Does NOT Include:**
- New canonical rules or game logic (Track A/E)
- New archive operations or persistence (Track B)
- New Discord command infrastructure (Track C)

---

## vD.1.1 Phases

### Phase D40: Private-First Builder Experience

**Goal:** Make character builder interview happen in DM by default, not in public archive channel.

**Requirements:** PRIVATE-01, PRIVATE-02, PRIVATE-03

**Success Criteria** (what must be TRUE):
1. `/start_builder` sends first question to user's DM, not archive channel
2. Archive channel shows only "建卡中..." indicator, not interview content
3. Archive channel guidance clearly explains builder flow vs profile viewing
4. Builder prompts feel like Keeper shaping a person, not a generic questionnaire

**Depends on:** Nothing (first phase)

**Plans:** 1 plan

Plans:
- [x] D40-01-PLAN.md — Route builder to DM, add archive guidance, rewrite prompts with Keeper voice

---

### Phase D41: Archive Card Redesign

**Goal:** Present archive profiles as investigator cards, not dense text dumps.

**Requirements:** PRESENT-01, PRESENT-02

**Success Criteria** (what must be TRUE):
1. `/profile_detail` outputs card-like format with visual sections
2. Long-lived archive fields clearly distinguished from campaign-local state
3. Output remains readable within Discord message constraints
4. Card format is reusable for future Activity UI (not Discord-only)

**Depends on:** D40

**Plans:** 1 completed plan

Plans:
- [x] D41-01-PLAN.md — Redesign archive detail output into sectioned investigator cards reusable beyond Discord-only formatting

---

### Phase D42: Keeper Prompt Polish

**Goal:** Polish all remaining Keeper voice across the system beyond builder prompts — model-guided system prompts, narration service, consequence formatting, and system messages.

**Requirements:** KEEPER-01, KEEPER-02, KEEPER-03, KEEPER-04

**Success Criteria** (what must be TRUE):
1. Model-guided system prompts use "你是克苏鲁的呼唤的 Keeper" instead of "你是XX器"
2. Consequence formatting uses narrative Keeper-style text instead of mechanical labels
3. All player-facing system messages use consistent Chinese
4. Narration service prompt remains solid (no changes needed)
5. No regression in builder prompt quality (D40's work preserved)

**Depends on:** D40

**Plans:** 1 plan

Plans:
- [x] D42-01-PLAN.md — Polish model prompts, consequence formatting, and system messages

---

### Phase D43: Activity-Ready Presentation Contracts

**Goal:** Define presentation contracts that can be reused by future Discord Activity UI.

**Requirements:** PRESENT-03, ACTIVITY-01, ACTIVITY-02

**Success Criteria** (what must be TRUE):
1. Archive card format defined as reusable sections (not hardcoded to Discord message format)
2. Presentation-layer changes do not redefine archive ownership or canonical state
3. All contracts documented for future Activity consumption

**Depends on:** D41, D42

**Plans:** 1 plan

Plans:
- [x] D43-01-PLAN.md — Create CardSection/CardRenderer contracts, refactor card_view(), wire DiscordCardRenderer

**Delivered outcomes:**
- `/start_builder` defaults to DM-first builder flow with clearer archive-channel guidance
- `/profile_detail` now renders sectioned investigator cards instead of dense dumps
- archive presentation is split from archive truth via `CardSection` and `DiscordCardRenderer`
- Keeper voice and Chinese player-facing system messages are more consistent across builder and consequence surfaces

---

## Next Milestone

### vD.1.2: Session Boards And Keeper Scene Presentation

**Goal:** Present session state, scene context, and consequences in Keeper-style boards once Track A's shared scene resolution contracts are stable.

**Status:** Queued behind `track-a / vA.1.2`

**Recommendation:** Do not start this milestone until Track A finalizes shared scene batching/consequence contracts, otherwise Track D will end up reworking presentation contracts around moving runtime semantics.

---

## Queued Milestones

### vD.1.3: New-Player Start Pack And Rules Boards

**Goal:** Package COC minimum rules and module intro for fast onboarding.

**4 Planned Phases:**
- D48: What-Is-COC Pack
- D49: Skill/Profession Guide
- D50: Combat Flow Board
- D51: SAN/Injury Flow Board

**What This Consumes:**
- Track A: COC rules, module onboarding metadata
- Track B: Profession/skill recommendations
- Track E: Combat, SAN, injury rules

---

## Progress Table

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| **vD.1.1** | | | |
| D40. Private-First Builder Experience | 1/1 | Complete | D40-01 |
| D41. Archive Card Redesign | 1/1 | Complete | D41-01 |
| D42. Keeper Prompt Polish | 1/1 | Complete | D42-01 |
| D43. Activity-Ready Presentation Contracts | 1/1 | Complete | D43-01 |
| **vD.1.2** | | | |
| D44. Session Board | 0/0 | Queued | - |
| D45. Scene Framing | 0/0 | Queued | - |
| D46. Clue/History Board | 0/0 | Queued | - |
| D47. Consequence Summary | 0/0 | Queued | - |
| **vD.1.3** | | | |
| D48. What-Is-COC Pack | 0/0 | Queued | - |
| D49. Skill/Profession Guide | 0/0 | Queued | - |
| D50. Combat Flow Board | 0/0 | Queued | - |
| D51. SAN/Injury Flow Board | 0/0 | Queued | - |

---

## Dependencies Map

```
Track B ─────► Track D
(Builder)      (Presentation)
(Archive)           │
                    │
Track C ───────────►│
(Discord)           │
                    │
Track A ───────────►│
(Modules)           │
                    │
Track E ───────────►│
(Rules)             │
```

**Rule:** Track D presents canonical truth from A/B/C/E. It never redefines it.

---

*Last updated: 2026-04-02 after workstream boundary reconciliation and vD.1.1 completion normalization*
