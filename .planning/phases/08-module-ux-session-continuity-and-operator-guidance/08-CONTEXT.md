# Phase 8: Module UX, Session Continuity, and Operator Guidance - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Mode:** Auto-generated for autonomous execution

<domain>
## Phase Boundary

This phase makes packaged adventure play resilient and operator-friendly by persisting campaign sessions across restarts, restoring packaged-adventure state per campaign, and surfacing useful in-channel/debug status about current room, clues, objectives, and pressure.

</domain>

<decisions>
## Implementation Decisions

### Persistence Strategy
- Reuse the existing SQLite `PersistenceStore` instead of adding a new storage layer.
- Persist campaign session bindings and memberships explicitly.
- Load gameplay state for a campaign on demand before actions, then save it back after state-changing commands and turn handling.

### UX Surface
- Keep natural channel messages as the main play input.
- Improve existing command output and debug/status summaries instead of inventing a larger command system.
- Favor short, table-facing state summaries similar to mature Discord D&D tooling.

### Documentation
- Update the main README and operator docs around the formal `疯狂之馆` flow.
- Make restart recovery and natural-message caveats explicit.

### the agent's Discretion
- Exact wording of summaries and status surfaces can stay pragmatic as long as the operator can tell current room, goals, clues, and blockers quickly.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `PersistenceStore` already owns SQLite setup and campaign state persistence.
- `SessionStore` already models channel bindings, members, and active characters.
- `DiagnosticsService` and `/debug_status` already provide a command surface to extend.
- `README.md` and `docs/operations/*` already document the starter flow and can be updated in place.

### Established Patterns
- Runtime composition happens centrally in `main.py`.
- BotCommands is the current seam for slash commands and natural-message dispatch.
- Tests already cover commands, persistence, diagnostics, and natural-message runtime.

### Integration Points
- Add session persistence hooks in `src/dm_bot/persistence/store.py` and `src/dm_bot/orchestrator/session_store.py`.
- Wire restore/load-save behavior through `src/dm_bot/discord_bot/commands.py` and `src/dm_bot/main.py`.
- Expand `src/dm_bot/diagnostics/service.py` for packaged-adventure summaries.

</code_context>

<specifics>
## Specific Ideas

- Restore bound channels at startup so normal messages work again without rerunning `/bind_campaign` and `/join_campaign`.
- Summaries should mention current room, countdown, key discovered clues, and whether an ending or exit condition is currently available.

</specifics>

<deferred>
## Deferred Ideas

- Fully isolated per-campaign gameplay engines remain deferred; this phase can use on-demand state load/save around a shared gameplay object.
- Rich GM dashboards or web UI remain deferred.

</deferred>
