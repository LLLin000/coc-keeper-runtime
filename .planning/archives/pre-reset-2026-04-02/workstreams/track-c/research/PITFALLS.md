# Domain Pitfalls: Channel Governance and Command Discipline

**Project:** Discord AI Keeper  
**Researched:** 2026-03-28  
**Domain:** Track C - Discord 交互层 (Channel Governance)  
**Confidence:** MEDIUM

## Executive Summary

Adding channel discipline and command routing to an existing Discord bot with established patterns presents specific integration risks. The existing `SessionStore` already has channel binding infrastructure (`bind_archive_channel`, `bind_trace_channel`, `bind_admin_channel`), but lacks enforcement — commands execute regardless of channel type. This creates opportunities for users to invoke profile commands in game channels, admin commands in public channels, and diagnostic output in player-facing channels.

The primary risks are not in the channel binding logic itself, but in **integration with existing command handlers**, **persistence compatibility**, and **graceful handling of unbound channels**. Most pitfalls stem from adding validation layers that either break existing flows or create confusing user experiences.

---

## Critical Pitfalls

### Pitfall 1: Session Lookup Returns None But Command Proceeds

**What goes wrong:** Commands that check session existence (`get_by_channel`) but don't halt execution when `None` is returned. In `commands.py`, many methods check for `session is None` and return an error message — but the pattern is inconsistent, and some code paths bypass these checks entirely.

**Why it happens:** The original command handlers were designed for a single campaign-per-channel model. Adding channel-type enforcement requires consistent session lookup + validation at the start of every command, but retrofitting this is error-prone.

**Consequences:**
- Commands silently do nothing (no error, no action)
- Users see no response and think bot is broken
- State mutations attempt anyway, causing exceptions

**Prevention:** Create a decorator or wrapper that validates channel context before command execution:

```python
def require_channel_bound():
    async def wrapper(self, interaction, **kwargs):
        session = self._session_store.get_by_channel(str(interaction.channel_id))
        if session is None:
            await interaction.response.send_message(
                "当前频道未绑定任何战役。请先使用 `/bind_campaign` 绑定。",
                ephemeral=True
            )
            return
        return await original_method(self, interaction, **kwargs)
    return wrapper
```

**Detection:** Search for all `get_by_channel` calls and verify every code path has a `None` check with user-facing response.

**Phase to address:** Phase 45 (Command Routing) — this is core routing logic.

---

### Pitfall 2: Persistence Schema Migration Missing New Channel Fields

**What goes wrong:** Adding new channel binding fields to `SessionStore` but forgetting to handle them in `dump_sessions()` / `load_sessions()`. The existing `dump_sessions` already has a `_meta` section for channel bindings — but if new binding types are added without updating both serialization and deserialization, old saves silently lose data.

**Why it happens:** The `dump_sessions` / `load_sessions` pattern is manual. Each new field requires updating both methods, and there's no automated migration path.

**Consequences:**
- After bot restart, channel bindings disappear
- Users must re-run bind commands every restart
- Inconsistent state between runtime and persisted data

**Prevention:** 
1. Use Pydantic models with sensible defaults for all new channel bindings
2. Add version field to persistence format
3. Write a migration function that handles missing keys gracefully

```python
def load_sessions(self, payload: dict[str, dict[str, object]]) -> None:
    meta = dict(payload.get("_meta", {}))
    # Always provide defaults - don't assume keys exist
    self._archive_channels = dict(meta.get("archive_channels", {}))
    self._trace_channels = dict(meta.get("trace_channels", {}))
    self._admin_channels = dict(meta.get("admin_channels", {}))
    # For future fields, add with defaults:
    # self._game_channels = dict(meta.get("game_channels", {}))
```

**Phase to address:** Phase 44 (Channel Structure) — affects persistence foundation.

---

### Pitfall 3: Wrong-Channel Command Silently Fails or Confuses Users

**What goes wrong:** A user runs `/sheet` in a game hall instead of archive channel. The command checks channel type and redirects, but the redirect message is ephemeral (hidden), so the user never sees it.

**Why it happens:** In `commands.py` line 540-543, the `/sheet` command already has channel enforcement, but uses `ephemeral=True`:

