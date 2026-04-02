# CONCERNS.md

## Known Concerns & Technical Debt

### Discord Startup & Delivery

**Status**: Initial implementation complete but needs ongoing validation

- Slash command sync can fail silently
- Streaming responses may drop on slow connections
- No guaranteed delivery for ephemeral messages
- Guild vs DM command visibility differences

**See Also**: `src/dm_bot/discord_bot/client.py` — command registration

### Multiplayer Complexity

**Status**: Working but limited

- Session state synchronization is eventual, not immediate
- No optimistic locking on concurrent character updates
- `MessageBuffer` handles round-robin but edge cases exist
- `TurnCoordinator` assumes sequential submission

**See Also**: `src/dm_bot/orchestrator/turns.py`, `src/dm_bot/router/message_buffer.py`

### Character Archive & Builder Integration

**Status**: Functional but incomplete

- Archive projection (semantic extraction) quality varies with model
- `ModelGuidedArchiveSemanticExtractor` depends heavily on narrator model quality
- No formal migration path when archive schema changes
- Profile selection vs campaign binding boundary fuzzy

**See Also**: `src/dm_bot/coc/archive.py`, `src/dm_bot/coc/builder.py`

### Adventure Module Structure

**Status**: Room graph implemented, event graph nascent

- Trigger tree execution is brittle for complex conditions
- Consequence chain lacks transactional semantics
- Reveal policies not formally enforced
- Module extraction workflow not mature for large-scale collaborative authoring

**See Also**: `src/dm_bot/adventures/trigger_engine.py`, `src/dm_bot/adventures/reaction_engine.py`

### Private Information Flow

**Status**: Partial implementation

- KP trace channel exists but visibility dispatch is incomplete
- Per-player private info (secrets, SAN, clues) not fully isolated
- No formal "reveal gate" — relies on narrative discipline

**See Also**: `src/dm_bot/orchestrator/visibility.py`, `src/dm_bot/discord_bot/visibility_dispatcher.py`

### UI Richness

**Status**: Text-only, Discord native

- No rich UI panels (buttons, select menus) beyond basic views
- Character sheets, clue boards, maps are text-formatted
- Future direction: Discord Activity for richer UI
- Current workaround: ASCII art, code blocks

**See Also**: `src/dm_bot/coc/panels.py`, `src/dm_bot/gameplay/scene_formatter.py`

### Model Dependency

**Status**: Local models required

- Requires Ollama running with specific models
- `qwen3:1.7b` (router) + `qwen3:4b-instruct-2507-q4_K_M` (narrator) minimum
- 8GB+ VRAM recommended for narrator
- No fallback to cloud models

**See Also**: `src/dm_bot/models/ollama_client.py`, `src/dm_bot/config.py`

### Governance & Admin Roles

**Status**: First layer only

- Admin role binding exists (`bind_admin_channel`)
- Single-main-character assumption
- Campaign ownership transfer not implemented
- Archive profile deletion is soft-delete only

**See Also**: `src/dm_bot/discord_bot/commands.py` — admin commands

### Testing Coverage

**Status**: 68 test files but gaps

- Scenario runner exists but not all scenarios covered
- BDD tests limited to combat round
- No performance/load testing
- Integration tests use fakes, not real Discord

**See Also**: `tests/`, `src/dm_bot/testing/`

### Code Quality Observations

- `src/dm_bot/main.py` has dead code (duplicate `message_buffer`, `intent_handler_registry`, `turn_runner`, `session_store` initialization — lines 124-158 repeats lines 88-118)
- Some modules lack docstrings
- No formal deprecation policy for CLI commands

### Documentation Gaps

- No formal API docs for REST endpoints
- Module authoring guide missing
- Developer onboarding relies on tribal knowledge
- README "What Is Still Missing" section is extensive but not prioritized
