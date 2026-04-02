# STACK.md

## Technology Stack

### Core Language & Runtime
- **Python**: `>=3.12`
- **Package Manager**: `uv` (via `pyproject.toml`)

### Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `discord.py` | `>=2.7.0` | Discord API client, slash commands, streaming |
| `fastapi` | `>=0.116.0` | REST API / control panel |
| `pydantic` | `>=2.11.0` | Data validation, settings |
| `pydantic-settings` | `>=2.10.0` | Environment-based settings |
| `sqlalchemy` | `2.0+` | ORM (via direct usage in `persistence/store.py`) |
| `httpx` | `>=0.28.0` | HTTP client for Ollama API |
| `openai` | `>=2.0.0` | OpenAI-compatible client for Ollama |
| `orjson` | `>=3.11.0` | Fast JSON serialization |
| `structlog` | `>=25.0.0` | Structured logging |
| `tenacity` | `>=9.1.0` | Retry logic |
| `uvicorn` | `>=0.35.0` | ASGI server |
| `d20` | `>=1.1.2` | Dice rolling library |

### Testing Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | `>=9.0.0` | Test framework |
| `pytest-asyncio` | `>=1.3.0` | Async test support |
| `pytest-bdd` | `>=8.0.0` | BDD-style tests |
| `vcrpy` | `>=6.0.0` | HTTP cassette recording |

### Model Layer

- **Local Models**: Ollama (OpenAI-compatible API)
- **Default Models**:
  - `router_model`: `qwen3:1.7b` — fast, structured routing
  - `narrator_model`: `qwen3:8b` (configured) / `qwen3:4b-instruct-2507-q4_K_M` (production) — narration

### Infrastructure

- **Database**: SQLite (`dm_bot.sqlite3`)
- **Persistence**: File-based + SQLite (see `src/dm_bot/persistence/store.py`)
- **Configuration**: Environment variables via `pydantic-settings` with `DM_BOT_` prefix
- **Runtime Control**: FastAPI + local process/restart tooling under `src/dm_bot/runtime/`

### Project Structure

```
pyproject.toml          # Package definition, dependencies
.env.example             # Environment template
src/dm_bot/              # Main package (105 Python files as of 2026-04-02)
tests/                   # Test suite (77 test modules as of 2026-04-02)
```

### Python Path Configuration

```toml
[tool.pytest.ini_options]
pythonpath = ["src", "."]
testpaths = ["tests"]
asyncio_mode = "auto"
```
