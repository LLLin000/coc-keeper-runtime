# Feature Research: Channel Governance and Command Discipline

**Domain:** Discord bot channel discipline and command routing
**Researched:** 2026-03-28
**Confidence:** HIGH

## Executive Summary

This research covers standard patterns for Discord channel discipline and command routing in bot applications. The project already has foundational channel binding infrastructure (archive, trace, admin channels). This research identifies patterns to harden command routing, enforce channel-specific usage, and reduce command clutter.

Key findings:
- **discord.py provides channel context checks** via `ctx.channel`, channel ID comparisons, and custom command checks
- **Existing codebase already has channel bindings** - archive, trace, admin channels can be bound via slash commands
- **Standard patterns include** redirect messages, command visibility by channel, ephemeral guidance, and slash command permissions
- **Avrae (D&D bot)** uses channel role patterns - game commands only work in game channels, character commands in dedicated channels

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels broken for a governance-focused bot.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Channel type enforcement** | Users expect commands to work only in appropriate channels - profile commands in archive channel, game commands in game hall | MEDIUM | Requires channel binding checks at command entry point |
| **Wrong-channel redirect messages** | When users run commands in wrong channel, they need clear guidance on where to go | LOW | Existing pattern in `show_sheet` - expand to other commands |
| **Channel-aware command help** | Slash command suggestions should include where to run them | LOW | Can use command descriptions and ephemeral help |
| **Ephemeral administrative responses** | Admin commands should not clutter game channels | LOW | Already using `ephemeral=True` in many commands |
| **Campaign-bound channel validation** | Game commands should only work in bound campaign channels | LOW | Already implemented in `take_turn`, `join_campaign` |

### Differentiators (Competitive Advantage)

Features that set this bot apart from generic Discord bots.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **COC-specific channel roles** | Archive (角色档案), Game Hall (游戏大厅), Trace (KP-trace), Admin (管理) - each with semantic meaning for COC sessions | LOW | Built on existing channel binding system |
| **Multi-channel session context** | Session state spans multiple channels - game in hall, trace for KP, archive for profiles | MEDIUM | Requires cross-channel session awareness |
| **Builder flow channel gating** | Character builder should only work in archive channel during creation | LOW | Already partially implemented in `_consume_archive_builder_message` |
| **Scene-mode channel isolation** | When in scene mode (multi-NPC), commands are contextually different | MEDIUM | Depends on existing `enter_scene`/`end_scene` |
| **Combat initiative channel discipline** | During combat, only active combatant can act; others get redirect | LOW | Partially implemented in `_combat_gate_message` |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Global command availability** | "Make all commands work everywhere for flexibility" | Creates confusion about where to do what; clutters help | Channel-specific commands with clear redirects |
| **Per-user channel preferences** | "Let users choose their preferred channels" | Breaks session coherence; KP can't track what's happening | Server-defined channel roles enforced by bot |
| **Auto-create channels on demand** | "Magic channel creation" | Adds complexity; Discord permissions are server-specific | Document required channel structure |
| **Cross-guild command routing** | "Let one campaign span multiple Discord servers" | Security nightmare; breaks Discord permission model | Keep campaigns within single guild |

## Feature Dependencies

```
[Channel Binding System (EXISTING)]
    └──requires──> [Channel Type Validation]

[Channel Type Validation]
    └──requires──> [Wrong-Channel Redirect Messages]

[Wrong-Channel Redirect]
    └──requires──> [Channel-Aware Command Help]

[Session Store Channel Tracking (EXISTING)]
    └──enhances──> [Multi-Channel Session Context]

[Profile Commands]
    └──requires──> [Archive Channel Binding]
        └──before──> [Builder Flow Channel Gating]

[Game Commands]
    └──requires──> [Campaign Bound Channel Validation]
        └──before──> [Combat Initiative Channel Discipline]
```

### Dependency Notes

- **Channel Type Validation requires Channel Binding System:** The existing binding infrastructure must be in place first
- **Wrong-Channel Redirect requires Channel Type Validation:** Can't redirect without knowing what's "wrong"
- **Channel-Aware Help requires Channel Type Validation:** Help text needs to know correct channels
- **Multi-Channel Session enhances existing Session Store:** Current session store tracks campaign-channel, extend to multi-channel awareness
- **Builder Flow Channel Gating requires Archive Channel Binding:** Builder should only work in archive channel

## MVP Definition

### Launch With (vC.1.1)

Minimum viable channel governance - what's needed to validate command discipline works.

- [x] **Channel binding commands** — Already implemented: `/bind_archive_channel`, `/bind_trace_channel`, `/bind_admin_channel`
- [ ] **Phase 44: Channel Structure** — Define and implement channel role enforcement
- [ ] **Phase 45: Command Routing** — Implement channel-aware routing with redirects
- [ ] **Phase 46: Guidance & Polish** — Add user guidance, reduce clutter

### Add After Validation (vC.1.x)

Features to add once core channel discipline is working.

- [ ] **Command-specific channel requirements** — Each command declares which channel type it requires
- [ ] **Dynamic command visibility** — Hide commands not applicable to current channel in slash menu
- [ ] **Cross-channel session awareness** — KP sees trace in trace channel, players in game hall

### Future Consideration (vC.2+)

Features to defer until governance patterns are proven.

- [ ] **Channel creation automation** — Bot creates required channels on campaign init
- [ ] **Channel permission templates** — Apply standard permission sets to bound channels
- [ ] **Activity integration** — Future Discord Activity support with embedded experience

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Channel binding enforcement | HIGH | MEDIUM | P1 |
| Wrong-channel redirect messages | HIGH | LOW | P1 |
| Command help with channel context | HIGH | LOW | P1 |
| Ephemeral admin responses | MEDIUM | LOW | P1 |
| Campaign-bound validation | HIGH | LOW | P1 |
| Multi-channel session context | MEDIUM | MEDIUM | P2 |
| Builder flow channel gating | MEDIUM | LOW | P2 |
| Combat initiative discipline | MEDIUM | LOW | P2 |
| Dynamic command visibility | LOW | HIGH | P3 |
| Channel creation automation | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Avrae (D&D Bot) | Mee6 | Our Approach |
|---------|-----------------|------|--------------|
| Channel-specific commands | Yes - game commands in game channels only | Partial - moderation in mod channels | Enforce archive/game/trace channel roles |
| Wrong-channel redirects | Yes - clear error messages | Limited | Expand existing redirect pattern |
| Command visibility by channel | Partial - help shows context | No | Slash command permissions per channel |
| Multi-channel session | No - single channel focus | No | Track session across archive/game/trace |
| Character builder gating | Yes - character commands in character channels | No | Builder flow in archive channel only |

## Sources

- **discord.py docs:** Channel type checking with `isinstance()`, custom command checks via `@commands.check()` decorator
- **Stack Overflow patterns:** Channel ID comparisons, redirect message patterns
- **Avrae bot:** Reference for D&D-specific channel discipline patterns
- **Existing codebase:** Channel binding system in `session_store.py`, redirect in `show_sheet`, admin guidance in `_admin_channel_guidance`
- **Discord developer docs:** Slash command permissions per channel

---

*Feature research for: Discord AI Keeper Channel Governance*
*Researched: 2026-03-28*
