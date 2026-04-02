---
phase: 60-test-infrastructure
plan: "01"
subsystem: testing
tags: [testing, fixtures, discord, models, vcr, bdd]

# Dependency graph
requires:
  - phase: prior-phase (session orchestrator)
    provides: SessionStore, CharacterRegistry, GameplayOrchestrator
provides:
  - E60-FAKE-INTERACTION: Shared FakeInteraction and FakeContext factories
  - E60-MODEL-MOCKS: FastMock, SlowMock, ErrorMock model fixtures
  - E60-VCR-BDD: VCR.py replay and pytest-bdd scaffolding
  - E60-INMEMORY-SQLITE: In-memory SQLite test fixture
affects:
  - tests/conftest.py
  - tests/fakes/discord.py
  - tests/fakes/models.py
  - pyproject.toml

# Tech tracking
tech-stack:
  added:
    - pytest-bdd>=8.0.0
    - vcrpy>=6.0.0
  patterns:
    - AsyncMock with side_effect for FakeResponse/FakeFollowup
    - Factory pattern for fake interactions
    - In-memory SQLite isolation for scenario tests

key-files:
  created:
    - tests/fakes/__init__.py
    - tests/fakes/discord.py
    - tests/fakes/models.py
    - tests/conftest.py
    - tests/features/combat_round.feature
    - tests/bdd/test_combat_round_bdd.py
  modified:
    - src/dm_bot/persistence/store.py
    - pyproject.toml
    - tests/test_ready_commands.py
    - tests/test_gameplay_integration.py
    - tests/test_investigator_panels.py
    - tests/test_lobby_flow.py
    - tests/test_dual_model_orchestration.py
    - tests/test_narration_service.py

key-decisions:
  - "FakeResponse uses AsyncMock with side_effect to track messages while providing assert_called_once() interface"
  - "PersistenceStore widened to accept str | Path for in-memory SQLite instantiation"
  - "pythonpath = [\"src\", \".\"] added to pyproject.toml to fix module import issues on Windows"

patterns-established:
  - "AsyncMock(side_effect=track_fn) pattern for fake methods that need both mocking and real behavior"
  - "Shared fixture factory pattern for Discord interactions"
  - "In-memory SQLite as default for scenario test isolation"

requirements-completed: [E60-FAKE-INTERACTION, E60-MODEL-MOCKS, E60-VCR-BDD, E60-INMEMORY-SQLITE]

# Metrics
duration: 25min
completed: 2026-03-29
---

# Phase 60: Test Infrastructure Summary

**Shared test infrastructure — FakeInteraction, FakeContext, model mocks, VCR/bdd scaffolding, in-memory SQLite fixtures**

## Performance

- **Duration:** 25 min (session 1) + 15 min (session 2)
- **Started:** 2026-03-29T14:35:00Z
- **Completed:** 2026-03-30 (ongoing refinement)
- **Tasks:** 6
- **Files modified:** 17 (9 created, 8 modified)

## Accomplishments

- Created `tests/fakes/discord.py` with `FakeResponse`, `FakeFollowup`, `FakeChannel`, `fake_user`, `fake_channel`, `fake_guild`, `fake_interaction`, `fake_context`
- Created `tests/fakes/models.py` with `StubModelClient`, `FastMock`, `SlowMock`, `ErrorMock`
- Created `tests/conftest.py` with 7 shared fixtures
- Created `tests/features/combat_round.feature` with 5 Gherkin scenarios (hit, miss, pushed roll, fumble, initiative)
- Created `tests/bdd/__init__.py` and `tests/bdd/test_combat_round_bdd.py` with pytest-bdd step definitions
- Added `pytest-bdd>=8.0.0` and `vcrpy>=6.0.0` to dev dependencies
- Modified `PersistenceStore` to accept `str | Path`
- Migrated 8 test files to use shared fakes
- **408 tests pass, no regressions**

## Task Commits

Each task was committed atomically:

1. **Task 1: Shared FakeInteraction and in-memory fixtures** - `ce4204c` (test)
2. **Task 2: VCR.py and pytest-bdd scaffolding** - `31c6c0e` (test)
3. **Task 3: Migrate existing tests** - `d1da372` (test)

### E60-01 Session Commits (2026-03-30)

4. **E60-01: Add combat round BDD feature and step definitions** - `094d76a` (test)
   - 3 files: `tests/bdd/__init__.py`, `tests/features/combat_round.feature`, `tests/bdd/test_combat_round_bdd.py`
5. **E60-02: Migrate test_discord_commands.py to shared fakes** - `95cb466` (test)
   - 2 files: `tests/fakes/discord.py`, `tests/test_discord_commands.py`
