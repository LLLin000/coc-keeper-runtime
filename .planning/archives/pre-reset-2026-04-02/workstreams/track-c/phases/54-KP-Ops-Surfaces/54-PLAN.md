# Phase 54: KP Ops Surfaces - Implementation Plan

## Context

**Phase Goal:** Create dedicated KP/operator operational surfaces showing session ops, runtime state, player participation, and routing diagnostics.

**Key Decisions (Locked):**
- D-01: Dedicated KP/operator ops channel (separate from player status)
- D-02: Render from existing VisibilitySnapshot — no new data structures
- D-03: Higher information density than player surfaces
- D-04: Routing history shows last 10 decisions
- D-05: Explicit round number visibility

**Requirements:** OPS-01, OPS-02, OPS-03

---

## Task Dependency Graph

| Task | Depends On | Reason |
|------|------------|--------|
| Task 1: Extend VisibilitySnapshot with round_number and routing history | None | Starting point - foundation for all other tasks |
| Task 2: Create KP Ops Renderer (kp_ops_renderer.py) | Task 1 | Requires new routing history data structure |
| Task 3: Wire to Discord (ops channel + /ops_status command) | Task 2 | Requires renderer to exist before wiring |
| Task 4: Write tests for OPS-01, OPS-02, OPS-03 | Tasks 1, 2, 3 | Requires all implementation to be in place |

---

## Parallel Execution Graph

**Wave 1 (Start Immediately):**
- Task 1: Extend VisibilitySnapshot with round_number and routing history

**Wave 2 (After Wave 1 completes):**
- Task 2: Create KP Ops Renderer

**Wave 3 (After Wave 2 completes):**
- Task 3: Wire to Discord

**Wave 4 (After Wave 3 completes):**
- Task 4: Write tests

---

## Tasks

### Task 1: Extend VisibilitySnapshot with round_number and routing history

**Description:** Add round_number field to SessionVisibility and create routing history storage mechanism.

**Delegation Recommendation:**
- Category: `deep` - Goal-oriented autonomous problem-solving with thorough research
- Skills: [`superpowers/test-driven-development`] - TDD approach needed for defining data contracts

**Skills Evaluation:**
- INCLUDED `test-driven-development`: Required for TDD approach to define new data structures
- OMITTED `systematic-debugging`: Not needed yet, no bugs to investigate
- OMITTED `brainstorming`: Not needed, requirements already clear

**Depends On:** None

**Files Modified:**
- `src/dm_bot/orchestrator/visibility.py`

**Implementation Details:**

1. **Add round_number to SessionVisibility:**
   ```python
   class SessionVisibility(BaseModel):
       phase: SessionPhase
       ready_count: int
       total_members: int
       admin_started: bool
       round_number: int | None = None  # NEW: D-05
   ```

2. **Create RoutingHistoryEntry model:**
   ```python
   class RoutingHistoryEntry(BaseModel):
       timestamp: datetime
       user_id: str
       intent: str
       outcome: RoutingOutcome
       explanation: str | None
   ```

3. **Add routing_history to VisibilitySnapshot:**
   ```python
   class VisibilitySnapshot(BaseModel):
       # ... existing fields
       routing_history: list[RoutingHistoryEntry] = Field(default_factory=list)  # NEW: D-04
   ```

4. **Update build_visibility_snapshot to include:**
   - Round number from session (need to add to CampaignSession if not present)
   - Routing history from a new routing history store

5. **Create new file: `src/dm_bot/orchestrator/routing_history.py`:**
   - `RoutingHistoryStore` class with `add_entry()` and `get_recent(n=10)` methods
   - In-memory storage with configurable max entries (default 10 per D-04)

**TDD Test Cases (write first):**
```python
# tests/orchestrator/test_kp_ops_visibility.py
def test_session_visibility_includes_round_number():
    """SessionVisibility should include optional round_number field."""
    vis = SessionVisibility(
        phase=SessionPhase.SCENE_ROUND_OPEN,
        ready_count=3,
        total_members=5,
        admin_started=True,
        round_number=3
    )
    assert vis.round_number == 3

def test_routing_history_entry_stores_complete_info():
    """RoutingHistoryEntry should store timestamp, user, intent, outcome, explanation."""
    entry = RoutingHistoryEntry(
        timestamp=datetime.now(),
        user_id="user123",
        intent="OOC",
        outcome=RoutingOutcome.BUFFERED,
        explanation="OOC在行动收集阶段被缓存"
    )
    assert entry.user_id == "user123"
    assert entry.intent == "OOC"

def test_routing_history_store_limits_entries():
    """RoutingHistoryStore should limit to max entries (default 10)."""
    store = RoutingHistoryStore(max_entries=10)
    for i in range(15):
        store.add_entry(RoutingHistoryEntry(...))
    assert len(store.get_recent()) == 10
```

