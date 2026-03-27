# Feature Landscape

**Domain:** Discord-native local-AI D&D DM system
**Focus:** Multiplayer play, multi-character performance, heavy rules support
**Researched:** 2026-03-27
**Confidence:** MEDIUM-HIGH

## v1 Table Stakes

These are the minimum features for a first release to feel campaign-usable rather than like a demo.

| Feature | Why it is table stakes | Complexity | Notes |
|---------|-------------------------|------------|-------|
| Multiplayer session loop in one Discord channel or thread | The core promise is real group play, not solo chat | Medium | Must support multiple human players posting naturally into the same scene |
| Character linking or import from an external source | Users already expect import/link flows rather than rebuilding sheets in Discord | Medium | Prefer D&D Beyond, Dicecloud, or a similarly mature import path |
| Dice rolling plus character-aware actions | Players expect rolls, checks, saves, attacks, and spell use to resolve inside Discord | Medium | Natural-language input can wrap these, but the system still needs deterministic roll execution |
| Full combat state management | Initiative, HP, conditions, turn order, death saves, resources, and target resolution are expected for real 5e play | High | This is the main credibility threshold for a rules-heavy DM product |
| Rules and spell lookup on demand | Users expect fast rulings and reference without leaving Discord | Medium | SRD-backed lookup is enough for v1 if response quality is strong |
| Persistent campaign and session state | A one-shot or short campaign must survive restarts and resume cleanly | High | Include scene summary, NPC state, combat state, and player resources |
| DM mode switching between narration and ensemble NPC performance | This is part of the product thesis, not a bonus | Medium | Needs distinct speaker framing so several NPCs can speak clearly in one scene |
| Recoverable session context after interruption | Discord play is stop-start by nature | High | Resume should reconstruct who is present, what just happened, and whose turn it is |
| Basic safety rails for rules authority | Heavy-rules users will not tolerate silent hallucination during combat | High | Use tool-first resolution for mechanics and clearly mark uncertain rulings |

## v2 Candidates

These improve stickiness, but they should not block the first playable release.

| Feature | Why it is a v2 candidate | Complexity | Notes |
|---------|---------------------------|------------|-------|
| GM control panel for overrides and corrections | Valuable once real sessions expose edge cases | Medium | Needed after v1 proves where the AI misfires most often |
| Scene recap and campaign journal generation | Useful for between-session continuity | Low | Good leverage feature after basic persistence works |
| Rich NPC memory and relationship tracking | Improves roleplay quality over longer arcs | High | Worth doing only after the base session loop is reliable |
| Optional async play between live sessions | Helpful for downtime and party chatter | Medium | Easy to overbuild; keep out of v1 |
| Voice or TTS for DM and NPC delivery | Nice for immersion, not needed for campaign usability | Medium | Text-first keeps debugging much simpler |
| Lightweight map or encounter visualization hooks | Some groups will want it, but it is not required to prove the DM system | High | If added later, integrate rather than build a VTT |
| Advanced homebrew support | Important for some tables, but not for first validation | High | Start with structured overrides, not universal custom content ingestion |
| Player-facing memory tools | Party notes, quest summaries, and inventory reminders help retention | Low | Useful follow-on once persistence is stable |

## Explicit Out-of-Scope

These should stay out of the first release on purpose.

| Feature | Why it should be out of scope | What to do instead |
|---------|-------------------------------|--------------------|
| Full custom character builder/sheet manager | Recreates mature products and burns time on low-differentiation work | Import/link existing sheets |
| Full VTT with maps, fog of war, tokens, and positioning UI | Turns the project into a second product | Keep combat text-native in Discord; integrate later if needed |
| Support for every tabletop system at launch | Dilutes rules quality and multiplies testing surface | Focus on one 5e-style ruleset first |
| Deep autonomous sandbox campaigns with no guardrails | Memory drift and rules drift will undermine trust fast | Optimize for one-shots and short-to-medium guided campaigns |
| Multi-platform chat support in v1 | Splits UX and orchestration effort | Stay Discord-native |
| Full voice-first experience | Adds ASR/TTS latency and recovery complexity too early | Keep the core loop text-first |
| Fine-tuning or custom model training before product validation | Premature optimization | Use prompt, tool, and memory orchestration first |

## User Journey Expectations for Multiplayer Sessions

Players will expect this flow to work smoothly:

1. Join a campaign channel or thread and see the active session state.
2. Link or import a character with minimal setup friction.
3. Speak in natural language, with the system handling rolls and rules calls when needed.
4. Watch the DM shift cleanly between narration and multiple NPC voices without losing who is speaking.
5. Enter combat with visible initiative flow, targetable actions, HP changes, conditions, and resource updates.
6. Pause and resume later without manually reconstructing the scene.
7. End the session with a clear recap and saved state for the next play block.

If any of those break, the product will feel unreliable even if the prose quality is good.

## Risk of Over-Scoping the First Release

The main risk is trying to ship three products at once: an AI DM, a D&D automation bot, and a VTT/character platform. That leads to shallow reliability everywhere.

For v1, the correct boundary is narrower: run the Discord gameplay loop end-to-end, keep mechanics deterministic, preserve session state, and make multi-character performance feel coherent. If the team adds maps, voice, custom sheet management, deep homebrew ingestion, or broad async systems before that loop is stable, the first release will likely miss the actual validation target.

## Recommended MVP Cut

Prioritize:
1. Multiplayer Discord session orchestration
2. Character import/link plus rules-backed roll execution
3. Combat automation with persistence and resume
4. DM narration plus multi-NPC scene performance

Defer:
- Maps/VTT features
- Voice features
- Advanced homebrew tooling
- Long-horizon campaign memory systems

## Sources

- Internal project context: [PROJECT.md](/C:/Users/Lin/Documents/Playground/.planning/PROJECT.md)
- Avrae getting started and character import: https://avrae.readthedocs.io/en/latest/cheatsheets/get_started.html
- Avrae D&D Beyond integration and channel-linked dice sync: https://avrae.readthedocs.io/en/latest/ddb.html
- Avrae player combat guide: https://avrae.readthedocs.io/en/latest/cheatsheets/pc_combat.html
- Avrae DM combat guide: https://avrae.readthedocs.io/en/stable/cheatsheets/dm_combat.html
- RPG Sessions Discord bot overview: https://rpgsessions.com/docs/discord-bot
