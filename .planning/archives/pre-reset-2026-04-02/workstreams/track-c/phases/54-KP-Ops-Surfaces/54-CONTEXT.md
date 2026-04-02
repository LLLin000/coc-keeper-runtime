# Phase 54: KP Ops Surfaces - Context

**Workstream:** Track C - Discord 交互层
**Milestone:** vC.1.3 Campaign Surfaces And Intent Clarity
**Requirements:** OPS-01, OPS-02, OPS-03
**Status:** Ready for planning

---

## Domain

### Phase Boundary

Add a separate KP/operator operational surface showing session ops, runtime state, player participation, and routing diagnostics. This completes the vC.1.3 surface work by providing operator-facing visibility that's distinct from player-facing surfaces.

**Core value:** KP/operators should never need to dig through raw logs or ask players "what phase are we in?" — all operational information should be visible in a dedicated ops surface.

---

## Prior Phase Context

### Phase 51: Visibility Core Contracts (COMPLETE)
- Created `VisibilitySnapshot` model in `src/dm_bot/orchestrator/visibility.py`
- Defined sub-blocks: `campaign`, `adventure`, `session`, `waiting`, `players`, `routing`
- Added `SessionVisibility` with phase, ready_count, total_members, admin_started
- Added `WaitingVisibility` with reason_code, message, and structured metadata
- Added `PlayerSnapshot` with is_ready, has_submitted_action fields
- Added `RoutingVisibility` with outcome + explanation

### Phase 52: Player Status Surfaces (COMPLETE)
- Created `PlayerStatusRenderer` in `src/dm_bot/orchestrator/player_status_renderer.py`
- Three render modes: overview, concise, personal_detail
- Player-facing surfaces use medium information density
- Separate channel for status/info (distinct from game channel)

### Phase 53: Handling Reason Surfaces (COMPLETE)
- Added ephemeral feedback for buffered/ignored/deferred messages
- `IntentHandlingResult.feedback_message` populated and wired
- Player-facing explanations stay concise (≤50 characters)

### What's Already Built But Not Used by KP

The Phase 51 `VisibilitySnapshot` already contains all data needed for Phase 54:

| Sub-block | KP Ops Use |
|-----------|------------|
| `session.phase` | Current session phase |
| `session.ready_count` / `total_members` | Readiness overview |
| `waiting.reason_code` + `message` | What session is waiting on |
| `waiting.metadata` | Pending user IDs, submitted user IDs |
| `players[].is_ready` | Per-player ready state |
| `players[].has_submitted_action` | Per-player action submission |
| `routing.outcome` | Last routing decision |
| `routing.explanation` | Last routing reason |

**Phase 54's job:** Render this same data in an operator-friendly format, plus add routing history that Phase 53 intentionally deferred.

---

## Decisions

### D-01: KP Ops Channel Separation
**Decision:** Phase 54 should establish a dedicated KP/operator ops channel that's formally separate from the player status channel.

**Rationale:**
- Phase 52 explicitly kept player status channel "distinct from the future KP/operator ops surface"
- Operator surfaces need higher information density than player surfaces
- Diagnostics and routing history are not appropriate for player channels

### D-02: Render from Existing VisibilitySnapshot
**Decision:** KP ops surfaces should render from the existing `VisibilitySnapshot` without creating new data structures.

**Rationale:**
- Consistent with vC.1.3 "logic-first" principle (Phase 51 context)
- Avoids duplicating state computation
- Future Activity UI can reuse the same rendering approach

### D-03: Information Density
**Decision:** KP ops surfaces should use higher information density than player surfaces — more detail, less summarization.

**Rationale:**
- OPS-01 requires showing phase, round state, blockers, AND runtime state in one place
- Operators need diagnostic detail that players don't need
- Still should be readable, not a raw debug dump

### D-04: Routing History Scope
**Decision:** KP ops routing history should show the last N routing decisions (configurable, default 10) with outcome + explanation + timestamp + user.

**Rationale:**
- OPS-03 requires inspecting routing outcomes "without digging through raw logs"
- Phase 53 intentionally deferred this to Phase 54
- History should be queryable but not infinite (avoid memory issues)

### D-05: Round State Visibility
**Decision:** KP ops surfaces should explicitly show round number when in SCENE_ROUND_OPEN or SCENE_ROUND_RESOLVING phases.

**Rationale:**
- OPS-01 mentions "round state" specifically
- Round tracking exists in session_store but may need exposure
- Operators need to know which round players are acting in

---

## Code Context

### Key Files to Modify or Create

1. **`src/dm_bot/orchestrator/visibility.py`**
   - May need to add round_number field to SessionVisibility if not already tracked
   - May need to extend routing history tracking

2. **`src/dm_bot/orchestrator/kp_ops_renderer.py`** (NEW)
   - New renderer for KP/operator surfaces
   - Render modes: overview, detailed, routing_history
   - Higher information density than PlayerStatusRenderer

3. **Message processing pipeline**
   - Where to store routing history for KP inspection
   - Need to append to a routing history list (not replace)

