# vE.2.2 Testing Infrastructure Gap Analysis

**Audit Date:** 2026-03-30
**Purpose:** Identify gaps between existing codebase and vE.2.2 milestone requirements

---

## Executive Summary

Of ~20 components required by vE.2.2:
- **10 MUST BUILD** from scratch
- **2 MUST EXTEND** (existing but insufficient)
- **9 CAN REUSE** (existing and sufficient)
- **2 HIGH-VALUE MIGRATION CANDIDATES** (existing tests → scenario scripts)

---

## 1. MUST BUILD (New — Does Not Exist)

| # | Component | Why New | Notes |
|---|-----------|--------|-------|
| 1 | `ScenarioRunner` | No scenario execution engine exists | Executes YAML scripts against RuntimeTestDriver |
| 2 | `RuntimeTestDriver` | Discord-free runtime interface doesn't exist | run_command, send_message, snapshot_state, etc. |
| 3 | Scenario DSL | No YAML/JSON scenario format defined | actors, steps, assertions, phase_timeline, dice_mode |
| 4 | `ArtifactWriter` | No artifact output system exists | run.json, summary.md, timeline.json, outputs_by_actor/ |
| 5 | `FailureCode` enum | No failure taxonomy exists | PHASE_TRANSITION_MISMATCH, VISIBILITY_LEAK, etc. |
| 6 | `SeededDiceRoller` | `rules/dice.py` uses `random.randint` (not seedable) | Needs source change to add seeded `random.Random` |
| 7 | `fake_clock` | No controllable time abstraction exists | For time-dependent trigger testing |
| 8 | `tests/scenarios/` directory | No scenario files exist | acceptance/, contract/, chaos/, recovery/ suites |
| 9 | `FakeStreamingTransport` | No streaming fake transport exists | `StreamingMessageTransport` in source has no fake counterpart |
| 10 | `FakeMessage.edit()` | `FakeChannel` only has `.send()`, no edit support | Needed for stream interrupt/resume testing |

---

## 2. MUST EXTEND (Exists But Insufficient)

| Component | Current State | Gap | How to Extend |
|-----------|--------------|-----|---------------|
| `tests/fakes/discord.py` | `FakeChannel` with `.send()` only | No `.edit()` for message editing; no `FakeStreamingTransport` | Add `FakeMessage` class with `.edit()`; add `FakeStreamingTransport` |
| `src/dm_bot/rules/dice.py` | `D20DiceRoller` uses `random.randint` directly | NOT deterministic — can't reproduce dice rolls | Add `SeededDiceRoller` class: `__init__(seed)`, uses `random.Random(seed)` |

---

## 3. CAN REUSE (Exists And Sufficient)

| Component | Location | Why Sufficient |
|-----------|----------|----------------|
| `FakeInteraction` / `fake_interaction()` | `tests/fakes/discord.py` | Already supports response/followup/channel fakes |
| `StubModelClient` / `FastMock` / `SlowMock` / `ErrorMock` | `tests/fakes/models.py` | Captures router/narrator requests, configurable responses, stream_narrator |
| `BotCommands` class | `src/dm_bot/discord_bot/commands.py` | Can be called directly with FakeInteraction — VERIFIED |
| `TurnCoordinator.handle_turn()` / `stream_turn()` | `src/dm_bot/orchestrator/turns.py` | Good entry point for message-based turns |
| `CampaignSession` + `SessionStore` | `src/dm_bot/orchestrator/session_store.py` | `dump_sessions()` / `load_sessions()` for state serialization |
| `GameplayOrchestrator.export_state()` / `import_state()` | `src/dm_bot/orchestrator/gameplay.py` | State snapshot/restore mechanism ready |
| `PersistenceStore` | `src/dm_bot/persistence/store.py` | SQLite checkpoint/recovery — already used by tests |
| `RulesEngine` (with dice injection) | `src/dm_bot/rules/engine.py` | Already accepts `dice_roller=` injection — just need seeded impl |
| `StreamingMessageTransport` | `src/dm_bot/discord_bot/streaming.py` | Source abstraction exists; needs fake counterpart |
| `conftest.py` fixtures | `tests/conftest.py` | 7 fixtures ready; can add scenario-specific ones |

---

## 4. MIGRATION CANDIDATES (Existing Tests → Scenario Scripts)

