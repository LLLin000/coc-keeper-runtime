# dm-bot

Discord-native local AI DM runtime.

## Quickstart

1. Copy `.env.example` to `.env`
2. Fill `DM_BOT_DISCORD_TOKEN`
3. Optionally fill `DM_BOT_DISCORD_GUILD_ID` for instant guild command sync
4. Ensure Ollama has the configured models locally:
   - `qwen3:1.7b`
   - `qwen3:4b-instruct-2507-q4_K_M`
5. Start the bot:

```powershell
uv run python -m dm_bot.main preflight
uv run python -m dm_bot.main run-bot
```

## Recommended Local Models

- Router: `qwen3:1.7b`
- Narrator: `qwen3:4b-instruct-2507-q4_K_M`

## First Session

In Discord, run:

```text
/setup
/bind_campaign campaign_id:test1
/join_campaign
/load_adventure adventure_id:mad_mansion
```

After that, ordinary messages in the bound channel become gameplay input. Players do not need to use `/turn` for every action.

Examples:

- `我推开铁门，先看看里面有什么。`
- `@队友 你掩护我，我进去看看。`
- `//等等，我去倒杯水`

Behavior:

- normal in-character action messages are processed
- `//` messages are treated as OOC and ignored
- obvious player-to-player social chatter is ignored
- `/turn` still exists as a fallback and debug path

## Restart Recovery

- bound campaigns and joined members are persisted in SQLite
- packaged adventure state is reloaded per campaign before play continues
- after bot restart, the group should usually be able to continue in the same channel without rebinding or rejoining
- `/debug_status campaign_id:test1` shows the current room, clues, pressure, and recent trace summary

## Multiplayer Flow

1. Bind one campaign to one channel or thread.
2. Each real player runs `/join_campaign`.
3. Optional: import a character with `/import_character`.
4. Load `疯狂之馆` with `/load_adventure adventure_id:mad_mansion`.
5. Use ordinary messages for exploration and roleplay.
6. Use `/enter_scene` and `/end_scene` for multi-NPC performance scenes.
7. Use `/start_combat`, `/show_combat`, and `/next_turn` for combat control.

During combat, only the active combatant's message is accepted as a turn. Other players are reminded whose turn it is.

## Runtime Commands

```powershell
uv run python -m dm_bot.main preflight
uv run python -m dm_bot.main run-api
uv run python -m dm_bot.main run-bot
```

## Docs

- [Multiplayer Quickstart](C:\Users\Lin\Documents\Playground\docs\operations\multiplayer-quickstart.md)
- [Starter Adventure Guide](C:\Users\Lin\Documents\Playground\docs\operations\starter-adventure-guide.md)
