# Track C vC.1.2 Overall Research: Multiplayer Session Governance

**Date:** 2026-03-28
**Scope:** Phases 48, 49, 50, 51

## Executive Summary
This research artifact evaluates the feasibility and implementation approach for Discord-based multiplayer session governance in Call of Cthulhu (Track C, vC.1.2). The core challenge is adapting synchronous tabletop pacing to an asynchronous Discord text environment. The proposed phases (Onboarding, Scene Collection, Intent Routing) are technically feasible using `discord.py`. 

By deepening the rulebook analysis and confirming Discord's technical constraints, this research provides concrete, actionable boundaries for the upcoming planning phases.

## Feasibility Verdict
**Feasible with Scope Adjustments.** Phases 48, 49, and 50 form a cohesive, highly feasible "Session Governance" loop that tightly maps to the Keeper rulebook's intent. Phase 51 (Campaign Status Visibility) is technically viable but represents an out-of-scope UI surface for this milestone.

## Call of Cthulhu Rulebook Implications
Based on direct extraction from the CoC 7th Edition Rulebook (克苏鲁的呼唤第七版):

1. **Time and Rounds (Pacing):**
   - *Outside Combat (Narrative Time):* Time is flexible. However, to translate this to a Discord medium where multiple players type at different speeds, **Phase 49 (Scene Round Collection)** is structurally mandatory. We must enforce a "Declare First, Resolve Together" flow to simulate the Keeper asking "What is everyone doing?" before resolving a single player's action.
   - *Inside Combat:* Highly structured. Participants act in descending **DEX** order. If DEX is tied, highest combat skill acts first.

2. **Action Declaration:** 
   - A player must state their *Goal* before rolling. In combat, the opponent must declare if they are *Fighting Back* or *Dodging* before dice are rolled. This means our action collection state machine must support "Reactions" as a distinct input type during combat.

3. **Core Onboarding Requirements (Phase 48):**
   - The onboarding must not be a lore dump. It strictly needs to cover four mechanical pillars to start play: 
     1. **D100 Roll:** Roll equal to or under skill. 
     2. **Sanity (SAN):** Mental resilience, consequences of witnessing horrors.
     3. **Pushing the Roll:** Re-rolling failed non-combat checks with severe consequences upon second failure.
     4. **Luck:** Group luck or situational fortune.

## Discord Official Constraints & Capabilities
Verified against `discord.py` API and Discord Developer documentation:

1. **Message Content Intent:** **CRITICAL.** The bot MUST have the Privileged Message Content Intent enabled in the Discord Developer Portal. Without this, `on_message` will be empty for regular text, breaking Phase 49 and 50 entirely.
2. **Persistent Views (Phase 48 Onboarding):**
   - Buttons must be part of a `discord.ui.View`.
   - To survive a bot restart or extended idle time, the View must have `timeout=None`.
   - Every button must have a statically defined `custom_id`.
   - The view must be registered via `bot.add_view(view)` in the `setup_hook`.
3. **Interaction Tokens:** When a user clicks an Onboarding button, the interaction token is valid for 15 minutes. The bot MUST respond or `defer()` within 3 seconds, or the Discord UI will show an "Interaction Failed" error.
4. **Rate Limits on Edits:** Discord strictly limits message edits to 5 edits per 5 seconds per message. For Phase 49 (Live Action Pool Status), we cannot update the message on every single keystroke or instant submission. We must implement debounce/batching logic.

## Phase 51 Boundary Recheck
**Recommendation: MOVE TO vC.1.3.** 
Phase 51 represents "Campaign Surfaces And Intent Clarity" (the exact stated goal of vC.1.3 in ROADMAP.md). 
- *Why:* vC.1.2 is about *control flow* (intents, rounds, onboarding). Building persistent UI elements (pinned messages tracking HP/SAN/Location) requires the engine from Phase 49/50 to be 100% stable. Mingling state-engine development (49/50) with UI-surface development (51) risks severe scope bloat and difficult debugging.
- *Action:* Proceed with 48, 49, 50. Formally defer 51 to vC.1.3.

## Planning Implications per Phase (Ready for /gsd-plan-phase)

### Phase 48: Pre-Play Onboarding
- **Flow:** Trigger automatically on `SessionPhase.ONBOARDING`. 
- **Tech:** Use a single, edited persistent View message with "Next" buttons, looping through: *Welcome -> D100 -> Pushing -> SAN/Luck -> Confirm*.
- **State:** Keep an `onboarding_ready_players` set in the DB. Transition to `SCENE_ROUND_OPEN` when all players click Confirm.

### Phase 49: Scene Round Collection
- **Flow:** In `SCENE_ROUND_OPEN`, intercept `on_message`. If intent is Action, add to `ActionPool`. 
- **Tech:** Do *not* use Python `asyncio.sleep()` for timeouts (they die on restart). Use explicit Keeper `/resolve-round` command to transition to `SCENE_ROUND_RESOLVING`.
- **Status UI:** Post a message "Waiting for actions: [Player A], [Player B]". Debounce updates to this message to respect the 5/5s rate limit.

### Phase 50: Message Intent Routing
- **Flow:** Pre-process messages before they hit the Action Pool or the Narrator LLM.
- **Tech:** 
  - **Layer 1 (Fast Heuristic):** If message starts with `(`, `[`, or `OOC:`, instantly tag as OOC.
  - **Layer 2 (LLM Router):** Use a structured-output local LLM to classify natural text into: `action`, `ooc`, `rules_query`, `social_ic`.
- **Integration:** Inject the current `SessionPhase` into the router's system prompt (e.g., "We are in combat, default ambiguous text to 'action'").

## Common Pitfalls to Avoid
- **Race Conditions:** Multiple players typing at once during Phase 49. DB transactions must handle concurrent action submissions safely.
- **LLM Latency Blocking Event Loop:** Running the Phase 50 routing LLM on the main Discord thread will cause the bot to disconnect. Ensure `on_message` intent classification runs via `asyncio.to_thread` or fully async LLM clients.
