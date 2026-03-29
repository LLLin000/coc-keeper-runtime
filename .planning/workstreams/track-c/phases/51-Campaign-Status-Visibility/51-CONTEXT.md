# Phase 51: Campaign Status Visibility - Context

**Gathered:** 2026-03-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Define the canonical visibility state for campaign, adventure, session, waiting reasons, routing outcomes, and existing player snapshot state so later Discord surfaces can render from one shared logic-first model instead of assembling ad hoc strings.

This phase delivers the shared visibility contract layer, not the full player-facing or KP-facing surface rollout. It should make later chat surfaces and future Discord Activity rendering reuse the same business logic.

</domain>

<decisions>
## Implementation Decisions

### Visibility contract shape
- **D-01:** Phase 51 should define a top-level `VisibilitySnapshot` rather than separate unrelated contracts or one flat blob.
- **D-02:** `VisibilitySnapshot` should be explicitly partitioned into these sub-blocks: `campaign`, `adventure`, `session`, `waiting`, `players`, and `routing`.
- **D-03:** Later phases should consume these sub-blocks selectively instead of inventing separate visibility sources per surface.

### Waiting / blocker reasons
- **D-04:** Waiting state should use a stable reason code plus a short display message.
- **D-05:** Waiting state should also carry a small amount of structured metadata, such as pending user ids, related phase, or round linkage when relevant.
- **D-06:** The canonical layer should own the reason code and metadata; renderers may vary wording later without changing the logic contract.

### Player snapshot boundary
- **D-07:** Player visibility in Phase 51 should surface existing canonical player snapshot state only; this phase must not redesign character semantics.
- **D-08:** The player snapshot should include participation state, bound character identity, and existing canonical HP / SAN / a small set of key attributes that are already stable in the runtime.
- **D-09:** Full sheet detail, skill dumps, journal/history, and richer role/character redesign are out of scope for this phase.

### Routing visibility scope
- **D-10:** Routing visibility in the Phase 51 contract should expose routing outcome plus a short explanation contract so later player and operator surfaces can render different views from the same source.
- **D-11:** Phase 51 should support richer downstream rendering later, but the core contract should stay concise and not become a raw debug dump.

### the agent's Discretion
- Exact field names and nesting depth inside each visibility sub-block
- Whether campaign and adventure are nested or sibling sub-blocks if both preserve the six-block contract cleanly
- Which existing player attributes qualify as the minimal “small set of key attributes” beyond HP and SAN
- Whether routing metadata stores both canonical reason code and already-rendered short text, or computes the short text from the code at snapshot-build time

</decisions>

<specifics>
## Specific Ideas

- Logic first, renderer second
- One canonical visibility model reused by player chat surfaces, KP ops surfaces, and future Discord Activity UI
- Future Activity support should come from reusing the same visibility contract, not by rebuilding the state model later
- 玩家状态里需要包含现有 canonical 的 HP / SAN / 少量关键属性，但只做展示，不做角色系统重构

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone and phase definition
- `.planning/workstreams/track-c/PROJECT.md` — vC.1.3 milestone goal, track boundary, secondary impact, and migration notes
- `.planning/workstreams/track-c/REQUIREMENTS.md` — vC.1.3 requirements for SURF-01/02/03/04 and related downstream surface requirements
- `.planning/workstreams/track-c/ROADMAP.md` — Phase 51 goal, mapped requirements, and success criteria

### Prior Track C decisions that constrain Phase 51
- `.planning/workstreams/track-c/phases/47-Session-Phases/47-CONTEXT.md` — established explicit session phases and phase visibility expectations
- `.planning/workstreams/track-c/phases/48-Pre-Play-Onboarding/48-CONTEXT.md` — onboarding completion and phase-transition state already belong to canonical session visibility
- `.planning/workstreams/track-c/phases/49-Scene-Round-Collection/49-CONTEXT.md` — round submission state and pending-player visibility already exist and should feed the new visibility model
- `.planning/workstreams/track-c/phases/50-Message-Intent-Routing/50-CONTEXT.md` — routing outcomes are phase-aware and explanations should remain short

### Existing code contracts and reusable state
- `src/dm_bot/orchestrator/session_store.py` — canonical session state already includes phase, ready state, onboarding completion, pending actions, and submitter tracking
- `src/dm_bot/router/intent_handler.py` — routing decisions and short feedback behavior already exist conceptually and should inform routing visibility contracts
- `src/dm_bot/router/message_buffer.py` — buffered message state and summary behavior inform waiting/routing visibility
- `src/dm_bot/coc/panels.py` — existing investigator panel exposes current HP, SAN, and related player state that may be surfaced read-only
- `src/dm_bot/discord_bot/commands.py` — current Discord command/message layer and existing status/guidance patterns that later phases will render through

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `CampaignSession` in `src/dm_bot/orchestrator/session_store.py` already stores session phase, ready state, onboarding completion, pending round actions, and action submitters.
- `InvestigatorPanel` in `src/dm_bot/coc/panels.py` already exposes HP, SAN, MP, luck, and related player state that can inform a read-only snapshot.
- `IntentHandlingResult` and feedback generation in `src/dm_bot/router/intent_handler.py` already model routing outcomes and short explanations.
- `MessageBuffer` in `src/dm_bot/router/message_buffer.py` already models buffered messages and buffer summaries.

### Established Patterns
- Session and routing behavior already use structured runtime models before rendering user-facing text.
- Phase-aware behavior is already a core pattern across vC.1.2 features.
- Existing Discord UX tends to use concise status/guidance text plus structured backend state.

### Integration Points
- The new visibility contract should aggregate existing data from `session_store`, routing/buffer modules, and existing player panel state.
- Later phases will render this contract through player-facing shared surfaces, KP/operator surfaces, and eventually Activity-ready renderers.
- This phase should sit between canonical runtime state and Discord renderers, not inside any one renderer.

</code_context>

<deferred>
## Deferred Ideas

- Rich player-facing status surfaces belong primarily to Phase 52, not Phase 51
- Short player-facing handling explanation surfaces belong primarily to Phase 53, not Phase 51
- Separate KP/operator operational surfaces belong primarily to Phase 54, not Phase 51
- Future Discord Activity UI implementation belongs after the activity-ready core is complete
- Character-system redesign, full sheet expansion, and broader character semantics normalization remain outside this phase and outside Track C’s primary scope

</deferred>

---

*Phase: 51-Campaign-Status-Visibility*
*Context gathered: 2026-03-29*
