# Requirements: Discord AI Keeper

**Defined:** 2026-03-28
**Core Value:** Run a real multiplayer Call of Cthulhu session in Discord where a local AI Keeper can narrate, roleplay multiple characters, and enforce investigation-heavy rules flow without constant manual bookkeeping.

## vB.1.1 Requirements (Track B)

Milestone: Archive And Builder Normalization

### AI Summarization (核心修复)

- [ ] **AI-01**: User completes builder interview, AI synthesizes cohesive character profile from raw answers instead of copying verbatim
- [ ] **AI-02**: AI summarization respects COC 7e rules - no invented skills or occupations
- [ ] **AI-03**: Summarization distinguishes derived fields (calculated by rules) from intent fields (user's explicit choices)
- [ ] **AI-04**: Confirmation step before AI overwrites user's explicit character choices

### Archive Field Normalization

- [ ] **FN-01**: Existing "life_goal" field maps to standard COC backstory section
- [ ] **FN-02**: Existing "weakness" field maps to standard COC backstory section
- [ ] **FN-03**: Existing "key past event" field maps to standard COC backstory section
- [ ] **FN-04**: New fields follow COC 7e character sheet structure (Birthplace, Residence, Family, Education)
- [ ] **FN-05**: Schema versioning - new fields are nullable with defaults for backward compatibility

### Builder-Archive Contracts

- [ ] **BC-01**: Pydantic contracts define builder-to-archive communication schema
- [ ] **BC-02**: AnswerNormalizer component cleans raw user input to canonical slot format
- [ ] **BC-03**: CharacterSheetSynthesizer component transforms normalized answers into cohesive narrative
- [ ] **BC-04**: SectionNormalizer maps synthesis output to COC 7e character sheet sections
- [ ] **BC-05**: ArchiveProfileFactory creates profiles from synthesis output
- [ ] **BC-06**: Fallback from synthesis to heuristic extraction for robustness

### Archive-Projection Sync

- [ ] **PS-01**: Archive normalization updates automatically propagate to campaign projections
- [ ] **PS-02**: Diagnostic command shows sync status between archive and projection
- [ ] **PS-03**: Single active profile governance still works after normalization changes

## v2.2 Requirements

### Track Governance

- [ ] **TRACK-01**: The planning system should define the long-lived product tracks explicitly so future work can be classified without relying on chat history.
- [ ] **TRACK-02**: Each future milestone should declare one primary track, even when it has cross-track effects.
- [ ] **TRACK-03**: The repository should document how a collaborator or GSD agent chooses the correct track before starting a new milestone.

### Global Rules

- [ ] **GOV-01**: Repository-wide rules such as smoke-check gating, canonical COC rule truth, auditability, and documentation expectations should be documented once as global constraints instead of re-derived ad hoc.
- [ ] **GOV-02**: Those global rules should be visible from core planning files so they remain hard to miss during future milestone creation.
- [ ] **GOV-03**: README-level collaboration guidance should align with the same governance model used in `.planning`.
- [ ] **GOV-04**: Cross-track changes should be allowed only when their affected tracks, contracts, and migration notes are explicitly declared.

### Planning Restructure

- [ ] **PLAN-01**: `PROJECT.md` should describe the track model and global rules as the top-level project map.
- [ ] **PLAN-02**: `ROADMAP.md` should group future work by track so AI agents can choose a layer first and then a milestone.
- [ ] **PLAN-03**: `STATE.md` should expose the current active track and the next milestone candidates by track.
- [ ] **PLAN-04**: `MILESTONES.md` should preserve the linear history while labeling historical milestones by their primary track(s).
- [ ] **PLAN-05**: Future milestone planning guidance should explain how to handle multi-track work without losing a single primary track.

## v2.1 Requirements

### Delivery Smoke Check

- [ ] **SMOKE-01**: The project should include a repeatable local smoke-check command or script that runs tests, starts the bot, waits for `READY`, and verifies the process remains alive for a bounded window.
- [ ] **SMOKE-02**: Delivery claims should be blocked when the smoke check fails, even if unit tests pass.
- [ ] **SMOKE-03**: The smoke check should avoid false positives caused by stale logs or duplicate background bot processes.

### Single Active Archive Profile

- [ ] **ROLE-01**: Each player account should default to exactly one active long-lived archive profile.
- [ ] **ROLE-02**: Creating or promoting a new main character should require an explicit archive/replace action for the previous active profile rather than silently leaving multiple active profiles.
- [ ] **ROLE-03**: Archive profile lifecycle should be visible and reviewable, with statuses such as active, archived, or replaced.

### Admin Profile Governance

- [ ] **ADMIN-01**: Administrators should be able to inspect all player archive profiles, not only their own.
- [ ] **ADMIN-02**: Administrators should be able to archive, replace, activate, or delete profiles through explicit commands.
- [ ] **ADMIN-03**: Admin profile-management commands should work from any channel but prefer and guide toward a dedicated admin-management channel.

## v2.0 Requirements

### Rich Archive Schema

- [ ] **ARCHX-01**: Long-lived archive profiles should store a fuller set of investigator-card fields, including specialty, career arc, core belief, desire/goal, weakness, key past event, and other structured identity anchors.
- [ ] **ARCHX-02**: Builder answers should be normalized into explicit archive fields wherever possible instead of remaining buried in freeform background text.
- [ ] **ARCHX-03**: Archive data should distinguish clearly between rule-derived mechanical fields and narrative identity fields.

### Archive Presentation

- [ ] **PRES-01**: `/profiles` should remain a compact listing, but the system should add a richer detail view for a selected archive profile.
- [ ] **PRES-02**: Archive presentation in Discord should be organized into readable sections, closer to an investigator card than a debug dump.
- [ ] **PRES-03**: Players should be able to inspect the richer archive details in the archive channel without polluting live-play game halls.

### COC-Bounded Finishing Logic

- [ ] **FIN-01**: Interview-driven signals may influence finishing choices or recommended allocation only through explicit COC-compatible rules or bounded supported modes.
- [ ] **FIN-02**: The system should never invent arbitrary stat bonuses from prompt output; any adjustment path must be reviewable and rules-scoped.
- [ ] **FIN-03**: The archive should preserve both the raw investigator card and the normalized reasoning behind any interview-driven finishing recommendations.

### Module Reuse

- [ ] **MODARCH-01**: Future modules should be able to consume richer archive identity fields for onboarding hooks, private prompts, and role overlays.
- [ ] **MODARCH-02**: Campaign projection should continue to protect the archive base record from scenario-specific mutations.
- [ ] **MODARCH-03**: The richer archive format should remain compatible with the existing projection and panel flows.

## v1.9 Requirements

### Immersive Character-Shaping Flow

- [x] **CHAR-01**: Character creation should begin from a short concept or premise and evolve through adaptive Keeper-style follow-up questions instead of a fixed questionnaire.
- [x] **CHAR-02**: The builder should explicitly shape a character's life goal, weakness/flaw, key past event, and other roleplay anchors so the finished investigator feels like a person rather than just a sheet.
- [x] **CHAR-03**: Follow-up questions should vary by the concept already given, rather than asking the same generic prompts to every player.

### Model-Guided Builder Control

- [x] **ASK-01**: A fast local model may select the next best follow-up question, but only within structured slots and strict interview constraints.
- [x] **ASK-02**: The builder must stop asking questions once the required narrative and mechanical information is sufficient, instead of dragging through unnecessary rounds.
- [x] **ASK-03**: The system should be able to summarize collected answers into structured narrative fields for downstream archive storage and campaign projection.

### COC-Legal Generation Discipline

- [x] **COCGEN-01**: Core attributes and other canonical sheet fields must still come from supported COC generation rules or explicit allowed modes, never from freeform model invention.
- [x] **COCGEN-02**: Narrative answers should influence occupation detail, background, finishing choices, and skill leanings without breaking COC legality.
- [x] **COCGEN-03**: The finished archive profile should clearly distinguish rules-derived values from narrative characterization fields.

### Archive Value And Future Module Reuse

- [x] **ARCH-01**: Archive profiles should store richer long-term identity fields, including life goal and weakness, for reuse across future modules.
- [x] **ARCH-02**: Campaign projections should continue to derive from archive profiles without mutating the archive base.
- [x] **ARCH-03**: Complex modules should be able to read the richer archive characterization to improve onboarding, private hooks, and role overlays.

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
| AI-01 | Phase 41 | Pending |
| AI-02 | Phase 42 | Pending |
| AI-03 | Phase 42 | Pending |
| AI-04 | Phase 42 | Pending |
| FN-01 | Phase 42 | Pending |
| FN-02 | Phase 42 | Pending |
| FN-03 | Phase 42 | Pending |
| FN-04 | Phase 42 | Pending |
| FN-05 | Phase 40 | Pending |
| BC-01 | Phase 40 | Pending |
| BC-02 | Phase 40 | Pending |
| BC-03 | Phase 41 | Pending |
| BC-04 | Phase 41 | Pending |
| BC-05 | Phase 41 | Pending |
| BC-06 | Phase 42 | Pending |
| PS-01 | Phase 42 | Pending |
| PS-02 | Phase 42 | Pending |
| PS-03 | Phase 42 | Pending |
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
| CHAR-01 | Phase 31 | Completed |
| CHAR-02 | Phase 32 | Completed |
| CHAR-03 | Phase 32 | Completed |
| ASK-01 | Phase 31 | Completed |
| ASK-02 | Phase 31 | Completed |
| ASK-03 | Phase 33 | Completed |
| COCGEN-01 | Phase 33 | Completed |
| COCGEN-02 | Phase 33 | Completed |
| COCGEN-03 | Phase 33 | Completed |
| ARCH-01 | Phase 32 | Completed |
| ARCH-02 | Phase 33 | Completed |
| ARCH-03 | Phase 33 | Completed |
| ARCHX-01 | Phase 34 | Planned |
| ARCHX-02 | Phase 34 | Planned |
| ARCHX-03 | Phase 34 | Planned |
| PRES-01 | Phase 35 | Planned |
| PRES-02 | Phase 35 | Planned |
| PRES-03 | Phase 35 | Planned |
| FIN-01 | Phase 36 | Planned |
| FIN-02 | Phase 36 | Planned |
| FIN-03 | Phase 36 | Planned |
| MODARCH-01 | Phase 36 | Planned |
| MODARCH-02 | Phase 36 | Planned |
| MODARCH-03 | Phase 36 | Planned |
| SMOKE-01 | Phase 37 | Planned |
| SMOKE-02 | Phase 37 | Planned |
| SMOKE-03 | Phase 37 | Planned |
| ROLE-01 | Phase 38 | Planned |
| ROLE-02 | Phase 38 | Planned |
| ROLE-03 | Phase 38 | Planned |
| ADMIN-01 | Phase 39 | Planned |
| ADMIN-02 | Phase 39 | Planned |
| ADMIN-03 | Phase 39 | Planned |
| TRACK-01 | Phase 44 | Deferred |
| TRACK-02 | Phase 44 | Deferred |
| TRACK-03 | Phase 44 | Deferred |
| GOV-01 | Phase 44 | Deferred |
| GOV-02 | Phase 44 | Deferred |
| GOV-03 | Phase 46 | Deferred |
| GOV-04 | Phase 44 | Deferred |
| PLAN-01 | Phase 45 | Deferred |
| PLAN-02 | Phase 45 | Deferred |
| PLAN-03 | Phase 45 | Deferred |
| PLAN-04 | Phase 45 | Deferred |
| PLAN-05 | Phase 45 | Deferred |

**Coverage:**
- vB.1.1 requirements: 18 total (100% mapped to Phases 40-43)
- v1.8 requirements: 13 total (completed)
- v1.9 requirements: 12 total (completed)
- v2.0 requirements: 12 total (completed)
- v2.1 requirements: 9 total (completed)
- v2.2 requirements: 12 total (deferred to Phases 44-46)
- Completed: 25
- Planned: 18 (vB.1.1)
- Deferred: 12 (v2.2)
- Unmapped: 0

---
*Requirements defined: 2026-03-28*
*Last updated: 2026-03-28 after vB.1.1 roadmap creation - phases 40-43*
