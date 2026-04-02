# Discord AI Keeper - Track D

## Track D: 游戏呈现层

**Owns perceived table experience:**
- Keeper-style narration boundaries
- Guidance and stall recovery tone
- Clue/history/panel presentation
- Consequence framing
- Player-facing readability and immersion

**Core Principle:** Track D does NOT define canonical truth. It presents what Tracks A, B, C, E have already resolved in a Keeper-style way.

### Typical Work
- Prompt shaping for Keeper voice
- Player-facing boards and summaries
- Archive/game presentation contracts
- Keeper-feel polish

### Out of Scope
- Canonical rules truth (Track A/E)
- Archive persistence semantics (Track B)
- Discord command governance (Track C)

---

## Active Milestone

**vD.1.1** - Keeper-Guided Archive Experience
- **Status:** Planned (not started)
- **Goal:** Make archive and builder feel like a Keeper-guided experience
- **Phases:** D40 → D41 → D42 → D43

---

## What Track D Consumes From Other Tracks

```
Track B (Builder/Archive)
  → ConversationalCharacterBuilder
  → InvestigatorArchiveProfile
  → InvestigatorPanel

Track C (Discord Interaction)
  → VisibilityDispatcher
  → Slash commands (ephemeral routing)
  → PlayerStatusRenderer, KPOpsRenderer

Track A (Module & Rules)
  → Structured modules (sad_carnival.json)
  → Room graphs, triggers, clue reveals
  → Scene transitions

Track E (Runtime Control)
  → COC rules engine
  → Combat, SAN, chase mechanics
  → Bestiary, equipment
```

---

## vD.1.1: Keeper-Guided Archive Experience

**Target features:**
- Private-first builder with DM interview
- Archive presented as investigator cards
- Keeper-voice prompts throughout
- Activity-ready presentation contracts

**Secondary Impact:**
- Track B: richer card sections, builder staging
- Track C: ephemeral/DM routing, archive channel flow

**Contracts Changed:**
- `ConversationalCharacterBuilder` prompts (Keeper voice)
- `InvestigatorArchiveProfile.card_view()` (presentation format)
- Archive channel guidance text

**Migration Notes:**
- Do not reintroduce rules truth into presentation logic
- Preserve existing archive operations while shifting perceived experience
- Keep presentation format Activity-ready

---

## Queued Milestones

### vD.1.2: Session Boards And Keeper Scene Presentation

**Target features:**
- Session board (campaign/adventure/session identity)
- Scene framing ("场景：XXX" format)
- Clue/history board
- Consequence summary in Keeper voice

**Primary Track:** Track D

**Secondary Impact:**
- Track C: command/status surfaces
- Track A: structured scene and consequence summaries

### vD.1.3: New-Player Start Pack And Rules Boards

**Target features:**
- What-is-COC pack
- Skill/profession guide
- Combat flow board
- SAN/injury flow board

**Primary Track:** Track D

**Secondary Impact:**
- Track A: rules summaries, module onboarding
- Track B: profession/skill guidance surfaces
- Track C: onboarding stage

---

*Last updated: 2026-03-31*
