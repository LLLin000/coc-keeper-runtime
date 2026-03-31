# Track E Codebase Mapping Report

**Analysis Date:** 2026-03-31
**Track:** E - Runtime Control & Operations Panel Layer
**Milestones Analyzed:** vE.1.1, vE.2.1, vE.2.2, vE.3.1 (E40-E78)

---

## Executive Summary

Track E has built a comprehensive testing and runtime control infrastructure for the Discord AI Keeper project. The track successfully delivered:

- **39 phases** across 4 milestones (E40-E78)
- **222 COC rules unit tests** + **14 E2E scenarios**
- **80 test files** covering all major subsystems
- **Complete COC 7th Edition rules engine** (6 modules)
- **Scenario-driven testing framework** with YAML DSL
- **RuntimeTestDriver** for Discord-free E2E testing

---

## 1. Built Features by Phase

### vE.1.1: Runtime Control Panel Foundations (E40-E43)

| Phase | Feature | Key Files | Status |
|-------|---------|-----------|--------|
| E40 | Runtime Control Contracts | `src/dm_bot/runtime/control_service.py` | ✅ Complete |
| E41 | CLI Control Surface | `src/dm_bot/main.py` (CLI commands) | ✅ Complete |
| E42 | Web Control Panel | `src/dm_bot/runtime/app.py` | ✅ Complete |
| E43 | Runtime Integration | `src/dm_bot/runtime/process_control.py` | ✅ Complete |

**Contracts Defined:**
- `ControlState` - Runtime state management
- `ControlActionResult` - Action outcomes
- `ProcessStatus` - Process health monitoring
- `ModelStatus` - AI model connectivity

### vE.2.1: Full Process Interaction Validation Framework (E60-E68)

| Phase | Feature | Key Files | Status |
|-------|---------|-----------|--------|
| E60 | Test Infrastructure | `tests/fakes/discord.py`, `tests/fakes/models.py` | ✅ Complete |
| E61 | Discord Command Layer | `tests/test_discord_commands.py` | ✅ Complete |
| E62 | Session/Orchestrator | `tests/test_session_phase_transitions.py` | ✅ Complete |
| E63 | Adventure Runtime | `tests/test_trigger_chains.py`, `tests/test_room_transitions_and_reveals.py` | ✅ Complete |
| E64 | Rules Engine | `tests/test_coc_rules_flow.py` | ✅ Complete |
| E65 | Character/Archive | `tests/test_character_archive_flow.py` | ✅ Complete |
| E66 | Model/Router | `tests/test_router_service_flow.py`, `tests/test_intent_classification_flow.py` | ✅ Complete |
| E67 | Narration Pipeline | `tests/test_narration_pipeline_flow.py`, `tests/test_narration_streaming_flow.py` | ✅ Complete |
| E68 | Persistence + E2E | `tests/test_e2e_15turn_scenario.py`, `tests/test_persistence_store.py` | ✅ Complete |

### vE.2.2: Unified Scenario-Driven E2E Framework (E69-E72)

| Phase | Feature | Key Files | Status |
|-------|---------|-----------|--------|
| E69 | Scenario Runner + RuntimeTestDriver | `src/dm_bot/testing/runtime_driver.py`, `src/dm_bot/testing/scenario_runner.py` | ✅ Complete |
| E70 | Scenario DSL + Artifact Writer | `src/dm_bot/testing/scenario_dsl.py`, `src/dm_bot/testing/artifact_writer.py` | ✅ Complete |
| E71 | Failure Taxonomy + Contract Scenarios | `src/dm_bot/testing/failure_taxonomy.py`, `tests/scenarios/contract/` | ✅ Complete |
| E72 | Acceptance Scenarios | `tests/scenarios/acceptance/`, `tests/scenarios/chaos/`, `tests/scenarios/recovery/` | ✅ Complete |

**Key Deliverables:**
- `RuntimeTestDriver` - Unified Discord-free test interface
- `ScenarioRunner` - YAML scenario execution engine
- `ArtifactWriter` - Test result documentation
- `FailureCode` enum - 13 standardized failure types
- `SeededDiceRoller` - Deterministic dice for reproducible tests

### vE.3.1: Character Lifecycle E2E (E73-E78)

