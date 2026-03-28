# Phase 50: Message Intent Routing - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning
**Source:** Discuss phase with user

<domain>
## Phase Boundary

Implement intelligent message intent routing where AI classifies messages into intents (OOC, IC action, rules query, admin) and handles them differently based on session phase. Priority of handling varies by phase.

**Requirements addressed:** INTENT-01, INTENT-02, INTENT-03

</domain>

<decisions>
## Implementation Decisions

### Intent Classification
- **INTENT-01:** AI real-time classification
- Each message is classified into: OOC, social IC, player action, rules query, admin action
- Classification happens before processing, as part of the router model
- Intent stored with message for debugging/logging

### Intent Handling (Phase-Dependent)
- **INTENT-02, INTENT-03:** Different handling per intent:
  - **OOC:** Always responded, but may be buffered in high-intensity phases
  - **Social IC:** Responded normally in exploration phases, may be brief in combat
  - **Player action:** Primary focus during SCENE_ROUND_OPEN and COMBAT phases
  - **Rules query:** Responded when explicitly asked, may be deferred in combat
  - **Admin action:** Always processed, separate from player flows

### Phase-Affecting Priority
- **INTENT-03:** Session phase affects intent priority:
  - **SCENE_ROUND_OPEN:** Player actions prioritized, OOC deferred
  - **SCENE_ROUND_RESOLVING:** All inputs buffered until resolution complete
  - **COMBAT:** Player actions only, everything else deferred/ignored
  - **ONBOARDING:** Rules queries welcomed, actions deferred
- Users see feedback explaining why their message was handled differently

### the agent's Discretion
- Exact intent categories (can be extended)
- Whether to show "buffered" messages after phase ends
- How to handle ambiguous intent classification

</decisions>

<canonical_refs>
## Canonical References

**From Track C:**
- `.planning/workstreams/track-c/REQUIREMENTS.md` — vC.1.2 INTENT requirements
- `.planning/workstreams/track-c/phases/47-Session-Phases/47-CONTEXT.md` — Session phase model
- `.planning/workstreams/track-c/phases/48-Pre-Play-Onboarding/48-CONTEXT.md` — Phase 48 decisions
- `.planning/workstreams/track-c/phases/49-Scene-Round-Collection/49-CONTEXT.md` — Phase 49 decisions

**From Project:**
- `src/dm_bot/router/` — Existing routing implementation
- `src/dm_bot/discord_bot/client.py` — Message handling

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Router model already exists for message classification
- Session phase model provides phase context
- Message handling infrastructure in Discord client

### Established Patterns
- Dual-model architecture: router (classification) + narrator (response)
- Phase-dependent behavior already in place

### Integration Points
- Intent classification extends router model
- Phase context available from session_store
- Message handling in Discord client integrates with router

</code_context>

<specifics>
## Specific Ideas

- "AI 实时判断" - 每次消息都用 AI 分类
- "阶段相关" - 不同阶段不同处理方式
- "阶段影响优先级" - 会话阶段影响意图优先级

</specifics>

<deferred>
## Deferred Ideas

- Campaign/adventure visibility (VIS-01, VIS-02, VIS-03) — Phase 51

</deferred>

---

*Phase: 50-Message-Intent-Routing*
*Context gathered: 2026-03-28*
