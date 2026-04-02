# Architecture Research: Channel Governance for Discord AI Keeper

**Domain:** Discord Bot Runtime - Channel Governance and Command Discipline
**Researched:** 2026-03-28
**Confidence:** HIGH

**Primary Track:** Track C - Discord 交互层
**Milestone:** vC.1.1 Channel Governance And Command Discipline Hardening

---

## Executive Summary

Channel governance in this Discord AI Keeper system requires a middleware layer that intercepts command execution, validates channel context, and provides guided redirection when users invoke commands in inappropriate channels. The existing `SessionStore` already maintains channel role bindings (`archive`, `trace`, `admin`) at the guild level, but command-level channel discipline is currently implemented ad-hoc in individual command handlers. This architecture standardizes that pattern.

---

## Current Architecture Analysis

### Existing Components

| Component | Responsibility | Current State |
|-----------|---------------|---------------|
| `SessionStore` | Guild-level channel bindings | Has `archive_channel_for()`, `trace_channel_for()`, `admin_channel_for()` at guild level |
| `CampaignSession` | Per-channel campaign state | Bound to `channel_id`, contains `member_ids`, `active_characters`, `selected_profiles` |
| `BotCommands` | Slash command handlers | Individual commands check channel context (e.g., `show_sheet` at lines 538-544, `_admin_channel_guidance` at lines 746-752) |
| `discord_bot/client.py` | Discord interaction layer | Registers slash commands, handles message events |

### Current Gap

Channel discipline is currently handled case-by-case:
- `/sheet` checks archive channel (commands.py:538-544)
- `admin_profiles` shows guidance for admin channel (commands.py:746-752)
- No unified middleware pattern for channel-aware routing

---

## Recommended Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Discord Interaction Layer                         │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │  Slash Commands │    │  Message Events │    │  Button/Modal   │  │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘  │
│           │                       │                       │            │
│           └───────────────────────┼───────────────────────┘            │
│                                   ↓                                      │
│                    ┌──────────────────────────────┐                      │
│                    │   Channel Governance Layer   │  NEW                │
│                    │   (ChannelEnforcer Middleware)│                      │
│                    └──────────────────────────────┘                      │
│                                   ↓                                      │
├───────────────────────────────────────────────────────────────────────────┤
│                           Session Store Layer                            │
├───────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                        SessionStore                                  │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │ │
│  │  │ Guild Chans │  │ Campaign    │  │ Member      │  │ Role      │ │ │
│  │  │ Archive/    │  │ Sessions    │  │ Bindings    │  │ Bindings  │ │ │
│  │  │ Trace/Admin │  │ (per ch)    │  │             │  │           │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
├───────────────────────────────────────────────────────────────────────────┤
│                           Command Handler Layer                          │
├───────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                         BotCommands                                  │ │
│  │  • archive commands (builder, profiles, sheet)                     │ │
│  │  • game commands (take_turn, ready, combat)                       │ │
│  │  • admin commands (profiles, debug_status)                         │ │
│  │  • roll commands (coc_check, san_roll, etc.)                       │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
```

### New Component: ChannelEnforcer

**File location:** `src/dm_bot/discord_bot/channel_enforcer.py`

```python
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Awaitable

class ChannelRole(Enum):
    ARCHIVE = "archive"      # Character profiles, builder, sheets
    GAME = "game"            # Game hall - main play channel
    ADMIN = "admin"          # Admin operations, diagnostics
    TRACE = "trace"          # KP diagnostics, debug output
    GENERAL = "general"      # Any channel, no restrictions

@dataclass
class ChannelPolicy:
    role: ChannelRole
    allowed_commands: set[str]
    redirect_to: ChannelRole | None = None
    redirect_message_template: str = "请到 {channel} 使用此命令。"

