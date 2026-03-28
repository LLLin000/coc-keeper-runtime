# Phase 40: Runtime Control Contracts - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning
**Mode:** Auto-generated for workstream execution

<domain>
## Phase Boundary

This phase establishes the stable control contracts for Track E milestone `vE.1.1`. It should define the runtime control state model, action result model, and service seams that both the CLI control surface and the future local web panel will consume.

This phase should not implement the full panel UI yet. It should create the shared contracts and service boundary that make the later CLI and web surfaces straightforward and safe.

</domain>

<decisions>
## Implementation Decisions

### Scope
- Create one unified runtime control state shape.
- Create one unified action result shape.
- Introduce a shared service that wraps existing smoke-check, restart, process inspection, log reading, and model inspection behavior.
- Keep the first implementation conservative and backward-compatible with current operational commands.

### Reuse Existing Runtime Work
- Reuse the current `smoke-check` command and implementation.
- Reuse the current `restart-system` command and implementation.
- Reuse Discord startup markers (`SYNC_START`, `SYNC_DONE`, `READY`) instead of inventing a second health source.

### First-Version Health Model
- Health should distinguish between:
  - process exists
  - runtime is actually usable
- A bot process without `READY` or sync evidence should not be considered healthy.

### Track Ownership
- Primary Track: Track E
- Secondary Impact: Track C
- This phase may expose better operator-facing status for Discord runtime concerns, but should not redefine Discord command contracts or gameplay behavior.

</decisions>

<code_context>
## Existing Code Insights

### Current Runtime Entry Points
- `src/dm_bot/main.py` already exposes:
  - `preflight`
  - `run-api`
  - `run-bot`
  - `smoke-check`
  - `restart-system`
- This phase should extend runtime entry points without breaking the existing ones.

### Existing Restart Orchestration
- `src/dm_bot/runtime/restart_system.py` already:
  - runs smoke-check
  - kills old bot processes
  - boots the bot
  - waits for sync and READY markers
  - confirms process survival
- This is the current operational truth for runtime bootstrap and should be wrapped, not replaced.

### Existing Startup Markers
- `src/dm_bot/discord_bot/client.py` writes:
  - `SYNC_START`
  - `SYNC_DONE ...`
  - `READY ...`
- These markers are already sufficient to bootstrap a first operational state model.

### Existing Logs
- Existing logs include:
  - `bot.startup.log`
  - `bot.restart.log`
  - `bot.stdout.log`
  - `bot.stderr.log`
- These are already useful enough to support a first log-summary contract.

</code_context>

<specifics>
## Specific Ideas

- Introduce a `RuntimeControlService` that exposes:
  - `get_state()`
  - `start_bot()`
  - `restart_bot()`
  - `stop_bot()`
  - `start_api()`
  - `restart_api()`
  - `stop_api()`
  - `restart_system()`
  - `run_smoke_check()`
  - `sync_commands()`
- Introduce typed state/result models such as:
  - `ProcessStatus`
  - `ModelAvailability`
  - `RuntimeControlState`
  - `ControlActionResult`
- Keep CLI and future web API thin by pushing orchestration into the service.

</specifics>

<deferred>
## Deferred Ideas

- Full CLI text dashboard belongs to Phase 41.
- Local web panel belongs to Phase 42.
- Final integration, logging polish, and stronger reliability behavior belong to Phase 43.
- Real-time log streaming is explicitly deferred beyond this milestone.

</deferred>