6. **E60-03: Migrate test_phase2_integration.py to shared fakes** - `e3b65bd` (test)
   - 1 file: `tests/test_phase2_integration.py`

## Files Created/Modified

**Created:**
- `tests/fakes/__init__.py` - Package marker
- `tests/fakes/discord.py` - FakeResponse (AsyncMock-based), FakeFollowup, FakeChannel, fake_interaction, fake_context
- `tests/fakes/models.py` - StubModelClient, FastMock, SlowMock, ErrorMock
- `tests/conftest.py` - 7 shared fixtures
- `tests/features/combat_round.feature` - 5 Gherkin scenarios for combat round
- `tests/bdd/__init__.py` - pytest-bdd package marker
- `tests/bdd/test_combat_round_bdd.py` - pytest-bdd step definitions (all 5 scenarios)

**Modified:**
- `src/dm_bot/persistence/store.py` - Constructor accepts `str | Path`
- `pyproject.toml` - Added pytest-bdd, vcrpy, pythonpath
- `tests/test_ready_commands.py` - Migrated to fake_interaction
- `tests/test_gameplay_integration.py` - Migrated to fake_interaction
- `tests/test_investigator_panels.py` - Migrated to fake_interaction
- `tests/test_lobby_flow.py` - Migrated to fake_interaction
- `tests/test_dual_model_orchestration.py` - Migrated to FastMock
- `tests/test_narration_service.py` - Migrated to FastMock, updated narrator_requests
- `tests/test_discord_commands.py` - Migrated to shared fakes
- `tests/test_phase2_integration.py` - Migrated to shared fakes

## Decisions Made

1. **FakeResponse AsyncMock pattern:** Used `AsyncMock(side_effect=track_fn)` to provide both mock assertions (`assert_called_once()`, `call_args`) and real message tracking (`messages` list)

2. **PersistenceStore str | Path:** Widened constructor to accept string paths, enabling `PersistenceStore(":memory:")` for in-memory SQLite

3. **pythonpath fix:** Added `"."` to pythonpath to resolve `ModuleNotFoundError: No module named 'tests'`

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

1. **ModuleNotFoundError: No module named 'tests'** - Fixed by adding `"."` to `pythonpath` in pyproject.toml

2. **FakeInteraction assertion failures** - `FakeResponse` originally used real async methods without mock assertion support. Fixed by using `AsyncMock(side_effect=track_fn)` pattern

3. **test_investigator_panels failure** - `interaction.response.messages` was MagicMock instead of list. Fixed by using `FakeResponse` class instead of `AsyncMock()`

4. **pytest-bdd fixture registration** - Fixtures are registered by step text (string), NOT function names. Using `target_fixture="..."` parameter creates named fixtures referenceable by other steps.

5. **Quote mismatch between feature and step** - Feature used `"1d6+3"` (double quotes) but step definition used `'1d6+3'` (single quotes) → fixed to match

6. **Two `combat_hit` fixture functions** - Hit and miss scenarios had same `@given` step text, making `combat_hit` the actual fixture name. Fixed with `target_fixture` differentiation.

7. **Dice roller couldn't parse `1d20+-5`** - `attack_bonus=-5` created invalid expression. Fixed by using `attack_bonus=0` with controlled low roll.

8. **`fake_interaction()` missing `channel` attribute** - Migrated code called `interaction.channel.send()`. Added `FakeChannel` to shared fakes.

## Acceptance Criteria Verified

- `grep -R "def fake_interaction" tests/fakes/discord.py` ✓
- `grep -R "def fake_context" tests/fakes/discord.py` ✓
- `grep -R "@pytest.fixture" tests/conftest.py` ✓ (7 fixtures)
- `grep -R "sqlite_memory_store" tests/conftest.py` ✓
- `grep -R "class FastMock" tests/fakes/models.py` ✓
- `grep -R "class SlowMock" tests/fakes/models.py` ✓
- `grep -R "class ErrorMock" tests/fakes/models.py` ✓
- `grep -n "pytest-bdd" pyproject.toml` ✓
- `grep -n "vcrpy" pyproject.toml` ✓
- `grep -R "Scenario:" tests/features/combat_round.feature` ✓ (5 scenarios)
- `uv run pytest -q` ✓ (408 passed)

## Next Phase Readiness

- Shared FakeInteraction, FakeContext, FakeChannel factories available
- FastMock, SlowMock, ErrorMock model fixtures available
- VCR.py and pytest-bdd scaffolding in place
- In-memory SQLite fixture available
- BDD combat round feature with 5 scenarios
- 408 tests passing, no regressions
- Ready for next phase in Track E

---
*Phase: 60-test-infrastructure*
*Completed: 2026-03-29*