class ChannelEnforcer:
    def __init__(self, session_store):
        self._session_store = session_store
        self._policies: dict[str, ChannelPolicy] = {}  # command_name -> policy
    
    def register_policy(self, command_name: str, policy: ChannelPolicy) -> None:
        self._policies[command_name] = policy
    
    def register_default_policies(self) -> None:
        # Archive channel commands
        self.register_policy("start_builder", ChannelPolicy(
            role=ChannelRole.ARCHIVE,
            allowed_commands={"start_builder", "builder_reply", "list_profiles"}
        ))
        self.register_policy("profiles", ChannelPolicy(
            role=ChannelRole.ARCHIVE,
            allowed_commands={"profiles", "profile_detail", "activate_profile"}
        ))
        self.register_policy("sheet", ChannelPolicy(
            role=ChannelRole.ARCHIVE,
            allowed_commands={"sheet"},
            redirect_to=ChannelRole.ARCHIVE
        ))
        
        # Game hall commands
        self.register_policy("take_turn", ChannelPolicy(
            role=ChannelRole.GAME,
            allowed_commands={"take_turn", "ready_for_adventure", "load_adventure"}
        ))
        self.register_policy("bind_campaign", ChannelPolicy(
            role=ChannelRole.GAME,
            allowed_commands={"bind_campaign", "join_campaign", "leave_campaign"}
        ))
        
        # Admin commands
        self.register_policy("admin_profiles", ChannelPolicy(
            role=ChannelRole.ADMIN,
            allowed_commands={"admin_profiles", "debug_status"}
        ))
        self.register_policy("debug_status", ChannelPolicy(
            role=ChannelRole.ADMIN,
            allowed_commands={"debug_status", "coc_assets_summary"}
        ))
    
    def get_channel_role(self, guild_id: str, channel_id: str) -> ChannelRole:
        """Determine channel role from SessionStore bindings."""
        if self._session_store.archive_channel_for(guild_id) == channel_id:
            return ChannelRole.ARCHIVE
        if self._session_store.admin_channel_for(guild_id) == channel_id:
            return ChannelRole.ADMIN
        if self._session_store.trace_channel_for(guild_id) == channel_id:
            return ChannelRole.TRACE
        # Check if bound to a campaign session = game channel
        session = self._session_store.get_by_channel(channel_id)
        if session is not None:
            return ChannelRole.GAME
        return ChannelRole.GENERAL
    
    def check_command(self, command_name: str, guild_id: str, channel_id: str) -> tuple[bool, str | None]:
        """
        Returns (allowed, redirect_message).
        If allowed=True, redirect_message=None.
        If allowed=False, redirect_message contains guidance.
        """
        policy = self._policies.get(command_name)
        if policy is None:
            return True, None  # No policy = allow
        
        current_role = self.get_channel_role(guild_id, channel_id)
        
        if policy.role == current_role:
            return True, None
        
        if policy.redirect_to:
            target_channel_id = self._get_channel_for_role(guild_id, policy.redirect_to)
            if target_channel_id:
                redirect_msg = policy.redirect_message_template.format(
                    channel=f"<#{target_channel_id}>"
                )
                return False, redirect_msg
        
        # No redirect configured - generic denial
        return False, f"此命令不能在当前频道使用。"
    
    def _get_channel_for_role(self, guild_id: str, role: ChannelRole) -> str | None:
        if role == ChannelRole.ARCHIVE:
            return self._session_store.archive_channel_for(guild_id)
        if role == ChannelRole.ADMIN:
            return self._session_store.admin_channel_for(guild_id)
        if role == ChannelRole.TRACE:
            return self._session_store.trace_channel_for(guild_id)
        return None
