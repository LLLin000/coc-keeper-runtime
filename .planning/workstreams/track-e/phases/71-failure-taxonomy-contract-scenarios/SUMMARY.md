# Phase E71 Summary: Failure Taxonomy + Contract Scenarios

**Phase:** E71-01
**Milestone:** vE.2.2 — 统一 Scenario-Driven E2E 验证框架
**Status:** COMPLETE
**Tests:** 423 passing

---

## Goal

Establish FailureCode taxonomy, write visibility/reveal/AI-contract scenarios, record VCR cassettes.

---

## What was accomplished

### Task 1: FailureCode Taxonomy ✅
- Created `src/dm_bot/testing/failure_taxonomy.py` with 16 FailureCode values and `Failure` dataclass
- All failure modes classified: `PHASE_TRANSITION_MISMATCH`, `VISIBILITY_LEAK`, `REVEAL_POLICY_VIOLATION`, etc.
- `ScenarioRunner` imports from `failure_taxonomy`

### Task 2: test_visibility.py Coverage Audit ✅
- Audited `tests/orchestrator/test_visibility.py` — found 3 coverage gaps
- Added audit doc: `visibility-coverage-audit.md`
- Identified: no gm_only leak test, no audience split test, no phase-gate test

### Task 3: Visibility Leak Scenarios ✅
- `tests/scenarios/contract/visibility/scen_no_gmonly_to_player.yaml` — player must NOT see gm_only state
- `tests/scenarios/contract/visibility/scen_gmonly_reaches_kp.yaml` — KP must see gm_only state
- `tests/scenarios/contract/visibility/scen_awaiting_ready_visibility.yaml` — visibility gated by phase

### Task 4: Reveal Policy Scenarios ✅
- `tests/scenarios/contract/reveal/scen_wrong_path_no_premature_reveal.yaml`
- `tests/scenarios/contract/reveal/scen_investigation_before_reveal.yaml`

### Task 5: AI Contract Tests ✅
- `tests/test_ai_contract.py` — 5 pytest tests verifying:
  - Router packet structure (valid request objects)
  - Narrator no gm_only leak in prompts
  - Audience split correctness (KP vs public outputs)

### Task 6: VCR Cassettes ✅
- `tests/cassettes/router/router_sample.yaml` — recorded live Ollama router call
- `tests/cassettes/narrator/narrator_sample.yaml` — recorded live Ollama narrator call
- `src/dm_bot/testing/cassette.py` — record/load functions for cassette management

### Task 7: API Model Mode ✅
- Added `API = "api"` to `ModelMode` enum in `scenario_dsl.py`
- Added `ApiModelClient` in `tests/fakes/models.py` — uses `DM_BOT_API_BASE_URL` / `DM_BOT_API_KEY` env vars
- Added `api` mode branch in `runtime_driver.py`

---

## Files changed

```
src/dm_bot/testing/failure_taxonomy.py        (new, 16 FailureCode + Failure dataclass)
src/dm_bot/testing/cassette.py               (new, record/load cassette)
src/dm_bot/testing/scenario_dsl.py            (ModelMode.API added)
src/dm_bot/testing/runtime_driver.py          (api mode + ApiModelClient import)
tests/fakes/models.py                         (ApiModelClient added)
tests/test_ai_contract.py                      (new, 5 AI contract tests)
tests/scenarios/contract/visibility/           (3 YAML scenarios)
tests/scenarios/contract/reveal/              (2 YAML scenarios)
tests/cassettes/router/router_sample.yaml     (recorded cassette)
tests/cassettes/narrator/narrator_sample.yaml (recorded cassette)
```

---

## Verification

```
uv run pytest -q  →  423 passed, 3 warnings
uv run python -m dm_bot.main smoke-check  →  (run to verify)
```
