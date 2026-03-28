# Phase 48: Pre-Play Onboarding - Plan

**Phase:** 48  
**Name:** Pre-Play Onboarding  
**Status:** Ready for execution  
**Created:** 2026-03-28

## Goal

Implement structured pre-play onboarding stage that runs automatically after `/start-session` command completes and before first scene narration. Onboarding presents interactive guidance covering theme, rules, and tips with KP-customizable content.

## Tasks

### Task 1: Extend SessionPhase and State Management
- [ ] **1.1** Add `ONBOARDING` phase handling in `session_store.py` if not already present
- [ ] **1.2** Add `onboarding_completion` tracking to `CampaignSession` model (per-player or session-wide)
- [ ] **1.3** Add `onboarding_content` field to support adventure-package custom content
- [ ] **1.4** Ensure `transition_to()` handles `AWAITING_ADMIN_START → ONBOARDING` correctly

**Expected artifact:** Updated `CampaignSession` model with onboarding state fields

### Task 2: Create Onboarding Content System
- [ ] **2.1** Define default onboarding content structure (theme, rules summary, tips, confirm)
- [ ] **2.2** Create COC 7E quick-start content (D100, SAN, Pushing, Luck)
- [ ] **2.3** Implement adventure-package override mechanism for custom onboarding
- [ ] **2.4** Add adventure schema field for optional custom onboarding sections

**Expected artifact:** Content loading system that merges defaults with adventure overrides

### Task 3: Build Interactive Onboarding View (Discord)
- [ ] **3.1** Create `OnboardingView` class extending `discord.ui.View`
- [ ] **3.2** Implement persistent View with `timeout=None` for survival across restarts
- [ ] **3.3** Add button flow: Welcome → D100 → Pushing → SAN/Luck → Confirm
- [ ] **3.4** Register View in bot's `setup_hook` via `bot.add_view()`
- [ ] **3.5** Handle button interactions with `defer()` within 3 seconds

**Expected artifact:** Interactive onboarding message with buttons

### Task 4: Implement Onboarding Flow Controller
- [ ] **4.1** Create `OnboardingController` to manage flow state
- [ ] **4.2** Trigger onboarding automatically after `/start-session` completes
- [ ] **4.3** Track per-player confirmation state
- [ ] **4.4** Auto-transition to `SCENE_ROUND_OPEN` when all players confirm (or timeout)
- [ ] **4.5** Handle timeout scenario gracefully

**Expected artifact:** Onboarding flow controller that manages phase transitions

### Task 5: Integrate with Adventure Loading
- [ ] **5.1** Load adventure's custom onboarding content (if present) during `/load_adventure`
- [ ] **5.2** Fall back to system defaults if adventure doesn't specify onboarding
- [ ] **5.3** Test KP can customize onboarding via adventure config

**Expected artifact:** Adventure content integration working

### Task 6: Tests and Verification
- [ ] **6.1** Write unit tests for onboarding state transitions
- [ ] **6.2** Write integration tests for button flow
- [ ] **6.3** Verify all players can confirm independently
- [ ] **6.4** Verify timeout handling works correctly
- [ ] **6.5** Run existing test suite to ensure no regressions

**Expected artifact:** Tests passing, no regressions

## Technical Constraints (from Research)

1. **Message Content Intent** - Must be enabled in Discord Developer Portal for bot to read messages
2. **Persistent Views** - Must use `timeout=None`, static `custom_id`, and register in `setup_hook`
3. **Interaction Token** - Must respond/defer within 3 seconds or UI shows error
4. **View Persistence** - Buttons survive bot restart only if properly registered

## Dependencies

- Phase 47 (Session Phases) - Must be complete for SessionPhase enum
- `src/dm_bot/discord_bot/commands.py` - For `/start-session` integration
- `src/dm_bot/orchestrator/session_store.py` - For CampaignSession model

## Success Criteria

- [ ] Onboarding triggers automatically after `/start-session`
- [ ] Players see interactive button-based guidance
- [ ] All players can confirm readiness independently
- [ ] KP can customize onboarding via adventure package
- [ ] System transitions to `SCENE_ROUND_OPEN` after completion
- [ ] Tests pass
- [ ] No regressions in existing functionality
