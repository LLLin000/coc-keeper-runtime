# Test Coverage Survey (vE.2.1)

## Overview
This document maps the existing test coverage across the Discord AI Keeper codebase and identifies critical gaps that need to be addressed in the vE.2.1 scenario-based reliability tracks.

## Test Coverage Map

| Test File | Lines | What it Tests | Coverage Assessment |
|-----------|-------|---------------|---------------------|
| `test_ready_commands.py` | 125 | `/select_profile`, `/ready` command responses & basic validation | Good unit coverage for command logic. |
| `test_ready_gate.py` | 180 | `SessionStore` ready/profile selection gates & logic | Strong unit coverage for edge cases in the ready gate. |
| `test_join_gates.py` | 78 | Campaign join restrictions (duplicates, unbound channels) | Good unit coverage for join lifecycle. |
| `test_persistence_store.py` | 280 | Save/Load of campaigns, sessions, archive profiles | Strong coverage for state recovery and legacy migration. |
| `test_identity_models.py` | 88 | Pydantic models for members, characters, roles | Solid model validation. |
| `test_kp_ops_renderer.py` | 366 | Rendering of KP Ops panel (overview, detailed, history) | High density coverage for the KP dashboard UI. |
| `test_visibility.py` | 104 | Building visibility snapshots for players and KP | Good coverage for information filtering. |
| `test_turns.py` | 88 | Turn serialization and session member tracking | Good unit coverage for the turn coordinator. |
| `test_phase2_integration.py` | 183 | End-to-end turn flow (Router -> Rules -> Narrator) | Good integration for a single turn. |
| `test_gameplay_integration.py` | 282 | Adventure loading, scene progression, interactables | Strong coverage for Adventure Runtime logic. |
| `test_natural_message_runtime.py` | 443 | Natural message handling, combat turns, guidance prompts | Extensive coverage for message routing and context-aware replies. |
| `test_commands.py` | 307 | Slash command orchestration and session binding | Broad coverage for command-to-orchestrator flow. |
| `test_intent_routing.py` | 450 | Message intent classification, buffering, and handling | Very strong coverage for the routing/buffering logic. |
| `test_round_collection.py` | 221 | Multi-player action collection and phase transitions | Good coverage for the "Wait for All" logic. |
| `test_smoke_check.py` | 25 | Log marker detection for system health | Basic utility coverage. |
| `test_runtime_control_service.py` | 96 | Process management, model status, and control actions | Good coverage for the local admin service. |
| `test_restart_system.py` | 27 | Log-based bootstrap detection | Basic utility coverage. |
| `test_main_runtime.py` | 61 | CLI command dispatching | Basic CLI coverage. |
| `test_health.py` | 69 | FastAPI health and control panel endpoints | Good coverage for the observability API. |
| `test_v18_archive_builder.py` | 683 | Conversational character building, archive projection | Deep coverage for the character creation lifecycle. |
| `test_channel_enforcer.py` | 154 | Command permissions across different channel types | Good coverage for Discord governance. |
| `test_dual_model_orchestration.py` | 273 | Router/Narrator coordination and context injection | Strong coverage for AI orchestration. |
| `test_complex_graphs.py` | 35 | Story nodes and knowledge logs in complex modules | Basic coverage for Track A logic. |
| `test_investigator_panels.py` | 104 | Panel updates, private knowledge, and sheet display | Good coverage for player-facing data. |
| `test_narration_service.py` | 109 | Narration prompts and streaming | Good coverage for the output layer. |
| `test_coc_prompts.py` | 54 | Keeper-focused prompt structure | Basic prompt validation. |
| `test_coc_assets.py` | 54 | Asset library and rulebook snippets | Basic asset management coverage. |
| `test_rules_engine.py` | 188 | COC checks, sanity rolls, and D&D attack rolls | Strong coverage for deterministic rules. |
| `test_adventure_loader.py` | 208 | Loading formal modules and room graph extraction | Good coverage for module ingestion. |
| `test_message_filters.py` | 19 | OOC and social message classification | Basic filter coverage. |
| `test_discord_client_runtime.py` | 8 | Bot instance initialization | Minimal coverage. |

## vE.2.1 Scenario Cross-Reference

| Scenario Category | Existing Coverage | Gap Summary |
|-------------------|-------------------|-------------|
| **1. 完整开团流程** (Full Session Lifecycle) | Unit tests for bind, join, ready, load. Integration for single turns. | Missing a "Day 1 to End" long-running integration test that handles the transition from lobby -> ready-up -> game start -> first scene. |
| **2. 多人协作流程** (Multi-player Coordination) | `test_round_collection` covers action gathering. `test_intent_routing` covers buffering. | Missing "Race Condition" tests where multiple players act simultaneously during a state transition (e.g., someone joins while a round is resolving). |
| **3. 边界与错误恢复** (Boundaries & Recovery) | `test_persistence_store` covers save/load. `test_smoke_check` covers health. | Missing tests for "Half-state Recovery" (e.g., bot crashes mid-turn narration, can it resume or cleanly restart that specific turn?). |
| **4. 模组呈现流程** (Module Presentation) | `test_gameplay_integration` covers room/scene changes. | Missing tests for "Multi-path Branching" where player actions in Scene A permanently lock out Scene B via Trigger Tree consequences. |

## Gap Analysis & Recommendations

### Identified Gaps
1. **Long-running State Transitions**: Most tests focus on a single command or a single turn. There is no automated coverage for a sequence of 10+ turns across different locations with persisting consequences.
2. **Discord API Resilience**: Tests use `MagicMock` or `FakeInteraction`. We lack tests for "Rate Limited" scenarios or "Message Edit Failures" during streaming.
3. **Multi-User Edge Cases**: While round collection is tested, the interplay between intent classification and state-locked channels (e.g., trying to use `/sheet` while a combat round is resolving) needs more "Governance" level testing.
4. **AI Output Hallucination Recovery**: No tests for when the Router returns valid JSON but invalid logical tool calls (e.g., calling a tool that doesn't exist for the current adventure).

### Recommendations for vE.2.1 Scenarios
1. **Scenario: The "Clean Start" (完整开团流程)**: Create a test that simulates the first 15 minutes of a campaign: Bind -> Join (3 players) -> Character Builder (for 1 player) -> Ready-up -> Load Mansion -> Move to Hall -> First Action.
2. **Scenario: The "Interrupted Narrator" (边界与错误恢复)**: Simulate a process crash during a streaming narration and verify that the session state remains canonical and recoverable upon restart.
3. **Scenario: The "Consequence Chain" (模组呈现流程)**: In `mad_mansion`, trigger a sequence of actions that leads to a specific Ending, verifying that all global flags were updated correctly along the way.
4. **Scenario: The "Chaos Lobby" (多人协作流程)**: Have 5 users spamming a mix of OOC, commands, and actions during a high-latency AI response window to verify the message buffer and routing priority hold firm.
