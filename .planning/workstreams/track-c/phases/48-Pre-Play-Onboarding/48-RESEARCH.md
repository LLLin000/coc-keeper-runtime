# Phase 48 Research: Pre-Play Onboarding

**Goal:** figure out what must be true before planning implementation.

## What already exists

- `SessionPhase.ONBOARDING` already exists in `src/dm_bot/orchestrator/session_store.py`, and `CampaignSession` already tracks `session_phase`, `player_ready`, `admin_started`, and `phase_history`.
- `/load_adventure` already sets adventure state to `awaiting_ready`, and `/ready` already sends a private role-specific onboarding blurb from `adventure.onboarding_tracks` when present.
- `/start-session` currently skips any structured onboarding and goes straight to `SCENE_ROUND_OPEN`, then sends first-scene opening narration immediately.
- `GameplayOrchestrator.begin_adventure()` currently flips adventure onboarding state to `in_progress` and marks `opening_sent=True`, but there is no real onboarding completion flow behind it.
- Message handling already blocks while `gameplay.onboarding_block_message()` returns a ready-up warning, but that helper only checks `awaiting_ready`, so it will not block normal play once `/start-session` runs.
- Adventure data already supports package-level `onboarding_tracks`, but today those tracks are role-specific private imports, not a session-wide pre-play onboarding stage.

## Key planning implication

This phase is not just "add a nicer start message". It needs a real state transition between **admin start** and **first scene narration**, plus a way to persist and resume that state.

## Biggest gaps to plan around

1. **Session persistence gap**
   - `SessionStore.dump_sessions()` currently does not serialize `session_phase`, `player_ready`, `admin_started`, or `phase_history`.
   - If onboarding lives in session state, it will be lost on restart unless this is added.

2. **Phase gating gap**
   - `handle_channel_message()` and the streaming path only block during the pre-start ready state.
   - Phase 48 needs a distinct "onboarding in progress" gate so players cannot freely advance into scene play before onboarding ends.

3. **Content-model gap**
   - Existing `onboarding_tracks` are per-role and private.
   - ONBOARD-02/03 require a session-wide onboarding package with theme/rules/tips content that KP can override or confirm.
   - That likely means a new package-level onboarding structure, not just reusing role tracks.

4. **Discord UI gap**
   - The codebase does not yet use Discord buttons/views.
   - This phase likely introduces the first `discord.ui.View` + button flow for confirmations/questions/timeout completion.
   - discord.py 2.7 supports views, button callbacks, ephemeral responses, and timeout handling, so the UI path is viable.

## Recommended design shape

- Treat **pre-play onboarding** as its own session-stage state, separate from ready-up.
- Keep the ready flow as-is, but after `/start-session`:
  1. set session phase to `ONBOARDING`
  2. send onboarding content (theme → rules → tips)
  3. collect player confirmations
  4. auto-complete on timeout or once all required players confirm
  5. transition to `SCENE_ROUND_OPEN`
  6. send the first scene narration only after onboarding completes

## Data decisions to make during planning

- **Where does onboarding state live?**
  - Best candidate: `CampaignSession` for phase/ack tracking, plus `adventure_state` for module-specific onboarding metadata.
  - If you split it, define one clear source of truth.
- **How is KP customization represented?**
  - Probably package-level onboarding sections with per-section override text and enabled/disabled flags.
- **How are confirmations tracked?**
  - Session-wide acknowledgment map is the simplest for the "all players confirm or timeout" rule.
- **What happens if content is missing?**
  - Fall back to system templates and/or derive sections from `premise`, `objectives`, and generic rules guidance.

## What to test in this phase

- `/start-session` enters `ONBOARDING` instead of going directly to scene open.
- Player messages are blocked or redirected during onboarding.
- Buttons/confirmations advance the onboarding state correctly.
- Timeout auto-advances cleanly.
- Custom adventure onboarding overrides defaults.
- Missing onboarding content still produces a usable default flow.
- Session state survives save/load with onboarding progress intact.

## Requirements mapping

- **ONBOARD-01**: automatic pre-play onboarding stage after `/start-session`
- **ONBOARD-02**: concise theme/rules/tips guidance, not full rulebook dump
- **ONBOARD-03**: KP/admin can confirm or choose the onboarding scope before play begins

## Planning risk to keep in mind

The current code already has a lightweight per-player onboarding message in `/ready`. Do not duplicate that blindly; phase 48 should be the **session-level onboarding gate** that happens after admin start, not another version of ready-up.
