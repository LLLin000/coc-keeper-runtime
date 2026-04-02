# INTEGRATIONS.md

## External Integrations

### Discord API

**Integration Pattern**: `discord.py` with app commands (slash commands)

- **Entry Point**: `src/dm_bot/discord_bot/client.py` — `DiscordDmBot` class
- **Intents**: `guilds`, `messages`, `message_content`
- **Command Registration**: `@tree.command` decorator in `_register_commands()`
- **Streaming**: `on_message` handler with `channel.typing()` for streaming responses
- **Config**: `DM_BOT_DISCORD_TOKEN`, `DM_BOT_DISCORD_APPLICATION_ID`, `DM_BOT_DISCORD_PUBLIC_KEY`, `DM_BOT_DISCORD_GUILD_ID`

**Key Commands** (40+ slash commands):
- Campaign: `bind_campaign`, `join_campaign`, `leave_campaign`
- Character: `start_builder`, `builder_reply`, `profiles`, `profile_detail`, `select_profile`
- Adventure: `load_adventure`, `ready`, `start-session`
- Combat: `start_combat`, `show_combat`, `next_turn`, `resolve_round`
- Rolls: `roll`, `check`, `save`, `coc_check`, `san_check`, `attack`
- Admin: `bind_archive_channel`, `bind_trace_channel`, `bind_admin_channel`

### Ollama (Local Models)

**Integration Pattern**: OpenAI-compatible API via `httpx` / `openai` client

- **Client**: `src/dm_bot/models/ollama_client.py` — `OllamaClient`
- **Base URL**: `http://localhost:11434/v1` (configurable via `DM_BOT_OLLAMA_BASE_URL`)
- **Auth**: API key `"ollama"` (placeholder)
- **Models Used**:
  - Router (`qwen3:1.7b`): Fast structured routing decisions
  - Narrator (`qwen3:8b` or `qwen3:4b-instruct-2507-q4_K_M`): Streaming narration

**Capabilities**:
- Non-streaming: `call_router()`, `call_narrator()`
- Streaming: `stream_narrator()` → `AsyncIterator[str]`

### SQLite Persistence

**Integration**: Direct SQLAlchemy 2.0 usage

- **Location**: `src/dm_bot/persistence/store.py` — `PersistenceStore`
- **Database**: `dm_bot.sqlite3` (file-based)
- **Data Stored**:
  - Archive profiles
  - Session state
  - Campaign data
  - Event logs

### FastAPI Control Panel

**Integration**: `src/dm_bot/runtime/app.py` + `src/dm_bot/runtime/control_service.py`

- **Port**: `8001` (control panel)
- **Purpose**: Local runtime diagnostics and control
- **Health checks**: `src/dm_bot/runtime/health.py`

### COC Asset Library

**Integration**: `src/dm_bot/coc/assets.py` — `COCAssetLibrary`

- **Local Assets**: PDF rulebooks, investigator PDFs
- **Community References**: External URLs (e.g., cthulhuclub.com)
- **Config**: `DM_BOT_COC_ASSET_ROOT` (default: `C:/Users/Lin/Downloads/COC`)

## No External Services

- No cloud DB (SQLite only)
- No hosted LLM (local Ollama only)
- No webhooks
- No authentication providers beyond Discord