**Acceptance Criteria:**
- [ ] SessionVisibility has optional round_number field
- [ ] RoutingHistoryEntry model exists with timestamp, user_id, intent, outcome, explanation
- [ ] RoutingHistoryStore limits entries to 10 (D-04)
- [ ] build_visibility_snapshot includes routing history

---

### Task 2: Create KP Ops Renderer

**Description:** Create kp_ops_renderer.py with overview, detailed, and routing_history render modes.

**Delegation Recommendation:**
- Category: `deep` - Complex rendering with multiple display modes
- Skills: [`superpowers/test-driven-development`] - TDD for renderer output verification

**Skills Evaluation:**
- INCLUDED `test-driven-development`: Required to verify renderer output formats
- OMITTED `systematic-debugging`: No bugs to investigate yet
- OMITTED `brainstorming`: Requirements already specified in context

**Depends On:** Task 1

**Files Created:**
- `src/dm_bot/orchestrator/kp_ops_renderer.py`

**Implementation Details:**

1. **Create KPOpsRenderer class:**
   ```python
   class KPOpsRenderer:
       """Renders VisibilitySnapshot for KP/operator surfaces."""
       
       def __init__(self, active_characters: dict[str, str] | None = None) -> None:
           self._active_characters = active_characters or {}
       
       def render_overview(self, snapshot: VisibilitySnapshot | None) -> str:
           """High-density overview for ops channel - D-03, OPS-01"""
           # Shows: phase, round state, blockers, runtime state
           # Higher density than player status
           
       def render_detailed(self, snapshot: VisibilitySnapshot | None) -> str:
           """Detailed per-player view - OPS-02"""
           # Shows: each player's ready/submitted/onboarding status
           
       def render_routing_history(self, snapshot: VisibilitySnapshot | None) -> str:
           """Routing history view - D-04, OPS-03"""
           # Shows: last 10 routing decisions with timestamps
   ```

2. **render_overview format (OPS-01):**
   ```
   🎭 Session: SCENE_ROUND_OPEN (Round 3)
   ⏳ Waiting: 2 players to submit actions
   📋 Pending: @player1, @player2
   📦 Adventure: mad_mansion | Scene: Entrance Hall
   👤 Ready: 3/5 | Admin Started: Yes
   ```

3. **render_detailed format (OPS-02):**
   ```
   👤 Player1 (Dr. Jones - Doctor)
     ✓ Ready | ✓ Action Submitted | ✓ Onboarded
   
   👤 Player2 (Sarah - Journalist)  
     ✓ Ready | ⏳ Pending Action | ✓ Onboarded
   
   👤 Player3 (Mike - Private Eye)
     ✗ Not Ready | - No Action | ✓ Onboarded
   ```

4. **render_routing_history format (OPS-03):**
   ```
   🕐 14:32 | @player1 | OOC | BUFFERED | "OOC在行动收集阶段被缓存"
   🕐 14:31 | @player2 | ACTION | PROCESSED | Keeper narration triggered
   🕐 14:30 | @player3 | RULES_QUERY | DEFERRED | "将在结算后回答"
   ```

**TDD Test Cases:**
```python
def test_kp_ops_overview_shows_round_number():
    """Overview should show round number when in scene round phases."""
    session = CampaignSession(...)
    session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    # Set round_number on session
    
    snapshot = build_visibility_snapshot(session, ...)
    renderer = KPOpsRenderer()
    output = renderer.render_overview(snapshot)
    
    assert "Round 3" in output or "(Round 3)" in output

def test_kp_ops_detailed_shows_all_player_statuses():
    """Detailed view should show each player's ready/submitted/onboarding."""
    # ... test implementation
    
def test_kp_ops_routing_history_shows_last_10():
    """Routing history should show up to 10 entries."""
    # ... test implementation
```

**Acceptance Criteria:**
- [ ] KPOpsRenderer.render_overview shows phase, round, blockers, runtime (OPS-01)
- [ ] KPOpsRenderer.render_detailed shows per-player ready/submitted/onboarding (OPS-02)
- [ ] KPOpsRenderer.render_routing_history shows last 10 decisions (OPS-03)
- [ ] Higher information density than PlayerStatusRenderer (D-03)

---

### Task 3: Wire to Discord

