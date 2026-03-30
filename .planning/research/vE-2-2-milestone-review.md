# vE.2.2 Milestone Design Review

**Project:** Discord AI Keeper
**Milestone:** vE.2.2 — 统一 Scenario-Driven E2E 验证框架
**Review Date:** 2026-03-30
**Confidence:** 5/10

---

## Executive Summary

The vE.2.2 4-phase plan (E69→E70→E71→E72) covers the major structural components of a unified scenario-driven E2E framework, but contains **significant gaps** that would cause phases to be incomplete or require modification mid-execution:

1. **Critical gap**: `fuzhe_mini.json` fixture is referenced in the roadmap but **does not exist**
2. **Architectural gap**: `deterministic_dice` requires modifying `rules/dice.py` source code, but no phase explicitly addresses this
3. **Missing cross-cutting plan**: `fake_clock`, `model_mode` parameter (fake_contract/recorded/live), CI integration strategy, and initial state setup are not assigned to any phase
4. **E70 can begin before E69 completes** — the YAML DSL definition can proceed independently, though ArtifactWriter needs E69's step contracts first

---

## 1. Coverage Map

Mapping each PRD requirement to its assigned phase:

| PRD Requirement | Assigned Phase | Coverage Status |
|-----------------|---------------|-----------------|
| ScenarioRunner (unified test driver) | E69 | ✅ Covered |
| RuntimeTestDriver (Discord-free interface) | E69 | ✅ Covered |
| Scenario DSL (YAML format) | E70 | ✅ Covered |
| ArtifactWriter (json + md output) | E70 | ✅ Covered |
| FailureCode taxonomy (standardized enum) | E71 | ✅ Covered |
| deterministic_dice (seeded) | E69 (implied) | ⚠️ Needs source code change |
| fake_clock | E69 (implied) | ❌ Not explicitly mentioned |
| 4 scenario suites: acceptance | E72 | ✅ Covered |
| 4 scenario suites: contract | E71 | ✅ Covered |
| 4 scenario suites: chaos | E72 | ✅ Covered |
| 4 scenario suites: recovery | E72 | ✅ Covered |
| Visibility leak detection | E71 | ✅ Covered |
| Reveal policy enforcement | E71 | ✅ Covered |
| AI contract tests (packet structure, schema stability) | E71 | ✅ Covered |
| Unified command: `run-scenario` | E70 (implied) | ⚠️ Not explicitly in E70 description |

**E69 description** ("deterministic dice, fake clock, step result contracts") implies these are in scope, but they are not explicitly named in the phase goals. This ambiguity is a risk.

---

## 2. Uncovered Requirements

### 2.1 `fuzhe_mini.json` Does Not Exist

**Problem:** The ROADMAP.md vE.2.1 section explicitly references `fuzhe_mini.json` as the test fixture for the 15-turn deterministic scenario:
> **Test Fixture:** `fuzhe_mini.json` — 4-node vertical slice of fuzhe for deterministic 15-turn scenario testing

But searching the entire codebase:
- No `fuzhe_mini.json` file exists
- Only `fuzhe.json` exists (737 lines, 9 locations, 14 triggers, 7 story nodes)
- No fixture generation logic exists

**Impact:** E72 cannot execute "15-turn fuzhe_mini" scenario as planned. Either:
- E69-E71 must include creating the `fuzhe_mini` fixture, or
- E72 must fall back to using the full `fuzhe.json`, which is NOT deterministic by default

**Recommendation:** Either create `fuzhe_mini.json` during E69 (adds scope) or redesignate E72 to use `fuzhe.json` with a seeded dice for determinism.

### 2.2 `fake_clock` Not Named Explicitly

The PRD calls for `fake_clock` (controllable time for testing time-dependent triggers). E69 description mentions "fake clock" as part of the RuntimeTestDriver but it's not explicitly listed in the phase goal. This is ambiguous — if it's not explicitly in E69's goal text, it could be deprioritized.

### 2.3 `model_mode` Parameter (fake_contract | recorded | live) Not Covered

