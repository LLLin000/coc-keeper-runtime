# Requirements: Discord AI Keeper

**Defined:** 2026-03-28
**Core Value:** Run a real multiplayer Call of Cthulhu session in Discord where a local AI Keeper can narrate, roleplay multiple characters, and enforce investigation-heavy rules flow without constant manual bookkeeping.

## v1.8 Requirements

### Discord Channel Discipline

- [x] **CHAN-01**: The system should support distinct Discord channel roles for character archives, live-play game halls, and optional keeper/trace output.
- [x] **CHAN-02**: Character/archive commands should be discouraged or blocked in live-play halls, with clear redirect messaging instead of silent failure.
- [x] **CHAN-03**: Live-play channels should stay focused on campaign actions, narration, and rules resolution rather than profile management noise.

### Conversational Character Builder

- [x] **BUILD-01**: The bot should support conversational investigator creation that feels like a Keeper-guided interview rather than a raw form.
- [x] **BUILD-02**: Core attributes must be generated through canonical COC rules or explicit supported generation modes, not freeform prompt invention.
- [x] **BUILD-03**: The conversational layer should shape occupation, background, skill leaning, portrait/persona summary, and recommended finishing choices without breaking rules validity.
- [x] **BUILD-04**: Character creation should support private-first operation through ephemeral replies or DM, while still allowing an archive-channel mode.

### Long-Lived Profiles And Campaign Projection

- [x] **PROF-01**: Players should own long-lived investigator archives that remain independent of any single module.
- [x] **PROF-02**: Campaigns should project an archive character into a module-specific instance whose SAN, injuries, secrets, and role state do not overwrite the archive base.
- [x] **PROF-03**: Complex modules should be able to add explicit role overlays, such as `覆辙`'s magical-girl track, on top of a projected archive character.

### COC Rule Discipline

- [x] **RULE-01**: Character generation and projection must stay grounded in the supplied local COC 7th rulebooks wherever the base system covers them.
- [x] **RULE-02**: Any scenario-specific modifications to a projected character must be recorded as explicit module metadata or runtime state, not as hidden prompt behavior.
- [x] **RULE-03**: Operator and player surfaces should be able to distinguish base investigator data from campaign-instance state.

## v2 Requirements

### Adventure Authoring And GM Controls

- **AUTHR-01**: Operators can author or edit adventures through a higher-level authoring tool instead of hand-editing JSON.
- **AUTHR-02**: The runtime supports per-player secret handouts or whisper reveals as a first-class mechanic.
- **AUTHR-03**: Operators can override or patch packaged adventure state live during a session without editing stored files manually.
- **AUTHR-04**: The module schema supports richer puzzle scripting and reusable logic macros beyond the first formal adventure set.

## Out Of Scope

| Feature | Reason |
|---------|--------|
| Inventing unsupported rules because a module feels dramatic | New logic must map to canonical COC rules or explicit module-specific rules. |
| Treating `覆辙` as a one-off special case with bespoke runtime hacks | This milestone is explicitly about reusable support for more complex COC modules. |
| Replacing the current room-graph/trigger foundations wholesale | The milestone should extend the runtime, not discard the foundation that already works. |
| Full visual parity with the public character generator in one round | The first goal is persistent player panels and runtime linkage, not a pixel-perfect website clone. |
| Replacing canonical COC generation with pure personality questionnaires | Questioning may shape the character, but stats and card validity must remain rules-grounded. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CHAN-01 | Phase 28 | Completed |
| CHAN-02 | Phase 28 | Completed |
| CHAN-03 | Phase 28 | Completed |
| BUILD-01 | Phase 29 | Completed |
| BUILD-02 | Phase 29 | Completed |
| BUILD-03 | Phase 29 | Completed |
| BUILD-04 | Phase 29 | Completed |
| PROF-01 | Phase 30 | Completed |
| PROF-02 | Phase 30 | Completed |
| PROF-03 | Phase 30 | Completed |
| RULE-01 | Phase 29 | Completed |
| RULE-02 | Phase 30 | Completed |
| RULE-03 | Phase 30 | Completed |

**Coverage:**
- v1.8 requirements: 13 total
- Completed: 13
- Unmapped: 0

---
*Requirements defined: 2026-03-28*
*Last updated: 2026-03-28 after milestone v1.8 execution*
