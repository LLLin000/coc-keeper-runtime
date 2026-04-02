---
phase: 47-Session-Phases
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/orchestrator/session.py
  - src/dm_bot/discord_bot/commands/session.py
  - src/dm_bot/persistence/schema.sql
autonomous: true
requirements:
  - SESSION-01
  - SESSION-02
  - SESSION-03
---

<objective>
Implement explicit session phases for multiplayer campaigns with ready-check and admin-start discipline.

Purpose: Make session flow explicit in Discord so players understand why messages are accepted, buffered, or ignored based on the current session phase.
Output: SessionPhase enum, campaign state updates, modified ready command, admin start command, phase visibility
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/workstreams/track-c/phases/47-Session-Phases/47-CONTEXT.md
@.planning/workstreams/track-c/REQUIREMENTS.md
@.planning/workstreams/track-c/PROJECT.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Define SessionPhase enum and state contracts</name>
  <files>src/dm_bot/orchestrator/session.py</files>
  <action>
Create or extend the session management module to include:

1. SessionPhase enum with phases: `onboarding`, `lobby`, `awaiting_ready`, `awaiting_admin_start`, `scene_round_open`, `scene_round_resolving`, `combat`, `paused`

2. CampaignSessionState class with fields:
   - `session_phase: SessionPhase` — current phase
   - `player_ready: dict[discord_user_id, bool]` — player ready states
   - `admin_started: bool` — whether admin has explicitly started
   - `phase_history: list[tuple[SessionPhase, datetime]]` — transition log for visibility

3. Add methods:
   - `transition_to(new_phase: SessionPhase)` — logs transition with timestamp
   - `set_player_ready(user_id, ready: bool)` — updates ready state
   - `can_start_session()` — returns True when all players ready AND admin_started

Example enum:
```python
class SessionPhase(str, Enum):
    ONBOARDING = "onboarding"
    LOBBY = "lobby"
    AWAITING_READY = "awaiting_ready"
    AWAITING_ADMIN_START = "awaiting_admin_start"
    SCENE_ROUND_OPEN = "scene_round_open"
    SCENE_ROUND_RESOLVING = "scene_round_resolving"
    COMBAT = "combat"
    PAUSED = "paused"
```
  </action>
  <verify>
<automated>grep -n "class SessionPhase" src/dm_bot/orchestrator/session.py && grep -n "class CampaignSessionState" src/dm_bot/orchestrator/session.py</automated>
  </verify>
  <done>SessionPhase enum and CampaignSessionState class exist with required fields and methods</done>
</task>

<task type="auto">
  <name>Task 2: Modify ready command to separate ready from start</name>
  <files>src/dm_bot/discord_bot/commands/session.py</files>
  <action>
Update the `/ready` command (or create if doesn't exist):

1. When player runs `/ready`:
   - Set `player_ready[user_id] = True`
   - Update campaign session state
   - Do NOT auto-start adventure
   - Show message: "You are ready. Waiting for admin to start the session."

2. When all required players are ready:
   - Transition to `awaiting_admin_start` phase
   - Notify: "All players ready. Admin can start the session with /start-session"

3. Track ready status per player
   - Allow players to toggle ready off: `/ready --cancel`
   - Show current ready status in campaign info

Keep existing `/ready` behavior as fallback for backward compatibility if session phases not yet enabled.
  </action>
  <verify>
<automated>grep -n "awaiting_admin_start" src/dm_bot/discord_bot/commands/session.py</automated>
  </verify>
  <done>Ready command updates player ready state but does not auto-start; transitions to awaiting_admin_start when all ready</done>
</task>

<task type="auto">
  <name>Task 3: Add admin start command</name>
  <files>src/dm_bot/discord_bot/commands/session.py</files>
  <action>
Create `/start-session` admin command:

1. Requirements:
   - Only callable by admin/KP (check admin role)
   - Only works when session phase is `awaiting_admin_start` or `lobby`
   - Checks that required players are ready

2. When executed:
   - Set `admin_started = True`
   - Transition to `scene_round_open` phase
   - Log transition with timestamp
   - Notify channel: "Session started! Players can now take actions in the scene."

3. Validation messages:
   - If players not ready: "Cannot start: not all players are ready. Players must /ready first."
   - If wrong phase: "Session cannot be started from {current_phase}. Ready players first."
  </action>
  <verify>
<automated>grep -n "start_session\|/start-session" src/dm_bot/discord_bot/commands/session.py</automated>
  </verify>
  <done>Admin start command exists, validates ready state, and transitions to scene_round_open</done>
</task>

<task type="auto">
  <name>Task 4: Add phase visibility to message processing</name>
  <files>src/dm_bot/orchestrator/turn.py</files>
  <action>
Update the message processing/turn handling to include phase context:

1. When processing a player message in a campaign:
   - Include current `session_phase` in debug logs
   - Add `session_phase` to turn metadata stored in database

2. When message is accepted/buffered/ignored:
   - Log the reason including current phase
   - Example: "Player message accepted in phase {phase}: {message_preview}"

3. Create helper method in CampaignSessionState:
   - `get_phase_context()` — returns dict with phase, player_ready_count, admin_started for debugging

This enables SESSION-03: session phase transitions are visible enough to explain message handling.
  </action>
  <verify>
<automated>grep -n "session_phase" src/dm_bot/orchestrator/turn.py | head -10</automated>
  </verify>
  <done>Message processing logs include session phase; phase context available for debugging</done>
</task>

</tasks>

<verification>
- [ ] SessionPhase enum contains all 8 phases
- [ ] CampaignSessionState tracks player_ready, admin_started, phase_history
- [ ] /ready command updates player state without auto-starting
- [ ] /start-session command requires ready players and transitions to scene_round_open
- [ ] Phase transitions logged with timestamps
- [ ] Message processing includes phase context in logs
</verification>

<success_criteria>
- Campaign sessions have explicit phases (SESSION-01)
- Players can ready without auto-starting adventure (SESSION-02)
- Phase transitions visible in logs/context (SESSION-03)
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-c/phases/47-Session-Phases/47-01-SUMMARY.md`
</output>
