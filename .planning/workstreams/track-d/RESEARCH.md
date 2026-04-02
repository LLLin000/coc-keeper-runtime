# Track D Research: 游戏呈现层

**Created:** 2026-03-31
**Status:** Research in progress

---

## Executive Summary

Track D (游戏呈现层) is the only track that has not started. Other tracks have built substantial infrastructure that Track D must now consume and present to players in an immersive, Keeper-style way.

**Key insight:** Track D's job is NOT to build new functionality, but to wrap existing infrastructure (from Tracks B, C, E, A) in a player-facing experience that feels like a Keeper-guided tabletop session.

---

## What Other Tracks Have Built

### Track B (Character Builder & Archive) - COMPLETE

**Key files:**
- `src/dm_bot/coc/builder.py` - ConversationalCharacterBuilder (interview flow)
- `src/dm_bot/coc/archive.py` - InvestigatorArchiveProfile, InvestigatorArchiveRepository
- `src/dm_bot/coc/panels.py` - InvestigatorPanel (runtime state)

**What Track D must present:**
- Private-first builder experience (interview in DM, not archive channel)
- Archive profile as "investigator card" not "command dump"
- Clear transition between: viewing profiles ↔ building new character

**Current issues:**
- Builder prompts feel like a "generic questionnaire" not a Keeper shaping a person
- `detail_view()` in archive.py is text-heavy, not card-like
- No visual distinction between long-lived archive vs campaign-local state

### Track C (Discord Interaction) - COMPLETE

**Key files:**
- `src/dm_bot/discord_bot/commands.py` - All slash commands
- `src/dm_bot/discord_bot/visibility_dispatcher.py` - PUBLIC/PRIVATE/GROUP/KEEPER routing
- `src/dm_bot/orchestrator/player_status_renderer.py` - PlayerStatusRenderer
- `src/dm_bot/orchestrator/kp_ops_renderer.py` - KPOpsRenderer

**What Track D must present:**
- Session boards (campaign/adventure/session identity)
- Scene framing and consequence summaries
- Clue/history/current-state boards
- New-player-friendly rules boards

**Current issues:**
- Player status renderer uses emoji but format is basic
- No "session board" that summarizes current scene + pressure
- No keeper-style scene presentation format

### Track E (Runtime Control & Ops) - RECENTLY COMPLETED

**Key files:**
- `src/dm_bot/rules/coc/` - Full COC rules engine (combat, SAN, skills, chase)
- `src/dm_bot/coc/bestiary.py` - 10 creature templates
- `src/dm_bot/coc/equipment.py` - Weapons + armor database
- `src/dm_bot/gameplay/chase.py` - Chase mechanics
- `tests/rules/coc/` - 222 COC tests

**What Track D must present:**
- Keeper-style narration for combat/SAN/chase outcomes
- Creature encounter presentation (sanity loss, combat stats)
- Equipment effects in combat narration

### Track A (Module & Rules) - vA.1.1 COMPLETE

**Key files:**
- `src/dm_bot/adventures/sad_carnival.json` - Structured module
- `src/dm_bot/adventures/` - Module room graphs, triggers

**What Track D must present:**
- Scene transition narration
- Clue reveal presentation
- Consequence framing (what happened because of player action)

---

## Current State Analysis

### What Exists for Presentation

| Component | Current Output | Track D Gap |
|-----------|---------------|-------------|
| `InvestigatorArchiveProfile.detail_view()` | Text with 【调查员档案】sections | Not card-like, too dense |
| `PlayerStatusRenderer.render_personal_detail()` | Emoji + text | Basic, no scene context |
| `KPOpsRenderer.render_overview()` | Dense ops view | KP-only, not player-facing |
| `VisibilityDispatcher` | Routes to PUBLIC/PRIVATE/GROUP | No presentation format |
| `ConversationalCharacterBuilder` | Interview questions | Not Keeper-feel, public by default |

### What Doesn't Exist Yet

1. **Session Board** - Single view showing: campaign name, adventure, current scene, recent history, player states
2. **Scene Presentation** - Keeper-style framing: "场景：XXX，你们发现..." format
3. **Clue Board** - What clues have been found, which are revealed, which are still hidden
4. **Keeper Narration Wrapper** - Take rule resolution outcomes and present them in Keeper voice
5. **New-Player Rules Cards** - Minimum COC rules in digestible format for new players

---

## vD.1.1 Requirements Analysis

### PRIVATE-01/02/03: Private-First Builder Experience

**Current:** `/start_builder` can be run in archive channel, response visible to all

