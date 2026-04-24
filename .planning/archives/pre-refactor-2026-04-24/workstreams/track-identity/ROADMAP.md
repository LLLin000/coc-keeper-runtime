# Roadmap: `track-identity`

## Status

Standardized on `2026-04-09` for GSD phase parsing.

**Ownership**
- archive schema and migration
- builder flow and profile creation
- profile lifecycle
- campaign-local vs archive state boundary
- character import
- identity governance

## v1.0 Archive Stability And Two-Tier Builder

**Goal:** Freeze archive schema, establish builder two-tier paths, and formalize import/delete/validation contracts.

### Phase 19: Archive Schema Freeze

**Goal:** Lock archive schema versioning and document canonical archive fields.
**Depends on:** Nothing
**Requirements:** IDN-01
**Plans:** 1 plan

### Phase 20: Builder Two-Tier

**Goal:** Provide fast-path and full-path builder entry points over the same archive truth.
**Depends on:** Phase 19
**Requirements:** IDN-02
**Plans:** 0 plans

### Phase 21: Model-Guided Interview

**Goal:** Make model-guided interview planning primary with safe heuristic fallback.
**Depends on:** Phase 19, Phase 20
**Requirements:** IDN-03
**Plans:** 0 plans

### Phase 22: Import Paste

**Goal:** Add manual paste import with a documented archive-compatible parsing contract.
**Depends on:** Phase 19
**Requirements:** IDN-04
**Plans:** 0 plans

### Phase 23: Soft Delete And Hard Delete

**Goal:** Formalize recoverable delete and explicit permanent delete behavior.
**Depends on:** Phase 19
**Requirements:** IDN-05
**Plans:** 0 plans

### Phase 24: COC Validation

**Goal:** Enforce COC legality boundaries at finalize time without collapsing the conversational flow.
**Depends on:** Phase 19, Phase 20, Phase 23
**Requirements:** IDN-06
**Plans:** 0 plans

## v1.1 Archive Evolution And Session Integration

**Goal:** Formalize post-session archive evolution and growth tracking without collapsing the archive/runtime boundary.

### Phase 25: Session Checkpoint

**Goal:** Add explicit post-session checkpoint writes from campaign-instance state into archive truth.
**Depends on:** Phase 24
**Requirements:** IDN-07
**Plans:** 0 plans

### Phase 26: Schema Migration

**Goal:** Implement lightweight archive migration paths once real user data exists.
**Depends on:** Phase 25
**Requirements:** IDN-08
**Plans:** 0 plans

### Phase 27: Skill Improvement Tracking

**Goal:** Track COC skill improvements across sessions with auditable history.
**Depends on:** Phase 25, Phase 26
**Requirements:** IDN-09
**Plans:** 0 plans

### Phase 28: Experience Journal

**Goal:** Add structured adventure experience logging distinct from free-form narrative journaling.
**Depends on:** Phase 25, Phase 26, Phase 27
**Requirements:** IDN-10
**Plans:** 0 plans

### Phase 29: Builder Enhancements

**Goal:** Tune the fast/full builder split and improve guided quality based on earlier milestone usage.
**Depends on:** Phase 24
**Requirements:** IDN-11
**Plans:** 0 plans
