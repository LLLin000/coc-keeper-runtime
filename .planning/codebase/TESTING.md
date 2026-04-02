# TESTING.md

## Testing Approach

### Test Framework

- **Framework**: `pytest` (>=9.0.0)
- **Async Support**: `pytest-asyncio` (>=1.3.0) with `asyncio_mode = "auto"`
- **BDD Style**: `pytest-bdd` (>=8.0.0) for scenario-based tests
- **HTTP Cassettes**: `vcrpy` (>=6.0.0) for recording HTTP interactions

### Test Configuration

```toml
[tool.pytest.ini_options]
pythonpath = ["src", "."]
testpaths = ["tests"]
asyncio_mode = "auto"
```

### Test File Organization

```
tests/
├── conftest.py                 # Shared fixtures
├── fakes/
│   ├── __init__.py
│   ├── discord.py             # Fake Discord objects
│   ├── models.py              # Fake model responses
│   └── clock.py               # Fake clock for time-based tests
├── orchestrator/
│   ├── test_visibility.py
│   └── test_kp_ops_renderer.py
├── bdd/
│   ├── __init__.py
│   └── test_combat_round_bdd.py
└── test_*.py                  # 60+ unit/integration tests
```

### Test Types

| Type | Location | Description |
|------|----------|-------------|
| Unit | `tests/test_*.py` | Individual component tests |
| Integration | `tests/test_*_integration.py` | Cross-component flow tests |
| BDD | `tests/bdd/test_*.py` | Scenario-based behavior tests |
| Scenario | `tests/scenarios/*.yaml` + `src/dm_bot/testing/` | DSL-driven end-to-end flow validation |
| Smoke | Via `smoke-check` CLI | Runtime health validation |

### Key Test Files (77 test modules as of 2026-04-02)

**Core Flows**:
- `test_router_service_flow.py` — Intent routing
- `test_narration_service.py` — Narration generation
- `test_narration_streaming_flow.py` — Streaming output
- `test_coc_rules_flow.py` — COC rule resolution
- `test_pushed_roll_flow.py` — Pushed roll mechanics

**Session/Character**:
- `test_character_archive_flow.py` — Archive management
- `test_character_profile_projection.py` — Profile projection
- `test_identity_models.py` — Identity handling
- `test_multi_user_session.py` — Multiplayer session
- `test_ready_gate.py` — Ready-up validation

**Adventure/Gameplay**:
- `test_adventure_loader.py` — Module loading
- `test_fuzhe_adventure_loader.py` — Complex module
- `test_room_transitions_and_reveals.py` — Room graph
- `test_trigger_chains.py` — Trigger execution
- `test_combat_loop.py` — Combat system
- `test_combat_resolution_flow.py` — Combat resolution

**Discord Integration**:
- `test_discord_commands.py` — Slash command handlers
- `test_discord_client_runtime.py` — Discord client lifecycle
- `test_channel_enforcer.py` — Channel enforcement

**Testing Infrastructure**:
- `test_scenario_runner.py` — Scenario execution
- `test_scenario_dsl.py` — DSL parsing
- `test_smoke_check.py` — Smoke check validation
- `test_chaos_lobby_stress.py` — concurrency/ready-gate stress validation

### Fixtures (conftest.py)

Key fixtures provided:
- Discord fake objects
- Model response fakes
- Clock fakes for time-based tests
- Test database (in-memory SQLite)

### Running Tests

```bash
# All tests
uv run pytest -q

# Specific file
uv run pytest tests/test_coc_rules_flow.py

# With output
uv run pytest -v

# Run scenarios (BDD-style)
uv run python -m dm_bot.main run-scenario --all
```

### Smoke Check

```bash
uv run python -m dm_bot.main smoke-check
```

Validates:
- Discord token configured
- Ollama connectivity
- Model availability
- Asset paths

### Current Gate Status

Latest verified repository gate before this map refresh:
- `uv run pytest -q` → `923 passed`
- `uv run python -m dm_bot.main smoke-check` → `923 passed`
