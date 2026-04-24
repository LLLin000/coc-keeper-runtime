# Phase 30: Session Board Core - Research

## Research Summary

The surface layer already has player- and KP-facing renderers, but session status is still mostly delivered as purpose-specific strings. This phase should consolidate a clearer session-board surface without inventing new runtime semantics.

## Findings

### 1. Structured visibility snapshots already exist

- `src/dm_bot/orchestrator/visibility.py` defines structured snapshot models.
- `player_status_renderer.py` already consumes these snapshots and renders readable status blocks.
- This is a good base for a session-board phase because the surface can stay downstream of runtime truth.

### 2. Current rendering is useful but not yet board-oriented

- Existing renderers are channel-specific and string-oriented.
- They communicate session identity and waiting state, but the output is still closer to a status message than a reusable board contract.
- A first board surface can likely reuse these renderers or their data paths rather than replacing everything.

### 3. There is already an operator-facing parallel renderer

- `kp_ops_renderer.py` suggests the codebase already distinguishes player and operator presentation concerns.
- Session Board Core should preserve that split instead of collapsing all audience needs into one renderer.

### 4. Surface must stay downstream of runtime

- This phase depends on runtime state being structured enough to expose campaign/session/blocker truth.
- If some fields are still weak, the correct move is to consume what exists and note thin adapter needs, not re-infer state through Discord copy.

## Recommended Planning Direction

1. Build a session-board renderer contract on top of visibility snapshots.
2. Reuse existing player/KP renderers where possible, but factor shared board semantics cleanly.
3. Keep scope to current session identity and blocker/pending state.

## Risks

- Overreaching into clue/history or consequence boards will blur the boundary with later phases.
- If this phase starts inventing session truth in presentation code, later runtime work will fork the state model again.
