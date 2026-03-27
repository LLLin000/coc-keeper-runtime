# Requirements: Discord AI Keeper

**Defined:** 2026-03-28
**Core Value:** Run a real multiplayer Call of Cthulhu session in Discord where a local AI Keeper can narrate, roleplay multiple characters, and enforce investigation-heavy rules flow without constant manual bookkeeping.

## v1.7 Requirements

### Investigator Panels

- [ ] **PANEL-01**: Each player should have a persistent investigator panel that surfaces canonical COC investigator data and scenario-linked mutable state.
- [ ] **PANEL-02**: Investigator panels should support both standard investigators and structured alternate templates such as `覆辙`'s investigation and magical-girl tracks.
- [ ] **PANEL-03**: Scenario outcomes such as SAN changes, injuries, resource shifts, and explicit module-specific effects should write back into the investigator panel.
- [ ] **PANEL-04**: Investigator panel fields should map back to local COC rules or explicit module metadata rather than freeform prompt invention.

### Private Knowledge And Complex Module Graphs

- [ ] **GRAPH-01**: The runtime should support mixed room/scene/event graphs so more complex COC modules are not forced into a room-only shape.
- [ ] **GRAPH-02**: The runtime should support private and group-scoped clues, truths, and tasking so different players can know different things.
- [ ] **GRAPH-03**: Multiple entry tracks and role-specific onboarding should be expressible structurally rather than hard-coded into one adventure.
- [ ] **GRAPH-04**: All added graph and knowledge features should stay reusable across future COC modules, not only `覆辙`.

### COC Rule Discipline

- [ ] **RULE-01**: New runtime mechanics should be grounded in the supplied local COC 7th rulebooks wherever the base system covers them.
- [ ] **RULE-02**: When a module introduces special behavior not covered by base COC rules, that behavior should be recorded as explicit module-specific rules rather than implied prompt behavior.
- [ ] **RULE-03**: Diagnostics and operator surfaces should distinguish canonical COC rules from module-specific overrides.

### 覆辙 Migration

- [ ] **FUZHE-01**: `覆辙` should be migrated as the first complex-module sample, including its dual entry tracks, asymmetrical truths, and scenario-specific long-state consequences.
- [ ] **FUZHE-02**: The migration should reveal any missing runtime primitives needed for future complex COC modules and fold them back into reusable abstractions.

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

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PANEL-01 | Phase 25 | Planned |
| PANEL-02 | Phase 25 | Planned |
| PANEL-03 | Phase 25 | Planned |
| PANEL-04 | Phase 25 | Planned |
| GRAPH-01 | Phase 26 | Planned |
| GRAPH-02 | Phase 26 | Planned |
| GRAPH-03 | Phase 26 | Planned |
| GRAPH-04 | Phase 26 | Planned |
| RULE-01 | Phase 26 | Planned |
| RULE-02 | Phase 26 | Planned |
| RULE-03 | Phase 26 | Planned |
| FUZHE-01 | Phase 27 | Planned |
| FUZHE-02 | Phase 27 | Planned |

**Coverage:**
- v1.7 requirements: 13 total
- Completed: 0
- Unmapped: 0

---
*Requirements defined: 2026-03-28*
*Last updated: 2026-03-28 after milestone v1.7 kickoff*
