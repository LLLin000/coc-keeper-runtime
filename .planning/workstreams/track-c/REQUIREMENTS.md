# Requirements: Discord AI Keeper - Track C

**Defined:** 2026-03-28
**Core Value:** Run a real multiplayer Call of Cthulhu session in Discord where a local AI Keeper can narrate, roleplay multiple characters, enforce investigation-heavy rules flow, and keep canonical module state without constant manual bookkeeping.

## vC.1.1 Requirements (Track C)

Milestone: C1 Channel Governance And Command Discipline Hardening

### Channel Discipline

- [ ] **CHAN-01**: Archive channel commands should only work in designated archive channels
- [ ] **CHAN-02**: Admin channel commands should only work in designated admin channels  
- [ ] **CHAN-03**: Game hall commands should be blocked or redirected in non-game channels
- [ ] **CHAN-04**: Wrong-channel commands show clear redirect message to correct channel

### Command Guidance

- [ ] **GUIDE-01**: Command help text includes recommended channel for usage
- [ ] **GUIDE-02**: Channel-specific commands show contextual guidance
- [ ] **GUIDE-03**: New users get welcome message with channel structure explanation

### Command Clutter Reduction

- [ ] **CLUTTER-01**: Long command outputs use ephemeral or follow-up modes
- [ ] **CLUTTER-02**: Diagnostic commands prefer trace/admin channels
- [ ] **CLUTTER-03**: Gameplay narration stays in game halls, not cross-posted

### Command Stability (命令稳定性)

- [ ] **STABLE-01**: Commands with in-progress state (e.g., start-builder) detect existing sessions and reject duplicate invocations with clear message
- [ ] **STABLE-02**: Command state is persisted so mid-command failures don't leave orphaned state
- [ ] **STABLE-03**: Users can cancel/abort in-progress commands gracefully

### UX Improvements (玩家交互体验)

- [ ] **UX-01**: Commands show confirmation prompts before destructive actions (archive, delete, replace)
- [ ] **UX-02**: Error messages are friendly and guide users to correct usage
- [ ] **UX-03**: Loading/processing states are visible to users
- [ ] **UX-04**: Success messages confirm what happened with relevant details

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CHAN-01 | 44 | Pending |
| CHAN-02 | 44 | Pending |
| CHAN-03 | 44 | Pending |
| CHAN-04 | TBD | Pending |
| GUIDE-01 | TBD | Pending |
| GUIDE-02 | TBD | Pending |
| GUIDE-03 | TBD | Pending |
| CLUTTER-01 | TBD | Pending |
| CLUTTER-02 | TBD | Pending |
| CLUTTER-03 | TBD | Pending |
| STABLE-01 | TBD | Pending |
| STABLE-02 | TBD | Pending |
| STABLE-03 | TBD | Pending |
| UX-01 | TBD | Pending |
| UX-02 | TBD | Pending |
| UX-03 | TBD | Pending |
| UX-04 | TBD | Pending |

**Coverage:**
- vC.1.1 requirements: 18 total
- Mapped to phases: TBD
- Unmapped: 0 ✓

---
*Requirements updated: 2026-03-28 - Added command stability and UX requirements*
*Last updated: 2026-03-28 for vC.1.1*

---

## vC.1.2 Requirements (Track C)

Milestone: C2 Multiplayer Session Governance

### Session Phases

- [ ] **SESSION-01**: Campaign sessions have explicit phases for onboarding, lobby, ready, admin-start, scene-round-open, scene-round-resolving, combat, and pause
- [ ] **SESSION-02**: All required players can ready without automatically starting the adventure before an admin/KP start action
- [ ] **SESSION-03**: Session phase transitions are visible enough to explain why a player message was accepted, buffered, or ignored

### Session Onboarding

- [ ] **ONBOARD-01**: A campaign can surface a structured pre-play onboarding stage before free scene play begins
- [ ] **ONBOARD-02**: Onboarding can present minimum-rules guidance and module theme/expectation summaries without dumping the entire rulebook
- [ ] **ONBOARD-03**: KP/admin can choose or confirm new-player-friendly onboarding scope before starting the session

### Scene Round Collection

- [ ] **ROUND-01**: Non-combat scenes can collect one action declaration per player before resolving a shared KP response
- [ ] **ROUND-02**: Players can see whether they have already submitted an action this round
- [ ] **ROUND-03**: KP/admin can resolve or advance the scene round without relying on implicit narration timing

### Message Intent Routing

- [ ] **INTENT-01**: Natural messages are classified into clearer intents than only ignore/process
- [ ] **INTENT-02**: Archive, gameplay, admin, and rules intents do not silently steal each other's messages
- [ ] **INTENT-03**: OOC, social IC, player action, rules, and admin intents can be handled differently by session phase

### Campaign And Adventure Visibility

- [ ] **VIS-01**: Users can clearly see which adventure is loaded into a campaign
- [ ] **VIS-02**: Users can clearly see campaign members and ready status
- [ ] **VIS-03**: Users can clearly see the current scene/location or understand when no scene is active
