# Requirements: Discord AI Keeper - Track E vE.3.2

**Defined:** 2026-03-31
**Milestone:** vE.3.2 - Gap Closure & Integration
**Goal:** Fill critical gaps in COC integration and Discord bot functionality

## Core Value

Close the identified gaps from codebase mapping to make the Discord AI Keeper system production-ready for multiplayer COC sessions.

---

## High Priority Requirements

### Skill Usage Tracking (SKILL-TRACK)

- [ ] **SKILL-TRACK-01**: Combat system tracks which skills are used during each combat encounter
- [ ] **SKILL-TRACK-02**: Session state stores skill usage history per character
- [ ] **SKILL-TRACK-03**: Post-session improvement phase can access skill usage data
- [ ] **SKILL-TRACK-04**: E2E scenario validates skill tracking across combat → improvement flow

### Visibility Dispatcher (VIS-DISP)

- [ ] **VIS-DISP-01**: Visibility dispatcher sends messages to actual Discord channels
- [ ] **VIS-DISP-02**: DM support works for private player messages
- [ ] **VIS-DISP-03**: Group DM support works for KP-to-party communications
- [ ] **VIS-DISP-04**: Visibility leak detection prevents gm_only content reaching players
- [ ] **VIS-DISP-05**: Integration tests validate all 3 TODOs from visibility_dispatcher.py

### Creature Bestiary (BESTIARY)

- [ ] **BESTIARY-01**: Bestiary data structure defined for COC creatures
- [ ] **BESTIARY-02**: Stats for 10+ common COC creatures (ghouls, deep ones, zombies, cultists, etc.)
- [ ] **BESTIARY-03**: Creature stats integrate with combat system
- [ ] **BESTIARY-04**: Sanity loss values linked to creature encounters
- [ ] **BESTIARY-05**: Creatures usable in fuzhe_mini adventure scenarios

---

## Medium Priority Requirements

### Chase Rules (CHASE)

- [ ] **CHASE-01**: COC 7e chase mechanics implemented (pursuer/fleeer, CON rolls, obstacles)
- [ ] **CHASE-02**: Chase state machine with location tracking
- [ ] **CHASE-03**: Obstacle resolution with skill checks
- [ ] **CHASE-04**: Chase conclusion conditions (escape, capture, combat)
- [ ] **CHASE-05**: E2E scenario tests chase flow

### Archive Repository (ARCHIVE)

- [ ] **ARCHIVE-01**: Archive repository implements full CRUD operations
- [ ] **ARCHIVE-02**: Character profile storage and retrieval
- [ ] **ARCHIVE-03**: Campaign state persistence
- [ ] **ARCHIVE-04**: Archive wired into RuntimeTestDriver
- [ ] **ARCHIVE-05**: E2E tests validate archive operations

### Character Builder Integration (BUILDER)

- [ ] **BUILDER-01**: Character builder wired into RuntimeTestDriver
- [ ] **BUILDER-02**: Builder produces valid archive profiles
- [ ] **BUILDER-03**: Builder integrates with COC rules for validation
- [ ] **BUILDER-04**: E2E scenario validates full builder flow

---

## Low Priority Requirements

### Equipment System (EQUIP)

- [ ] **EQUIP-01**: Weapon database with COC 7e stats
- [ ] **EQUIP-02**: Armor database with protection values
- [ ] **EQUIP-03**: Equipment effects on combat resolution
- [ ] **EQUIP-04**: Basic inventory management
- [ ] **EQUIP-05**: Equipment usable in scenarios

---

## Out of Scope

- **Vehicle Combat**: Drive Auto, Pilot integration (defer to vE.4.x)
- **Poison/Disease**: COC 7e Chapter 8 mechanics (defer to vE.4.x)
- **Book Tomes Reading Mechanics**: Detailed reading/sanity mechanics (defer to vE.4.x)
- **Expanded Magic System**: More spells, ritual casting time (defer to vE.4.x)
- **Full Character Sheet UI**: Complete character sheet panels (Track B responsibility)

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SKILL-TRACK-01 | E79 | Planned |
| SKILL-TRACK-02 | E79 | Planned |
| SKILL-TRACK-03 | E79 | Planned |
| SKILL-TRACK-04 | E79 | Planned |
| VIS-DISP-01 | E80 | Planned |
| VIS-DISP-02 | E80 | Planned |
| VIS-DISP-03 | E80 | Planned |
| VIS-DISP-04 | E80 | Planned |
| VIS-DISP-05 | E80 | Planned |
| BESTIARY-01 | E81 | Planned |
| BESTIARY-02 | E81 | Planned |
| BESTIARY-03 | E81 | Planned |
| BESTIARY-04 | E81 | Planned |
| BESTIARY-05 | E81 | Planned |
| CHASE-01 | E82 | Planned |
| CHASE-02 | E82 | Planned |
| CHASE-03 | E82 | Planned |
| CHASE-04 | E82 | Planned |
| CHASE-05 | E82 | Planned |
| ARCHIVE-01 | E83 | Planned |
| ARCHIVE-02 | E83 | Planned |
| ARCHIVE-03 | E83 | Planned |
| ARCHIVE-04 | E83 | Planned |
| ARCHIVE-05 | E83 | Planned |
| BUILDER-01 | E84 | Planned |
| BUILDER-02 | E84 | Planned |
| BUILDER-03 | E84 | Planned |
| BUILDER-04 | E84 | Planned |
| EQUIP-01 | E85 | Planned |
| EQUIP-02 | E85 | Planned |
| EQUIP-03 | E85 | Planned |
| EQUIP-04 | E85 | Planned |
| EQUIP-05 | E85 | Planned |

---
*Last updated: 2026-03-31 for vE.3.2*
