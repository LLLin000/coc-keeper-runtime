# Requirements: Discord AI DM

**Defined:** 2026-03-27
**Core Value:** Run a real multiplayer D&D session in Discord where a local AI DM can narrate, roleplay multiple characters, and enforce heavy rules flow without constant manual bookkeeping.

## v1.3 Requirements

### Judgement And Roll Triggers

- [ ] **JUDGE-01**: The runtime can determine when a player action in `疯狂之馆` should trigger a formal roll, when it should succeed automatically, and when it should be blocked or clarified, instead of leaving that decision mostly to narration.
- [ ] **JUDGE-02**: When a roll is required, the bot can tell the table what kind of check or save is needed, who should roll, and why, using concise table-facing language.
- [ ] **JUDGE-03**: Success, failure, and partial-information outcomes are reflected in structured state and downstream narration rather than being flattened into generic scene prose.
- [ ] **JUDGE-04**: Mature patterns and existing conventions from real tabletop tooling are preferred over custom homegrown judgement rules unless the module specifically requires bespoke logic.

### Hinting, Clueing, And Reveal Timing

- [ ] **HINT-01**: `疯狂之馆` can surface context-sensitive hints when the group stalls, loops, or misses required next steps, without leaking protected hidden information too early.
- [ ] **HINT-02**: The bot can separate ambient description, discoverable clue prompts, and explicit actionable guidance so players are not forced to guess what is interactable.
- [ ] **HINT-03**: Important module beats such as the countdown, the function of the four halls, sacrifice costs, and the blood-exit condition are introduced at deliberate times instead of by accidental prompt drift.
- [ ] **HINT-04**: Reveal timing remains module-safe: table-facing hints never bypass canonical hidden-state gates or spoil late-stage truths prematurely.

### Keeper-Style Scene Presentation

- [ ] **PRESENT-01**: The opening hall, each branch hall, and each major branch-specific interaction in `疯狂之馆` have stronger DM framing that feels closer to a real Keeper/DM introduction than a generic AI paragraph.
- [ ] **PRESENT-02**: The runtime can present clearer transitions between free exploration, explicit roll prompts, consequences, and return-to-choice moments so the session rhythm feels intentional.
- [ ] **PRESENT-03**: Scene output can call attention to salient props, risks, NPC posture, and available interaction vectors without turning into a menu dump.
- [ ] **PRESENT-04**: The table can recover from failed exploration or wrong assumptions because the bot knows when to restate pressure, recap discovered truths, or redirect attention.

## v2 Requirements

### Adventure Authoring And GM Controls

- **AUTHR-01**: Operators can author or edit adventures through a higher-level authoring tool instead of hand-editing JSON.
- **AUTHR-02**: The runtime supports per-player secret handouts or whisper reveals as a first-class mechanic.
- **AUTHR-03**: Operators can override or patch packaged adventure state live during a session without editing stored files manually.
- **AUTHR-04**: The module schema supports richer puzzle scripting and reusable logic macros beyond the first formal adventure set.

## Out Of Scope

| Feature | Reason |
|---------|--------|
| Rewriting the whole runtime around a new game system | This milestone is about polishing the existing `疯狂之馆` experience. |
| Adding a second formal module before `疯狂之馆` presentation is strong enough | The current priority is depth and quality, not breadth. |
| Making the narrator the source of truth for whether rolls or clues should happen | Canonical judgement must stay in structured runtime logic. |
| Building a full visual GM dashboard in this round | Better in-session guidance matters more than a new UI surface. |
| Replacing mature external libraries with custom equivalents | The milestone should keep reusing stable prior art and only add thin module-specific logic. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| JUDGE-01 | Phase 13 | Planned |
| JUDGE-02 | Phase 13 | Planned |
| JUDGE-03 | Phase 13 | Planned |
| JUDGE-04 | Phase 13 | Planned |
| HINT-01 | Phase 14 | Planned |
| HINT-02 | Phase 14 | Planned |
| HINT-03 | Phase 14 | Planned |
| HINT-04 | Phase 14 | Planned |
| PRESENT-01 | Phase 15 | Planned |
| PRESENT-02 | Phase 15 | Planned |
| PRESENT-03 | Phase 15 | Planned |
| PRESENT-04 | Phase 15 | Planned |

**Coverage:**
- v1.3 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0

---
*Requirements defined: 2026-03-27*
*Last updated: 2026-03-27 for milestone v1.3 planning*
