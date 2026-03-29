# Phase 60: Test Infrastructure & Process Health - Context

**Status:** Planned
**Phase Directory:** `.planning/workstreams/track-e/phases/60-test-infrastructure`
**Primary Goal:** Establish the shared test infrastructure foundation so later Track E scenario phases can add reliable Discord, model, narration, and end-to-end coverage without rebuilding fixtures per test file.

## Why This Phase Exists

Track E vE.2.1 is explicitly a scenario-based reliability milestone. The roadmap already defines Phase 60 as the foundation layer for the rest of the milestone:

- FakeInteraction factory
- model mock fixtures
- VCR.py replay setup
- pytest-bdd scaffolding

Without this base layer, the later command/orchestrator/narration/persistence phases will keep duplicating Discord mocks, model stubs, and scenario setup code.

## Inputs Read For This Context

- `.planning/workstreams/track-e/ROADMAP.md`
- `.planning/workstreams/track-e/STATE.md`
- `.planning/workstreams/track-e/codebase-architecture.md`
- `.planning/workstreams/track-e/test-coverage-survey.md`
- `.planning/workstreams/track-e/research-test-strategy.md`

## Current Codebase Signals

### Existing coverage already proves the need for shared fixtures

- `tests/test_ready_commands.py` uses ad hoc `MagicMock` + `AsyncMock` interaction setup.
- `tests/test_gameplay_integration.py`, `tests/test_phase2_integration.py`, and `tests/test_investigator_panels.py` each define their own `FakeInteraction` classes.
- `tests/test_dual_model_orchestration.py` and `tests/test_narration_service.py` use one-off model stub classes instead of a shared fixture contract.
- `tests/test_natural_message_runtime.py` currently uses temp-file SQLite persistence, but Track E wants a tighter isolation rule for scenario infrastructure.

### Architecture boundaries this phase must support

From `codebase-architecture.md`, the main scenario path spans:

1. Discord bot command/message entry
2. Session/orchestrator routing
3. Rules/adventure resolution
4. persistence save/load
5. narration generation and streaming

Phase 60 should not try to fully test those layers yet. It should only provide reusable testing primitives that later phases can consume.

## Research Findings To Carry Forward

1. **FakeInteraction factory** should replace repeated hand-written interaction/context mocks and provide nested response/followup/channel/user defaults.
2. **Model mocks need exactly three standard modes**:
   - `FastMock` — immediate successful response
   - `SlowMock` — delayed response for timeout/race-window coverage
   - `ErrorMock` — API failure / upstream exception path
3. **VCR.py** should record and replay narration-facing model responses so prompt/response handling can be regression-tested deterministically.
4. **pytest-bdd** should scaffold Gherkin scenarios for combat/investigation flows so later scenario plans can express user journeys in plain language.
5. **All tests should use in-memory SQLite for isolation** as the default infrastructure rule for scenario tests.

## Constraints For The Plan

- Keep this phase focused on infrastructure, not full scenario implementation.
- Prefer shared test utilities under `tests/` over production-only abstractions unless production code must be adjusted to support test isolation.
- Make acceptance checks grep-verifiable where possible.
- Ensure later phases can import fixtures instead of re-declaring local stubs.
- Keep concrete file targets and commands explicit so an executor can implement without rediscovering structure.

## Expected Outputs From Phase 60

- shared Discord interaction/context factory utilities
- shared model mock fixtures covering fast/slow/error paths
- baseline VCR.py config and first cassette-backed narration replay test
- pytest-bdd config, feature directory, and starter step definitions
- test fixture path for in-memory SQLite-backed scenario isolation

## Success Shape

After this phase, later Track E plans should be able to say:

- “Use `fake_interaction()` instead of building local Discord mocks.”
- “Use `fast_model_mock`, `slow_model_mock`, or `error_model_mock` instead of local stub clients.”
- “Add scenario `.feature` files under `tests/features/` with shared BDD steps already wired.”
- “Use the standard in-memory persistence fixture instead of ad hoc temp DB setup.”
