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

- Current milestone: `vE.1.1`
- Primary track: `Track E - 运行控制与运维面板层`
- Goal: Build a unified runtime control service plus a local operator panel for bot/api/model health and restart flows

## Milestone vE.1.1: E1 Runtime Control Panel Foundations

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
