# STRUCTURE.md

## Codebase Structure

### Directory Layout

```
C:\Users\Lin\Documents\Playground\
├── pyproject.toml                  # Package definition, dependencies
├── .env.example                    # Environment variable template
├── README.md                        # Project overview
├── AGENTS.md                        # GSD workflow documentation
├── src/dm_bot/                     # Main package (105 Python files as of 2026-04-02)
│   ├── __init__.py
│   ├── main.py                     # CLI entry: preflight, run-bot, smoke-check, etc.
│   ├── config.py                   # Settings via pydantic-settings
│   ├── logging.py                  # Structured logging setup
│   │
│   ├── adventures/                 # Module runtime (8 files)
│   │   ├── __init__.py
│   │   ├── models.py               # Adventure data models
│   │   ├── loader.py               # Load packaged adventures
│   │   ├── intent_parser.py        # Parse player intent within adventure
│   │   ├── intent_validator.py     # Validate adventure actions
│   │   ├── action_intent.py        # Action intent representation
│   │   ├── extraction.py           # Extract info from adventure
│   │   ├── extraction_validator.py # Validate extractions
│   │   ├── reaction_engine.py      # NPC/environment reactions
│   │   └── trigger_engine.py       # Trigger tree execution
│   │
│   ├── characters/                 # Character import sources
│   │   ├── __init__.py
│   │   ├── models.py               # Character data models
│   │   ├── sources.py              # Source definitions
│   │   ├── importer.py            # Character importer
│   │   └── skill_types.py         # Skill type definitions
│   │
│   ├── coc/                        # COC rules & character layer
│   │   ├── __init__.py
│   │   ├── archive.py             # InvestigatorArchiveRepository
│   │   ├── builder.py             # ConversationalCharacterBuilder
│   │   ├── panels.py              # Character panel rendering
│   │   └── assets.py              # COCAssetLibrary (PDF refs)
│   │
│   ├── diagnostics/                # Runtime diagnostics
│   │   ├── __init__.py
│   │   └── service.py            # DiagnosticsService
│   │
│   ├── discord_bot/               # Discord integration
│   │   ├── __init__.py
│   │   ├── client.py             # DiscordDmBot (462 lines)
│   │   ├── commands.py           # BotCommands handler
│   │   ├── feedback.py           # Feedback delivery
│   │   ├── channel_enforcer.py   # Channel role enforcement
│   │   ├── streaming.py          # Stream handling
│   │   ├── onboarding_views.py   # Onboarding UI
│   │   └── visibility_dispatcher.py
│   │
│   ├── gameplay/                 # Combat & scene helpers
│   │   ├── __init__.py
│   │   ├── combat.py            # Combat loop
│   │   ├── scene_formatter.py   # Scene presentation
│   │   └── modes.py             # Scene/gameplay modes
│   │
│   ├── models/                   # Model client & schemas
│   │   ├── __init__.py
│   │   ├── ollama_client.py     # OllamaClient (OpenAI-compatible)
│   │   └── schemas.py           # ModelRequest/ModelResponse
│   │
│   ├── narration/              # Narrator service
│   │   ├── __init__.py
│   │   └── service.py          # NarrationService (streaming)
│   │
│   ├── orchestrator/           # Session orchestration
│   │   ├── __init__.py
│   │   ├── gameplay.py        # GameplayOrchestrator
│   │   ├── session_store.py   # SessionStore
│   │   ├── turn_runner.py     # TurnRunner
│   │   ├── turns.py           # TurnCoordinator
│   │   ├── onboarding.py      # OnboardingController
│   │   ├── onboarding_controller.py
│   │   ├── player_status_renderer.py
│   │   ├── kp_ops_renderer.py # KP operations surfaces
│   │   ├── visibility.py      # Visibility management
│   │   ├── visibility_dispatcher.py
│   │   ├── message_filters.py
│   │   ├── consequence_aggregator.py
│   │   ├── routing_history.py
│   │   └── player_status_renderer.py
│   │
│   ├── persistence/            # SQLite persistence
│   │   ├── __init__.py
│   │   └── store.py          # PersistenceStore
│   │
│   ├── router/                # Intent routing
│   │   ├── __init__.py
│   │   ├── service.py       # RouterService
│   │   ├── intent.py        # Intent representations
│   │   ├── intent_classifier.py  # IntentClassifier
│   │   ├── intent_handler.py     # IntentHandlerRegistry
│   │   ├── contracts.py     # Routing contracts
│   │   └── message_buffer.py    # MessageBuffer
│   │
│   ├── rules/                # COC rules engine
│   │   ├── __init__.py
│   │   ├── engine.py       # RulesEngine
│   │   ├── dice.py         # Dice rolling
│   │   ├── actions.py      # Action resolution
│   │   ├── compendium.py   # FixtureCompendium
│   │   ├── skill_points.py
│   │   ├── skill_triggers.py
│   │   ├── skill_resolution.py
│   │   ├── skills.py
│   │   └── coc/            # COC-specific rules
│   │       ├── __init__.py
│   │       ├── skills.py
│   │       ├── sanity.py
│   │       ├── combat.py
│   │       ├── magic.py
│   │       ├── experience.py
│   │       └── derived.py
│   │
│   ├── runtime/             # App lifecycle / local operator tooling
│   │   ├── __init__.py
│   │   ├── app.py          # FastAPI app (create_app)
│   │   ├── health.py       # Health checks
│   │   ├── smoke_check.py  # Local smoke check
│   │   ├── restart_system.py
│   │   ├── control_service.py
│   │   ├── process_control.py
│   │   └── model_checks.py
│   │
│   └── testing/            # Test infrastructure
│       ├── __init__.py
│       ├── scenario_runner.py   # ScenarioRunner
│       ├── scenario_dsl.py      # ScenarioRegistry, ScenarioParser
│       ├── runtime_driver.py    # RuntimeTestDriver
│       ├── step_result.py
│       ├── failure_taxonomy.py
│       ├── artifact_writer.py
│       ├── cassette.py
│       └── test_trigger_chains.py
│
├── tests/                   # Test suite (77 test modules)
│   ├── conftest.py         # Pytest fixtures
│   ├── fakes/              # Fake implementations
│   │   ├── discord.py
│   │   ├── models.py
│   │   └── clock.py
│   ├── orchestrator/       # Orchestrator-specific tests
│   ├── bdd/               # BDD-style tests
│   └── test_*.py         # Unit/integration tests
│
└── .planning/              # GSD workflow artifacts
    ├── codebase/          # Codebase maps
    ├── milestones/        # Archived phase directories by milestone
    ├── quick/             # Quick-task plans and summaries
    ├── reports/           # Project-level milestone summaries/reports
    ├── workstreams/       # Track-specific roadmap/state truth
    └── active-workstream  # Default workstream pointer
```

### Naming Conventions

- **Python Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Test Files**: `test_<module>_<flow>.py`

### Entry Points

| Command | Function | Purpose |
|---------|----------|---------|
| `uv run python -m dm_bot.main preflight` | `describe_runtime()` | Check setup |
| `uv run python -m dm_bot.main run-bot` | `run_discord_bot()` | Start Discord bot |
| `uv run python -m dm_bot.main run-api` | `run_api()` | Start REST API |
| `uv run python -m dm_bot.main smoke-check` | `run_local_smoke_check()` | Validate setup |
| `uv run python -m dm_bot.main restart-system` | `run_restart_system()` | Restart system |
| `uv run python -m dm_bot.main run-control-panel` | `run_control_panel()` | Start control panel |
| `uv run python -m dm_bot.main run-scenario` | `run_scenario_cli()` | Run test scenarios |
