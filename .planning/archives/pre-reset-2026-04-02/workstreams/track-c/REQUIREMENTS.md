# Requirements: Discord AI Keeper - Track C

**Defined:** 2026-03-29
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

---

## vC.1.2 Requirements (Track C)

Milestone: C2 Multiplayer Session Governance

### Session Phases

- [x] **SESSION-01**: Campaign sessions have explicit phases for onboarding, lobby, ready, admin-start, scene-round-open, scene-round-resolving, combat, and pause
- [x] **SESSION-02**: All required players can ready without automatically starting the adventure before an admin/KP start action
- [x] **SESSION-03**: Session phase transitions are visible enough to explain why a player message was accepted, buffered, or ignored

### Session Onboarding

- [x] **ONBOARD-01**: A campaign can surface a structured pre-play onboarding stage before free scene play begins
- [x] **ONBOARD-02**: Onboarding can present minimum-rules guidance and module theme/expectation summaries without dumping the entire rulebook
- [x] **ONBOARD-03**: KP/admin can choose or confirm new-player-friendly onboarding scope before starting the session

### Scene Round Collection

- [x] **ROUND-01**: Non-combat scenes can collect one action declaration per player before resolving a shared KP response
- [x] **ROUND-02**: Players can see whether they have already submitted an action this round
- [x] **ROUND-03**: KP/admin can resolve or advance the scene round without relying on implicit narration timing

### Message Intent Routing

- [x] **INTENT-01**: Natural messages are classified into clearer intents than only ignore/process
- [x] **INTENT-02**: Archive, gameplay, admin, and rules intents do not silently steal each other's messages
- [x] **INTENT-03**: OOC, social IC, player action, rules, and admin intents can be handled differently by session phase

### Campaign And Adventure Visibility

- [ ] **VIS-01**: Users can clearly see which adventure is loaded into a campaign
- [ ] **VIS-02**: Users can clearly see campaign members and ready status
- [ ] **VIS-03**: Users can clearly see the current scene/location or understand when no scene is active

---

## vC.1.3 Requirements (Track C)

Milestone: C3 Campaign Surfaces And Intent Clarity

### Visibility Core

- [x] **SURF-01**: Discord-facing surfaces read from a canonical visibility model for campaign, adventure, session, and current runtime state rather than assembling ad hoc text independently per command
- [x] **SURF-02**: The visibility model includes explicit waiting/blocker reasons so users and operators can see what the session is currently waiting on
- [x] **SURF-03**: The visibility model includes routing outcome plus a short explanation contract describing why a message was processed, buffered, ignored, or deferred
- [x] **SURF-04**: The visibility model can surface existing canonical player snapshot state, including participation status and already-existing HP / SAN / attribute values, without redefining character semantics in Track C

### Player-Facing Surfaces

- [ ] **PLAY-01**: Players can see the current campaign/adventure identity and current session state from Discord without relying on hidden operator knowledge
- [ ] **PLAY-02**: Players can see shared round/session waiting reasons, including who or what the table is waiting on
- [ ] **PLAY-03**: Players receive short, practical explanations when their messages are ignored, buffered, or handled under a different routing path
- [ ] **PLAY-04**: Player-facing status surfaces stay concise and readable in ordinary Discord play channels

### KP / Operator Surfaces

- [ ] **OPS-01**: KP/operators have a separate operational surface that shows session phase, round state, blockers, and current adventure/runtime state
- [ ] **OPS-02**: KP/operators can see per-player participation state such as ready, submitted, pending, and other already-canonical session statuses
- [ ] **OPS-03**: KP/operators can inspect routing outcomes and short routing diagnostics for incoming messages without digging through raw logs

### Current-Only Visibility

- [ ] **CURR-01**: Discord surfaces can show the currently loaded campaign/adventure/session identity and status without requiring a broader multi-campaign browser in this milestone
- [ ] **CURR-02**: When no active scene or session state exists, users get an explicit “not active / not loaded / waiting to start” style explanation instead of ambiguous silence

### Activity-Ready Boundary

- [ ] **ACT-01**: Visibility state and surface contracts are structured so a future Discord Activity UI can reuse the same canonical model without rewriting business logic
- [ ] **ACT-02**: This milestone does not require building the Discord Activity UI itself

## Future Requirements

### Broader Visibility

- **LIST-01**: Users can browse broader campaign/adventure inventories beyond the currently active runtime context
- **LIST-02**: Operators can inspect richer historical visibility and cross-session status views

### Activity UI

- **ACT-03**: Discord Activity UI can render campaign/session/player visibility through a richer interactive surface

### Character Semantics

- **CHAR-01**: Character snapshot semantics for HP / SAN / attributes can be redesigned or normalized across tracks when needed

## Out of Scope

| Feature | Reason |
|---------|--------|
| Discord Activity UI implementation | Deferred until after activity-ready core contracts exist |
| Character-system redesign for HP / SAN / attributes | Track C should surface existing canonical state, not redefine character semantics |
| Broad campaign/adventure browsing across all records | vC.1.3 focuses on current-state clarity first |
| Deep debug-only internals for ordinary players | Player surfaces should remain concise and practical |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SESSION-01 | 47 | Complete |
| SESSION-02 | 47 | Complete |
| SESSION-03 | 47 | Complete |
| ONBOARD-01 | 48 | Complete |
| ONBOARD-02 | 48 | Complete |
| ONBOARD-03 | 48 | Complete |
| ROUND-01 | 49 | Complete |
| ROUND-02 | 49 | Complete |
| ROUND-03 | 49 | Complete |
| INTENT-01 | 50 | Complete |
| INTENT-02 | 50 | Complete |
| INTENT-03 | 50 | Complete |
| VIS-01 | 51 | Pending |
| VIS-02 | 51 | Pending |
| VIS-03 | 51 | Pending |
| SURF-01 | 51 | Complete |
| SURF-02 | 51 | Complete |
| SURF-03 | 51 | Complete |
| SURF-04 | 51 | Complete |
| PLAY-01 | TBD | Pending |
| PLAY-02 | TBD | Pending |
| PLAY-03 | TBD | Pending |
| PLAY-04 | TBD | Pending |
| OPS-01 | TBD | Pending |
| OPS-02 | TBD | Pending |
| OPS-03 | TBD | Pending |
| CURR-01 | TBD | Pending |
| CURR-02 | TBD | Pending |
| ACT-01 | TBD | Pending |
| ACT-02 | TBD | Pending |

**Coverage:**
- vC.1.3 requirements: 14 total
- Mapped to phases: TBD
- Unmapped: 0 ✓

---
*Requirements updated: 2026-03-29 - Added vC.1.3 Campaign Surfaces And Intent Clarity requirements*
*Last updated: 2026-03-29 for vC.1.3*
