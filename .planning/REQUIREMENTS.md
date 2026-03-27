# Requirements: Discord AI Keeper

**Defined:** 2026-03-28
**Core Value:** Run a real multiplayer Call of Cthulhu session in Discord where a local AI Keeper can narrate, roleplay multiple characters, and enforce investigation-heavy rules flow without constant manual bookkeeping.

## v1.6 Requirements

### COC Runtime Foundations

- [ ] **COC-01**: The rules runtime should model core COC 7th investigation checks, including regular/hard/extreme success tiers and failure without relying on freeform narrator interpretation.
- [ ] **COC-02**: The runtime should support bonus dice, penalty dice, pushed rolls, opposed rolls, and combined rolls in ways that can feed deterministic consequences.
- [ ] **COC-03**: SAN, temporary pressure, and key COC investigator state should become first-class structured runtime concepts instead of ad hoc narrative text.
- [ ] **COC-04**: Keeper-facing resolution should support “what happens on success/failure/push failure” patterns common to COC modules.

### COC Asset And Character Intake

- [ ] **ASSET-01**: Local COC rulebooks should be ingested into a reviewable knowledge layer so prompts and extraction flows can reference stable structured rule concepts.
- [ ] **ASSET-02**: Pregenerated investigators and blank investigator templates should have a viable intake path even when source PDFs are dynamic forms or otherwise hard to text-extract.
- [ ] **ASSET-03**: The system should support a canonical COC investigator data model aligned with local assets rather than D&D sheet assumptions.
- [ ] **ASSET-04**: Curated ecosystem references such as COC community sites should enrich metadata and context, but the runtime must preserve local-first, reviewable truth.

### COC Module And Keeper Experience

- [ ] **KP-01**: Module extraction and runtime prompts should shift from D&D/DM framing to COC/Keeper framing, especially around investigation, clue gating, terror escalation, and hidden truth.
- [ ] **KP-02**: The room graph and trigger engine should remain reusable for future COC modules rather than overfitting to a single adventure.
- [ ] **KP-03**: Player-facing guidance should feel like a Keeper orienting investigators toward leads and risks without collapsing into scripted walkthroughs.
- [ ] **KP-04**: Operator-facing diagnostics should surface COC-relevant state such as SAN pressure, clue status, pending push consequences, and location-based danger.

### Migration And Compatibility

- [ ] **MIG-01**: Existing Discord, room-graph, trigger, and streaming infrastructure should remain intact while COC-first semantics are introduced on top.
- [ ] **MIG-02**: The system should provide a migration path away from D&D-specific concepts in prompts, schemas, and runtime assumptions without breaking current module tooling.

## v2 Requirements

### Adventure Authoring And GM Controls

- **AUTHR-01**: Operators can author or edit adventures through a higher-level authoring tool instead of hand-editing JSON.
- **AUTHR-02**: The runtime supports per-player secret handouts or whisper reveals as a first-class mechanic.
- **AUTHR-03**: Operators can override or patch packaged adventure state live during a session without editing stored files manually.
- **AUTHR-04**: The module schema supports richer puzzle scripting and reusable logic macros beyond the first formal adventure set.

## Out Of Scope

| Feature | Reason |
|---------|--------|
| Keeping D&D-first terminology and sheet assumptions as the project center | This milestone explicitly pivots the product toward COC/Keeper-first play. |
| Treating community web references as canonical runtime truth | Local rulebooks and reviewable structured assets should stay authoritative. |
| Rebuilding the whole bot from scratch for COC | The Discord, room graph, trigger, persistence, and streaming foundations should be reused. |
| Solving every future COC module in this milestone | This round establishes the reusable COC base, not total content parity. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| COC-01 | Phase 22 | Planned |
| COC-02 | Phase 22 | Planned |
| COC-03 | Phase 22 | Planned |
| COC-04 | Phase 22 | Planned |
| ASSET-01 | Phase 23 | Planned |
| ASSET-02 | Phase 23 | Planned |
| ASSET-03 | Phase 23 | Planned |
| ASSET-04 | Phase 23 | Planned |
| KP-01 | Phase 24 | Planned |
| KP-02 | Phase 24 | Planned |
| KP-03 | Phase 24 | Planned |
| KP-04 | Phase 24 | Planned |
| MIG-01 | Phase 24 | Planned |
| MIG-02 | Phase 24 | Planned |

**Coverage:**
- v1.6 requirements: 14 total
- Completed: 0
- Unmapped: 0

---
*Requirements defined: 2026-03-28*
*Last updated: 2026-03-28 after milestone v1.6 kickoff*