4. **`src/dm_bot/discord_bot/commands.py`**
   - Add ops surface update triggers
   - Add `/ops_status` command for manual refresh

### Existing Components to Reuse

| Component | Location | Reuse For |
|-----------|----------|-----------|
| `VisibilitySnapshot` | `orchestrator/visibility.py` | Primary data source |
| `SessionVisibility` | `orchestrator/visibility.py` | Phase, readiness, admin_started |
| `WaitingVisibility` | `orchestrator/visibility.py` | Blocker info with metadata |
| `PlayerSnapshot` | `orchestrator/visibility.py` | Per-player detail |
| `RoutingVisibility` | `orchestrator/visibility.py` | Last routing outcome |
| `PlayerStatusRenderer` | `orchestrator/player_status_renderer.py` | Reference for renderer patterns |
| `IntentHandlingResult` | `router/intent_handler.py` | Feedback message source |
| `CampaignSession` | `orchestrator/session_store.py` | Session state underlying snapshot |

### Session Phases for Ops Context

- `ONBOARDING` — Who's incomplete, who's done
- `AWAITING_READY` — Who ready, who not
- `AWAITING_ADMIN_START` — Waiting on owner
- `SCENE_ROUND_OPEN` — Pending actions, round number
- `SCENE_ROUND_RESOLVING` — Submitted actions, who's done
- `COMBAT` — Combat state, initiative order
- `PAUSED` — Pause reason

---

## Specifics

### OPS-01: Session Phase, Round State, Blockers, Runtime State

**KP ops surface should show:**
1. **Session Phase** — Current phase with clear label (not enum value)
2. **Round State** — Round number (if applicable), scene round open/resolving status
3. **Blockers** — What's holding up progress (from waiting metadata)
4. **Runtime State** — Adventure ID, scene ID, admin started flag

**Example display:**
```
🎭 Session: SCENE_ROUND_OPEN (Round 3)
⏳ Waiting: 2 players to submit actions
📋 Pending: user_123, user_456
📦 Adventure: mad_mansion | Scene: Entrance Hall
👤 Ready: 3/5 | Admin Started: Yes
```

### OPS-02: Per-Player Participation State

**KP ops surface should show per player:**
- Ready status (yes/no)
- Action submitted status (yes/no/pending)
- Onboarding complete (yes/no)
- Basic character info (name, occupation)

**Example per-player block:**
```
👤 Player1 (Dr. Jones - Doctor)
  ✓ Ready | ✓ Action Submitted | ✓ Onboarded

👤 Player2 (Sarah - Journalist)  
  ✓ Ready | ⏳ Pending Action | ✓ Onboarded

👤 Player3 (Mike - Private Eye)
  ✗ Not Ready | - No Action | ✓ Onboarded
```

### OPS-03: Routing Outcomes and Diagnostics

**KP routing history should show:**
- Timestamp
- User who sent message
- Intent type (OOC, ACTION, RULES_QUERY, etc.)
- Outcome (PROCESSED, BUFFERED, IGNORED, DEFERRED)
- Short explanation

**Example routing history:**
```
🕐 14:32 | @player1 | OOC | BUFFERED | "OOC在行动收集阶段被缓存"
🕐 14:31 | @player2 | ACTION | PROCESSED | Keeper narration triggered
🕐 14:30 | @player3 | RULES_QUERY | DEFERRED | "将在结算后回答"
🕐 14:28 | @player1 | UNKNOWN | IGNORED | "无法识别意图"
```

---

## Deferred Ideas

| Idea | Reason for Deferral |
|------|---------------------|
| Real-time push updates to KP ops channel | Requires WebSocket or Discord activity subscription — beyond vC.1.3 |
| Configurable routing history length | After baseline works, add config |
| Routing statistics (aggregated counts) | Phase 55 or later |
| Cross-campaign KP ops view | Beyond current-only visibility scope |
| Interactive buttons in KP ops (pause, advance phase) | Requires admin action surface — future milestone |
| Export routing history to file | Debug feature for later |

---

## Test Scenarios

The TDD plan should verify:

1. **OPS-01 Verification:**
   - Session in SCENE_ROUND_OPEN shows round number and pending members
   - Session in COMBAT shows combat state indicator
   - Session PAUSED shows pause reason

2. **OPS-02 Verification:**
   - All players in session appear with correct ready/submitted status
   - Status updates when player readsies up
   - Status updates when player submits action

3. **OPS-03 Verification:**
   - Routing history shows last 10 decisions
   - Each entry has timestamp, user, intent, outcome, explanation
   - New routing decisions append to history

4. **Integration:**
   - KP ops surface updates when visibility snapshot updates
   - KP ops surface is in a dedicated channel (not player channel)
   - `/ops_status` command refreshes the surface

---

## Next Step

After this context is approved, proceed to create the implementation plan with:

1. Whether to extend SessionVisibility with round_number or derive from session_store
2. Where to store routing history (in-memory list vs persisted)
3. New KP ops renderer design
4. Discord channel setup for KP ops surface
5. Testing strategy

---

*Phase: 54-KP-Ops-Surfaces*
*Context gathered: 2026-03-29*
