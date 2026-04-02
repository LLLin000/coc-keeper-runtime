# Requirements: Track D - 游戏呈现层

**Defined:** 2026-03-31
**Updated:** 2026-03-31
**Core Value:** Owns perceived table experience — Keeper-style presentation, clue/history/panel readability, player-facing immersion without redefining canonical runtime truth.

---

## vD.1.1: Keeper-Guided Archive Experience

### Phase D40: Private-First Builder Experience

**Requirements:**

- [ ] **PRIVATE-01**: Character creation defaults to a private DM interaction instead of public archive channel
  - `/start_builder` sends first question to user's DM
  - Archive channel shows only "建卡中..." indicator

- [ ] **PRIVATE-02**: Archive channels clearly explain when a reply continues builder flow vs when it is only viewing/managing profiles
  - Add guidance text: "建卡请用 `/start_builder`，访谈将在私信中进行"
  - Profile viewing commands (`/profiles`, `/profile_detail`) clearly documented

- [ ] **PRIVATE-03**: Builder prompts feel like a Keeper shaping a person, not a generic questionnaire
  - Rewrite INTRO_QUESTION: "让我先了解一下这位即将踏入黑暗的调查员..."
  - Rewrite CONCEPT_QUESTION in Keeper voice
  - All follow-up questions maintain Keeper character

### Phase D41: Archive Card Redesign

**Requirements:**

- [ ] **PRESENT-01**: Player-facing archive details feel like an investigator card rather than a thin command dump
  - Add `card_view()` method with visual sections
  - Use emoji for stat indicators (❤️ HP, 🧠 SAN, 💧 MP, 🍀 LUCK)
  - Separate long-lived archive from campaign-local state

- [ ] **PRESENT-02**: Rich archive sections remain readable in Discord message constraints
  - Keep each section under 1024 characters
  - Use compact but scannable format
  - Multiple messages allowed for full card

- [ ] **PRESENT-03**: Long-lived archive details and campaign-local details are visually distinguishable
  - Archive sections clearly labeled as "长期档案"
  - Campaign state shown separately (via InvestigatorPanel)

### Phase D42: Keeper Prompt Polish

**Requirements:**

- [ ] **KEEPER-01**: INTRO_QUESTION opens with Keeper tone
  - Current: "先给这位调查员起个名字。"
  - New: "让我先了解一下这位即将踏入黑暗的调查员。请先告诉我他的名字。"

- [ ] **KEEPER-02**: CONCEPT_QUESTION asks in character
  - Current: "用一句短话描述这个人的人物骨架，例如"38岁的落魄临床医生"。"
  - NewKeeper-feel: Ask as if Keeper is getting to know them, not filling a form

- [ ] **KEEPER-03**: Follow-up questions maintain Keeper voice
  - Age question: "他的年龄是多少？" → "这位调查员看起来有多大？"
  - Occupation: "他的职业是什么？" → "他在成为调查员之前，以什么为生？"

- [ ] **KEEPER-04**: Finalization prompt feels like Keeper summarizing
  - Make player feel they shaped a person, not submitted a form
  - Clear call-to-action: "如果没问题，回复 `定卡`"

### Phase D43: Activity-Ready Presentation Contracts

**Requirements:**

- [ ] **ACTIVITY-01**: Archive presentation defined in reusable sections suitable for future Discord Activity panel
  - `CardSection` protocol with title, content, visibility
  - Not hardcoded to Discord embed format

- [ ] **ACTIVITY-02**: Presentation-layer changes do not redefine archive ownership or canonical state
  - All canonical state comes from Tracks A/B/C/E
  - Track D only controls formatting, not data

---

## vD.1.2: Session Boards And Keeper Scene Presentation

### Phase D44: Session Board

**Requirements:**

- [ ] **BOARD-01**: Player-facing board summarizes campaign/adventure/session identity in one readable surface
  - Campaign name, adventure title, session number
  - Current scene/location
  - All players and their ready status

- [ ] **BOARD-02**: Session board readable within Discord constraints
  - Compact format for channel message
  - Expandable details available on request

### Phase D45: Scene Framing

**Requirements:**

- [ ] **SCENE-01**: Scene transitions presented in Keeper-style framing
  - Format: "【场景】你们来到了XXX，..."
  - Describe atmosphere and immediate situation

- [ ] **SCENE-02**: Scene consequences framed as Keeper narration
  - What happened because of player action
  - Not just stat changes, but story impact

### Phase D46: Clue/History Board

**Requirements:**

- [ ] **CLUE-01**: Players can see what clues have been discovered
  - Clue name and brief description
  -区分 revealed to party vs still private

- [ ] **CLUE-02**: Recent history summarized in digestible format
  - Last 3-5 significant events
  - Who was involved

### Phase D47: Consequence Summary

**Requirements:**

- [ ] **CONS-01**: Consequence outcomes presented in Keeper voice
  - Not just "You took 2d6 damage"
  - "那道伤口比你预想的更深..."

- [ ] **CONS-02**: Status changes (SAN, HP, etc.) clearly communicated
  - Use emoji for quick scanning
  - Explain in narrative context

---

## vD.1.3: New-Player Start Pack And Rules Boards

### Phase D48: What-Is-COC Pack

**Requirements:**

- [ ] **NEWPLAYER-01**: COC elevator pitch in Chinese
  - What is Call of Cthulhu
  - Investigator role vs Keeper role
  - Horror atmosphere tone

- [ ] **NEWPLAYER-02**: Today's module theme presented clearly
  - One-line hook
  - What kind of investigation

### Phase D49: Skill/Profession Guide

**Requirements:**

- [ ] **SKILL-01**: Top 5 professions for new players explained simply
  - Each with one-sentence description
  - Suggested skill focus

- [ ] **SKILL-02**: Basic skill categories explained
  - Combat, Investigation, Social, Academic

### Phase D50: Combat Flow Board

**Requirements:**

- [ ] **COMBAT-01**: Turn order explained simply
  - Initiative roll → Act in order
  - Each player describes action → Keeper narrates result

- [ ] **COMBAT-02**: Damage and injury flow clearly presented
  - Success等级 → Damage formula
  - HP tracking and death

### Phase D51: SAN/Injury Flow Board

**Requirements:**

- [ ] **SAN-01**: SAN loss explained with tone guidance
  - What triggers SAN loss
  - Short-term vs long-term effects

- [ ] **SAN-02**: Insanity types and recovery explained
  - Temporary vs Indefinite madness
  - Recovery methods

---

## Requirement Traceability Matrix

| Requirement | Phase | Priority |
|-------------|-------|----------|
| PRIVATE-01 | D40 | High |
| PRIVATE-02 | D40 | High |
| PRIVATE-03 | D40, D42 | High |
| PRESENT-01 | D41 | High |
| PRESENT-02 | D41 | Medium |
| PRESENT-03 | D41 | Medium |
| KEEPER-01 | D42 | High |
| KEEPER-02 | D42 | High |
| KEEPER-03 | D42 | High |
| KEEPER-04 | D42 | Medium |
| ACTIVITY-01 | D43 | High |
| ACTIVITY-02 | D43 | High |
| BOARD-01 | D44 | High |
| BOARD-02 | D44 | Medium |
| SCENE-01 | D45 | High |
| SCENE-02 | D45 | High |
| CLUE-01 | D46 | Medium |
| CLUE-02 | D46 | Medium |
| CONS-01 | D47 | High |
| CONS-02 | D47 | Medium |

---

*Last updated: 2026-03-31*
