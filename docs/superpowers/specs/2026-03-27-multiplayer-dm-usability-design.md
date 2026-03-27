# Multiplayer DM Usability Design

**Date:** 2026-03-27

## Goal

Make the Discord D&D bot actually usable for a small group by tightening multiplayer turn flow, improving Chinese DM narration, and shipping a ready-to-run one-shot plus practical operator docs.

## Scope

This design covers three linked deliverables:

1. Multiplayer runtime flow that works predictably in one Discord channel.
2. Chinese DM output and command UX that are easier for players to use.
3. A packaged one-shot adventure template that can be loaded and followed by the DM bot and the human operator.

This does not attempt to become a full campaign authoring platform, map UI, or complete external character sheet sync system.

## Current Problems

- The current command set is functional but not self-explanatory.
- Multiplayer participation exists, but the runtime does not clearly model whose turn it is, which players are in the campaign, or what actions are allowed in scene vs combat.
- Scene mode and combat mode exist, but the state model is too thin to support smooth group play.
- README does not explain how to run a real session.
- There is no packaged adventure content, so the bot has no structured material to anchor a full session.
- Narration works, but it still sounds like a generic narrator more often than a practical Chinese DM.

## Product Shape

The bot remains a single Discord bot bound to a channel/thread. One campaign runs in one channel. Players join that campaign and interact through slash commands. The router stays responsible for structured intent. The narrator stays responsible for DM prose. Deterministic gameplay state decides what is allowed and what state changes happen.

The design should feel closer to Avrae or RPG Sessions in structure: commands drive campaign state, combat has explicit turn control, and diagnostics can explain what the bot thinks is happening. The difference is that this bot remains DM-forward and narration-heavy instead of rules-only.

## Architecture

### 1. Campaign Session Layer

Extend the in-memory session model so it tracks:

- campaign id
- bound channel/guild
- owner id
- joined member ids
- per-user active character reference
- optional ready state / last action marker

This layer remains lightweight and in-memory for active play, while persistence continues to store event traces and restorable gameplay state.

### 2. Gameplay State Layer

Extend gameplay state so it can represent the active table state, not just isolated combat or scene flags.

Required additions:

- active mode: `dm`, `scene`, `combat`
- scene speaker roster
- combat encounter plus current actor
- soft turn policy for non-combat mode
- one-shot metadata such as current scene node, clues discovered, and pending objectives

This is still deterministic state owned by code, not by the narrator model.

### 3. Command UX Layer

Keep the existing slash command model, but reorganize it into a coherent play loop:

- `/setup`
- `/bind_campaign`
- `/join_campaign`
- `/leave_campaign`
- `/import_character`
- `/turn`
- `/enter_scene`
- `/end_scene`
- `/start_combat`
- `/show_combat`
- `/next_turn`
- `/debug_status`
- optional `/load_adventure`

The main usability improvement is not adding many commands; it is making the commands map directly to the mental model of running a table.

The biggest UX change is that slash commands stop being the primary gameplay input. They remain management and state-transition tools, while normal channel messages become the default way players act in character.

### 3.1 Natural Message Intake

In a bound campaign channel, the bot should listen to normal user messages and treat them as candidate player turns.

Recommended behavior:

- normal channel messages are the default gameplay input
- slash commands remain for setup, import, scene/combat transitions, and diagnostics
- bot ignores its own messages and other bot messages
- bot ignores obvious OOC messages, using `//` as the first explicit OOC escape hatch
- bot ignores social chatter that is primarily user-to-user mention traffic

Mention handling should be intent-based, not mention-based. A message that includes another player mention but is still clearly an action declaration should still enter the DM flow. A message that is primarily out-of-character coordination should be ignored.

Examples:

- `@队友 我先去推门，你掩护我` -> valid gameplay input
- `@队友 你晚上还打吗` -> ignored
- `//等我两分钟，我去接水` -> ignored

This keeps the play experience natural without letting the bot consume every line of chatter as a state-changing action.

### 4. Narration Layer

The narrator prompt must be adjusted from “Chinese narrator” to “Chinese D&D DM.”

The output contract should bias toward:

- concise sensory description
- explicit actionable details
- named NPC dialogue when relevant
- clear combat framing
- no repeated filler
- no state invention beyond what the plan and gameplay layer already decided

Scene mode should preserve speaker labeling. DM mode should end with an implied or explicit prompt for player action when appropriate.

