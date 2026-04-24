# Roadmap: `track-ops`

## Status

Standardized on `2026-04-09` for GSD phase parsing.

**Ownership**
- scenario runner
- smoke-check and preflight
- control panel and operator status
- restart/recovery flows
- delivery gates and diagnostics

## v1.0 Startup And Delivery Gate Reliability

**Goal:** Make local startup checks and gate signals dependable enough that later execution work is not blocked by ambiguous operator failures.

### Phase 45: Preflight Contract

**Goal:** Standardize preflight output around required models, Discord config, assets, and operator prerequisites.
**Depends on:** Nothing
**Requirements:** OPS-01
**Plans:** 1 plan

### Phase 46: Smoke-Check Reliability

**Goal:** Make smoke-check distinguish pytest failures from startup/boot failures with reliable status artifacts.
**Depends on:** Phase 45
**Requirements:** OPS-02
**Plans:** 0 plans

### Phase 47: Restart And Boot Integrity

**Goal:** Harden restart-system and startup marker handling so boot progress is observable and diagnosable.
**Depends on:** Phase 45, Phase 46
**Requirements:** OPS-02, OPS-03
**Plans:** 0 plans

### Phase 48: Control Status Model

**Goal:** Normalize control-status and control-panel runtime state around canonical operator facts.
**Depends on:** Phase 45, Phase 46, Phase 47
**Requirements:** OPS-03, OPS-04
**Plans:** 0 plans

## v1.1 Scenario And Recovery Coverage

**Goal:** Make verification representative enough that runtime, identity, and surface regressions are caught by operator tooling rather than by play sessions.

### Phase 49: Scenario Taxonomy

**Goal:** Standardize suites and metadata so scenario coverage is explicit instead of accidental.
**Depends on:** Phase 48
**Requirements:** OPS-05
**Plans:** 0 plans

### Phase 50: Recovery And Resume Suites

**Goal:** Add scenario and integration coverage for restart/recovery/resume paths.
**Depends on:** Phase 47, Phase 49
**Requirements:** OPS-06
**Plans:** 0 plans

### Phase 51: Failure Artifact Standardization

**Goal:** Make failures leave consistent artifacts for smoke, scenario, and restart paths.
**Depends on:** Phase 46, Phase 47, Phase 49, Phase 50
**Requirements:** OPS-07
**Plans:** 0 plans

## v1.2 Diagnostics And Operator Workflow

**Goal:** Build actionable operator workflows on top of stable health, restart, and verification signals.

### Phase 52: Diagnostics Aggregation

**Goal:** Aggregate runtime/session/failure diagnostics into an operator-readable summary model.
**Depends on:** Phase 48, Phase 51
**Requirements:** OPS-08
**Plans:** 0 plans

### Phase 53: Operator Inspection

**Goal:** Add inspection paths for audit, recovery, and runtime state without requiring raw file/db spelunking.
**Depends on:** Phase 50, Phase 51, Phase 52
**Requirements:** OPS-09
**Plans:** 0 plans

### Phase 54: Gate Parity And Automation

**Goal:** Align local gate semantics, operator tooling, and future automation around the same health contract.
**Depends on:** Phase 46, Phase 52, Phase 53
**Requirements:** OPS-10
**Plans:** 0 plans