```

### Integration Pattern: Middleware Wrapper

**Option A: Command Handler Wrapper (Recommended)**

Modify `BotCommands` to wrap execution with channel enforcement:

```python
class BotCommands:
    def __init__(self, /* existing params */, channel_enforcer=None):
        # ... existing init
        self._channel_enforcer = channel_enforcer
    
    async def _execute_with_channel_check(self, interaction, command_name: str, handler: Callable):
        """Middleware wrapper for channel discipline."""
        if self._channel_enforcer is None:
            return await handler()
        
        allowed, redirect = self._channel_enforcer.check_command(
            command_name=command_name,
            guild_id=str(interaction.guild_id),
            channel_id=str(interaction.channel_id)
        )
        
        if not allowed:
            await interaction.response.send_message(redirect, ephemeral=True)
            return None
        
        return await handler()
    
    async def sheet(self, interaction) -> None:
        await self._execute_with_channel_check(interaction, "sheet", self._sheet_impl)
    
    async def _sheet_impl(self, interaction) -> None:
        # Original implementation
        ...
```

**Option B: Discord.py Cog Pattern**

Use Discord.py's cog system with channel checks as bot checks:

```python
from discord import app_commands
from discord.ext import commands

class ArchiveCog(commands.Cog):
    def __init__(self, bot, channel_enforcer):
        self.bot = bot
        self.channel_enforcer = channel_enforcer
    
    @app_commands.command(name="profiles")
    @app_commands.check(self.archive_channel_check)
    async def profiles(self, interaction):
        ...
    
    async def archive_channel_check(self, interaction) -> bool:
        allowed, redirect = self._channel_enforcer.check_command(
            "profiles",
            str(interaction.guild_id),
            str(interaction.channel_id)
        )
        if not allowed:
            await interaction.response.send_message(redirect, ephemeral=True)
            return False
        return True
```

**Recommendation:** Option A preserves existing command structure and minimizes refactoring. Option B provides cleaner separation but requires restructuring commands into cogs.

---

## Channel Role Definitions

| Role | Purpose | Typical Commands | Binding Method |
|------|---------|------------------|----------------|
| `ARCHIVE` | Character profiles, builder, long-term data | `/start_builder`, `/profiles`, `/sheet`, `/profile_detail` | `bind_archive_channel` |
| `GAME` | Active play, narrative turns | `/take_turn`, `/ready`, `/load_adventure`, combat cmds | Campaign bound to channel |
| `ADMIN` | Server management, diagnostics | `/admin_profiles`, `/debug_status` | `bind_admin_channel` |
| `TRACE` | KP-only diagnostics, debug output | `/debug_status` (KP) | `bind_trace_channel` |
| `GENERAL` | Unrestricted channels | `/roll`, `/check`, inline dice | None required |

---

## Data Flow Changes

### Current Flow (Commands)

```
User → Slash Command → BotCommands.handler() → SessionStore lookup → Execute → Response
```

### New Flow (With Channel Governance)

```
User → Slash Command → ChannelEnforcer.check_command() 
                                        ↓
                    ┌───────────────────┴───────────────────┐
                    ↓                                       ↓
            Allowed: Pass to                  Blocked: Return redirect message
            BotCommands.handler()             to user (ephemeral)
                    ↓
            SessionStore lookup
                    ↓
            Execute → Response
