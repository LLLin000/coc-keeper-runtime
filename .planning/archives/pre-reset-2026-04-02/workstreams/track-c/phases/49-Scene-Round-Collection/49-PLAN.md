# Phase 49: Scene Round Collection - Plan

**Phase:** 49  
**Name:** Scene Round Collection  
**Status:** Ready for execution  
**Created:** 2026-03-28

## Goal

Implement scene round collection where players submit action declarations in natural language, and KP resolves after all players have submitted. Status of who has submitted is visible to all.

**Requirements addressed:** ROUND-01, ROUND-02, ROUND-03

## Tasks

### Task 1: Extend Session State for Round Collection
- [ ] **1.1** Add `pending_actions` field to `CampaignSession` model to store player action submissions
- [ ] **1.2** Add `action_submitters` tracking to know who has submitted
- [ ] **1.3** Ensure session phase includes `SCENE_ROUND_OPEN` and `SCENE_ROUND_RESOLVING` states
- [ ] **1.4** Add methods to set, update, and clear player actions

**Expected artifact:** Updated CampaignSession with round collection state fields

### Task 2: Message Handler Integration
- [ ] **2.1** Modify message handling to detect `SCENE_ROUND_OPEN` phase
- [ ] **2.2** Capture natural language messages as player actions during round collection
- [ ] **2.3** Handle duplicate submissions (latest replaces previous)
- [ ] **2.4** Update status display after each submission

**Expected artifact:** Message handler that collects player actions during scene rounds

### Task 3: Status Display System
- [ ] **3.1** Create status embed showing "已提交: X, Y | 待提交: Z"
- [ ] **3.2** Update status after each player action submission
- [ ] **3.3** Add clear visual indicator when all players have submitted
- [ ] **3.4** Make status visible to all players and KP

**Expected artifact:** Real-time status display visible to all session participants

### Task 4: Resolution Flow
- [ ] **4.1** Add `/resolve-round` command for KP to trigger resolution
- [ ] **4.2** Handle transition: `SCENE_ROUND_OPEN` → `SCENE_ROUND_RESOLVING`
- [ ] **4.3** After KP response, transition back to `SCENE_ROUND_OPEN`
- [ ] **4.4** Clear pending actions after resolution completes

**Expected artifact:** Round resolution flow with proper phase transitions

### Task 5: Edge Case Handling
- [ ] **5.1** Handle case where some players don't submit (KP can proceed with available)
- [ ] **5.2** Handle timeout scenario (optional: auto-clear after X minutes)
- [ ] **5.3** Handle empty submission (should not count as action)
- [ ] **5.4** Handle player who leaves mid-round

**Expected artifact:** Robust edge case handling

### Task 6: Tests and Verification
- [ ] **6.1** Write unit tests for round collection state transitions
- [ ] **6.2** Write integration tests for action submission flow
- [ ] **6.3** Test status display updates correctly
- [ ] **6.4** Run existing test suite to ensure no regressions

**Expected artifact:** Tests passing, no regressions

## Technical Constraints (from Research)

1. **Message Content Intent** - Must be enabled in Discord Developer Portal for bot to read messages
2. **Interaction Token** - Must respond/defer within 3 seconds or UI shows error
3. **Rate Limits** - 5 edits/5s rate limit on message edits

## Dependencies

- Phase 47 (Session Phases) - Must be complete for SessionPhase enum
- Phase 48 (Pre-Play Onboarding) - Flow continues from onboarding completion
- `src/dm_bot/discord_bot/commands.py` - For message handling and commands
- `src/dm_bot/orchestrator/session_store.py` - For CampaignSession model

## Success Criteria

- [ ] Players can submit actions via natural language messages
- [ ] Status shows who has submitted and who is pending
- [ ] KP can trigger resolution after all submit
- [ ] Phase transitions work correctly: SCENE_ROUND_OPEN → SCENE_ROUND_RESOLVING → SCENE_ROUND_OPEN
- [ ] Edge cases handled gracefully
- [ ] Tests pass
- [ ] No regressions in existing functionality
