# Phase 45: Preflight Contract - Research

## Research Summary

The repository already has a `preflight` command, but it is currently a thin string dump. There is also a richer health/control surface in the runtime layer. This phase should align those two worlds into a stable operator contract.

## Findings

### 1. Preflight currently reports only a minimal settings dump

- `dm_bot.main describe_runtime()` prints configuration presence and selected model names.
- That is useful, but it is not yet framed as a full readiness contract.
- A dedicated ops phase is justified because later operator tooling should be able to rely on the same readiness semantics.

### 2. Health/control surfaces already contain richer readiness information

- `runtime/health.py` and `runtime/control_service.py` already aggregate model and process information.
- Preflight should reuse that logic where it makes sense instead of maintaining a second conflicting readiness model.

### 3. Operator trust depends on deterministic output

- Preflight must remain non-destructive and should not silently mutate process state.
- It is best suited to configuration and environment checks that can run before bot startup.

### 4. Clear separation from smoke-check is important

- Smoke-check runs pytest and a startup flow; preflight should not turn into a partial smoke-check.
- If the contract is cleanly separated now, later phases can diagnose “config bad” versus “boot failed” without ambiguity.

## Recommended Planning Direction

1. Define explicit readiness categories for preflight.
2. Reuse structured health helpers where possible.
3. Add tests that prove preflight output covers the expected operator prerequisites.

## Risks

- If preflight starts owning process boot behavior, it will blur the boundary with Phases 46 and 47.
- If preflight remains a plain string dump, later ops surfaces will continue to re-invent readiness logic.
