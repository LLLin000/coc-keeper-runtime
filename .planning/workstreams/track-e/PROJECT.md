# Discord AI Keeper - Track E

## Track E: 运行控制与运维面板层

Owns runtime operations and operator control:
- bot/api/model lifecycle management
- startup, restart, stop, and sync orchestration
- runtime status aggregation
- smoke-check visibility
- local control panel surfaces

### Typical Work
- unified runtime control service
- CLI and web operator panel
- process and health visibility
- restart/bootstrap reliability

### Out of Scope
- Discord gameplay UX as the main goal
- archive semantics as the main goal
- module truth or narration truth as the main goal

## Active Milestone

- Current milestone: `vE.2.1`
- Primary track: `Track E - 运行控制与运维面板层`
- Goal: Build a scenario-based process reliability test suite that validates end-to-end workflows across all layers without requiring a live Discord connection

## Milestone vE.2.1: 全流程交互验证框架

**Goal:** Build a scenario-based process reliability test suite that validates end-to-end workflows across all layers without requiring a live Discord connection.

**Target features:**
- FakeInteraction factory for Discord command/adapter testing
- Model mock fixtures (instant/delay/error modes)
- VCR.py replay for deterministic narration output
- pytest-bdd Gherkin scenarios for combat and investigation flows
- fuzhe_mini.json — 4-node vertical slice for 15-turn deterministic tests
- Complete coverage of: 完整开团流程, 多人协作流程, 边界与错误恢复, 模组呈现流程

**Primary Track**
- Track E - 运行控制与运维面板层

**Secondary Impact**
- Track A - 模组与规则运行层 (fuzhe_mini extraction advances vA.1.3 extraction contract)
- Track B - 人物构建与管理层 (character flow tests validate archive lifecycle)
- Track C - Discord 交互层 (command handlers validated in isolation)

**Contracts Changed**
- Test infrastructure contracts (FakeInteraction factory interface)
- Model mock contract (FastMock/SlowMock/ErrorMock)

**Migration Notes**
- Tests do not modify production runtime; all test modules use isolated in-memory SQLite
- fuzhe_mini.json is a new fixture file, not a modification of existing runtime

**Goal:** Centralize bot, API, model, sync, and smoke-check operations behind one runtime control layer, then expose that layer through a CLI fallback and a local web control panel.

**Target features:**
- unified runtime state model
- unified control actions
- local web operator panel
- CLI fallback surface
- clear visibility into READY/SYNC/smoke-check/bootstrap failures

**Primary Track**
- Track E - 运行控制与运维面板层

**Secondary Impact**
- Track C - Discord 交互层

**Contracts Changed**
- runtime control state contract
- runtime lifecycle action contract
- operator-facing health surface

**Migration Notes**
- reuse existing `smoke-check` and `restart-system` behavior where practical
- do not replace canonical gameplay/runtime truth with panel-local state

---
*Last updated: 2026-03-28 for milestone vE.1.1 E1 Runtime Control Panel Foundations*
