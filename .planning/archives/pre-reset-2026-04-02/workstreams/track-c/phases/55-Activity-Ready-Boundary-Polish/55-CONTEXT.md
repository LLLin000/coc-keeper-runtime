# Phase 55: Activity-Ready Boundary Polish

**Workstream:** Track C - Discord 交互层  
**Milestone:** vC.1.3 Campaign Surfaces And Intent Clarity  
**Requirements:** ACT-01, ACT-02  
**Status:** Ready for planning

---

## Domain

### Phase Boundary

Consolidate the visibility contracts and surfaces from Phases 51-54 so future Discord Activity UI can reuse the same business logic without rewriting the model. This is a **boundary polish phase** — it does not add new surface implementations but ensures existing ones are properly separated from canonical state.

**Core value:** The visibility model should be reusable across rendering contexts (Discord chat, Discord Activity, future web panels) without requiring business logic changes when the rendering layer changes.

---

## Prior Phase Context

### Phase 51: Visibility Core Contracts (COMPLETE)
- Created `VisibilitySnapshot` model in `src/dm_bot/orchestrator/visibility.py`
- Six sub-blocks: `campaign`, `adventure`, `session`, `waiting`, `players`, `routing`
- Pure functional builder `build_visibility_snapshot()`
- Requirements satisfied: SURF-01, SURF-02, SURF-03, SURF-04

### Phase 52: Player Status Surfaces (COMPLETE)
- Created `PlayerStatusRenderer` in `src/dm_bot/orchestrator/player_status_renderer.py`
- Three render modes: overview, concise, personal_detail
- Medium information density for player-facing surfaces

### Phase 53: Handling Reason Surfaces (COMPLETE)
- Added ephemeral feedback for buffered/ignored/deferred messages
- `IntentHandlingResult.feedback_message` populated and wired to Discord
- Concise feedback (≤50 characters) for ordinary routing

### Phase 54: KP Ops Surfaces (IN PROGRESS)
- Dedicated KP/operator operational surface
- Higher information density than player surfaces
- Routing history tracking

### What's Been Built

| Component | Location | Status |
|-----------|----------|--------|
| `VisibilitySnapshot` | `orchestrator/visibility.py` | ✅ Core contract |
| `build_visibility_snapshot()` | `orchestrator/visibility.py` | ✅ Builder function |
| `PlayerStatusRenderer` | `orchestrator/player_status_renderer.py` | ✅ Discord renderer |
| `KPStatusRenderer` | `orchestrator/kp_ops_renderer.py` | ✅ Discord renderer (Phase 54) |
| Feedback delivery | Router → Discord pipeline | ✅ Wired (Phase 53) |

---

## Decisions

### D-01: Canonical State Isolation
**Decision:** The `VisibilitySnapshot` and its sub-models must remain purely data classes with no rendering-specific logic, imports, or dependencies.

**Rationale:**
- ACT-01 requires the visibility model to be reusable beyond Discord chat
- Embed-specific formatting (colors, components, Discord UI) should live only in renderers
- If the visibility model imports or depends on Discord types, it cannot be reused by Activity UI

### D-02: Renderer Separation Pattern
**Decision:** Each renderer (player, KP, future Activity) must implement a common interface pattern: receive a `VisibilitySnapshot` → return renderer-specific output.

**Rationale:**
- Ensures surface implementations clearly separate canonical state from renderer logic
- New renderers can be added without modifying the visibility model
- Follows the "logic-first, renderer-second" principle from Phase 51

### D-03: Type Export Strategy
**Decision:** Visibility types must be exported from a dedicated module that has zero Discord-specific imports.

**Rationale:**
- Future Activity UI (likely a separate process/service) can import visibility types without pulling in Discord dependencies
- Clean dependency graph: visibility types → business logic → renderers → Discord/Activity
- Enables testing visibility logic without Discord infrastructure

### D-04: No New Surface Features in Phase 55
**Decision:** Phase 55 does not implement new surface features (no new channels, no new commands, no new feedback types).

**Rationale:**
- Phase 55 is explicitly a "boundary polish" phase (per ROADMAP.md)
- ACT-02: This milestone remains Activity-ready without implementing Activity UI itself
- Focus is on consolidation and separation, not feature expansion

---

## Code Context

### Key Files to Audit/Refactor