| Phase | Feature | Key Files | Tests | Status |
|-------|---------|-----------|-------|--------|
| E73 | COC Derived Attributes | `tests/rules/coc/test_derived_attributes.py` | 75 | ✅ Complete |
| E74 | COC Combat + Insanity | `tests/rules/coc/test_combat_and_insanity.py` | 56 | ✅ Complete |
| E75 | COC Experience + Skill Catalog | `tests/rules/coc/test_experience_and_skill_catalog.py` | 91 | ✅ Complete |
| E76 | Character Creation E2E | `tests/scenarios/acceptance/scen_character_creation.yaml` | - | ✅ Complete |
| E77 | Combat + SAN E2E | `tests/scenarios/acceptance/scen_combat_san.yaml` | - | ✅ Complete |
| E78 | Skill Improvement Lifecycle | `tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml` | - | ✅ Complete |

---

## 2. COC (Call of Cthulhu) Systems

### 2.1 COC Rules Engine Modules

All located in `src/dm_bot/rules/coc/`:

#### `__init__.py` - Public API
**Exports:**
- Skills: `resolve_skill_check`, `COC_SKILLS` (80+ skills), `SuccessRank`
- Combat: `resolve_fighting_attack`, `resolve_shooting_attack`, `calculate_damage_bonus`
- Sanity: `resolve_sanity_check`, `roll_insanity_break`, `calculate_sanity_recovery`
- Magic: `resolve_spell_cast`, `COC_SPELLS` (20+ spells), `Spellbook`
- Derived: `calculate_all_derived_attributes`, `apply_age_modifiers`
- Experience: `roll_skill_improvement`, `calculate_new_session_skill_points`

#### `skills.py` - Skill System (903 lines)
**Features:**
- 80+ COC 7e skills with Chinese localization
- 9 skill categories: COMBAT, LANGUAGE, KNOWLEDGE, INTERPERSONAL, OBSERVATION, PRACTICAL, CRAFT, MAGIC, COMBAT_SPECIALTY
- Success ranks: CRITICAL, EXTREME, HARD, REGULAR, FAILURE, FUMBLE
- Bonus/penalty dice support
- Specialized skill handling (e.g., Fighting: Sword)
- Skill point allocation tables (Credit Rating → occupational points, INT → interest points)

**Key Skills:**
- Combat: fighting, shooting, brawl, dodge, throw, grapple
- Languages: 15 languages including English, Chinese, Japanese, Latin
- Knowledge: accounting, anthropology, archaeology, cthulhu_mythos, history, law, medicine, occult, politics, psychoanalysis, psychology, science
- Interpersonal: charm, fast_talk, intimidate, persuade, leadership
- Observation: listen, spot_hidden, search, track

#### `combat.py` - Combat System (692 lines)
**Features:**
- Initiative: DEX-based with random roll
- Fighting attacks: opposed check vs dodge, critical/fumble handling, impale on extreme+
- Shooting attacks: range/recoil modifiers, armor piercing
- Brawl: unarmed 1d3+DB damage
- Grapple: opposed check with self-damage on fumble
- Damage Bonus (DB): STR+SIZ based (+1d4, +1d6, +2d6)
- Build calculation: -2 to +3
- Armor absorption and penetration
- Major wound detection (HP ≤ 0)

**Combat Actions:**
```python
CombatAction.FIGHT, CombatAction.SHOOT, CombatAction.BRAWL,
CombatAction.DODGE, CombatAction.GRAPPLE, CombatAction.THROW,
CombatAction.RETREAT, CombatAction.GUARD, CombatAction.RELOAD
```

#### `sanity.py` - Sanity System (636 lines)
**Features:**
- Sanity loss tables for 25+ creature types
- Mythos gain tracking
- Insanity types: TEMPORARY (acute trauma), INDEFINITE (SAN=0)
- 70+ common phobias (Claustrophobia, Hemophobia, Nyctophobia, etc.)
- 50+ common manias (Pyromania, Kleptomania, etc.)
- 13 acute trauma responses (panic-flee, catatonic stupor, etc.)
- Sanity recovery: rest (1/session), therapy (1d6/session), real-world experiences
- Luck expenditure for sanity re-rolls

**Sanity Loss References:**
- Minor creatures: 1d6 (ghouls, deep ones, zombies)
- Greater horrors: 1d10 (Cthulhu, Nyarlathotep)
- Violence/death: 0-3

#### `magic.py` - Magic System (779 lines)
**Features:**
- 20+ spells across 7 schools (conjuration, divination, enchantment, evocation, necromancy, transmutation, general)
- Spell types: SPELL, RITUAL, SUMMONING, BINDING, SUMMONING_BINDING
- MP cost calculation (flat or percentage-based)
- Casting threshold: INT×2 + POW×2
- Spell prerequisites: required skills, Cthulhu Mythos minimum
- Spellbook management
- Creature summoning (ghouls, deep ones, byakhee, shantak, Cthulhu)

