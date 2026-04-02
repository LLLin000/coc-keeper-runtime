# Phase 69 Context

**Phase:** E69
**Milestone:** vE.2.2 — 统一 Scenario-Driven E2E 验证框架
**Created:** 2026-03-30

---

## What This Phase Does

Creates the foundational driver layer that the entire vE.2.2 milestone builds on:
- `RuntimeTestDriver` — the one interface all scenarios use to interact with the runtime
- `ScenarioRunner` — parses and executes YAML scenario scripts
- `SeededDiceRoller` — deterministic dice (source code change required)
- `fake_clock` + `FakeStreamingTransport` + `FakeMessage.edit()` — supporting fakes
- `fuzhe_mini.json` — 4-node adventure fixture

---

## Key Files to Read

### Source Files (read before implementing)
- `src/dm_bot/discord_bot/commands.py` — BotCommands, how slash commands work
- `src/dm_bot/orchestrator/turns.py` — TurnCoordinator, handle_turn / stream_turn
- `src/dm_bot/orchestrator/gameplay.py` — GameplayOrchestrator, state management
- `src/dm_bot/orchestrator/session_store.py` — SessionStore interface
- `src/dm_bot/persistence/store.py` — PersistenceStore
- `src/dm_bot/rules/dice.py` — D20DiceRoller (needs seeded variant)
- `src/dm_bot/rules/engine.py` — RulesEngine with dice_roller injection
- `src/dm_bot/discord_bot/streaming.py` — StreamingMessageTransport

### Test Files (read before implementing)
- `tests/fakes/discord.py` — FakeInteraction, FakeChannel
- `tests/fakes/models.py` — StubModelClient, FastMock
- `tests/conftest.py` — existing fixtures

### Existing Test Patterns (for reference)
- `tests/test_e2e_15turn_scenario.py` — session setup pattern
- `tests/test_chaos_lobby_stress.py` — chaos setup pattern

---

## Constraints

1. **Source code change — SeededDiceRoller:** `rules/dice.py` MUST be modified to add seeded deterministic dice. This is a source code change, not just test infrastructure.
2. **No live Discord:** RuntimeTestDriver must never import or call real Discord APIs.
3. **No live AI:** Use `FastMock` / `StubModelClient` by default. Ollama only in `live` model_mode (not default).
4. **Async throughout:** `RuntimeTestDriver` and `ScenarioRunner` must be async-compatible.
5. **StepResult must be returned from every driver operation** — don't swallow phase/output state.

---

## Out of Scope

- Scenario DSL format (E70)
- ArtifactWriter (E70)
- FailureCode taxonomy (E71)
- VCR cassettes (E71)
- Acceptance scenarios (E72)
- CI configuration (E72)
