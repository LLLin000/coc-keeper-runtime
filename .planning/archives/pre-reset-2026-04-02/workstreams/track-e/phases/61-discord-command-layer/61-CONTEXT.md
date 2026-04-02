# Phase 61: Discord Command/Adapter Layer - Context

**Status:** Planned
**Phase Directory:** `.planning/workstreams/track-e/phases/61-discord-command-layer`
**Primary Goal:** Validate the Discord command layer independently with the shared `FakeInteraction` test infrastructure so slash-command handlers and channel/session gates can be trusted before deeper orchestrator and scenario phases.

## Why This Phase Exists

Track E vE.2.1 splits reliability work by layer. The roadmap defines Phase 61 as the Discord command/adapter slice immediately after Phase 60 infrastructure work:

- `/bind_campaign`
- `/join`
- `/select_profile`
- `/ready`
- `/load_adventure`
- channel enforcement and session binding gates

The test coverage survey already shows broad command coverage, but not the exact integration gap this phase is supposed to close: command handlers still lack full FakeInteraction-backed validation of state transitions plus governance rejections at the command boundary.

## Inputs Read For This Context

- `.planning/workstreams/track-e/ROADMAP.md`
- `.planning/workstreams/track-e/REQUIREMENTS.md`
- `.planning/workstreams/track-e/test-coverage-survey.md`
- `.planning/workstreams/track-e/codebase-architecture.md`
- `.planning/workstreams/track-e/research-test-strategy.md`
- `src/dm_bot/discord_bot/commands.py`
- `src/dm_bot/orchestrator/session_store.py`
- `src/dm_bot/discord_bot/channel_enforcer.py`
- `tests/test_ready_commands.py`
- `tests/test_commands.py`

## Current Codebase Signals

### Existing tests are useful but still fragmented for this phase target

- `tests/test_commands.py` already covers bind/join/load flows, but it uses a local `FakeInteraction` class instead of the shared Phase 60 factory contract.
- `tests/test_ready_commands.py` covers `select_profile` and `ready`, but only as focused command tests rather than one cohesive command-layer validation pass.
- `.planning/workstreams/track-e/test-coverage-survey.md` identifies the exact gap: command handlers still lack full integration-style coverage.
- `tests/test_channel_enforcer.py` already exists, but this phase needs command-layer planning that ties governance checks back to the slash handlers in `commands.py`.

### Architecture boundaries relevant to this phase

From `codebase-architecture.md`, the Discord command layer is intentionally thin:

1. `DiscordDmBot`/`commands.py` receives the slash interaction.
2. `SessionStore` owns campaign binding, membership, selected profile, and ready validation state.
3. `ChannelEnforcer` decides whether the current channel may execute a command.
4. command handlers send the final Discord-facing response and persist resulting state.

Phase 61 should validate that layer boundary itself, not the full downstream turn pipeline.

## Research Findings To Carry Forward

1. `FakeInteraction` should be the default slash-command test entry point rather than ad hoc local fakes.
2. Command tests should assert both response payloads and state mutation, not only one or the other.
3. Channel governance should be tested at the same boundary the bot uses in production: handler → `check_channel()` → `ChannelEnforcer` → redirect response.
4. Test isolation should stay local and deterministic; no live Discord connection is needed.

## Concrete Command/Gate Surfaces In Scope

### Command handlers

- `BotCommands.bind_campaign()`
- `BotCommands.join_campaign()`
- `BotCommands.select_profile()`
- `BotCommands.ready()` and/or the slash-ready entry path wired through `ready_for_adventure()` where channel enforcement applies
- `BotCommands.load_adventure()`

### Session binding gates

- `SessionStore.bind_campaign()` establishes the owner/member baseline.
- `SessionStore.join_campaign()` rejects unbound or duplicate joins.
- `SessionStore.select_archive_profile()` rejects no-session, non-member, missing-profile, inactive-profile, and wrong-owner cases.
- `SessionStore.validate_ready()` rejects no-session, non-member, and no-profile-selected cases.

### Channel enforcement gates

- `ChannelEnforcer` currently applies game-channel routing for `join_campaign`, `ready`, and `load_adventure`.
- The phase must verify rejected interactions respond with redirect guidance when the required channel exists but the command runs elsewhere.

## Constraints For The Plan

- Keep the phase focused on Discord command-layer validation, not session/orchestrator multi-user lifecycle coverage from Phase 62.
- Reuse the Phase 60 `tests/fakes/discord.py` factory instead of introducing another fake interaction shape.
- Prefer extending existing command-focused suites unless a dedicated command-layer file is clearer.
- Make acceptance checks grep-verifiable and execution commands explicit.
- Cover both requirements in this phase only:
  - `DISC-01`: command handlers produce correct session state changes
  - `DISC-02`: unauthorized channel usage is rejected

## Expected Outputs From Phase 61

- FakeInteraction-backed command tests for bind, join, select_profile, ready, and load_adventure
- explicit assertions on `SessionStore` membership/profile/ready/adventure-related state after handler execution
- command-layer rejection tests proving wrong-channel invocations return governance guidance
- a phase summary file after implementation completes

## Success Shape

After this phase, later Track E plans should be able to assume:

- slash-command tests use one shared Discord fake layer
- the lobby command lifecycle is validated at the handler boundary before Phase 62 broadens to multi-user orchestrator flows
- governance failures are covered where users actually experience them: the slash command response path