```python
await interaction.response.send_message(
    f"请到角色档案频道 `<#{archive_channel}>` 查看长期角色信息。",
    ephemeral=True,
)
```

**Consequences:**
- User thinks command worked but didn't
- User pings moderators asking why bot is broken
- Confusion multiplies in multiplayer sessions

**Prevention:** Use `ephemeral=False` for channel redirect messages so the user sees the guidance:

```python
await interaction.response.send_message(
    f"此命令需在角色档案频道使用。当前频道 `<#{interaction.channel_id}>` 非档案频道。",
    ephemeral=False,  # User needs to see this
)
```

**Phase to address:** Phase 45 (Command Routing) — requires consistent ephemeral policy per message type.

---

### Pitfall 4: Guild-Scoped Bindings Conflict Across Multiple Campaigns

**What goes wrong:** The `SessionStore` binds archive/trace/admin channels at guild level (`_archive_channels[guild_id] = channel_id`), but campaigns are bound at channel level. In a server with two simultaneous campaigns, they share the same archive channel binding — but each campaign might want separate archive displays.

**Why it happens:** Original design assumed one campaign per guild. The binding model is flat (`guild_id -> channel_id`) rather than hierarchical (`campaign_id -> channel_id`).

**Consequences:**
- Two campaigns in same server show same archive data
- Privacy leaks between campaigns
- Confusion about which campaign's data is active

**Prevention:** Document the single-campaign-per-guild assumption and enforce it, OR upgrade bindings to be campaign-scoped:

```python
# Option A: Document and enforce
def bind_campaign(self, *, campaign_id: str, channel_id: str, guild_id: str, owner_id: str) -> CampaignSession:
    # Check existing campaign in this guild
    existing = [s for s in self._sessions.values() if s.guild_id == guild_id]
    if existing:
        raise ValueError(f"Guild {guild_id} already has campaign {existing[0].campaign_id}")
    
# Option B: Scope bindings to campaign
def archive_channel_for(self, campaign_id: str) -> str | None:
    session = self._get_by_campaign(campaign_id)
    return session.archive_channel if session else None
```

**Phase to address:** Phase 44 (Channel Structure) — requires architectural decision before Phase 45.

---

### Pitfall 5: Command Validation Logic Duplicated Across Handlers

**What goes wrong:** Each command method manually checks channel type, guild permissions, session existence. When adding channel governance, developers copy-paste validation patterns, creating inconsistent behavior.

**Why it happens:** No central command validation middleware. Each `async def` in `BotCommands` is independent.

**Consequences:**
- Some commands enforce channel rules, others don't
- Maintenance burden increases linearly with command count
- Security holes when new commands forget validation

**Prevention:** Extract validation to a command wrapper:

```python
class ChannelCommandRouter:
    def __init__(self, session_store, commands: BotCommands):
        self._session_store = session_store
        self._commands = commands
    
    async def route(self, interaction, command_name: str):
        handler = getattr(self._commands, command_name, None)
        
        # Get command's required channel type from metadata
        required_type = self._command_channel_requirements.get(command_name)
        if required_type:
            if not self._validate_channel(interaction, required_type):
                await self._send_redirect(interaction, required_type)
                return
        
        await handler(interaction)
    
    # Metadata-driven validation
    _command_channel_requirements = {
        "list_profiles": "archive",
        "admin_profiles": "admin",
        "debug_status": "trace",
        "take_turn": "game",
    }
```

**Phase to address:** Phase 45 (Command Routing) — benefits entire command ecosystem.

---

## Moderate Pitfalls

### Pitfall 6: Natural Message Processing Ignores Channel Type

**What goes wrong:** `handle_channel_message` and `handle_channel_message_stream` process any message in any channel that has a bound campaign, without checking if that channel type is appropriate for narrative input.

**Why it happens:** Message handlers were designed around campaign membership (`user_id in session.member_ids`) but not channel role.

**Consequences:**
- Players can inject narrative in admin-only channels
- Diagnostic triggers fire in game channels
- Archive builder accepts input in wrong channel

**Prevention:** Add channel type validation to message handlers:

```python
def _is_game_channel(self, guild_id: str, channel_id: str) -> bool:
    game_channel = self._session_store.game_channel_for(guild_id)
    return game_channel and str(channel_id) == str(game_channel)
