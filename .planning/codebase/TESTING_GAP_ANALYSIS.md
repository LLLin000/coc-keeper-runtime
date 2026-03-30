# vE.2.2 Gap Analysis: Test Infrastructure

**Analysis Date:** 2026-03-30

---

## MUST BUILD (new, does not exist)

### 1. `src/dm_bot/testing/` — Testing infrastructure module
**Gap:** No `src/dm_bot/testing/` directory exists at all.

This module should contain:
- `scenario_runner.py` — ScenarioRunner class
- `runtime_test_driver.py` — RuntimeTestDriver class
- `artifacts.py` — ArtifactWriter class
- `deterministic_dice.py` — SeededDiceRoller
- `fake_clock.py` — Controllable clock for timeout testing
- `failure_codes.py` — FailureCode enum taxonomy
- `scenario_dsl.py` — YAML/JSON scenario schema and loaders

### 2. Scenario DSL schema
**Gap:** No YAML or JSON scenario definition format exists anywhere in the codebase.

Must define schema for:
- `actors` — player/KP identities and profiles
- `steps` — sequence of commands/inputs per phase
- `assertions` — expected state assertions per step
- `phase_timeline` — expected phase transitions
- `visibility_rules` — private/public message expectations
- `dice_mode` — deterministic vs. random

### 3. ScenarioRunner
**Gap:** No scenario execution engine exists.

Requirements:
- Load YAML scenario files from `tests/scenarios/{acceptance,contract,chaos,recovery}/`
- Execute steps in sequence using RuntimeTestDriver
- Collect outputs, state snapshots, and assertion results
- Produce artifacts via ArtifactWriter

### 4. RuntimeTestDriver (Discord-free interface)
**Gap:** No unified Discord-free runtime driver exists.

Required interface:
```python
run_command(command_name, **kwargs)           # Call BotCommands directly
send_message(content)                         # Route message to TurnCoordinator
snapshot_state()                             # Dump session + gameplay state
get_outputs(actor_id)                         # Get accumulated outputs per actor
restart_runtime()                            # Fresh runtime with same config
simulate_crash()                             # Kill/restart without cleanup
simulate_stream_interrupt()                   # Halt streaming mid-chunk
```

Implementation path: Use `TurnCoordinator.handle_turn()` / `stream_turn()` + `BotCommands` methods + direct session manipulation.

### 5. ArtifactWriter
**Gap:** No artifact output system exists.

Required outputs:
- `run.json` — full run metadata (scenario_id, timestamp, duration, pass/fail)
- `summary.md` — human-readable summary
- `timeline.json` — chronological list of steps and state changes
- `outputs_by_actor/` — per-actor accumulated output files
- `state_before.json` — state snapshot before scenario
- `state_after.json` — state snapshot after scenario
- `failure.json` — FailureCode + context for failed assertions

### 6. FailureCode taxonomy enum
**Gap:** No failure classification system exists.

Must define at minimum:
```python
class FailureCode(str, Enum):
    PHASE_TRANSITION_MISMATCH    # Expected phase ≠ actual phase
    REVEAL_POLICY_VIOLATION      # Private info leaked
    VISIBILITY_LEAK             # Actor saw content they shouldn't
    ASSERTION_FAILED            # Generic assertion mismatch
    STREAM_INTERRUPT_UNHANDLED  # Crash recovery didn't resume correctly
    DICE_NON_DETERMINISTIC      # Same seed produced different results
    TIMEOUT_EXCEEDED            # Operation exceeded fake_clock threshold
    SESSION_STATE_CORRUPT       # Deserialization/recovery failed
    COMMAND_REROUTE_ERROR       # Command didn't reach expected handler
```

### 7. deterministic_dice — SeededDiceRoller
**Gap:** `src/dm_bot/rules/dice.py` uses `random.randint()` which is NOT reproducible.

Current: `D20DiceRoller.roll_percentile()` uses `random.randint(0, 9)` per call.

Required: A `SeededDiceRoller` implementing the `DiceRoller` Protocol that accepts a seed and produces identical sequences across runs.

Note: `RulesEngine` already accepts `dice_roller=` injection — this is a wiring concern, not an architectural change.

### 8. fake_clock — Controllable time for timeouts
**Gap:** No fake clock exists for testing time-sensitive behavior.

Must support:
- `advance(seconds)` — move clock forward
- `freeze()` / `unfreeze()` — pause/resume
- `tick()` — advance by one "tick"
- Injection point: wherever `time.monotonic()` or `asyncio.sleep()` is called

### 9. `tests/scenarios/` — YAML scenario file directories
**Gap:** No scenario scripts exist.

Must create directory structure:
```
tests/scenarios/
  acceptance/   # Happy-path scenario scripts
  contract/     # Interface contract verification
  chaos/        # Stress and failure injection
  recovery/     # Crash recovery scenarios
```

### 10. FakeStreamingTransport
**Gap:** `tests/fakes/discord.py` has no fake for streaming behavior.

