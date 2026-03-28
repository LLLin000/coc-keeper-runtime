# Roadmap: Track C - Discord 交互层

## Active Milestone

**vC.1.1** - C1 Channel Governance And Command Discipline Hardening
- **Primary Track:** Track C - Discord 交互层
- **Goal:** Make channel responsibilities obvious and enforceable for players, operators, and admins

---

## vC.1.1 Phases

- [x] **Phase 44: Channel Structure** - Define channel roles and bindings
- [x] **Phase 45: Command Routing** - Implement channel-aware command routing
- [ ] **Phase 46: Guidance & Polish** - Add guidance, reduce clutter

### Phase 44: Channel Structure

**Goal:** Define and implement channel role structure for archive, admin, game, and trace channels.

**Depends on:** Nothing (first phase of vC.1.1)

**Requirements:** CHAN-01, CHAN-02, CHAN-03

**Success Criteria** (what must be TRUE):
  1. Each channel type (archive/admin/game/trace) has explicit role definition
  2. Commands are bound to appropriate channel types
  3. Channel bindings are configurable via settings

**Plans:** 1 plan
- [ ] 44-01-PLAN.md — Channel structure foundation (game_channel binding + ChannelEnforcer)

### Phase 45: Command Routing

**Goal:** Implement channel-aware routing with clear redirect messages for wrong-channel usage.

**Depends on:** Phase 44

**Requirements:** CHAN-04, GUIDE-01, GUIDE-02

**Success Criteria** (what must be TRUE):
  1. Wrong-channel commands show redirect message to correct channel
  2. Command help includes channel recommendation
  3. Contextual guidance based on current channel

**Plans:** TBD

### Phase 46: Guidance & Polish

**Goal:** Add user guidance and reduce command clutter in game halls.

**Depends on:** Phase 45

**Requirements:** GUIDE-03, CLUTTER-01, CLUTTER-02, CLUTTER-03

**Success Criteria** (what must be TRUE):
  1. New users see welcome message with channel structure
  2. Long outputs use ephemeral mode
  3. Diagnostics stay in trace/admin channels
  4. Gameplay narration stays focused in game halls

**Plans:** TBD

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 44. Channel Structure | 1/1 | Planning complete | - |
| 45. Command Routing | 0/1 | Not started | - |
| 46. Guidance & Polish | 0/1 | Not started | - |

---
*Last updated: 2026-03-28 for milestone vC.1.1*
