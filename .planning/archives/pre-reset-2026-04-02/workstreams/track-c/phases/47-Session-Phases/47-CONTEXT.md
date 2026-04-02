# Phase 47: Session Phases - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning
**Source:** Requirements from vC.1.2 milestone

<domain>
## Phase Boundary

Implement explicit session phases for multiplayer campaigns with admin-controlled start flow and visibility into phase transitions.

**Requirements addressed:** SESSION-01, SESSION-02, SESSION-03

</domain>

<decisions>
## Implementation Decisions

### Session Phase Model
- **SESSION-01:** Define explicit session phases: `onboarding`, `lobby`, `awaiting_ready`, `awaiting_admin_start`, `scene_round_open`, `scene_round_resolving`, `combat`, `paused`
- Session phase stored in campaign/session state
- Phase transitions controlled by explicit actions (ready, admin_start, resolve, pause)

### Ready-Check Behavior
- **SESSION-02:** Players can ready up without auto-starting the adventure
- Admin/KP must explicitly start the session after all required players are ready
- Track both player ready state AND admin start state separately

### Phase Visibility
- **SESSION-03:** Session phase and transition history visible to explain message acceptance/buffering/ignoring
- When a player message is processed, the current phase should be logged/explainable

### the agent's Discretion
- Session phase persistence mechanism (database schema vs in-memory)
- Exact Discord channel/role mapping for phase notifications
- Whether to retroactively show phase history or just current state

</decisions>

<canonical_refs>
## Canonical References

**From Track C:**
- `.planning/workstreams/track-c/REQUIREMENTS.md` — vC.1.2 requirements
- `.planning/workstreams/track-c/PROJECT.md` — Milestone vC.1.2 goals
- `.planning/workstreams/track-c/research/ARCHITECTURE.md` — Current Discord layer architecture

**From Project:**
- `src/dm_bot/discord_bot/` — Existing Discord command implementation
- `src/dm_bot/orchestrator/` — Session/campaign management
- `src/dm_bot/persistence/` — State persistence

</canonical_refs>

<specifics>
## Specific Ideas

- SessionPhase enum in orchestrator contracts
- Campaign state includes: `session_phase`, `player_ready_states`, `admin_start_required`
- Phase transitions visible in bot logs for debugging
- Ready command updates player state but does NOT trigger adventure start

</specifics>

<deferred>
## Deferred Ideas

- Scene round collection (ROUND-01, ROUND-02, ROUND-03) — Phase 48
- Message intent routing (INTENT-01, INTENT-02, INTENT-03) — Phase 49
- Campaign/adventure visibility (VIS-01, VIS-02, VIS-03) — Phase 50

</deferred>

---

*Phase: 47-Session-Phases*
*Context gathered: 2026-03-28 from vC.1.2 requirements*