Required: A `FakeStreamingTransport` that captures `send_initial()` calls and `edit_message()` calls with their arguments, for verifying streaming output correctness and interrupt behavior.

---

## MUST EXTEND (exists but insufficient)

### 1. `tests/fakes/discord.py` — Missing message.edit support
**Current:** `FakeChannel` has `.send()` but no `.edit()` method. No `FakeMessage` class exists.

**Insufficient for:** Testing `StreamingMessageTransport` which calls `message.edit(content=updated)`.

**Fix:** Add `FakeSentMessage` class (already partially defined in `test_discord_commands.py` line 21-28) and `FakeStreamingTransport` class to `tests/fakes/discord.py`.

### 2. `src/dm_bot/rules/dice.py` — Non-deterministic D20DiceRoller
**Current:** Uses `random.randint()` internally — two calls with same input produce different outputs.

**Insufficient for:** Reproducible scenario runs requiring deterministic dice.

**Fix:** Keep `D20DiceRoller` as-is for production. Create `SeededDiceRoller(seed: int)` in `src/dm_bot/testing/deterministic_dice.py` that implements `DiceRoller` Protocol with `random.Random(seed)` internally.

---

## CAN REUSE (exists and sufficient)

### 1. `src/dm_bot/orchestrator/turns.py` — TurnCoordinator
**File:** `src/dm_bot/orchestrator/turns.py`
- `TurnCoordinator.handle_turn()` — synchronous turn entry point
- `TurnCoordinator.stream_turn()` — streaming turn entry point
- Both accept `TurnRequest` or keyword args
- Returns `TurnDispatchResult` with `trace_id` and `reply`

**Ready for:** Direct use in RuntimeTestDriver without Discord.

### 2. `src/dm_bot/orchestrator/session_store.py` — SessionStore + CampaignSession
**File:** `src/dm_bot/orchestrator/session_store.py`
- `SessionStore.dump_sessions()` → `dict` — full session serialization
- `SessionStore.load_sessions(dict)` — full session restoration
- `CampaignSession.transition_to()` — phase transitions
- `CampaignSession.set_player_action()` / `clear_all_actions()` — action collection
- `CampaignSession.phase_history` — chronological phase log

**Ready for:** State snapshot and recovery testing.

### 3. `src/dm_bot/orchestrator/gameplay.py` — GameplayOrchestrator
**File:** `src/dm_bot/orchestrator/gameplay.py`
- `GameplayOrchestrator.export_state()` → dict — full gameplay state
- `GameplayOrchestrator.import_state(dict)` — full gameplay restore
- `resolve_manual_roll()` — dice resolution entry point
- `adventure_snapshot(user_id)` — per-user visibility-aware snapshot

**Ready for:** Checkpoint/restart testing and visibility assertion.

### 4. `src/dm_bot/discord_bot/commands.py` — BotCommands
**File:** `src/dm_bot/discord_bot/commands.py`
- `BotCommands` methods are async and accept `interaction`
- `FakeInteraction` from `tests/fakes/discord.py` provides the needed interface
- Verified workable in `tests/test_discord_commands.py`

**Ready for:** Direct method calling via RuntimeTestDriver.

### 5. `src/dm_bot/persistence/store.py` — PersistenceStore
**File:** `src/dm_bot/persistence/store.py`
- `save_campaign_state()` / `load_campaign_state()` — per-campaign blob
- `save_sessions()` / `load_sessions()` — full session state
- `append_event()` / `list_events()` — event log for timeline reconstruction
- In-memory: `path=":memory:"` works

**Ready for:** Database checkpoint testing and event timeline validation.

### 6. `tests/fakes/models.py` — StubModelClient, FastMock, SlowMock, ErrorMock
**File:** `tests/fakes/models.py`
- `StubModelClient` — capture router/narrator calls, return configurable content
- `FastMock` — instant response
- `SlowMock` — configurable delay
- `ErrorMock` — exception raising
- All implement both `call_router()` / `call_narrator()` and `stream_narrator()`

**Ready for:** Model layer mocking in scenario runs.

### 7. `tests/conftest.py` — Shared fixtures
**File:** `tests/conftest.py`
- `interaction_factory` → `fake_interaction`
- `context_factory` → `fake_context`
- `sqlite_memory_store` → `PersistenceStore(":memory:")`
- `fast_model_mock`, `slow_model_mock`, `error_model_mock`

**Ready for:** Integration with new testing infrastructure.

### 8. `src/dm_bot/rules/engine.py` — RulesEngine with dice injection
**File:** `src/dm_bot/rules/engine.py`
- `RulesEngine(dice_roller=...)` accepts any `DiceRoller` implementation
- `RulesEngine.execute(RuleAction)` dispatches all rule types
- `_roll_percentile()` handles bonus/penalty dice, pushed rolls

**Ready for:** Injecting `SeededDiceRoller` for deterministic scenario runs.

### 9. `src/dm_bot/discord_bot/streaming.py` — StreamingMessageTransport
**File:** `src/dm_bot/discord_bot/streaming.py`
- Already structured as a clean abstraction: `send_initial` + `edit_message` callbacks
- The `StreamingMessageTransport` class itself is testable with the right fakes

