# CONVENTIONS.md

## Code Conventions

### Python Standards

- **Python Version**: `>=3.12`
- **Type Safety**: Strict — no `as any`, `@ts-ignore`, `@ts-expect-error` (Pydantic v2 + explicit typing)
- **Error Handling**: No empty `catch(e) {}` blocks — always handle or re-raise
- **Async**: Use `asyncio` for I/O-bound operations

### Project-Specific Conventions

#### Settings Configuration

```python
# Use pydantic-settings with DM_BOT_ prefix
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DM_BOT_",
        env_file=".env",
        extra="ignore",
    )
```

#### Pydantic Models

```python
from pydantic import Field

class MyModel(BaseModel):
    field: str = Field(default="", description="Description")
```

#### Async Iterator Pattern (Streaming)

```python
from collections.abc import AsyncIterator

async def stream_narrator(self, request: ModelRequest) -> AsyncIterator[str]:
    async for chunk in self._stream_model(self.narrator_model, request):
        yield chunk
```

### Git Conventions

#### Branch Naming

```
codex/<feature-name>
```

Examples:
- `codex/track-b-archive-polish`
- `codex/fix-router-intent-classification`

#### Commit Message Format

```
<type>: <description>

<type> = feat | fix | docs | refactor | test | chore
```

Examples:
- `feat: add character archive`
- `fix: resolve SAN check overflow`
- `docs: update README with new commands`

#### Cross-Track Changes

Commit/PR descriptions must state:
- `Primary Track`
- `Secondary Impact`
- `Contracts Changed`
- `Migration Notes`

### GSD Workflow Conventions

**Workflow Entry Points** (use slash commands):
- `/gsd-quick` — small fixes, ad-hoc tasks
- `/gsd-debug` — investigation
- `/gsd-plan-phase` — plan a new phase
- `/gsd-execute-phase` — execute a planned phase
- `/gsd-verify-work` — validate features through UAT

**Phase Planning Flow**:
```
1. /gsd-plan-phase E## --prd <roadmap-file>   # Load phase context
2. [Optional] /gsd-discuss-phase              # Clarify scope
3. /gsd-execute-phase --auto                 # Plan → verify → execute
```

**Delivery Gate** (before claiming complete):
1. `uv run pytest -q` — all tests pass
2. `uv run python -m dm_bot.main smoke-check` — must pass
3. Diagnostics clean on all changed files

### Test Conventions

- **Location**: `tests/` directory mirroring `src/dm_bot/`
- **Naming**: `test_<module>_<flow>.py`
- **Fixtures**: `conftest.py` at `tests/conftest.py`
- **Async Tests**: `pytest-asyncio` with `asyncio_mode = "auto"`
- **Cassettes**: `vcrpy` for HTTP recording (see `tests/fakes/`)

### No Type Suppression

```python
# BAD
x = some_value  # type: ignore
x = some_value as Any

# GOOD
x: ExpectedType = some_value
```

### No Empty Catch Blocks

```python
# BAD
try:
    risky_operation()
except SomeException:
    pass  # silently ignoring

# GOOD
try:
    risky_operation()
except SomeException as e:
    logger.warning("Operation failed: %s", e)
    raise  # or handle appropriately
```
