# Project Research Summary

**Project:** Discord AI Keeper — Track C: Discord 交互层
**Domain:** Discord Bot Channel Governance and Command Discipline
**Researched:** 2026-03-28
**Confidence:** HIGH

## Executive Summary

This research addresses channel governance and command discipline for the Discord AI Keeper system. The project already has foundational channel binding infrastructure (archive, trace, admin channels via `SessionStore`), but lacks enforcement — commands execute regardless of channel type. Users can invoke profile commands in game channels, admin commands in public channels, and diagnostic output leaks into player-facing channels.

The core finding is that **no new external dependencies are required**. The existing discord.py stack already provides all primitives needed: `@commands.check` decorators for channel restrictions, `SessionStore` for channel bindings, and existing redirect patterns in commands like `show_sheet`. The implementation should focus on building a `ChannelEnforcer` middleware layer that intercepts command execution, validates channel context, and provides guided redirection.

The recommended approach uses a command wrapper pattern (Option A) over the Discord.py Cog pattern, preserving existing command structure while adding centralized policy enforcement. Three phases are suggested: Phase 44 (Channel Structure foundation), Phase 45 (Command Routing enforcement), and Phase 46 (Guidance & Polish).

Key risks center on integration with existing command handlers, persistence schema migration for new channel fields, and graceful handling of unbound channels. Most pitfalls stem from adding validation layers that either break existing flows or create confusing user experiences through inconsistent ephemeral message usage.

## Key Findings

### Recommended Stack

The existing stack is fully sufficient. No new external libraries are required.

**Core technologies:**
- **discord.py** (latest stable) — Discord bot framework with built-in `@commands.check` decorator for custom channel restrictions
- **Python 3.12+** — Already in use
- **SessionStore** — Existing guild-level channel bindings (archive, trace, admin)

**What needs to be built (not purchased):**
- **Channel context utility** — New module to detect current channel type from session store
- **Command routing layer** — New decorator/wrapper for channel-aware routing with redirects
- **Channel-aware checks** — Uses `@commands.check` pattern with custom failures

The existing `SessionStore` already provides `archive_channel_for()`, `trace_channel_for()`, `admin_channel_for()` at guild level, and `get_by_channel()` for campaign-bound channels. The new channel context utility should wrap these methods.

### Expected Features

**Must have (table stakes):**
- **Channel type enforcement** — Commands work only in appropriate channels (profile commands in archive, game commands in game hall)
- **Wrong-channel redirect messages** — Clear guidance when users run commands in wrong channel
- **Channel-aware command help** — Slash command suggestions include where to run them
- **Ephemeral administrative responses** — Admin commands don't clutter game channels
- **Campaign-bound channel validation** — Game commands only work in bound campaign channels

**Should have (competitive differentiators):**
- **COC-specific channel roles** — Archive (角色档案), Game Hall (游戏大厅), Trace (KP-trace), Admin (管理)
- **Multi-channel session context** — Session state spans archive, game, and trace channels
- **Builder flow channel gating** — Character builder only works in archive channel during creation
- **Combat initiative channel discipline** — During combat, only active combatant can act

**Defer (v2+):**
- **Channel creation automation** — Bot creates required channels on campaign init
- **Channel permission templates** — Apply standard permission sets to bound channels
- **Activity integration** — Future Discord Activity support

### Architecture Approach

The recommended architecture introduces a **ChannelEnforcer** middleware layer that sits between Discord interaction handlers and command execution. This layer intercepts commands, validates channel context against registered policies, and either passes execution to handlers or returns redirect messages.

**Major components:**
1. **ChannelEnforcer** (`discord_bot/channel_enforcer.py`) — Centralized channel policy enforcement with `ChannelPolicy` dataclass for command-to-channel mapping
2. **Channel context utility** — Determines channel role from SessionStore bindings
3. **Command wrapper** — Wraps existing BotCommands handlers with channel enforcement

**Data flow:**
```
User → Slash Command → ChannelEnforcer.check_command()
                              ↓
              ┌───────────────┴───────────────┐
              ↓                               ↓
      Allowed: Pass to              Blocked: Return redirect
      BotCommands.handler()          message (ephemeral=False)
              ↓
      SessionStore lookup
              ↓
      Execute → Response
```

### Critical Pitfalls

1. **Session lookup returns None but command proceeds** — Commands that check session existence but don't halt execution when None is returned. Prevention: Create a decorator that validates channel context before command execution.

2. **Persistence schema migration missing new channel fields** — Adding new channel binding fields but forgetting to handle them in `dump_sessions()` / `load_sessions()`. Prevention: Use Pydantic models with defaults, add version field to persistence format.

3. **Wrong-channel command silently fails or confuses users** — Redirect messages use `ephemeral=True`, hiding guidance. Prevention: Use `ephemeral=False` for channel redirect messages.

4. **Guild-scoped bindings conflict across multiple campaigns** — SessionStore binds archive/trace/admin at guild level, but campaigns are bound at channel level. Prevention: Document single-campaign-per-guild assumption or upgrade to campaign-scoped bindings.

