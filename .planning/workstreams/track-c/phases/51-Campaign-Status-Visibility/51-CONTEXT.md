# Phase 51: Campaign Status Visibility - Context

**Gathered:** 2026-03-28
**Status:** Deferred to vC.1.3 pending future planning
**Source:** Discuss phase with user; overall research boundary review

<domain>
## Phase Boundary

Implement campaign and adventure status visibility surfaces that show players what's loaded, who's participating, and where they are in the story. Information is rich, real-time, and contextual to the current scene.

**Requirements addressed:** VIS-01, VIS-02, VIS-03
**Milestone note:** Overall research concluded this phase belongs with vC.1.3 visibility/intake clarity work rather than vC.1.2 governance/control-flow work.

</domain>

<decisions>
## Implementation Decisions

### Adventure Information Display
- **VIS-01:** Rich adventure information:
  - Adventure name, synopsis, current chapter/progress
  - Discovered clues (hidden vs revealed)
  - Visited locations
  - Key NPCs encountered
- Use Discord embed with collapsible sections for detail

### Member Status Display
- **VIS-02:** Real-time member status updates:
  - Campaign members with ready/not ready status
  - HP and SAN values (player can see their own, KP sees all)
  - Real-time notifications in channel when anyone ready/unready
  - Status updates posted as the bot

### Scene/Location Display
- **VIS-03:** Complete scene state displayed:
  - Current scene type: combat / exploration / roleplay / none
  - Participating players
  - Round status (if applicable)
  - Current location name + description
  - Available actions / exploration options
- Updates automatically when scene changes

### the agent's Discretion
- How often to auto-post status (on phase change only, or periodic)
- Whether to show "none active" state and what that means
- How to handle very long adventure summaries (truncation vs detailed view command)

</decisions>

<canonical_refs>
## Canonical References

**From Track C:**
- `.planning/workstreams/track-c/REQUIREMENTS.md` — vC.1.2 VIS requirements that now inform future vC.1.3 visibility work
- `.planning/workstreams/track-c/ROADMAP.md` — milestone boundary showing Phase 51 deferred to vC.1.3
- `.planning/workstreams/track-c/research/vC.1.2-OVERALL-RESEARCH.md` — boundary review recommending defer to vC.1.3
- `.planning/workstreams/track-c/phases/47-Session-Phases/47-CONTEXT.md` — Session phase model
- `.planning/workstreams/track-c/phases/48-Pre-Play-Onboarding/48-CONTEXT.md` — Phase 48 decisions
- `.planning/workstreams/track-c/phases/49-Scene-Round-Collection/49-CONTEXT.md` — Phase 49 decisions
- `.planning/workstreams/track-c/phases/50-Message-Intent-Routing/50-CONTEXT.md` — Phase 50 decisions

**From Project:**
- `src/dm_bot/discord_bot/commands.py` — Existing command implementation
- `src/dm_bot/orchestrator/session_store.py` — Session state management

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Session phase model provides phase context
- Campaign/adventure state already persisted
- Ready status tracking from Phase 47/48

### Established Patterns
- Rich embeds used in existing commands
- Real-time updates via bot messages

### Integration Points
- Status surfaces connect to session_store
- Adventure data from module runtime
- Uses existing Discord message delivery

</code_context>

<specifics>
## Specific Ideas

- "丰富信息" - 冒险名称 + 线索 + 地点 + NPC
- "实时更新通知" - 成员状态变化实时通知
- "完整场景状态" - 场景类型 + 参与者 + 回合状态 + 位置
- Keep this phase planning-ready, but treat it as queued behind vC.1.2 governance work

</specifics>

<deferred>
## Deferred Ideas

- Deferred from vC.1.2 to vC.1.3 after overall research boundary review

</deferred>

---

*Phase: 51-Campaign-Status-Visibility*
*Context gathered: 2026-03-28; boundary updated after overall research review*