```

**Phase to address:** Phase 45 (Command Routing) — extends routing logic to message flows.

---

### Pitfall 7: Missing Graceful Degradation When No Channel Bound

**What goes wrong:** Commands fail completely when no channel is bound, rather than providing helpful guidance. Users see technical errors ("NoneType has no attribute...") or silent failures.

**Why it happens:** Error handling focuses on expected states (campaign exists, user is member) but not on missing configuration.

**Consequences:**
- New users unable to figure out initial setup
- Bot appears broken on first use
- Support burden increases

**Prevention:** Every command should handle "not configured" state with user-friendly message:

```python
async def take_turn(self, interaction, *, content: str) -> None:
    # First: check if campaign is bound at all
    if not self._session_store.get_by_channel(str(interaction.channel_id)):
        await interaction.response.send_message(
            "此频道未绑定战役。请先创建或绑定一个战役后再开始游戏。\n"
            "使用 `/bind_campaign campaign_id:xxx` 绑定现有战役，"
            "或联系管理员创建新战役。",
            ephemeral=True
        )
        return
    
    # Then: check session membership
    session = self._session_store.get_by_channel(str(interaction.channel_id))
    if str(interaction.user.id) not in session.member_ids:
        await interaction.response.send_message(
            "你尚未加入此战役。请先使用 `/join_campaign` 加入。",
            ephemeral=True
        )
        return
    
    # Proceed with normal flow...
```

**Phase to address:** Phase 46 (Guidance & Polish) — user experience improvement.

---

### Pitfall 8: Duplicate Channel Bindings Allowed Without Warning

**What goes wrong:** Calling `bind_archive_channel` twice with different channels silently overwrites the old binding without warning. Server admins may accidentally bind wrong channels.

**Why it happens:** Simple dict assignment, no validation:

```python
def bind_archive_channel(self, *, guild_id: str, channel_id: str) -> None:
    self._archive_channels[guild_id] = channel_id  # Overwrites silently
```

**Consequences:**
- Lost channel bindings without user awareness
- Confusion about which channel is "official"
- Debugging difficulty when bindings mysteriously change

**Prevention:** Add confirmation or overwrite warning:

```python
def bind_archive_channel(self, *, guild_id: str, channel_id: str) -> str:
    existing = self._archive_channels.get(guild_id)
    if existing and existing != channel_id:
        # Return signal that overwrote
        self._archive_channels[guild_id] = channel_id
        return f"overwritten:{existing}"
    self._archive_channels[guild_id] = channel_id
    return "ok"
```

**Phase to address:** Phase 44 (Channel Structure) — governance feature.

---

## Minor Pitfalls

### Pitfall 9: Inconsistent Ephemeral Usage Confuses Users

**What goes wrong:** Some command responses are ephemeral (private), others are public, with no clear pattern. Users can't predict what they'll see.

**Prevention:** Establish clear policy:
- **Ephemeral:** Personal errors, profile details, admin-only data
- **Public:** Game narration, roll results, channel redirects, welcome messages

**Phase to address:** Phase 46 (Guidance & Polish)

---

### Pitfall 10: Channel ID Type Mismatch (str vs int)

**What goes wrong:** Discord channel IDs are integers in the API but stored as strings in `SessionStore`. Mixing types causes lookup failures.

**Prevention:** Normalize to string at boundary entry:

```python
def bind_campaign(self, *, campaign_id: str, channel_id: str, guild_id: str, owner_id: str) -> CampaignSession:
    channel_id = str(channel_id)  # Always normalize
    guild_id = str(guild_id)
    # ...
```

**Phase to address:** Phase 44 (Channel Structure) — foundation fix.

---

## Phase-Specific Warnings

| Phase | Likely Pitfall | Mitigation |
|-------|----------------|------------|
| **Phase 44: Channel Structure** | Persistence schema mismatch with new binding types | Use Pydantic defaults, add migration path |
| **Phase 44: Channel Structure** | Guild-level binding conflicts with multi-campaign servers | Decide single-campaign-per-guild policy now |
| **Phase 45: Command Routing** | Duplicate validation logic across commands | Build command router with metadata-driven rules |
| **Phase 45: Command Routing** | Natural messages process in wrong channels | Add channel-type check to message handlers |
| **Phase 46: Guidance & Polish** | Ephemeral messages hide redirect guidance | Use public messages for channel redirects |

---

## Integration Checkpoints

When implementing channel governance, verify these existing patterns still work:

1. **SessionStore persistence** — Run `smoke-check` after any `SessionStore` change
2. **Slash command registration** — Commands should still register after adding channel validation
3. **Archive channel binding** — `/sheet` redirect already works; verify it still does
4. **Message handling in game hall** — Ensure narrative input still flows after adding channel checks
5. **Campaign bind/join flow** — Verify `bind_campaign` + `join_campaign` + `ready` still works end-to-end

---

## Sources

- Discord.py command handling: https://discordjs.guide/creating-your-bot/command-handling
- Discord bot architecture patterns: https://arnauld-alex.com/building-a-production-ready-discord-bot-architecture-beyond-discordjs
- Avrae channel design: https://avrae.readthedocs.io/
- Session state issues: GitHub issue #41825 (response delivered to wrong channel after session compaction)