```

### State Changes Required

| Area | Change | Scope |
|------|--------|-------|
| `SessionStore` | Add `game_channels: dict[str, str]` for guild→game channel mapping | NEW - track which channels are game halls |
| `ChannelEnforcer` | New module | NEW |
| `BotCommands` | Add `channel_enforcer` param, wrap handlers | MODIFY |
| Config/Settings | Add channel governance toggle | MODIFY |

---

## Recommended Project Structure

```
src/dm_bot/
├── discord_bot/
│   ├── __init__.py
│   ├── client.py              # Discord client, event registration
│   ├── commands.py            # Slash command handlers (MODIFY: add enforcer)
│   ├── channel_enforcer.py    # NEW: Channel discipline middleware
│   ├── streaming.py           # Message transport
│   └── Cog/                   # Optional: if using cog pattern
│       ├── __init__.py
│       ├── archive_cog.py
│       ├── game_cog.py
│       └── admin_cog.py
├── orchestrator/
│   └── session_store.py       # MODIFY: add game_channels binding
└── ...
```

### Structure Rationale

- **`channel_enforcer.py`**: Centralized channel policy enforcement - single responsibility
- **`Cog/` folder**: Only needed if migrating to Discord.py cog pattern for cleaner command grouping
- **Minimal changes to existing**: Keep `session_store.py` modifications minimal, only add what's needed

---

## Phase-Specific Implementation Order

### Phase 44: Channel Structure (Foundation)

1. **Add `game_channels` to `SessionStore`:**
   ```python
   def bind_game_channel(self, *, guild_id: str, channel_id: str) -> None:
       self._game_channels[guild_id] = channel_id
   
   def game_channel_for(self, guild_id: str) -> str | None:
       return self._game_channels.get(guild_id)
   ```

2. **Create `ChannelEnforcer` class** with basic policy registration

3. **Wire `ChannelEnforcer` into `BotCommands` constructor**

### Phase 45: Command Routing (Enforcement)

1. **Register default policies** for all existing commands
   - Extract current ad-hoc checks (show_sheet, admin_profiles) into policies
   - Add new policies for commands lacking channel discipline

2. **Add middleware wrapper** to command handlers

3. **Add redirect messages** with helpful channel references

### Phase 46: Guidance & Polish (UX)

1. **Add welcome message** for new users explaining channel structure
2. **Configure ephemeral mode** for long outputs
3. **Add help command enhancement** showing recommended channel
4. **Add diagnostics channel isolation** - ensure trace stays in trace

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Hardcoding Channel IDs in Commands

**What people do:**
```python
async def sheet(self, interaction):
    if str(interaction.channel_id) == "123456789":
        # Show sheet
```

**Why it's wrong:** Fragile, not configurable, breaks when channels change

**Do this instead:** Use `ChannelEnforcer` with `SessionStore` bindings

### Anti-Pattern 2: Blocking All Commands in Wrong Channel

**What people do:** Redirect everything to archive channel, including rolls

**Why it's wrong:** Dice rolls (`/roll`, `/coc`) should work anywhere

**Do this instead:** Define allowed commands per role, not blanket bans

### Anti-Pattern 3: Storing Channel Policies in Database

**What people do:** Create database tables for channel policies

**Why it's wrong:** Over-engineering for a Discord bot; policies are code, not data

**Do this instead:** Keep policies in `ChannelEnforcer` as Python objects; only store bindings in `SessionStore`

---

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `ChannelEnforcer` ↔ `SessionStore` | Direct method calls | `ChannelEnforcer` reads bindings, doesn't modify |
| `ChannelEnforcer` ↔ `BotCommands` | Handler wrapper | Commands check policy before execution |
| `ChannelEnforcer` → Discord API | Redirect messages | Sends via `interaction.response.send_message()` |

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Discord API | `interaction.response.send_message(ephemeral=True)` | Used for redirect messages |
| Persistence | Via existing `SessionStore.dump_sessions()` | No new persistence needed |

---

## Scalability Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1 servers | Single `ChannelEnforcer` instance is fine |
| 1-10 servers | Add `guild_id` scoping to all `ChannelEnforcer` methods |
| 10+ servers | Consider `ChannelEnforcer` as injectable service, not singleton |

### Scaling Priorities

1. **First consideration:** Guild scoping - ensure channel policies are per-guild, not global
2. **Second consideration:** Policy caching - policies are read-heavy, consider caching

---

## Sources

- Existing `SessionStore` implementation: `src/dm_bot/orchestrator/session_store.py`
- Existing command handlers: `src/dm_bot/discord_bot/commands.py`
- Discord.py app commands: https://discordpy.readthedocs.io/en/stable/
- Discord.py checks: https://discordpy.readthedocs.io/en/stable/api.html#discord.app_commands.check

---

*Architecture research for: Discord AI Keeper - Channel Governance*
*Researched: 2026-03-28*
*Confidence: HIGH - Based on existing codebase analysis and standard Discord.py patterns*
