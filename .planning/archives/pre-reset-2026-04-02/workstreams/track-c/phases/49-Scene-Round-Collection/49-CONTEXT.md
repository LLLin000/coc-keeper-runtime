# Phase 49: Scene Round Collection - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning
**Source:** Discuss phase with user

<domain>
## Phase Boundary

Implement scene round collection where players submit action declarations in natural language, and KP resolves after all players have submitted. Status of who has submitted is visible to all.

**Requirements addressed:** ROUND-01, ROUND-02, ROUND-03

</domain>

<decisions>
## Implementation Decisions

### Action Submission
- **ROUND-01:** Players submit actions via natural language messages in the game channel
- No special command needed - just describe what your character does
- Messages in game channel during `SCENE_ROUND_OPEN` phase are collected as actions
- Duplicate submissions allowed (latest replaces previous)

### Resolution Timing
- **ROUND-03:** KP triggers resolution after all players have submitted
- KP uses `/resolve-round` or similar command to trigger KP response
- Session transitions: `SCENE_ROUND_OPEN` → `SCENE_ROUND_RESOLVING` → (after KP response) → `SCENE_ROUND_OPEN`
- If some players don't submit, KP can choose to proceed with available actions or wait

### Status Visibility
- **ROUND-02:** All players and KP can see who has submitted
- Display a status message showing: "已提交: 玩家A, 玩家B | 待提交: 玩家C"
- Update status after each submission
- Clear visual indicator when all have submitted

### the agent's Discretion
- How to handle players who submit very late (timeout)
- Whether to show what actions others submitted (might influence late submitters)
- Whether to allow action modification after submission

</decisions>

<canonical_refs>
## Canonical References

**From Track C:**
- `.planning/workstreams/track-c/REQUIREMENTS.md` — vC.1.2 ROUND requirements
- `.planning/workstreams/track-c/phases/47-Session-Phases/47-CONTEXT.md` — Session phase model
- `.planning/workstreams/track-c/phases/48-Pre-Play-Onboarding/48-CONTEXT.md` — Phase 48 decisions

**From Project:**
- `src/dm_bot/discord_bot/commands.py` — Existing command implementation
- `src/dm_bot/orchestrator/session_store.py` — Session phase state management

</canonical_refs>

<code_context
## Existing Code Insights

### Reusable Assets
- SessionPhase enum already includes `SCENE_ROUND_OPEN` and `SCENE_ROUND_RESOLVING` phases
- Phase transition methods exist: `transition_to()`, `get_phase_context()`
- Message handling in Discord client can be extended for round collection

### Established Patterns
- Natural message handling already implemented
- Phase transitions logged with timestamps

### Integration Points
- Round collection connects to session_store.py CampaignSession
- Uses existing message handling infrastructure
- Phase transitions trigger AI routing changes

</code_context>

<specifics>
## Specific Ideas

- "自然语言消息" - 玩家直接打字描述行动
- "全部提交后" - KP 等所有人提交后再响应
- "所有人可见" - 透明度高，状态对所有玩家和 KP 可见

</specifics>

<deferred>
## Deferred Ideas

- Message intent routing (INTENT-01, INTENT-02, INTENT-03) — Phase 50
- Campaign/adventure visibility (VIS-01, VIS-02, VIS-03) — Phase 51

</deferred>

---

*Phase: 49-Scene-Round-Collection*
*Context gathered: 2026-03-28*
