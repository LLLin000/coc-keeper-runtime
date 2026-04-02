# Phase 52: Player Status Surfaces - Context

**Gathered:** 2026-03-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Add player-facing shared status surfaces for current campaign/adventure/session identity and waiting state, using the canonical visibility contracts from Phase 51. This phase covers the player-facing rendering path: a persistent shared status surface plus a dedicated player-visible status/info channel for overview panels and queries.

This phase is about player-visible status clarity, not KP/operator diagnostics and not Activity UI implementation.

</domain>

<decisions>
## Implementation Decisions

### Primary player entrypoint
- **D-01:** Phase 52 should use a persistent shared status message as the main player-facing status entrypoint.
- **D-02:** Phase 52 should also provide an on-demand detail path instead of forcing all detail into the shared status message.
- **D-03:** The player-facing surface should read from the Phase 51 `VisibilitySnapshot` rather than rebuilding status text ad hoc.

### Status channel model
- **D-04:** Phase 52 should formally include a player-visible status/info channel for summary panels and query results.
- **D-05:** The player status channel is distinct from the future KP/operator ops surface and must not become a diagnostics-heavy admin channel.
- **D-06:** The main game/play channel should keep a concise shared status presence, while the status/info channel can hold the more complete player-facing overview panel.

### Information density
- **D-07:** The default shared player-facing status surface should use medium information density.
- **D-08:** Default content should include current campaign/adventure identity, current session/scene status, current waiting reason, and player participation summary.
- **D-09:** Detailed personal state should not be stuffed into the default shared panel.

### Visibility scope between players
- **D-10:** Shared player-facing surfaces should show public summary information for everyone, not per-user hidden detail inside the same public message.
- **D-11:** Personal detailed state should be delivered through ephemeral/private query paths rather than exposed in the shared status channel.
- **D-12:** Other players should appear as summarized participation state (for example ready/submitted/pending) rather than full private character detail.

### Identity presentation
- **D-13:** Campaign/adventure/session identity should use a mixed presentation: a structured title/header at the top plus one short narrative/status line below it.
- **D-14:** The identity/header should be optimized for quick scanning in Discord rather than long prose.

### the agent's Discretion
- Exact command names, button labels, or panel trigger mechanics for the on-demand detail path
- Whether the player-visible status/info channel is mandatory or optional/configurable per guild, so long as Phase 52 still supports the dedicated channel pattern
- Exact wording and formatting of the short narrative/status line
- Exact breakdown of which personal fields appear in private detail views, so long as they stay inside existing canonical state and do not expand semantics

</decisions>

<specifics>
## Specific Ideas

- 主游戏频道保留共享持久状态消息
- 另建一个玩家可见的状态/信息频道，用来放总 panel 和查询结果
- 公共状态只展示公共摘要
- 个人详细状态通过 ephemeral / 私人查询获取
- 顶部结构化标题 + 一句短叙事说明
- 默认信息密度保持中等，不做又长又杂的全量面板

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone and phase definition
- `.planning/workstreams/track-c/PROJECT.md` — vC.1.3 goal, migration notes, and player-facing visibility direction
- `.planning/workstreams/track-c/REQUIREMENTS.md` — PLAY-01, PLAY-02, CURR-01, CURR-02 and surrounding scope boundaries
- `.planning/workstreams/track-c/ROADMAP.md` — Phase 52 goal and success criteria

### Upstream Track C decisions
- `.planning/workstreams/track-c/phases/51-Campaign-Status-Visibility/51-CONTEXT.md` — canonical visibility contract structure that Phase 52 must render from
- `.planning/workstreams/track-c/phases/51-Campaign-Status-Visibility/51-SUMMARY.md` — summary of the implemented visibility core if present and accurate
- `.planning/workstreams/track-c/phases/47-Session-Phases/47-CONTEXT.md` — established session phase semantics
- `.planning/workstreams/track-c/phases/49-Scene-Round-Collection/49-CONTEXT.md` — waiting/pending visibility expectations for player participation
- `.planning/workstreams/track-c/phases/50-Message-Intent-Routing/50-CONTEXT.md` — player-facing explanation brevity and phase-aware routing behavior

### Existing code and rendering patterns
- `src/dm_bot/orchestrator/visibility.py` — Phase 51 shared visibility snapshot model to render from
- `src/dm_bot/discord_bot/commands.py` — existing command and embed/status delivery patterns
- `src/dm_bot/orchestrator/session_store.py` — underlying session/member state feeding the visibility model
- `src/dm_bot/coc/panels.py` — existing player panel field conventions that may inform private detail presentation

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `VisibilitySnapshot` and related sub-blocks in `src/dm_bot/orchestrator/visibility.py` provide the canonical source of truth for this phase.
- Existing Discord command and status/embed patterns in `src/dm_bot/discord_bot/commands.py` can be reused for player-facing surfaces.
- Existing player panel field conventions in `src/dm_bot/coc/panels.py` can inform private detail views without expanding semantics.

### Established Patterns
- vC.1.3 is explicitly logic-first: renderers should consume canonical visibility state rather than recomputing their own truth.
- Player-facing explanations and surfaces should stay concise in normal Discord play contexts.
- Phase-aware and waiting-aware status is already part of the runtime model and should stay structured before rendering.

### Integration Points
- Phase 52 should render from the Phase 51 visibility builder/model.
- The shared play-channel status message and the new player-visible status channel should both derive from the same visibility source.
- Personal detail queries should be fed by the same canonical snapshot but delivered through private/ephemeral response paths.

</code_context>

<deferred>
## Deferred Ideas

- KP/operator diagnostics and ops-specific surfaces belong to Phase 54
- Player-facing handling reason surfaces in depth belong to Phase 53
- Discord Activity UI implementation remains deferred beyond vC.1.3 core surface work
- Broad multi-campaign browsing remains out of scope for this phase

</deferred>

---

*Phase: 52-Player-Status-Surfaces*
*Context gathered: 2026-03-29*