No mention of VCR.py integration strategy for model interaction recording/playback:
- `fake_contract` mode — uses existing `FastMock`/`StubModelClient` ✓ (already exists in `tests/fakes/models.py`)
- `recorded` mode — VCR.py cassettes needed (but `tests/cassettes/` is empty, no recordings exist)
- `live` mode — real Ollama calls

The existing `conftest.py` has VCR config ready but no cassettes exist. Phase E60-E68 used FastMock extensively but no VCR recording was made. This means the `recorded` mode infrastructure exists but has never been exercised.

---

## 3. Cross-Cutting Gaps

### 3.1 Deterministic Dice Requires Source Code Changes

**Current state:**
- `rules/dice.py` uses `random.randint()` directly (line 72: `ones = random.randint(0, 9)`)
- `RulesEngine` accepts a `dice_roller` injection point (line 17-25 of `engine.py`)
- Tests use `StubPercentileRoller` classes for deterministic results

**What's needed for true determinism:**
- A seeded `DeterministicDiceRoller` class in `rules/dice.py` that accepts a seed
- ScenarioRunner must inject this roller when running deterministic scenarios
- The `GameplayOrchestrator` currently creates `RulesEngine` without dice roller injection (line 80-82 of `main.py`)

**Gap:** No phase explicitly addresses modifying `rules/dice.py` to add a seeded roller. This is a **source code change**, not just test infrastructure.

### 3.2 Initial State Setup Not Defined

The roadmap doesn't specify:
- How ScenarioRunner gets the runtime to a known initial state before each scenario
- Whether each scenario gets a fresh in-memory store or a restored persistent store
- How state isolation between scenarios is achieved

The existing `e2e_session` fixture in `test_e2e_15turn_scenario.py` manually sets up state (line 26-47), but this is inline test code, not a reusable runtime API.

### 3.3 Large Output / Streaming Artifact Handling

`ArtifactWriter` must handle `stream_narrator` output which can be large. The current `StubModelClient.stream_narrator()` (line 38-43 of `tests/fakes/models.py`) is a simple char-by-char generator. No plan for:
- Chunking large artifacts
- Truncation strategy
- Streaming artifact format (json lines? one file per chunk?)

### 3.4 CI vs Local Execution Strategy

No plan for:
- How scenarios run in CI (headless? withXvfb?)
- Whether `run-scenario` command works in CI environment without Discord
- Test parallelization strategy for chaos scenarios

### 3.5 Visibility Leak Detection — Existing Infrastructure?

`tests/orchestrator/test_visibility.py` exists and tests visibility. E71 will add "visibility leak tests" — but this may be redundant with existing tests. Need to verify existing test coverage before E71 scope is finalized.

---

## 4. Dependency Issues

### 4.1 Phase Ordering Assessment

| Current Order | Correct? | Rationale |
|---------------|----------|-----------|
| E69 → E70 | ⚠️ Can overlap | E70 (YAML DSL) can start before E69 complete — DSL is a spec, not implementation |
| E70 → E71 | ✅ Correct | E71 needs DSL + ArtifactWriter contracts from E70 |
| E71 → E72 | ✅ Correct | E72 needs FailureCode + Contract Scenarios from E71 |

**E69 → E70 overlap is safe if:**
- E70 starts with DSL specification only (no ArtifactWriter implementation)
- E70 implementation waits for E69's step result contracts

### 4.2 Actual E69 Deliverables Needed by E70

E70 needs from E69:
- `StepResult` contract schema (what does a step return?)
- RuntimeTestDriver interface (what operations are available?)
- Whether steps are sync or async

If E70 starts before E69 defines these, E70 implementation will be guesswork.

### 4.3 E71 Dependency on E70

E71 needs:
- YAML scenario format (from E70 DSL)
- ArtifactWriter to exist for producing run records

**Risk:** If E70 is delayed, E71 is blocked.

---

## 5. AI Contract Tests Assessment

### 5.1 What "AI Contract Tests" Means in Current Context