**Sample Spells:**
- Contact spells: contact_ghoul, contact_deep_one, contact_cthulhu
- Combat: energy_bolt (1d6), call_lightning (2d6)
- Utility: astral_sense, protection_circle, mind_control

#### `derived.py` - Derived Attributes (414 lines)
**Calculations:**
- Luck: POW × 5
- HP: (CON + SIZ) / 10
- MP: POW / 5
- SAN: POW × 5 (starting)
- MOV: Based on STR/DEX/SIZ comparison, age penalties (40-49: -1, 50-59: -2, etc.)
- Build: STR+SIZ bands (-2 to +3)
- Damage Bonus: STR+SIZ bands (-2 to +2d6)

**Age Modifiers (9 bands):**
- 20-29: No change
- 30-39: INT+1, EDU+1
- 40-49: STR-5, CON-10, DEX-10, APP-10, INT+2, EDU+3
- 70-79: STR-20, CON-25, DEX-25, APP-25, INT+5, EDU+10
- 90-99: STR-30, CON-35, DEX-35, APP-35, INT+7, EDU+14

#### `experience.py` - Experience System (511 lines)
**Features:**
- Skill improvement: Roll 1d100 < skill → +1d10
- Occupational skill points: Based on Credit Rating (0-40 points)
- Interest skill points: Based on INT (0-7 points)
- Character advancement tracking
- 25+ occupation skill suggestions (Antiquarian, Doctor, Police Detective, etc.)
- Build point calculation (480 standard)

### 2.2 COC Test Coverage

| Module | Test File | Tests | Coverage |
|--------|-----------|-------|----------|
| Derived Attributes | `test_derived_attributes.py` | 75 | HP, MP, SAN, LUCK, MOV, Build, DB, age modifiers, characteristic rolling, luck system |
| Combat + Insanity | `test_combat_and_insanity.py` | 56 | Initiative, fighting, shooting, brawl, grapple, armor, insanity triggers, recovery |
| Experience + Skills | `test_experience_and_skill_catalog.py` | 91 | Skill improvement, point allocation, COC_SKILLS catalog (80+), COC_SPELLS catalog (20+) |
| **Total** | | **222** | |

---

## 3. Test Infrastructure

### 3.1 Test Organization

```
tests/
├── rules/coc/              # COC rules unit tests (222 tests)
│   ├── test_derived_attributes.py
│   ├── test_combat_and_insanity.py
│   └── test_experience_and_skill_catalog.py
├── scenarios/              # E2E scenario tests (14 scenarios)
│   ├── acceptance/         # Happy path, combat, character lifecycle
│   ├── contract/           # Visibility, reveal policy, AI contracts
│   ├── chaos/              # Concurrency stress tests
│   └── recovery/           # Crash recovery, stream interrupt
├── fakes/                  # Test fixtures
│   ├── discord.py          # FakeInteraction, FakeChannel, FakeMessage
│   ├── models.py           # StubModelClient, ApiModelClient
│   └── clock.py            # FakeClock for time-based tests
├── bdd/                    # BDD-style tests
├── orchestrator/           # Orchestrator-specific tests
└── *.py                    # 60+ integration test files
```

### 3.2 Scenario Files (14 Total)

**Acceptance Scenarios (6):**
- `scen_character_creation.yaml` - Session join and ready flow
- `scen_combat_san.yaml` - Combat → SAN → insanity chain
- `scen_skill_improvement_lifecycle.yaml` - Full lifecycle with skill improvement
- `scen_fuzhe_15turn.yaml` - 15-turn fuzhe_mini adventure
- `scen_session_happy_path.yaml` - Full session lifecycle
- `scen_smoke.yaml` - Smoke check

**Contract Scenarios (4):**
- `scen_awaiting_ready_visibility.yaml`
- `scen_gmonly_reaches_kp.yaml`
- `scen_no_gmonly_to_player.yaml`
- `scen_investigation_before_reveal.yaml`
- `scen_wrong_path_no_premature_reveal.yaml`

**Chaos Scenarios (1):**
- `scen_chaos_lobby.yaml` - 5 concurrent users stress test

**Recovery Scenarios (2):**
- `scen_crash_recovery.yaml` - Mid-scenario crash + restart
- `scen_stream_interrupt.yaml` - Streaming interruption + resume

### 3.3 Testing Framework Components

