# Phase 2 Discussion Log

**Mode:** Auto
**Date:** 2026-03-27

## Inputs Carried Forward

- Discord-first runtime is already complete from Phase 1.
- The product should avoid rebuilding mature ecosystems and should prefer open structured data and proven UX patterns.
- The system must support heavy rules, but the rules engine rather than the narrator must remain authoritative.
- Character import should be the simplest mature path, not a broad integration matrix.

## Auto Conclusions

1. Phase 2 should lock the system to `2014 SRD only` and reject mixed-baseline data.
2. Character import should start with one snapshot-style adapter into a normalized local character model.
3. Rules lookup and mechanical execution should sit behind adapters so Discord commands and narrator prompts stay insulated from source churn.
4. Model-produced actions must be validated against typed rules contracts before any canonical state changes are applied.

## Open Planning Questions

- Which single v1 character source yields the lowest debugging cost in practice?
- How much of the 5e SRD corpus should be mirrored locally for deterministic tests?
- Which minimal normalized character shape is sufficient for Phase 3 combat without overbuilding the data model?
