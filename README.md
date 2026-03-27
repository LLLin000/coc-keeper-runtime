# dm-bot

Discord-native local AI DM runtime.

## Local Setup

1. Copy `.env.example` to `.env`
2. Fill `DM_BOT_DISCORD_TOKEN`
3. Optionally fill `DM_BOT_DISCORD_GUILD_ID` for instant guild command sync
4. Ensure Ollama has the configured models locally

## Runtime Commands

```powershell
uv run python -m dm_bot.main preflight
uv run python -m dm_bot.main run-api
uv run python -m dm_bot.main run-bot
```

## Default Local Models

- Router: `qwen3:1.7b`
- Narrator: `fluffy/l3-8b-stheno-v3.2:q4_K_M`