**RuntimeTestDriver** (`src/dm_bot/testing/runtime_driver.py`):
- Discord-free test interface
- Supports 4 model modes: fake_contract, recorded, live, api
- Seeded dice for deterministic testing
- State snapshotting and DB inspection
- Command execution: `run_command()`, `send_message()`
- Crash/stream interrupt simulation

**ScenarioRunner** (`src/dm_bot/testing/scenario_runner.py`):
- YAML scenario parsing and execution
- Step-by-step execution with phase tracking
- Assertion checking (phase_timeline, state, visible)
- Artifact generation (run.json, summary.md, timeline.json)

**Failure Taxonomy** (`src/dm_bot/testing/failure_taxonomy.py`):
```python
FailureCode:
    PHASE_TRANSITION_MISMATCH
    COMMAND_GATE_FAILURE
    REVEAL_POLICY_VIOLATION
    VISIBILITY_LEAK
    RULE_RESOLUTION_MISMATCH
    SESSION_STATE_MISMATCH
    PERSISTENCE_RECOVERY_FAILURE
    STREAM_RECOVERY_FAILURE
    INTENT_ROUTING_MISMATCH
    NARRATION_CONTRACT_VIOLATION
    CONCURRENCY_INVARIANT_FAILURE
    SCENARIO_TIMEOUT
    UNSUPPORTED_TEST_CONTRACT
```

**ArtifactWriter** (`src/dm_bot/testing/artifact_writer.py`):
- Generates machine-readable (JSON) and human-readable (Markdown) artifacts
- Outputs: run.json, summary.md, timeline.json, outputs_by_actor/, state_before.json, state_after.json

---

## 4. Gaps and Missing Features

### 4.1 COC Rules Gaps

| Feature | Status | Notes |
|---------|--------|-------|
| Pushed Rolls | ⚠️ Partial | Framework exists but limited test coverage |
| Firearms (detailed) | ⚠️ Partial | Basic shooting, missing burst fire, malfunctions |
| Chase Rules | ❌ Missing | COC 7e chase mechanics not implemented |
| Vehicle Combat | ❌ Missing | Drive Auto, Pilot integration |
| Poison/Disease | ❌ Missing | COC 7e Chapter 8 |
| Book Tomes | ⚠️ Partial | Basic sanity loss, no reading mechanics |
| Creature Stats | ❌ Missing | No bestiary with creature stats |
| Equipment/Weapons | ⚠️ Partial | Basic weapon damage strings only |
| Character Sheets | ⚠️ Partial | Panels exist but not fully integrated |

### 4.2 Discord Bot Gaps

| Feature | Status | Location |
|---------|--------|----------|
| Visibility Dispatcher | ⚠️ Stub | `src/dm_bot/discord_bot/visibility_dispatcher.py` - 3 TODOs |
| DM Support | ⚠️ Partial | Framework exists, not fully wired |
| Channel Enforcement | ✅ Complete | `src/dm_bot/discord_bot/channel_enforcer.py` |
| Streaming | ✅ Complete | `src/dm_bot/discord_bot/streaming.py` |

**TODOs Found:**
- `visibility_dispatcher.py:89` - "Send to actual Discord channel when integrated with runtime"
- `visibility_dispatcher.py:133` - "Fetch user and send DM when integrated with runtime"
- `visibility_dispatcher.py:168` - "Identify group members and send DMs when integrated with runtime"

### 4.3 Integration Gaps

| Feature | Status | Notes |
|---------|--------|-------|
| Archive Repository | ⚠️ Stub | Referenced in RuntimeTestDriver but not fully implemented |
| Character Builder | ⚠️ Stub | Referenced but not wired |
| COC Assets | ⚠️ Stub | `coc_assets` is None in RuntimeTestDriver |
| Skill Usage Tracking | ❌ Missing | Combat doesn't track which skills were used for improvement |
| Automatic Skill Improvement | ❌ Missing | Post-session improvement phase not implemented |
| VCR Cassettes | ⚠️ Partial | Framework exists, limited recordings |

### 4.4 Test Coverage Gaps

| Area | Coverage | Gap |
|------|----------|-----|
| Discord Commands | Good | 60+ tests |
| Session/Orchestrator | Good | Phase transitions tested |
| Adventure Runtime | Good | Trigger chains, room transitions |
| COC Rules | Excellent | 222 tests |
| Narration Pipeline | Good | Streaming flow tested |
| Model/Router | Good | Intent classification tested |
| Persistence | Good | SQLite recovery tested |
| **Combat Integration** | ⚠️ Partial | Combat scenarios exist but limited combat state assertions |
| **SAN Integration** | ⚠️ Partial | SAN loss triggers exist but cross-system chain not fully tested |
| **Character Import** | ⚠️ Partial | Dicecloud source exists, other sources missing |

