# Phase 45: Preflight Contract - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Standardize the preflight contract so operators can tell whether the local runtime is ready before they attempt bot startup, smoke-check, or restart flows.
</domain>

<decisions>
## Implementation Decisions

### Operator Ownership
- Preflight is an operator-facing readiness contract, not a gameplay feature.
- It should report configuration, model availability, and required local assets clearly enough that failures are actionable.
- This phase should not try to solve smoke-check timing or restart orchestration in full; those belong to later ops phases.

### Output Discipline
- Preflight should be deterministic, non-destructive, and readable in terminal contexts.
- The contract should be explicit enough that later control surfaces can reuse it instead of re-implementing their own readiness logic.

### the agent's Discretion
- Exact output shape (plain text sections vs structured JSON helper + renderer) so long as the command remains readable and testable.
- Whether shared readiness helpers should live in `config.py`, `runtime/health.py`, or a dedicated ops helper file.
</decisions>

<canonical_refs>
## Canonical References

### Planning Truth
- `.planning/workstreams/track-ops/ROADMAP.md` — phase goal and requirement mapping
- `.planning/workstreams/track-ops/REQUIREMENTS.md` — `OPS-01`
- `.planning/workstreams/track-ops/STATE.md` — milestone and phase position
- `AGENTS.md` — repository workflow and verification rules

### Existing Ops Code
- `src/dm_bot/main.py` — current `preflight` command output path
- `src/dm_bot/config.py` — settings and environment contract
- `src/dm_bot/runtime/health.py` — current health snapshot entrypoint
- `src/dm_bot/runtime/control_service.py` — operator state aggregation
</canonical_refs>

<specifics>
## Specific Ideas

- Preflight should explicitly cover Discord token/public key presence, model names/base URL, and asset-root visibility.
- If a structured snapshot already exists, prefer reusing it instead of duplicating checks inline.
</specifics>

<deferred>
## Deferred Ideas

- Smoke-check boot marker reliability belongs to Phase 46.
- Restart-system marker and process orchestration belong to Phase 47.
</deferred>
