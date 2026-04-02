# Phase 50: Message Intent Routing - Plan

**Phase:** 50  
**Name:** Message Intent Routing  
**Status:** Ready for execution  
**Created:** 2026-03-28

## Goal

Implement intelligent message intent routing where AI classifies messages into intents (OOC, IC action, rules query, admin) and handles them differently based on session phase. Priority of handling varies by phase.

**Requirements addressed:** INTENT-01, INTENT-02, INTENT-03

## Tasks

### Task 1: Define Intent Classification Schema
- [ ] **1.1** Define message intent enum/types: OOC, social IC, player action, rules query, admin action
- [ ] **1.2** Add intent classification to message processing pipeline
- [ ] **1.3** Store intent with message metadata for debugging/logging
- [ ] **1.4** Create Pydantic models for intent classification requests/responses

**Expected artifact:** Intent schema and classification contract

### Task 2: Implement Intent Classification via Router
- [ ] **2.1** Extend router model to classify message intent
- [ ] **2.2** Add intent classification prompt to router
- [ ] **2.3** Handle classification failures gracefully (default to a safe intent)
- [ ] **2.4** Add tests for intent classification

**Expected artifact:** Router can classify messages by intent

### Task 3: Phase-Dependent Intent Handling
- [ ] **3.1** Implement handling rules per intent type:
  - OOC: Always responded, may buffer in high-intensity phases
  - Social IC: Normal in exploration, brief in combat
  - Player action: Primary focus during SCENE_ROUND_OPEN, COMBAT
  - Rules query: Respond when asked, may defer in combat
  - Admin action: Always processed
- [ ] **3.2** Create intent handler registry/strategy pattern
- [ ] **3.3** Add user feedback explaining why message was handled differently
- [ ] **3.4** Test phase-dependent behavior

**Expected artifact:** Different intents handled differently based on phase

### Task 4: Implement Buffered Messages
- [ ] **4.1** Add message buffering during SCENE_ROUND_RESOLVING, COMBAT
- [ ] **4.2** Implement deferred message delivery after phase ends
- [ ] **4.3** Option to show buffered messages after phase transition
- [ ] **4.4** Test buffering behavior

**Expected artifact:** Messages buffered appropriately during high-intensity phases

### Task 5: Integrate with Scene Round Collection
- [ ] **5.1** During SCENE_ROUND_OPEN: prioritize player actions, defer OOC
- [ ] **5.2** During SCENE_ROUND_RESOLVING: buffer all until resolution
- [ ] **5.3** Handle edge cases (late submissions, edits)
- [ ] **5.4** Test integration with Phase 49 functionality

**Expected artifact:** Works seamlessly with Scene Round Collection

### Task 6: Tests and Verification
- [ ] **6.1** Unit tests for intent classification
- [ ] **6.2** Integration tests for phase-dependent handling
- [ ] **6.3** Test buffering behavior
- [ ] **6.4** Run existing test suite to ensure no regressions

**Expected artifact:** Tests passing, no regressions

## Technical Constraints (from Research)

1. **Message Content Intent** - Must be enabled in Discord Developer Portal
2. **Interaction Token** - Must respond/defer within 3 seconds
3. **Router Model** - Classification adds latency; optimize prompt

## Dependencies

- Phase 47 (Session Phases) - SessionPhase enum
- Phase 48 (Pre-Play Onboarding) - Session flow
- Phase 49 (Scene Round Collection) - Round collection integration
- `src/dm_bot/router/` - Existing router implementation
- `src/dm_bot/discord_bot/client.py` - Message handling

## Success Criteria

- [ ] Messages classified by intent (OOC, IC, action, rules, admin)
- [ ] Phase-dependent handling works correctly
- [ ] User sees feedback explaining handling rationale
- [ ] Buffered messages delivered after phase transitions
- [ ] Integrates with Scene Round Collection
- [ ] Tests pass
- [ ] No regressions in existing functionality