**Needed:**
- Builder interview happens in DM (ephemeral) by default
- Archive channel only shows: "建卡中..." and final completion
- Builder prompts rewritten to feel like Keeper questions

**Changes required:**
1. `commands.py` - `start_character_builder()` defaults visibility="private"
2. `builder.py` - Rewrite INTRO_QUESTION and CONCEPT_QUESTION to feel like Keeper
3. Archive channel message explains when a reply is "builder in progress" vs "viewing profiles"

### PRESENT-01/02/03: Archive Card Presentation

**Current:** `detail_view()` outputs dense text block

**Needed:**
- Card-like format with visual sections
- Long-lived vs campaign-local clearly separated
- Readable in Discord constraints

**Changes required:**
1. `archive.py` - Add `card_view()` method with better formatting
2. Consider embed-based display for profile details

---

## Proposed Milestones for Track D

### vD.1.1: Keeper-Guided Archive Experience (4 phases)

**Goal:** Make archive and builder feel like a Keeper-guided experience, not a bot interface

| Phase | Focus | Requirements |
|-------|-------|--------------|
| D40 | Private-First Builder | PRIVATE-01, PRIVATE-02, PRIVATE-03 |
| D41 | Archive Card Redesign | PRESENT-01, PRESENT-02 |
| D42 | Keeper Prompt Polish | PRIVATE-03 (prompts feel like Keeper) |
| D43 | Activity-Ready Contracts | PRESENT-03, ACTIVITY-01, ACTIVITY-02 |

### vD.1.2: Session Boards And Keeper Scene Presentation (4 phases)

**Goal:** Present session state, scene context, and consequences in Keeper-style boards

| Phase | Focus | Requirements |
|-------|-------|--------------|
| D44 | Session Board | BOARD-01 |
| D45 | Scene Framing | BOARD-02 |
| D46 | Clue/History Board | BOARD-01, BOARD-03 |
| D47 | Consequence Summary | BOARD-02 |

### vD.1.3: New-Player Start Pack And Rules Boards (4 phases)

**Goal:** Package COC minimum rules and module intro for fast onboarding

| Phase | Focus | Requirements |
|-------|-------|--------------|
| D48 | What-Is-COC Pack | New-player onboarding |
| D49 | Skill/Profession Guide | New-player skill guidance |
| D50 | Combat Flow Board | RULE-02 |
| D51 | SAN/Injury Flow Board | RULE-02, RULE-03 |

---

## Dependencies Between Tracks

```
Track B (Builder/Archive)
    │
    │  consumed by
    ▼
Track D (Presentation)
    │
    │  also consumes
    ▼
Track C (Discord Interaction)
Track A (Modules)
Track E (Rules Engine)
```

**Key dependency:** Track D must not redefine canonical truth. It presents what other tracks have resolved.

---

## First Priority: vD.1.1

### D40: Private-First Builder Experience

**Changes needed:**

1. **`src/dm_bot/discord_bot/commands.py`** - `start_character_builder()`:
   - Change default visibility to `"private"` 
   - Add DM-first response explaining interview will continue in DM

2. **`src/dm_bot/coc/builder.py`** - Rewrite prompts:
   - `INTRO_QUESTION`: "先给这位调查员起个名字。" → "在开始之前，让我先了解一下这位即将踏入黑暗的调查员..."
   - `CONCEPT_QUESTION`: Make it feel like Keeper is asking, not a form

3. **Archive channel guidance** (`commands.py` `_build_channel_guidance`):
   - Add note: "建卡请用 `/start_builder`，访谈将在私信中进行"

### D41: Archive Card Redesign

**Changes needed:**

1. **`src/dm_bot/coc/archive.py`** - Add `card_view()`:
   - Replace dense text with sections using emoji
   - Separate long-lived (archive) from campaign-local (shown separately)
   - Add visual card border feel

2. **`src/dm_bot/discord_bot/commands.py`** - `profile_detail()`:
   - Use `card_view()` instead of `detail_view()`

---

## Verification Plan

After vD.1.1 complete:
1. `uv run pytest -q` - all existing tests pass
2. Manual test: `/start_builder` → verify DM response
3. Manual test: `/profile_detail` → verify card-like format
4. Check: builder prompts feel like Keeper questions

---

## Risks and Concerns

1. **Activity-ready contracts** - Need to ensure presentation formats are reusable beyond Discord (future Activity UI)
2. **Track D presentation must not redefine truth** - All canonical state stays in Tracks A/B/C/E
3. **Keeper-feel is subjective** - Need player feedback to validate "feels like Keeper"

---

*Research completed: 2026-03-31*
*Next step: Plan vD.1.1 milestone with phases D40-D43*