**Description:** Add ops channel setup and /ops_status command.

**Delegation Recommendation:**
- Category: `unspecified-high` - Integration work across multiple components
- Skills: [`superpowers/test-driven-development`] - May need tests for command wiring

**Skills Evaluation:**
- INCLUDED `test-driven-development`: Verify command integration
- OMITTED `brainstorming`: Requirements clear
- OMITTED `systematic-debugging`: Not yet needed

**Depends On:** Task 2

**Files Modified:**
- `src/dm_bot/orchestrator/session_store.py` (add ops channel tracking)
- `src/dm_bot/discord_bot/commands.py` (add /ops_status command)

**Implementation Details:**

1. **Add ops channel to SessionStore:**
   ```python
   class SessionStore:
       def __init__(self):
           # ... existing
           self._ops_channels: dict[str, str] = {}  # NEW: guild_id -> channel_id
       
       def bind_ops_channel(self, guild_id: str, channel_id: str):
           self._ops_channels[guild_id] = channel_id
       
       def ops_channel_for(self, guild_id: str) -> str | None:
           return self._ops_channels.get(guild_id)
   ```

2. **Add /ops_status command:**
   - Returns rendered KP ops overview
   - Can accept optional mode argument: overview | detailed | routing

3. **Add /bind_ops_channel command:**
   - Binds current channel as KP ops channel (D-01)

4. **Update channel guidance in setup_check:**
   - Add "KP Ops" to the 6-channel structure
   - Include new binding command

5. **Integration point:**
   - When visibility snapshot updates, optionally update ops channel
   - This may be deferred per context (real-time push is deferred)

**Acceptance Criteria:**
- [ ] /bind_ops_channel command exists and works
- [ ] /ops_status command returns rendered overview
- [ ] Ops channel is tracked in SessionStore
- [ ] Channel guidance includes KP Ops channel

---

### Task 4: Write Tests for OPS Requirements

**Description:** Create comprehensive tests verifying all three OPS requirements.

**Delegation Recommendation:**
- Category: `deep` - Tests require understanding of all components
- Skills: [`superpowers/test-driven-development`]

**Skills Evaluation:**
- INCLUDED `test-driven-development`: Core to this task
- OMITTED `brainstorming`: Not needed
- OMITTED `systematic-debugging`: Not yet needed

**Depends On:** Tasks 1, 2, 3

**Files Created:**
- `tests/orchestrator/test_kp_ops_renderer.py`

**Test Coverage:**

1. **OPS-01: Session Phase, Round State, Blockers, Runtime State**
   ```python
   def test_ops_overview_shows_phase_and_round():
       """OPS-01: Overview shows current phase with round number."""
       
   def test_ops_overview_shows_blockers():
       """OPS-01: Overview shows what's blocking progress."""
       
   def test_ops_overview_shows_runtime_state():
       """OPS-01: Overview shows adventure, scene, admin started."""
   ```

2. **OPS-02: Per-Player Participation State**
   ```python
   def test_ops_detailed_shows_player_ready_status():
       """OPS-02: Detailed shows each player's ready status."""
       
   def test_ops_detailed_shows_player_action_status():
       """OPS-02: Detailed shows submitted/pending action status."""
       
   def test_ops_detailed_shows_onboarding_status():
       """OPS-02: Detailed shows onboarding completion."""
   ```

3. **OPS-03: Routing Outcomes**
   ```python
   def test_ops_routing_history_shows_last_10():
       """OPS-03: Routing history limited to 10 entries."""
       
   def test_ops_routing_history_shows_all_fields():
       """OPS-03: Each entry has timestamp, user, intent, outcome, explanation."""
   ```

4. **Integration:**
   ```python
   def test_kp_ops_channel_separation():
       """D-01: Ops surface is in dedicated channel."""
       
   def test_higher_density_than_player_surface():
       """D-03: Ops surface has higher information density."""
   ```

**Acceptance Criteria:**
- [ ] All OPS-01 scenarios tested and passing
- [ ] All OPS-02 scenarios tested and passing
- [ ] All OPS-03 scenarios tested and passing
- [ ] Tests run with `uv run pytest -q`

---

## Commit Strategy

| Commit | Description |
|--------|-------------|
| 1 | `feat(ops): add round_number to SessionVisibility and RoutingHistoryEntry` - Data model changes |
| 2 | `feat(ops): add RoutingHistoryStore for tracking routing decisions` - History storage |
| 3 | `feat(ops): create KPOpsRenderer with overview/detailed/routing_history modes` - Renderer |
| 4 | `feat(ops): wire KP ops channel and /ops_status command to Discord` - Discord integration |
| 5 | `test(ops): add tests for OPS-01, OPS-02, OPS-03 requirements` - Tests |

