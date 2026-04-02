# Milestone vC.1.1: Channel Governance And Command Discipline Hardening

**Status:** ✅ SHIPPED 2026-03-28
**Primary Track:** Track C - Discord 交互层
**Phases:** 44-46
**Total Plans:** 3

## Overview

Goal: Make channel responsibilities obvious and enforceable for players, operators, and admins.

## Phases

### Phase 44: Channel Structure

**Goal:** Define and implement channel role structure for archive, admin, game, and trace channels.

**Depends on:** Nothing (first phase of vC.1.1)

**Requirements:** CHAN-01, CHAN-02, CHAN-03

**Plans:** 1 plan

- [x] 44-01-PLAN.md — Channel structure foundation (game_channel binding + ChannelEnforcer)

**Details:**
- Added `_game_channels` dict to SessionStore
- Created ChannelEnforcer class with ChannelType enum and ChannelPolicy dataclass
- Implemented channel type detection and command policy enforcement
- 13 tests passing

---

### Phase 45: Command Routing

**Goal:** Implement channel-aware routing with clear redirect messages for wrong-channel usage.

**Depends on:** Phase 44

**Requirements:** CHAN-04, GUIDE-01, GUIDE-02

**Plans:** 1 plan

- [x] 45-01-PLAN.md — Command routing integration

**Details:**
- Integrated ChannelEnforcer into BotCommands
- Added check_channel() helper method
- Applied channel checks to 9 commands (show_sheet, list_profiles, profile_detail, start_character_builder, builder_reply, admin_profiles, take_turn, load_adventure, ready_for_adventure)
- Redirect messages show correct channel with Chinese guidance

---

### Phase 46: Guidance & Polish

**Goal:** Add user guidance and reduce command clutter in game halls.

**Depends on:** Phase 45

**Requirements:** GUIDE-03, CLUTTER-01, CLUTTER-02, CLUTTER-03

**Plans:** 1 plan

- [x] 46-01-PLAN.md — Guidance and polish tasks

**Details:**
- Enhanced /setup command with comprehensive channel structure guidance
- Verified ephemeral mode on long outputs (list_profiles, profile_detail, etc.)
- Verified diagnostic commands use ephemeral (setup_check, debug_status)
- Verified gameplay narration stays in game halls via ChannelEnforcer

---

## Requirements Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| CHAN-01 | 44 | ✅ Implemented |
| CHAN-02 | 44 | ✅ Implemented |
| CHAN-03 | 44 | ✅ Implemented |
| CHAN-04 | 45 | ✅ Implemented |
| GUIDE-01 | 45 | ✅ Implemented |
| GUIDE-02 | 45 | ✅ Implemented |
| GUIDE-03 | 46 | ✅ Implemented |
| CLUTTER-01 | 46 | ✅ Implemented |
| CLUTTER-02 | 46 | ✅ Implemented |
| CLUTTER-03 | 46 | ✅ Implemented |

**Requirements shipped:** 10/18 (remaining: STABLE-01, STABLE-02, STABLE-03, UX-01, UX-02, UX-03, UX-04, are deferred to future milestones)

---

## Artifacts Created/Modified

| File | Description |
|------|-------------|
| src/dm_bot/discord_bot/channel_enforcer.py | Channel enforcement module |
| src/dm_bot/discord_bot/commands.py | Added channel checks + welcome guidance |
| src/dm_bot/orchestrator/session_store.py | Added game_channel binding |
| tests/test_channel_enforcer.py | 13 passing tests |

---

## Key Accomplishments

1. Created ChannelEnforcer with 4 channel types (ARCHIVE, GAME, ADMIN, TRACE)
2. Integrated channel enforcement into 9 slash commands
3. Implemented redirect messages for wrong-channel usage
4. Enhanced /setup with channel structure guidance
5. All 130 tests pass

---

_For current project status, see .planning/ROADMAP.md_
