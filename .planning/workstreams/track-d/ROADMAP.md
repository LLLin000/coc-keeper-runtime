# Roadmap: Track D - 游戏呈现层

## Overview

Track D owns the perceived table experience — Keeper-style narration, guidance and stall recovery tone, clue/history/panel presentation, consequence framing, and player-facing readability and immersion.

**Core Principle:** Track D does NOT define canonical truth. It presents what Tracks A, B, C, E have already resolved in a Keeper-style way.

## Completed Milestones

(None yet - Track D is starting)

## Active Milestone

**vD.1.1** - Keeper-Guided Archive Experience
- **Primary Track:** Track D - 游戏呈现层
- **Goal:** Make archive and builder feel like a Keeper-guided experience, not a bot interface
- **Status:** Planned (not started)

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

**Plans:** Not yet created

---

### Phase D42: Keeper Prompt Polish

**Goal:** Rewrite builder interview prompts to feel like a Keeper guiding character creation.

**Requirements:** PRIVATE-03

**Success Criteria** (what must be TRUE):
1. INTRO_QUESTION feels like Keeper's opening: "让我先了解一下这位即将踏入黑暗的调查员..."
2. CONCEPT_QUESTION asks in character, not as a form field
3. All follow-up questions maintain Keeper voice throughout interview
4. Finalization prompt makes player feel they shaped a person, not submitted a form

**Depends on:** D40

**Plans:** Not yet created

---

### Phase D43: Activity-Ready Presentation Contracts

**Goal:** Define presentation contracts that can be reused by future Discord Activity UI.

**Requirements:** PRESENT-03, ACTIVITY-01, ACTIVITY-02

**Success Criteria** (what must be TRUE):
1. Archive card format defined as reusable sections (not hardcoded to Discord message format)
2. Presentation-layer changes do not redefine archive ownership or canonical state
3. All contracts documented for future Activity consumption

**Depends on:** D41, D42

**Plans:** Not yet created

---

## Queued Milestone

### vD.1.2: Session Boards And Keeper Scene Presentation

**Goal:** Present session state, scene context, and consequences in Keeper-style boards.

**4 Planned Phases:**
- D44: Session Board (campaign/adventure/session identity)
- D45: Scene Framing (Keeper-style "场景：XXX" format)
- D46: Clue/History Board
- D47: Consequence Summary

**What This Consumes:**
- Track C: VisibilityDispatcher, PlayerStatusRenderer, session state
- Track A: Module triggers, scene transitions, clue reveals
- Track E: COC rules resolution outcomes

**What This Does NOT Include:**
- New session lifecycle logic (Track C)
- New module structure (Track A)
- New rule resolution (Track E)

---

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
| D40. Private-First Builder Experience | 0/0 | Planned | - |
| D41. Archive Card Redesign | 0/0 | Planned | - |
| D42. Keeper Prompt Polish | 0/0 | Planned | - |
| D43. Activity-Ready Presentation Contracts | 0/0 | Planned | - |
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

*Last updated: 2026-03-31 - Research completed, vD.1.1 ready to plan*
