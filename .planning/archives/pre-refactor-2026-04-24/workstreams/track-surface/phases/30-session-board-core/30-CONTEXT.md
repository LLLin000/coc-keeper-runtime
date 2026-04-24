# Phase 30: Session Board Core - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the first session-board surface that renders current session identity, phase, pending participants, and blocker summaries from canonical runtime truth.
</domain>

<decisions>
## Implementation Decisions

### Surface Ownership
- `track-surface` renders runtime truth; it does not invent or infer missing runtime semantics.
- Session board scope is current-session visibility, not historical browsing or audit tooling.
- This phase should prefer reusable view contracts over raw Discord-only string assembly when practical.

### Dependency Discipline
- If runtime does not expose a field cleanly, the phase should add a thin consumption boundary or explicit TODO, not invent a parallel truth source.
- KP-only or private visibility is out of scope unless runtime already exposes it clearly enough to consume safely.

### the agent's Discretion
- Whether the first board lands as a renderer refactor, a new board renderer, or a small presentation abstraction.
- Exact output density, as long as it remains readable in Discord and sourced from canonical state.
</decisions>

<canonical_refs>
## Canonical References

### Planning Truth
- `.planning/workstreams/track-surface/ROADMAP.md` — phase goal and requirement mapping
- `.planning/workstreams/track-surface/REQUIREMENTS.md` — `SUR-01`
- `.planning/workstreams/track-surface/STATE.md` — track position and execution caveat
- `AGENTS.md` — repository workflow and verification rules

### Existing Surface Code
- `src/dm_bot/orchestrator/player_status_renderer.py` — current player-facing status rendering
- `src/dm_bot/orchestrator/kp_ops_renderer.py` — current operator-facing status rendering
- `src/dm_bot/orchestrator/visibility.py` — visibility snapshot model
- `src/dm_bot/discord_bot/commands.py` — current command entrypoints and response paths
</canonical_refs>

<specifics>
## Specific Ideas

- Prefer a board-like renderer that can later feed Activity-style views, not only hand-built message strings.
- Keep this phase focused on current session status rather than clue boards or consequence publication.
</specifics>

<deferred>
## Deferred Ideas

- Clue/history boards belong to later phases.
- Component-driven actions and stateful pagination belong to later milestones.
</deferred>