---

## Success Criteria

1. **KP/operators can see phase, round state, blockers, and runtime state in one place** (OPS-01)
   - Verification: `KPOpsRenderer.render_overview()` output contains all four elements

2. **KP/operators can inspect per-player ready/submitted/pending state** (OPS-02)
   - Verification: `KPOpsRenderer.render_detailed()` shows all player statuses

3. **KP/operators can inspect routing outcomes without digging through raw logs** (OPS-03)
   - Verification: `KPOpsRenderer.render_routing_history()` shows last 10 decisions

4. **All tests pass:**
   ```bash
   uv run pytest -q
   ```

5. **Smoke check passes:**
   ```bash
   uv run python -m dm_bot.main smoke-check
   ```

---

## TODO List (ADD THESE)

> CALLER: Add these TODOs using TodoWrite/TaskCreate and execute by wave.

### Wave 1 (Start Immediately - No Dependencies)

- [ ] **1. Extend VisibilitySnapshot with round_number and routing history**
  - What: Add round_number field to SessionVisibility, create RoutingHistoryEntry model, add routing_history to VisibilitySnapshot, create RoutingHistoryStore class
  - Depends: None
  - Blocks: 2, 3, 4
  - Category: `deep`
  - Skills: [`superpowers/test-driven-development`]
  - QA: Tests pass for new data models; SessionVisibility has round_number, RoutingHistoryEntry exists, RoutingHistoryStore limits to 10 entries
  - Files: `src/dm_bot/orchestrator/visibility.py`, `src/dm_bot/orchestrator/routing_history.py`

### Wave 2 (After Wave 1 Completes)

- [ ] **2. Create KP Ops Renderer (kp_ops_renderer.py)**
  - What: Create KPOpsRenderer class with render_overview, render_detailed, render_routing_history methods; implement high-density output formats per context
  - Depends: 1
  - Blocks: 3, 4
  - Category: `deep`
  - Skills: [`superpowers/test-driven-development`]
  - QA: KPOpsRenderer renders correct output for all three modes (overview, detailed, routing_history)
  - Files: `src/dm_bot/orchestrator/kp_ops_renderer.py`

### Wave 3 (After Wave 2 Completes)

- [ ] **3. Wire to Discord (ops channel + /ops_status command)**
  - What: Add ops channel tracking to SessionStore, create /bind_ops_channel and /ops_status commands, update channel guidance
  - Depends: 2
  - Blocks: 4
  - Category: `unspecified-high`
  - Skills: [`superpowers/test-driven-development`]
  - QA: Commands exist and function correctly; channel binding works
  - Files: `src/dm_bot/orchestrator/session_store.py`, `src/dm_bot/discord_bot/commands.py`

### Wave 4 (After Wave 3 Completes)

- [ ] **4. Write tests for OPS-01, OPS-02, OPS-03 requirements**
  - What: Create comprehensive test file verifying all three OPS requirements with test cases for overview, detailed, and routing_history modes
  - Depends: 1, 2, 3
  - Blocks: None
  - Category: `deep`
  - Skills: [`superpowers/test-driven-development`]
  - QA: `uv run pytest -q` passes all tests
  - Files: `tests/orchestrator/test_kp_ops_renderer.py`

## Execution Instructions

1. **Wave 1**: Fire these tasks IN PARALLEL (no dependencies)
   ```
   task(category="deep", load_skills=["superpowers/test-driven-development"], run_in_background=false, prompt="Task 1: Extend VisibilitySnapshot with round_number and routing history...")
   ```

2. **Wave 2**: After Wave 1 completes, fire next wave
   ```
   task(category="deep", load_skills=["superpowers/test-driven-development"], run_in_background=false, prompt="Task 2: Create KP Ops Renderer...")
   ```

3. **Wave 3**: After Wave 2 completes, fire next wave
   ```
   task(category="unspecified-high", load_skills=["superpowers/test-driven-development"], run_in_background=false, prompt="Task 3: Wire to Discord...")
   ```

4. **Wave 4**: After Wave 3 completes, fire final wave
   ```
   task(category="deep", load_skills=["superpowers/test-driven-development"], run_in_background=false, prompt="Task 4: Write tests for OPS requirements...")
   ```

5. **Final QA**: Verify all tasks pass their QA criteria:
   - Run `uv run pytest -q`
   - Run `uv run python -m dm_bot.main smoke-check`