The PRD describes:
- Router: input packet correctness, output schema stability
- Narrator: prompt doesn't leak hidden state, audience split correct

### 5.2 Existing Infrastructure

**FastMock/StubModelClient** (`tests/fakes/models.py`):
- Captures `router_requests` and `narrator_requests`
- Returns configurable responses
- Can verify input packet structure
- Can check output schema against expected structure

**VCR.py** (`conftest.py`):
- Config exists but no cassettes recorded
- `record_mode: "once"` configured
- Filter headers set up for authorization redaction

### 5.3 What's Missing for AI Contract Tests

1. **Router output schema validation** — need a schema to validate against
2. **Prompt leak detection** — need to inspect prompts passed to narrator and verify no gm_only state leaks
3. **VCR cassettes** — have never been recorded, so `recorded` mode is theoretical
4. **`model_mode` parameter** — does not exist anywhere in codebase

**Assessment:** Existing FakeModel infrastructure is **partially sufficient** for `fake_contract` mode. `recorded` mode needs cassette recording first. E71 scope for "AI contract tests" is vague — needs refinement.

---

## 6. Summary of Issues by Severity

### Critical (will cause phase failure)

| Issue | Affects |
|-------|---------|
| `fuzhe_mini.json` does not exist | E72 |
| `deterministic_dice` requires source code change to `rules/dice.py` | E69 (not planned) |
| `run-scenario` CLI command not defined | E70/E72 |

### Moderate (adds scope or risk)

| Issue | Affects |
|-------|---------|
| `fake_clock` not explicitly in E69 goal | E69 |
| VCR cassettes not recorded | E71 (recorded mode) |
| `model_mode` parameter does not exist | E71 |
| Initial state setup mechanism not defined | All phases |
| Large artifact output handling not planned | E70 |

### Minor (documentation/coordination)

| Issue | Affects |
|-------|---------|
| E69→E70 overlap needs explicit coordination | E69, E70 |
| CI vs local execution not planned | E72 |
| Visibility leak tests may duplicate existing `test_visibility.py` | E71 |

---

## 7. Confidence Score

**5/10** — The current 4-phase plan covers the major structural components, but critical path items are missing or ambiguous:

1. `fuzhe_mini` fixture does not exist — this is a prerequisite for E72
2. `deterministic_dice` requires source code changes not assigned to any phase
3. Several cross-cutting concerns (fake_clock, model_mode, CI strategy) are implied but not explicitly assigned
4. AI contract test scope is vague

**Recommendation:** Before starting E69, resolve:
1. Either create `fuzhe_mini.json` or redesignate E72 to use `fuzhe.json`
2. Explicitly assign `deterministic_dice` source code changes to E69 scope
3. Define `fake_clock`, `model_mode`, and CI strategy in E69 or a preceding planning spike

---

## Appendix: Current Test Infrastructure Reference

### Existing Fixtures (`tests/conftest.py`)
- `interaction_factory` → FakeInteraction
- `context_factory` → FakeContext
- `sqlite_memory_store` → PersistenceStore
- `fast_model_mock` → FastMock (StubModelClient)
- `slow_model_mock` → SlowMock
- `error_model_mock` → ErrorMock
- `vcr_config` → VCR.py config (unused, no cassettes)

### Existing Fake Models (`tests/fakes/models.py`)
- `StubModelClient` with `call_router`, `call_narrator`, `stream_narrator`
- `router_requests` and `narrator_requests` lists for inspection
- **No VCR recording/playback** — all FakeModel returns hardcoded responses

### Existing Dice Stubbing Pattern
Tests use inline `StubPercentileRoller` classes:
```python
class StubPercentileRoller:
    def roll_percentile(self, *, value: int, ...):
        return {"kind": "percentile_check", "rolled": 27, ...}
```
No reusable `DeterministicDiceRoller` exists in source code.

### Existing `rules/dice.py`
Uses `random.randint()` directly — **not seedable**:
```python
ones = random.randint(0, 9)
tens_pool = [random.randint(0, 9) for _ in ...]
```