5. **Command validation logic duplicated across handlers** — Each command manually checks channel type, leading to inconsistent behavior. Prevention: Extract validation to a command wrapper with metadata-driven rules.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 44: Channel Structure
**Rationale:** Foundation must be laid before enforcement can work. Requires adding game channel tracking to SessionStore and creating the ChannelEnforcer class.

**Delivers:**
- `game_channels` binding in SessionStore
- ChannelEnforcer class with basic policy registration
- Channel role detection (ARCHIVE, GAME, ADMIN, TRACE, GENERAL)

**Addresses:** Channel binding enforcement from FEATURES.md (P1)

**Avoids:** Pitfall 2 (persistence schema mismatch) — add defaults and migration path from start

### Phase 45: Command Routing
**Rationale:** With foundation in place, enforcement can be added. Requires registering policies for all existing commands and adding middleware wrapper to command handlers.

**Delivers:**
- Default policies for all existing commands
- Middleware wrapper in BotCommands
- Redirect messages with helpful channel references
- Command validation router with metadata-driven rules

**Addresses:**
- Wrong-channel redirect messages (P1)
- Command help with channel context (P1)
- Campaign-bound validation (P1)

**Avoids:**
- Pitfall 5 (duplicate validation logic) — build router with metadata-driven rules
- Pitfall 1 (session lookup returns None) — consistent validation at entry point
- Pitfall 3 (wrong-channel fails silently) — use ephemeral=False for redirects

### Phase 46: Guidance & Polish
**Rationale:** With enforcement working, user experience can be refined. Requires adding welcome messages, help command enhancement, and diagnostics channel isolation.

**Delivers:**
- Welcome message for new users explaining channel structure
- Help command showing recommended channel per command
- Ephemeral policy: personal errors private, channel redirects public
- Graceful degradation messages when no channel is bound

**Addresses:**
- Channel-aware command help (P1)
- Multi-channel session context (P2)
- Builder flow channel gating (P2)

**Avoids:**
- Pitfall 7 (missing graceful degradation) — friendly messages when not configured
- Pitfall 9 (inconsistent ephemeral usage) — clear policy established

### Phase Ordering Rationale

- **Phase 44 first** — Persistence and core data structures must work before adding enforcement logic. Adding game_channel binding to SessionStore requires careful migration handling.
- **Phase 45 second** — Once foundation exists, command routing and validation can be added. This is where most integration risk lives.
- **Phase 46 last** — UX polish depends on enforcement working. This phase has lower risk and can iterate on feedback.

The grouping follows architecture patterns: foundation (44) → enforcement (45) → polish (46). This avoids Pitfall 2 by handling migration at the foundation phase, and Pitfall 5 by building the router in Phase 45.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 45:** Complex integration with existing command handlers — may need to trace through all 50+ commands to verify policy coverage
- **Phase 46:** Ephemeral message strategy — may need user testing to validate guidance visibility

Phases with standard patterns (skip research-phase):
- **Phase 44:** Well-documented discord.py patterns, existing SessionStore patterns to follow
- **Phase 45:** Standard command wrapper pattern from research, not novel

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | No new dependencies — discord.py provides all needed primitives; existing codebase patterns verified |
| Features | HIGH | Based on existing codebase (SessionStore, show_sheet redirect, admin guidance) and competitor analysis (Avrae) |
| Architecture | HIGH | ChannelEnforcer design derived from existing SessionStore and command patterns; option A (wrapper) recommended |
| Pitfalls | MEDIUM | Integration risks identified from codebase analysis; some persistence risks require validation during implementation |

**Overall confidence:** HIGH

### Gaps to Address

- **Multi-campaign-per-guild decision:** Current SessionStore binds at guild level, but real usage may need campaign-scoped bindings. Need to decide whether to enforce single-campaign-per-guild or upgrade architecture.

- **Message handler channel validation:** Research identified that `handle_channel_message` ignores channel type. Need to decide during Phase 45 planning whether to extend ChannelEnforcer to message flows.

- **Migration path validation:** Persistence schema changes need testing with real `dump_sessions` / `load_sessions` cycles. Recommend smoke-check after Phase 44.

## Sources

### Primary (HIGH confidence)
- **Context7 `/rapptz/discord.py`** — Custom command checks, channel validation patterns
- **Existing codebase** — SessionStore channel binding implementation in `session_store.py`, redirect in `commands.py:538-544`
- **discord.py docs** — @commands.check decorator, slash command permissions

### Secondary (MEDIUM confidence)
- **Avrae bot** — Reference for D&D-specific channel discipline patterns
- **Stack Overflow** — Community-validated channel restriction patterns
- **Discord developer docs** — Slash command permissions per channel

### Tertiary (LOW confidence)
- **DND5E-MCP** — Not recommended as core dependency per STACK.md

---

*Research completed: 2026-03-28*
*Ready for roadmap: yes*
