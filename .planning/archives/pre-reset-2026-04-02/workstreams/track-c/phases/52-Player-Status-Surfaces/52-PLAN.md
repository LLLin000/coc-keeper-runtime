# Phase 52: Player Status Surfaces - Plan

**Goal:** Add player-facing shared status surfaces for current campaign/adventure/session identity and waiting state, using canonical visibility contracts from Phase 51.

## 1. Context and Approach

This phase implements the player-facing rendering path for session visibility. Based on Phase 52 Context decisions, we will implement two primary shared surfaces and one private surface:
1. **Concise Game Channel Presence:** A persistent, concise shared status message in the main game channel.
2. **Dedicated Status/Info Channel:** A medium-density overview panel in a designated player-visible info channel.
3. **On-Demand Detail Path:** An ephemeral/private response for players querying their personal detailed state.

Both shared surfaces will present the campaign/adventure/session identity using a structured header and a short narrative line (D-13, D-14), explicitly showing current status and wait reasons (D-08), while reading directly from the Phase 51 `VisibilitySnapshot` (D-03).

## 2. Task Breakdown

### Task 1: Player Status/Info Channel Setup
**Objective:** Establish the routing and channel definition for a dedicated player-visible status channel (D-04, D-05, D-06).
- **1.1 Config & Enforcement:** Update `ChannelRoleConfig` and `ChannelEnforcer` to recognize `player_status_channel`.
- **1.2 Routing Logic:** Ensure player status queries and commands are directed to this channel if configured, separating it from game play and future admin diagnostics.

### Task 2: Medium-Density Player Overview Panel
**Objective:** Render the default shared player-facing status surface for the status/info channel (D-07, D-08, D-10, D-12, D-13, D-14).
- **2.1 Renderer Component:** Create `PlayerStatusRenderer` that consumes `VisibilitySnapshot`.
- **2.2 Identity Presentation:** Format the top section with a structured header (Campaign/Adventure/Session) and a single short narrative/status line.
- **2.3 Participation Summary:** Format the player list showing participation states (ready/submitted/pending) without exposing private details.
- **2.4 Wait Reasons Display:** Explicitly display the active session phase and who/what the table is waiting on (using Phase 51 blocker/waiting reasons).
- **2.5 Panel Delivery:** Implement the `/status overview` (or similar) command to post/update this panel in the status channel.

### Task 3: Concise Game Channel Presence
**Objective:** Maintain a lightweight, persistent status message in the main game channel (D-01, D-06).
- **3.1 Concise Renderer:** Create a stripped-down version of the renderer from Task 2 that only includes the structured header, short narrative line, and immediate wait reason.
- **3.2 Persistent Message Management:** Update the game loop/orchestrator to pin or maintain this short status message at the bottom of the game channel during active play.

### Task 4: Ephemeral Private Detail Query
**Objective:** Provide an on-demand path for detailed personal state (D-02, D-09, D-11).
- **4.1 Detail Renderer:** Create a renderer for personal character state (HP, SAN, attributes) based on canonical `VisibilitySnapshot.player_snapshots`.
- **4.2 Query Command:** Implement a `/status me` (or similar button interaction on the main panel) that returns the detailed payload.
- **4.3 Ephemeral Delivery:** Ensure this output is explicitly sent as an ephemeral Discord response, guaranteeing privacy.

### Task 5: Inactive and Unloaded States
**Objective:** Handle edge cases where no scene or session is active, providing explicit explanations (CURR-02).
- **5.1 Empty State Handling:** Update the `PlayerStatusRenderer` to detect null/inactive states in the `VisibilitySnapshot`.
- **5.2 Explicit Messaging:** Define and render explicit "not active / not loaded / waiting to start" blocks instead of failing silently or showing blank fields.

## 3. Requirement Mapping

| Task | Requirement | Description |
|------|-------------|-------------|
| 2, 3 | **PLAY-01** | Players can see the current campaign/adventure identity and current session state from Discord without relying on hidden operator knowledge |
| 2, 3 | **PLAY-02** | Players can see shared round/session waiting reasons, including who or what the table is waiting on |
| 2, 3 | **CURR-01** | Discord surfaces can show the currently loaded campaign/adventure/session identity and status without requiring a broader multi-campaign browser |
| 5    | **CURR-02** | When no active scene or session state exists, users get an explicit explanation instead of ambiguous silence |

*(Note: PLAY-03, PLAY-04 belong to Phase 53; OPS-01, OPS-02, OPS-03 belong to Phase 54. Activity and Character requirements are explicitly excluded.)*

## 4. Success Criteria Mapping

1. **Players can see current campaign/adventure/session identity from Discord:** Addressed by Tasks 2 and 3 using the mixed presentation header + narrative line.
2. **Players can see what the table is waiting on and who is pending when relevant:** Addressed by Task 2's participation summary and wait reasons block.
3. **Current-only visibility works without requiring broad browsing UI:** Addressed by Tasks 2, 3, and 4 focusing strictly on the active `VisibilitySnapshot`.
4. **Inactive or unloaded states are explained explicitly instead of failing silently:** Addressed by Task 5's dedicated empty-state rendering logic.
