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

- **Duration:** 25 min
- **Started:** 2026-03-29T14:35:00Z
- **Completed:** 2026-03-29T15:00:00Z
- **Tasks:** 3
- **Files modified:** 14 (6 created, 8 modified)

## Accomplishments

- Created `tests/fakes/discord.py` with `FakeResponse`, `FakeFollowup`, `fake_user`, `fake_channel`, `fake_guild`, `fake_interaction`, `fake_context`
- Created `tests/fakes/models.py` with `StubModelClient`, `FastMock`, `SlowMock`, `ErrorMock`
- Created `tests/conftest.py` with 8 shared fixtures
- Created `tests/features/combat_round.feature` with Gherkin scenario
- Created `tests/bdd/test_combat_round_bdd.py` with pytest-bdd step definitions
- Added `pytest-bdd>=8.0.0` and `vcrpy>=6.0.0` to dev dependencies
- Modified `PersistenceStore` to accept `str | Path`
- Migrated 6 test files to use shared fakes
- **403 tests pass, 1 skipped, no regressions**

## Task Commits

Each task was committed atomically:

1. **Task 1: Shared FakeInteraction and in-memory fixtures** - `ce4204c` (test)
2. **Task 2: VCR.py and pytest-bdd scaffolding** - `31c6c0e` (test)
3. **Task 3: Migrate existing tests** - `d1da372` (test)

## Files Created/Modified

**Created:**
- `tests/fakes/__init__.py` - Package marker
- `tests/fakes/discord.py` - FakeResponse (AsyncMock-based), FakeFollowup, fake_interaction, fake_context
- `tests/fakes/models.py` - StubModelClient, FastMock, SlowMock, ErrorMock
- `tests/conftest.py` - interaction_factory, context_factory, sqlite_memory_store, sqlite_memory_path, fast_model_mock, slow_model_mock, error_model_mock, vcr_config
- `tests/features/combat_round.feature` - Gherkin scenario for combat round
- `tests/bdd/test_combat_round_bdd.py` - pytest-bdd step definitions (stubbed)

**Modified:**
- `src/dm_bot/persistence/store.py` - Constructor accepts `str | Path`
- `pyproject.toml` - Added pytest-bdd, vcrpy, pythonpath
- `tests/test_ready_commands.py` - Migrated to fake_interaction
- `tests/test_gameplay_integration.py` - Migrated to fake_interaction
- `tests/test_investigator_panels.py` - Migrated to fake_interaction
- `tests/test_lobby_flow.py` - Migrated to fake_interaction
- `tests/test_dual_model_orchestration.py` - Migrated to FastMock
- `tests/test_narration_service.py` - Migrated to FastMock, updated narrator_requests

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

## Acceptance Criteria Verified

- `grep -R "def fake_interaction" tests/fakes/discord.py` ✓
- `grep -R "def fake_context" tests/fakes/discord.py` ✓
- `grep -R "@pytest.fixture" tests/conftest.py` ✓ (8 fixtures)
- `grep -R "sqlite_memory_store" tests/conftest.py` ✓
- `grep -R "class FastMock" tests/fakes/models.py` ✓
- `grep -R "class SlowMock" tests/fakes/models.py` ✓
- `grep -R "class ErrorMock" tests/fakes/models.py` ✓
- `grep -n "pytest-bdd" pyproject.toml` ✓
- `grep -n "vcrpy" pyproject.toml` ✓
- `grep -R "Scenario:" tests/features/combat_round.feature` ✓

## Next Phase Readiness

- Shared FakeInteraction and FakeContext factories available
- FastMock, SlowMock, ErrorMock model fixtures available
- VCR.py and pytest-bdd scaffolding in place
- In-memory SQLite fixture available
- 403 tests passing, no regressions
- Ready for next phase in Track E

---
*Phase: 60-test-infrastructure*
*Completed: 2026-03-29*