### HIGH: `tests/test_e2e_15turn_scenario.py`
- Already follows scenario pattern: setup → steps → assertions
- SCEN-01/02/03 (happy path, wrong path, consequence chain)
- Can be migrated to YAML scenarios under `acceptance/scen_fuzhe_15turn.yaml`
- Estimated rewrite effort: medium (pytest → YAML + assertions)

### MEDIUM: `tests/test_chaos_lobby_stress.py`
- SCEN-04 (chaos lobby 5 concurrent users)
- Follows session setup pattern
- Can be migrated to `chaos/scen_chaos_lobby.yaml`
- Estimated rewrite effort: medium

---

## 5. EXISTING INVENTORY (Verified)

### `tests/fakes/discord.py`
```
fake_interaction(user_id, channel_id, guild_id) → MagicMock
  ├── user, channel_id, guild_id, extras
  ├── response.send_message(), response.defer()
  ├── followup.send()
  └── channel.send()
FakeResponse, FakeFollowup, FakeChannel
fake_context(), fake_user(), fake_channel(), fake_guild()
```
**Missing:** `FakeMessage.edit()`, `FakeStreamingTransport`

### `tests/fakes/models.py`
```
StubModelClient: call_router(), call_narrator(), stream_narrator()
FastMock: StubModelClient (instant)
SlowMock: + asyncio.sleep delay
ErrorMock: raises RuntimeError
```
**Status:** ✅ Sufficient for `fake_contract` mode

### `src/dm_bot/discord_bot/commands.py`
```
BotCommands:
  bind_campaign(), join_campaign(), select_profile()
  ready(), load_adventure(), start_session()
  take_turn() — passes send_initial + edit_message lambdas
  handle_channel_message(), handle_channel_message_stream()
```
**Status:** ✅ Can be called directly with FakeInteraction

### `src/dm_bot/orchestrator/turns.py`
```
TurnCoordinator: handle_turn(), stream_turn()
TurnRequest, TurnDispatchResult
```

### `src/dm_bot/rules/dice.py`
```
D20DiceRoller: uses random.randint() — NOT DETERMINISTIC
DiceRoller: Protocol (can be injected)
```
**Status:** ⚠️ Needs SeededDiceRoller in source

---

## 6. FUZHE_MINI SITUATION

- **Only `fuzhe.json` exists** (737 lines, 9 locations, 14 triggers, 7 story nodes)
- **`fuzhe_mini.json` does NOT exist** — no fixture generation logic
- **E72 cannot run "15-turn fuzhe_mini" without creating it first**
- **Fix:** Create `fuzhe_mini.json` in E69 as part of RuntimeTestDriver setup (4-node subset)

---

## 7. VCR CASSETTES SITUATION

- `tests/conftest.py` has VCR config ready (`record_mode: "once"`, header filters)
- `tests/cassettes/` directory **does not exist**
- **No VCR recordings have ever been made**
- **`recorded` mode in `model_mode` parameter is currently empty**
- **Fix:** E71 must record at least one real router + narrator response as cassette

---

## 8. COMMAND ENTRY POINT

Current CLI entry: `uv run python -m dm_bot.main {preflight,run-api,run-bot,smoke-check,restart-system,control-status,run-control-panel}`

**No `run-scenario` command exists.**

- **Fix:** E70 adds `run-scenario` as new CLI subcommand

---

## 9. SUMMARY TABLE

| Category | Count | Items |
|----------|-------|-------|
| MUST BUILD | 10 | ScenarioRunner, RuntimeTestDriver, Scenario DSL, ArtifactWriter, FailureCode, SeededDiceRoller, fake_clock, tests/scenarios/, FakeStreamingTransport, FakeMessage.edit |
| MUST EXTEND | 2 | tests/fakes/discord.py (add FakeMessage + FakeStreamingTransport), src/dm_bot/rules/dice.py (add SeededDiceRoller) |
| CAN REUSE | 9 | FakeInteraction, StubModelClient, BotCommands, TurnCoordinator, CampaignSession, GameplayOrchestrator, PersistenceStore, RulesEngine (injection), StreamingMessageTransport |
| MIGRATION CANDIDATES | 2 | test_e2e_15turn_scenario.py (HIGH), test_chaos_lobby_stress.py (MEDIUM) |
| BLOCKING ISSUES | 3 | fuzhe_mini.json missing, SeededDiceRoller needs source change, run-scenario CLI missing |
