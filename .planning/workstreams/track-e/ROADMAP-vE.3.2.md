# Roadmap: Track E - vE.3.2 Gap Closure & Integration

## Milestones

- ✅ **vE.1.1** — Runtime Control Panel Foundations (completed)
- ✅ **vE.2.1** — 全流程交互验证框架 (completed)
- ✅ **vE.2.2** — 统一 Scenario-Driven E2E 验证框架 (complete)
- ✅ **vE.3.1** — Character Lifecycle E2E (complete)
- 🔄 **vE.3.2** — Gap Closure & Integration (in progress)

---

## vE.3.2 Summary

**Goal:** Fill critical gaps in COC integration and Discord bot functionality identified in codebase mapping.

**Planned Phases:**
- Phase E79: Skill Usage Tracking & Combat Integration
- Phase E80: Visibility Dispatcher Completion
- Phase E81: Creature Bestiary & Stats
- Phase E82: Chase Rules Implementation
- Phase E83: Archive Repository Completion
- Phase E84: Character Builder Integration
- Phase E85: Equipment System (optional)

**Depends on:** vE.3.1 (E73-E78) complete

---

## vE.3.2 Phases

- [ ] **Phase E79: Skill Usage Tracking & Combat Integration** — Track skills used during combat for post-session improvement
- [ ] **Phase E80: Visibility Dispatcher Completion** — Complete Discord channel/DM sending (resolve 3 TODOs)
- [ ] **Phase E81: Creature Bestiary & Stats** — Add monster stats for common COC creatures
- [ ] **Phase E82: Chase Rules Implementation** — COC 7e chase mechanics
- [ ] **Phase E83: Archive Repository Completion** — Complete CRUD operations
- [ ] **Phase E84: Character Builder Integration** — Wire into RuntimeTestDriver
- [ ] **Phase E85: Equipment System** — Weapon/armor database (optional)

---

### Phase E79: Skill Usage Tracking & Combat Integration

**Goal:** Implement skill usage tracking during combat encounters so skills used can feed into post-session improvement.

**Depends on:** E78 (vE.3.1 complete)

**Requirements:** SKILL-TRACK-01, SKILL-TRACK-02, SKILL-TRACK-03, SKILL-TRACK-04

**Success Criteria** (what must be TRUE):
1. Combat system records each skill check attempt with skill name and result
2. Session state maintains skill usage history per character per encounter
3. Post-session improvement phase can query which skills were used (and succeeded)
4. E2E scenario validates combat → skill tracking → improvement flow

**Plans:** TBD

---

### Phase E80: Visibility Dispatcher Completion

**Goal:** Complete the visibility dispatcher to actually send messages to Discord channels and DMs, resolving the 3 TODOs in visibility_dispatcher.py.

**Depends on:** E79

**Requirements:** VIS-DISP-01, VIS-DISP-02, VIS-DISP-03, VIS-DISP-04, VIS-DISP-05

**Success Criteria** (what must be TRUE):
1. Messages sent to Discord channels appear in the correct channels
2. Private messages (DMs) reach individual players
3. Group DMs work for KP-to-party communications
4. gm_only content never leaks to player channels (enforced + tested)
5. All 3 TODOs from visibility_dispatcher.py are resolved and tested

**Plans:** TBD

---

### Phase E81: Creature Bestiary & Stats

**Goal:** Create a bestiary system with stats for common COC creatures that integrates with combat and sanity systems.

**Depends on:** E80

**Requirements:** BESTIARY-01, BESTIARY-02, BESTIARY-03, BESTIARY-04, BESTIARY-05

**Success Criteria** (what must be TRUE):
1. Bestiary data structure supports COC creature stats (STR, CON, SIZ, etc.)
2. At least 10 common creatures defined (ghouls, deep ones, zombies, cultists, etc.)
3. Creature stats integrate with combat system (can be targets/attackers)
4. Sanity loss values are linked to creature encounters
5. Creatures can be used in fuzhe_mini adventure scenarios

**Plans:** TBD

---

### Phase E82: Chase Rules Implementation

**Goal:** Implement COC 7e chase mechanics including pursuer/fleeer roles, CON rolls, and obstacle resolution.

**Depends on:** E81

**Requirements:** CHASE-01, CHASE-02, CHASE-03, CHASE-04, CHASE-05

**Success Criteria** (what must be TRUE):
1. Chase mechanics support pursuer/fleeer roles with CON-based rolls
2. Chase state tracks locations and relative positions
3. Obstacles require appropriate skill checks to overcome
4. Chase ends correctly on escape, capture, or transition to combat
5. E2E scenario validates a complete chase flow

**Plans:** TBD

---

### Phase E83: Archive Repository Completion

**Goal:** Complete the archive repository with full CRUD operations and integrate it with RuntimeTestDriver.

**Depends on:** E82

**Requirements:** ARCHIVE-01, ARCHIVE-02, ARCHIVE-03, ARCHIVE-04, ARCHIVE-05

**Success Criteria** (what must be TRUE):
1. Archive repository supports Create, Read, Update, Delete operations
2. Character profiles can be stored and retrieved
3. Campaign state can be persisted across sessions
4. Archive is fully wired into RuntimeTestDriver
5. E2E tests validate archive CRUD operations

**Plans:** TBD

---

### Phase E84: Character Builder Integration

**Goal:** Wire the character builder into RuntimeTestDriver and validate the full builder flow with E2E tests.

**Depends on:** E83

**Requirements:** BUILDER-01, BUILDER-02, BUILDER-03, BUILDER-04

**Success Criteria** (what must be TRUE):
1. Character builder is accessible through RuntimeTestDriver
2. Builder produces valid archive-compatible profiles
3. Builder validates against COC rules (point totals, skill limits)
4. E2E scenario validates full builder → archive → projection flow

**Plans:** TBD

---

### Phase E85: Equipment System

**Goal:** Create an equipment database with weapons and armor that affect combat resolution.

**Depends on:** E84

**Requirements:** EQUIP-01, EQUIP-02, EQUIP-03, EQUIP-04, EQUIP-05

**Success Criteria** (what must be TRUE):
1. Weapon database includes COC 7e weapon stats (damage, range, ammo)
2. Armor database includes protection values
3. Equipment effects are applied in combat resolution
4. Basic inventory management tracks equipped items
5. Equipment can be used in scenario tests

**Plans:** TBD

---

## Progress Table

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| **vE.3.2** | | | |
| 79. Skill Usage Tracking & Combat Integration | 0/1 | Not started | — |
| 80. Visibility Dispatcher Completion | 0/1 | Not started | — |
| 81. Creature Bestiary & Stats | 0/1 | Not started | — |
| 82. Chase Rules Implementation | 0/1 | Not started | — |
| 83. Archive Repository Completion | 0/1 | Not started | — |
| 84. Character Builder Integration | 0/1 | Not started | — |
| 85. Equipment System | 0/1 | Not started | — |

---

*Last updated: 2026-03-31 for milestone vE.3.2*