**Ready for:** Extraction into RuntimeTestDriver as `simulate_stream_interrupt()` backbone.

---

## MIGRATION CANDIDATES (existing tests that follow scenario pattern)

### 1. `tests/test_e2e_15turn_scenario.py`
**Current pattern:**
- Python test with session-store-level setup (`e2e_session` fixture)
- Sequential `set_player_action()` → `clear_all_actions()` loop
- Verifies phase consistency and persistence recovery

**Scenario elements present:**
- Fixed actors: `kp`, `player1`, `player2`, `player3` with character names
- Sequential steps: turns 1-15 with action submission per turn
- State assertions: `session_phase == SCENE_ROUND_OPEN`, member counts, character names
- Recovery scenarios: DB save at turn 8, crash simulation

**Migration potential:** HIGH — convert to YAML with `phase_timeline` and `assertions` per step. The scenario is essentially already a scenario script in Python.

### 2. `tests/test_chaos_lobby_stress.py`
**Current pattern:**
- `ThreadPoolExecutor` for concurrent bind/join/ready
- Phase transition verification under load
- Duplicate member detection

**Scenario elements present:**
- Concurrent actor operations
- State invariants: no duplicate `member_ids`, all reach `SCENE_ROUND_OPEN`
- Phase transition timeline

**Migration potential:** MEDIUM — chaos suite candidate. The concurrent execution pattern is harder to express in YAML but `chaos/` suite is designed for this.

### 3. `tests/test_discord_commands.py`
**Current pattern:**
- `FakeInteraction` + direct `BotCommands` method calls
- Verifies session state changes from commands

**Migration potential:** LOW for ScenarioRunner — these are contract-style unit tests for individual command handlers, better suited as `contract/` suite scenarios.

---

## Edge Cases: BotCommands Calling Convention

**Verified: `BotCommands` methods CAN be called directly with `FakeInteraction`.**

Key verified patterns from `tests/test_discord_commands.py`:
- Methods are `async` — must `await`
- `interaction.user.id` → `str` — must stringify
- `interaction.guild_id` / `interaction.channel_id` → used directly, `FakeInteraction` provides these
- `interaction.response.send_message()` / `interaction.followup.send()` — `FakeResponse` / `FakeFollowup` track calls
- `interaction.channel.send()` — `FakeChannel` needed for `load_adventure` which sends to channel

**Edge cases identified:**

1. **`take_turn()`** (line 600-656): Passes `send_initial=lambda initial: interaction.followup.send(initial, wait=True)` and `edit_message=lambda message, updated: message.edit(content=updated)`. The `edit_message` closure captures a message object returned by `send_initial`. Requires `FakeMessage` with `.edit()`.

2. **`handle_channel_message()`** (line 1322+): Non-command path through `TurnCoordinator`. Not called via `BotCommands` directly — routes through session store + turn coordinator.

3. **`_stream_turn_to_transport()`** (internal): Creates `StreamingMessageTransport` with the `send_initial`/`edit_message` callbacks. This is the primary consumer of streaming infrastructure and requires `FakeMessage.edit()`.

4. **`check_channel()`** (line 54): Guards commands by channel role. Requires `self._enforcer` to be set (needs `session_store`). If `session_store=None`, returns `(True, None)` — no enforcement.

---

## Summary: Absolute Gaps for vE.2.2

| # | Component | Status | Files to Create/Modify |
|---|-----------|--------|------------------------|
| 1 | Scenario DSL schema | MUST BUILD | New: `src/dm_bot/testing/scenario_dsl.py` |
| 2 | ScenarioRunner | MUST BUILD | New: `src/dm_bot/testing/scenario_runner.py` |
| 3 | RuntimeTestDriver | MUST BUILD | New: `src/dm_bot/testing/runtime_test_driver.py` |
| 4 | ArtifactWriter | MUST BUILD | New: `src/dm_bot/testing/artifacts.py` |
| 5 | FailureCode enum | MUST BUILD | New: `src/dm_bot/testing/failure_codes.py` |
| 6 | SeededDiceRoller | MUST BUILD | New: `src/dm_bot/testing/deterministic_dice.py` |
| 7 | fake_clock | MUST BUILD | New: `src/dm_bot/testing/fake_clock.py` |
| 8 | Scenario file directories | MUST BUILD | New: `tests/scenarios/{acceptance,contract,chaos,recovery}/` |
| 9 | FakeStreamingTransport | MUST BUILD | Modify: `tests/fakes/discord.py` |
| 10 | FakeMessage.edit() | MUST BUILD | Modify: `tests/fakes/discord.py` |
| 11 | D20DiceRoller non-determinism | MUST EXTEND | No change to production code — inject `SeededDiceRoller` in tests |

**Estimated new files:** ~8 new Python modules + 4 scenario directory marker files + example YAML scenarios.

---

*Gap analysis: 2026-03-30*
