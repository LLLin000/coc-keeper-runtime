# Phase 1: Scene Lifecycle - Research

## Research Summary

Current runtime state is split across `session_store.py`, `gameplay.py`, and turn-routing code, but scene lifecycle is not modeled as a first-class concept. The codebase still behaves like a single-scene system with campaign-wide serialization.

## Findings

### 1. Session phase exists, scene lifecycle does not

- `src/dm_bot/orchestrator/session_store.py` already models session phases such as lobby, awaiting_ready, onboarding, and scene_round_open.
- There is no equivalent explicit model for scene-level lifecycle such as collecting, locked, resolving, or published.
- This means later batch logic would have to infer scene state from transient behavior unless Phase 1 introduces a canonical model first.

### 2. Gameplay state is still mostly dict-shaped

- `src/dm_bot/orchestrator/gameplay.py` stores adventure state in mutable dicts like `pending_roll`, `knowledge_log`, and location/scene identifiers.
- That shape is flexible enough for prototypes but weak as a long-term source of truth for scene orchestration.
- Introducing typed lifecycle models now will reduce follow-on refactors in v1.0-v1.1.

### 3. Turn coordination is campaign-serialized

- `src/dm_bot/orchestrator/turns.py` uses one `asyncio.Lock` per campaign.
- This is acceptable for current single-scene behavior, but it hides the boundary between campaign-level coordination and scene-level coordination.
- Phase 1 should avoid solving concurrency fully, but it should create the state model that later phases can coordinate against.

### 4. Existing renderers already expect structured status

- Player-facing and operator-facing renderers already consume structured snapshots rather than scraping arbitrary text.
- That is a good fit for a dedicated scene lifecycle model because downstream surfaces can render from explicit lifecycle state instead of heuristics.

## Recommended Planning Direction

1. Add narrow typed models for scene lifecycle and focus scope.
2. Integrate them through session/gameplay state without requiring a full multi-scene feature release in the same phase.
3. Keep migration compatibility for existing single-scene tests.

## Risks

- Overreaching into batch resolution or merge behavior will blur the boundary with Phases 2 and 3.
- If lifecycle and focus are not separated now, later phases will accumulate workaround state instead of extending a clean model.
