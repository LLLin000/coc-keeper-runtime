# Stack Research: Channel Governance and Command Discipline

**Domain:** Discord Bot Command Routing and Channel Enforcement
**Researched:** 2026-03-28
**Confidence:** HIGH

## Executive Summary

The existing discord.py stack is **fully sufficient** for implementing channel governance and command discipline. No new external libraries are required. The implementation should focus on:

1. Leveraging discord.py's built-in `@commands.check` decorator pattern for channel-specific restrictions
2. Creating a channel context utility for cleaner channel type detection
3. Adding a command routing layer with redirect messages

---

## Recommended Stack

### Core Technologies (No Changes)

| Technology | Current Version | Purpose | Why |
|------------|-----------------|---------|-----|
| `discord.py` | Latest stable | Discord bot framework | Already in use, provides all needed primitives |
| Python | 3.12+ | Runtime | Already in use |

**No new dependencies needed.** The existing stack already contains all primitives required for channel governance:
- `discord.py` has built-in `@commands.check` decorator for custom channel restrictions
- `SessionStore` already tracks channel bindings (archive, trace, admin per guild)
- Existing command handlers already perform ad-hoc channel validation (e.g., `show_sheet`)

### What Needs to Be Built (Not Purchased)

| Component | Implementation | Why |
|-----------|---------------|-----|
| Channel context utility | New module in `discord_bot/` | Detects current channel type from session store |
| Command routing layer | New decorator/wrapper | Routes commands to correct handler or shows redirect |
| Channel-aware checks | New check functions | Uses `@commands.check` pattern with custom failures |

---

## Implementation Patterns

### Pattern 1: Custom Channel Check with Redirect

```python
from discord.ext import commands
from discord.app_commands import AppCommandError

class WrongChannelError(AppCommandError):
    def __init__(self, command: str, correct_channel: str, channel_mention: str):
        self.command = command
        self.correct_channel = correct_channel
        self.channel_mention = channel_mention
        super().__init__(f"请在 {channel_mention} 使用此命令。")

def channel_check(channel_type: str):
    """Decorator to restrict command to specific channel type."""
    async def predicate(interaction: discord.Interaction) -> bool:
        # Implementation checks interaction.channel_id against SessionStore
        # Raises WrongChannelError with redirect message if wrong channel
        return True
    return commands.check(predicate)
```

**Source:** discord.py custom checks documentation - Context7 `/rapptz/discord.py`

### Pattern 2: Command Routing Table

```python
COMMAND_CHANNEL_MAP = {
    # Archive commands -> archive channel
    "profiles": {"channel": "archive", "redirect": "<#{archive_channel}>"},
    "profile_detail": {"channel": "archive", "redirect": "<#{archive_channel}>"},
    "start_builder": {"channel": "archive", "redirect": "<#{archive_channel}>"},
    # Game commands -> game hall (bound campaign channel)
    "turn": {"channel": "game", "redirect": None},  # None = allowed in game only
    "ready": {"channel": "game", "redirect": None},
    # Admin commands -> admin channel
    "admin_profiles": {"channel": "admin", "redirect": "<#{admin_channel}>"},
}
```

### Pattern 3: Contextual Guidance Based on Channel

```python
def channel_guidance(channel_type: str | None) -> str:
    """Returns contextual help text based on current channel."""
    guides = {
        "archive": "这是角色档案频道。使用 /profiles 查看角色，/start_builder 创建新角色。",
        "game": "这是游戏大厅。使用 /ready 就位后开始游戏，或直接发送消息推进剧情。",
        "admin": "这是管理员频道。用于角色治理和系统管理。",
        "trace": "这是 KP trace 频道。用于调试和运行时诊断。",
        None: "未绑定到任何已知频道类型。请先使用 /bind_archive_channel 等命令绑定。",
    }
    return guides.get(channel_type, guides[None])
```

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `discord-appcommands` package | Redundant - discord.py has built-in app command support | Native `discord.py` slash commands |
| Channel permission checks alone | Slash commands override channel permissions | Custom `@commands.check` decorators |
| Global command restrictions | Not flexible for multi-campaign servers | Per-guild channel binding via SessionStore |

---

## Implementation Architecture

### New Components

```
src/dm_bot/discord_bot/
  ├── __init__.py
  ├── client.py          (existing - register commands)
  ├── commands.py        (existing - command handlers)
  ├── checks.py          (NEW - channel check decorators)
  ├── routing.py         (NEW - command routing logic)
  └── guidance.py        (NEW - contextual help text)
```

### Data Flow

```
Interaction received
       ↓
routing.py: COMMAND_CHANNEL_MAP lookup
       ↓
checks.py: channel_check(channel_type) validates
       ↓
   ├── Valid → commands.py: handler executes
   └── Invalid → WrongChannelError with redirect
       ↓
guidance.py: channel_guidance(current_type) for help text
```

---

## Integration with Existing Code

### SessionStore Integration

The existing `SessionStore` already provides:
- `archive_channel_for(guild_id)` → channel_id or None
- `trace_channel_for(guild_id)` → channel_id or None  
- `admin_channel_for(guild_id)` → channel_id or None
- `get_by_channel(channel_id)` → CampaignSession or None

The new channel context utility should wrap these methods:

```python
def get_channel_type(session_store: SessionStore, guild_id: str, channel_id: str) -> str | None:
    """Determine channel type for the current channel."""
    if session_store.archive_channel_for(guild_id) == channel_id:
        return "archive"
    if session_store.trace_channel_for(guild_id) == channel_id:
        return "trace"
    if session_store.admin_channel_for(guild_id) == channel_id:
        return "admin"
    if session_store.get_by_channel(channel_id) is not None:
        return "game"
    return None
```

### Commands.py Integration

Existing pattern already shows channel validation in some commands:
- Line 538-544: `show_sheet` checks archive channel and redirects
- Line 746-752: `_admin_channel_guidance` provides channel hints

**Recommendation:** Refactor these ad-hoc checks into the new centralized routing layer.

---

## Version Compatibility

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| discord.py | Latest stable (2.x) | Python 3.10+ | Already in use |
| Python | 3.12+ | discord.py 2.x | Already in use |
| pydantic | v2 line | discord.py 2.x | Already in use |

---

## Sources

- **Context7 `/rapptz/discord.py`** — Custom command checks, channel validation patterns
- **Stack Overflow** — Discord.py channel restriction patterns (community validated)
- **Existing codebase** — SessionStore channel binding implementation already in place

---

## Summary

**No new stack additions required.** The existing discord.py stack is fully capable of implementing channel governance through:

1. Custom `@commands.check` decorators for channel restrictions
2. A new channel context utility module
3. A command routing layer with redirect messages
4. Contextual guidance helpers

The implementation should focus on **building** these patterns into the existing codebase rather than adding external dependencies.

---

*Stack research for: Channel Governance and Command Discipline*
*Researched: 2026-03-28*
*Confidence: HIGH*