1. **`src/dm_bot/orchestrator/visibility.py`**
   - Must verify: No Discord imports (discord.py, interactions, etc.)
   - Must verify: No embed-specific formatting in snapshot building
   - Must verify: Pure Pydantic data classes

2. **`src/dm_bot/orchestrator/player_status_renderer.py`**
   - Must verify: Receives `VisibilitySnapshot`, returns Discord-specific output
   - Must verify: No business logic mutations, only presentation logic

3. **`src/dm_bot/orchestrator/kp_ops_renderer.py`** (if exists)
   - Must verify: Same separation pattern as PlayerStatusRenderer

4. **Message processing pipeline**
   - Must verify: `IntentHandlingResult.feedback_message` generation stays in router/business logic
   - Must verify: Discord-specific delivery (ephemeral, embed) stays in Discord layer

### Existing Separation (Should Verify is Maintained)

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Canonical state | `visibility.py` | Pure data, no rendering |
| Business logic | `router/intent_handler.py` | Routing decisions, feedback messages |
| Discord rendering | `discord_bot/commands.py` | Embeds, ephemeral, channel posting |
| Status renderers | `orchestrator/*_renderer.py` | Snapshot → Discord format |

### Anti-Patterns to Detect and Fix

1. **Renderer logic in visibility model**
   - Example: `VisibilitySnapshot` importing `discord.Embed`
   - Fix: Move to renderer, keep visibility model pure

2. **Business logic in Discord layer**
   - Example: `/commands.py` computing what feedback to show instead of using pre-computed
   - Fix: Use `VisibilitySnapshot` or `IntentHandlingResult.feedback_message`

3. **Tight coupling between renderers**
   - Example: PlayerStatusRenderer importing KPStatusRenderer internals
   - Fix: Both import only from `visibility.py`

---

## Specifics

### ACT-01: Visibility Contracts Reusability

**Verification checklist:**
- [ ] `VisibilitySnapshot` and sub-models have zero Discord dependencies
- [ ] All types can be imported in a fresh Python environment without installing discord.py
- [ ] Snapshot builder (`build_visibility_snapshot()`) has no Discord imports
- [ ] Renderers are explicitly separate modules with clear interfaces

**Target state:**
```python
# This should work without Discord installed:
from dm_bot.orchestrator.visibility import VisibilitySnapshot, PlayerVisibility

# This is the renderer pattern:
from dm_bot.orchestrator.visibility import VisibilitySnapshot
from dm_bot.orchestrator.player_status_renderer import render_player_status

async def show_status(snapshot: VisibilitySnapshot):
    embed = render_player_status(snapshot)  # Discord-specific
    await channel.send(embed=embed)
```

### ACT-02: No Activity UI Implementation

**Explicit out-of-scope:**
- No new Activity UI components
- No new rendering pipelines for non-Discord contexts
- No stub interfaces that "would be used by Activity" without concrete purpose

**What Phase 55 DOES do:**
- Prepare the visibility model so Activity UI COULD use it
- Document the renderer interface pattern for future implementers
- Ensure separation enables Activity-ready development

---

## Deferred Ideas

| Idea | Reason for Deferral |
|------|---------------------|
| Discord Activity UI implementation | Explicitly out of scope per ACT-02 |
| Web panel rendering | Future work after Activity-ready core exists |
| Cross-process visibility serialization | Requires additional infrastructure |
| Real-time push to multiple renderers | Beyond vC.1.3 scope |

---

## Test Scenarios

Phase 55 verification should confirm:

1. **Import isolation:**
   - `VisibilitySnapshot` can be imported without discord.py installed
   - No `import discord` or `from discord` in visibility.py

2. **Renderer separation:**
   - Each renderer module imports only `visibility.py` for types
   - No circular dependencies between renderers

3. **Interface consistency:**
   - All renderers accept `VisibilitySnapshot` as input
   - All renderers return renderer-specific output (Embed, dict, etc.)

4. **No business logic leakage:**
   - Feedback message content is computed in router, not in Discord commands
   - Status content comes from snapshot, not from command-specific queries

---

## Next Step

After this context is approved, proceed to create the implementation plan with:

1. Audit of current visibility.py for Discord dependencies
2. Audit of current renderer files for separation compliance
3. Refactoring tasks to achieve clean separation
4. Testing strategy to verify zero-Discord in visibility layer
5. Documentation of renderer interface pattern for future Activity developers

---

*Phase: 55-Activity-Ready-Boundary-Polish*
*Context gathered: 2026-03-29*
