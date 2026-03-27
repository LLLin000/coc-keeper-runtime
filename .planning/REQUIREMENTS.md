# Requirements: Discord AI DM

**Defined:** 2026-03-27
**Core Value:** Run a real multiplayer D&D session in Discord where a local AI DM can narrate, roleplay multiple characters, and enforce heavy rules flow without constant manual bookkeeping.

## v1.1 Requirements

### Structured Adventure Runtime

- [ ] **MOD-01**: Operators can load a structured adventure package that declares scenes, state variables, triggers, reveal rules, and endings instead of relying on freeform raw script prompting.
- [ ] **MOD-02**: The runtime validates adventure packages before play and fails closed when required module data is missing or malformed.
- [ ] **MOD-03**: Canonical adventure state tracks room progress, discovered clues, trigger flags, timers, and module-specific variables independently of Discord chat history.
- [ ] **MOD-04**: The DM runtime can treat the narrator as omniscient over module data while still enforcing reveal policy so hidden information is only surfaced when allowed by current state or player discovery.

### 疯狂之馆 Module

- [ ] **MANS-01**: Players can play `疯狂之馆` from the opening hall through the four branch wings using structured room progression rather than ad hoc narration.
- [ ] **MANS-02**: The module enforces `疯狂之馆`'s special mechanics, including countdown pressure and room-specific costs or conditions, through deterministic state updates.
- [ ] **MANS-03**: The module tracks key hidden-status mechanics such as blood progress, sensory loss, saint-state style transformations, and other branch-specific consequences required by the script.
- [ ] **MANS-04**: The module supports the story's branching discoveries and endings so the session can conclude differently based on party choices and accumulated state.

### Discord Gameplay UX

- [ ] **UX-01**: Campaign-to-channel binding and joined-player membership survive bot restarts so ordinary channel messages continue to work without forcing the group to rebind and rejoin every time.
- [ ] **UX-02**: Joined players in a bound channel can use ordinary channel messages as their primary gameplay input during packaged adventures, with clear handling for OOC chatter and combat turn gating.
- [ ] **UX-03**: Bot replies and commands surface the current room, active pressure, known objectives, and next-action guidance clearly enough that a small group can keep playing without operator guesswork.
- [ ] **UX-04**: Operators can inspect packaged adventure state, current node, discovered clues, and blocked triggers from a compact command or debug surface.

### Reusable Adventure Pipeline

- [ ] **PACK-01**: Future adventures can be added by authoring a new package in the same schema instead of modifying core runtime code for each new script.
- [ ] **PACK-02**: The repository includes practical docs for loading, running, and authoring packaged adventures, using `疯狂之馆` as the first formal example.

## v2 Requirements

### Adventure Authoring And GM Controls

- **AUTHR-01**: Operators can author or edit adventures through a higher-level authoring tool instead of hand-editing JSON.
- **AUTHR-02**: The runtime supports per-player secret handouts or whisper reveals as a first-class mechanic.
- **AUTHR-03**: Operators can override or patch packaged adventure state live during a session without editing stored files manually.
- **AUTHR-04**: The module schema supports richer puzzle scripting and reusable logic macros beyond the first formal adventure set.

## Out Of Scope

| Feature | Reason |
|---------|--------|
| Running `疯狂之馆` by feeding the raw `.docx` directly to the narrator | Hidden-state modules need deterministic structure and reveal control. |
| A visual module editor in this milestone | The first priority is a real schema and one real module, not editor UI. |
| Rebuilding combat, rules, or character import foundations from scratch | Those shipped in v1.0 and this milestone builds on them. |
| Multi-platform chat runtimes outside Discord | Discord remains the sole runtime surface for this milestone. |
| NSFW-specific module behavior | Runtime and module quality are the priority for this round. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| MOD-01 | Phase 6 | Pending |
| MOD-02 | Phase 6 | Pending |
| MOD-03 | Phase 6 | Pending |
| MOD-04 | Phase 6 | Pending |
| MANS-01 | Phase 7 | Pending |
| MANS-02 | Phase 7 | Pending |
| MANS-03 | Phase 7 | Pending |
| MANS-04 | Phase 7 | Pending |
| UX-01 | Phase 8 | Pending |
| UX-02 | Phase 8 | Pending |
| UX-03 | Phase 8 | Pending |
| UX-04 | Phase 8 | Pending |
| PACK-01 | Phase 8 | Pending |
| PACK-02 | Phase 8 | Pending |

**Coverage:**
- v1.1 requirements: 14 total
- Mapped to phases: 14
- Unmapped: 0

---
*Requirements defined: 2026-03-27*
*Last updated: 2026-03-27 after starting milestone v1.1*