### 4.5 Documentation Gaps

- Combat state machine documentation
- SAN trigger integration guide
- Skill improvement workflow
- Character builder usage
- Archive repository API

---

## 5. Recommendations

### 5.1 High Priority

1. **Implement Skill Usage Tracking**
   - Track which skills are used during combat
   - Store in session state for post-session improvement
   - Add assertions to E78 scenario

2. **Complete Visibility Dispatcher**
   - Implement actual Discord channel sending
   - Wire DM support
   - Add visibility leak detection tests

3. **Add Creature Stats/Bestiary**
   - Create creature stats for common COC monsters
   - Integrate with combat system
   - Add to fuzhe_mini adventure

### 5.2 Medium Priority

4. **Implement Chase Rules**
   - COC 7e Chapter 6 chase mechanics
   - Add to rules engine
   - Create scenario tests

5. **Complete Archive Repository**
   - Implement full CRUD operations
   - Wire into RuntimeTestDriver
   - Add E2E tests

6. **Add More Acceptance Scenarios**
   - Full adventure playthrough
   - Multi-session campaign
   - Character death and retirement

### 5.3 Low Priority

7. **Expand Magic System**
   - More spells from COC 7e
   - Ritual casting time tracking
   - Spell learning mechanics

8. **Add Equipment System**
   - Weapon/armor database
   - Equipment effects on combat
   - Inventory management

---

## 6. File Index

### Key Source Files

**COC Rules:**
- `src/dm_bot/rules/coc/__init__.py` - Public API
- `src/dm_bot/rules/coc/skills.py` - 80+ skills
- `src/dm_bot/rules/coc/combat.py` - Combat resolution
- `src/dm_bot/rules/coc/sanity.py` - Sanity system
- `src/dm_bot/rules/coc/magic.py` - Spells and casting
- `src/dm_bot/rules/coc/derived.py` - Derived attributes
- `src/dm_bot/rules/coc/experience.py` - Skill improvement

**Testing Framework:**
- `src/dm_bot/testing/runtime_driver.py` - RuntimeTestDriver
- `src/dm_bot/testing/scenario_runner.py` - Scenario execution
- `src/dm_bot/testing/scenario_dsl.py` - YAML DSL parser
- `src/dm_bot/testing/artifact_writer.py` - Test artifacts
- `src/dm_bot/testing/failure_taxonomy.py` - Failure codes
- `src/dm_bot/testing/step_result.py` - Step results
- `src/dm_bot/rules/dice.py` - SeededDiceRoller

**Discord Bot:**
- `src/dm_bot/discord_bot/commands.py` - BotCommands
- `src/dm_bot/discord_bot/client.py` - Discord client
- `src/dm_bot/discord_bot/visibility_dispatcher.py` - Visibility (has TODOs)
- `src/dm_bot/discord_bot/streaming.py` - Streaming transport

**Orchestrator:**
- `src/dm_bot/orchestrator/session_store.py` - Session management
- `src/dm_bot/orchestrator/turns.py` - Turn coordination
- `src/dm_bot/orchestrator/turn_runner.py` - Turn execution
- `src/dm_bot/orchestrator/gameplay.py` - Gameplay orchestration
- `src/dm_bot/orchestrator/visibility.py` - Visibility management

### Key Test Files

**COC Rules:**
- `tests/rules/coc/test_derived_attributes.py` - 75 tests
- `tests/rules/coc/test_combat_and_insanity.py` - 56 tests
- `tests/rules/coc/test_experience_and_skill_catalog.py` - 91 tests

**Scenarios:**
- `tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml` - E78
- `tests/scenarios/acceptance/scen_combat_san.yaml` - E77
- `tests/scenarios/acceptance/scen_character_creation.yaml` - E76
- `tests/scenarios/acceptance/scen_fuzhe_15turn.yaml`
- `tests/scenarios/chaos/scen_chaos_lobby.yaml`
- `tests/scenarios/recovery/scen_crash_recovery.yaml`

---

## 7. Metrics Summary

| Metric | Value |
|--------|-------|
| Total Phases | 39 (E40-E78) |
| Completed Phases | 39 (100%) |
| Test Files | 80 |
| COC Unit Tests | 222 |
| E2E Scenarios | 14 |
| COC Skills | 80+ |
| COC Spells | 20+ |
| Source Files | 70+ |
| TODO Comments | 4 |

---

*Report generated: 2026-03-31*
*Track E Status: vE.3.1 Complete*