### 5. Adventure Package Layer

Introduce a simple structured adventure file format plus operator-facing markdown.

The first package should include:

- adventure summary
- opening hook
- scene nodes
- NPC roster
- monster roster
- clue list
- branching outcomes
- suggested checks and fail-forward notes

This should be lightweight JSON or YAML consumed by code, paired with a readable markdown guide for the human operator.

## Data Flow

### Normal Multiplayer Turn

1. User calls `/turn`.
2. Session layer resolves campaign membership and active character.
3. Gameplay layer checks whether this turn is allowed in the current mode.
4. Router receives player input plus compact state.
5. Gameplay/rules layer resolves deterministic actions.
6. Narrator receives player input, state snapshot, rule results, and a DM-oriented prompt.
7. Reply is posted to Discord.
8. Persistence records the event and updated state.

### Combat Turn

1. Combat starts with `/start_combat`.
2. Combat state defines initiative order and active combatant.
3. natural messages or `/turn` by a non-active actor are rejected or redirected with a helpful message.
4. Successful combat turns can advance or preserve initiative depending on rule result.
5. `/show_combat` reports order, HP summary, and current actor.
6. `/next_turn` explicitly advances if the current actor is done.

### Scene Mode

1. Operator calls `/enter_scene speakers:...`.
2. Scene state records active NPC speakers.
3. Router can emit `scene` plans with speaker hints.
4. Narrator formats multi-speaker output in a readable labeled style.
5. `/end_scene` returns to normal DM mode.

## Error Handling

- If a user calls `/turn` before joining a campaign, reply with a clear ephemeral error.
- If a user without an imported character attempts a rules-heavy action, allow narration-only play but mention missing sheet linkage when necessary.
- If a non-active combatant tries to act during combat, reject with current actor info.
- If the adventure package is missing or invalid, fail closed with a diagnostic error instead of freeforming unsupported content.
- If the narrator output is empty or malformed, return a short DM fallback response and retain trace diagnostics.

## Testing Strategy

### Unit Tests

- session membership and leave/join behavior
- combat actor gating and turn advancement
- scene entry/exit and speaker formatting
- adventure package parsing and scene progression
- narrator prompt shaping and response formatting

### Integration Tests

- multiplayer campaign flow in one channel
- combat command flow with multiple users
- loading an adventure and progressing from opening hook to encounter
- docs examples matched against actual commands and outputs

### Manual Validation

- run bot in a real guild
- create a test campaign with two users
- import at least one character
- play through the packaged one-shot opening scene and one combat

## Files and Responsibilities

- `src/dm_bot/orchestrator/session_store.py`
  Expand campaign membership and active character session data.
- `src/dm_bot/orchestrator/gameplay.py`
  Own richer table-state transitions and adventure progression hooks.
- `src/dm_bot/gameplay/combat.py`
  Enforce actor order, reporting, and turn advancement helpers.
- `src/dm_bot/discord_bot/commands.py`
  Add missing commands and user-facing flow messages.
- `src/dm_bot/discord_bot/client.py`
  Add Discord message intake for bound campaign channels.
- `src/dm_bot/narration/service.py`
  Tighten DM-specific Chinese prompting.
- `src/dm_bot/orchestrator/message_filters.py`
  New natural-message filtering and intent heuristics for OOC and mention-heavy chatter.
- `src/dm_bot/gameplay/scene_formatter.py`
  Keep dialogue readable and DM-facing.
- `src/dm_bot/adventures/*`
  New structured adventure package support.
- `README.md`
  Replace skeletal setup notes with a playable quickstart.
- `docs/operations/*`
  New user-facing multiplayer and adventure usage docs.

## Recommended Delivery Order

1. Tighten multiplayer runtime state and command flow.
2. Add natural-message gameplay intake and combat gating.
3. Improve narrator DM prompt and output shaping.
4. Add adventure package format and ship one starter one-shot.
5. Write operator docs and quickstart around the finished flow.

## Success Criteria

- Two real users can join one bound campaign and play without state confusion.
- Players can play through ordinary channel messages without invoking `/turn` for every action.
- Combat has an explicit current actor and usable turn progression.
- Scene mode supports multi-NPC output with readable labeling.
- The bot can run a complete short one-shot from packaged content.
- README is enough for a new operator to launch and test a session in under ten minutes.
