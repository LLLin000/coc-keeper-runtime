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
/ready character_name:调查员A
```

所有已加入玩家都 `/ready` 之后，bot 会自动发《疯狂之馆》开场。之后普通消息才会进入正式跑团流程，玩家不需要每句都 `/turn`。

长回复现在会在 Discord 里渐进更新，同一条消息会一边生成一边变长，而不是始终等到最后一次性出现。

Examples:

- `我推开铁门，先看看里面有什么。`
- `@队友 你掩护我，我进去看看。`
- `//等等，我去倒杯水`

Behavior:

- normal in-character action messages are processed
- `//` messages are treated as OOC and ignored
- obvious player-to-player social chatter is ignored
- `/turn` still exists as a fallback and debug path

骰子相关命令：

- `/roll expression:1d20+3`
- `/check label:Perception modifier:3 advantage:none`
- `/save label:DEX modifier:2 advantage:advantage`
- `/attack target_name:Goblin target_ac:13 attack_bonus:5 damage_expression:1d8+3`

普通消息里也支持简写：

- `roll 1d20+3`
- `check Perception 3`
- `save DEX 2 disadvantage`

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
5. Each player runs `/ready`, optionally with `character_name`.
6. Wait for the automatic DM opening post.
7. Use ordinary messages for exploration and roleplay.
8. Use `/enter_scene` and `/end_scene` for multi-NPC performance scenes.
9. Use `/start_combat`, `/show_combat`, and `/next_turn` for combat control.

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
