# Requirements: Discord AI DM

**Defined:** 2026-03-27
**Core Value:** Run a real multiplayer D&D session in Discord where a local AI DM can narrate, roleplay multiple characters, and enforce heavy rules flow without constant manual bookkeeping.

## v1.4 Requirements

### Room Graph Runtime

- [ ] **GRAPH-01**: Adventures should be represented as room or location graphs with explicit nodes, connections, reachable transitions, and geographic context rather than only ordered scene chunks.
- [ ] **GRAPH-02**: Each location should carry its own interactables, local triggers, reveal gates, and state transitions so runtime decisions are driven by place and context.
- [ ] **GRAPH-03**: Runtime play should be keyed to current location plus reachable locations, allowing players to say things naturally without needing script-order phrasing.
- [ ] **GRAPH-04**: Structured room graphs should remain compatible with existing narration, judgement, and persistence layers instead of replacing them with a parallel system.

### Trigger Trees And Consequence Flow

- [ ] **TREE-01**: Plot beats should be attached to rooms, objects, NPCs, and stateful triggers in branching trees rather than only to linear script position.
- [ ] **TREE-02**: Roll outcomes should feed directly into location state, clue state, and trigger progression so checks produce concrete downstream consequences.
- [ ] **TREE-03**: The runtime should distinguish between observing, approaching, entering, leaving, and activating so player intent is interpreted more like a human GM would.
- [ ] **TREE-04**: Hidden truths and endgame reveals must stay gated by trigger conditions and local state, even when players approach the same content through unexpected language.

### AI-First Adventure Extraction

- [ ] **EXTRACT-01**: The system should use AI to read source scripts and extract draft room graphs, trigger trees, and reveal-safe runtime data before human review.
- [ ] **EXTRACT-02**: Extraction should preserve the original script's topology, room purposes, key props, NPCs, and branching consequences as faithfully as practical.
- [ ] **EXTRACT-03**: Extracted output should remain editable and reviewable, so humans can correct or refine AI output without rebuilding the whole module by hand.
- [ ] **EXTRACT-04**: The extraction pipeline should be reusable for future adventures, not just `疯狂之馆`.

### 疯狂之馆 Room-Graph Migration

- [ ] **MANSION-01**: `疯狂之馆` should be migrated from its current scene-oriented formal module into a room-graph-first module without losing original content fidelity.
- [ ] **MANSION-02**: The module should explicitly model the central hall, branch halls, movement between them, and the major interactive landmarks inside each location.
- [ ] **MANSION-03**: Movement, investigation, and return paths should feel natural in play, including observing portals without forced entry and leaving rooms without bespoke hacks.
- [ ] **MANSION-04**: The migrated module should improve actual session feel by making room navigation, local triggers, and roll consequences feel more like a tabletop session than a scripted sequence.

## v2 Requirements

### Adventure Authoring And GM Controls

- **AUTHR-01**: Operators can author or edit adventures through a higher-level authoring tool instead of hand-editing JSON.
- **AUTHR-02**: The runtime supports per-player secret handouts or whisper reveals as a first-class mechanic.
- **AUTHR-03**: Operators can override or patch packaged adventure state live during a session without editing stored files manually.
- **AUTHR-04**: The module schema supports richer puzzle scripting and reusable logic macros beyond the first formal adventure set.

## Out Of Scope

| Feature | Reason |
|---------|--------|
| Reverting to sequence-first script playback as the main module model | This milestone is explicitly about place-first representation. |
| Fully manual from-scratch modeling for every new adventure | The goal is AI-first extraction with review, not handcrafted authoring as the default. |
| Rebuilding the entire Discord runtime around a separate map UI | The room graph should improve the existing runtime, not require a new client surface. |
| Perfect automated extraction with zero review | AI extraction should accelerate authoring, but human validation is still expected. |
| Supporting every TRPG system in this round | The focus remains the current D&D-oriented runtime and `疯狂之馆` migration path. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GRAPH-01 | Phase 16 | Planned |
| GRAPH-02 | Phase 16 | Planned |
| GRAPH-03 | Phase 16 | Planned |
| GRAPH-04 | Phase 16 | Planned |
| TREE-01 | Phase 17 | Planned |
| TREE-02 | Phase 17 | Planned |
| TREE-03 | Phase 17 | Planned |
| TREE-04 | Phase 17 | Planned |
| EXTRACT-01 | Phase 17 | Planned |
| EXTRACT-02 | Phase 17 | Planned |
| EXTRACT-03 | Phase 17 | Planned |
| EXTRACT-04 | Phase 17 | Planned |
| MANSION-01 | Phase 18 | Planned |
| MANSION-02 | Phase 18 | Planned |
| MANSION-03 | Phase 18 | Planned |
| MANSION-04 | Phase 18 | Planned |

**Coverage:**
- v1.4 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0

---
*Requirements defined: 2026-03-27*
*Last updated: 2026-03-27 for milestone v1.4 planning*
