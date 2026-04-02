---
phase: D43
plan: 01
subsystem: Presentation Layer
tags: [presentation, card-section, card-renderer, discord, activity-ready]
requirements: [ACTIVITY-01, ACTIVITY-02]
dependency:
  requires: [D41-archive-card-redesign]
  provides: [reusable-card-sections, swappable-renderers]
  affects: [archive.py, commands.py, presentation.py]
tech-stack:
  added: [dataclass, Protocol, Literal]
  patterns: [protocol-based-design, dataclass-contracts, renderer-pattern]
key-files:
  created: [src/dm_bot/coc/presentation.py, tests/test_presentation.py]
  modified: [src/dm_bot/coc/archive.py, src/dm_bot/discord_bot/commands.py, tests/test_v18_archive_builder.py]
decisions:
  - "CardSection uses dataclass not Pydantic model (lightweight, no validation overhead)"
  - "CardRenderer uses Protocol (structural subtyping) for swappable renderers"
  - "DiscordCardRenderer matches existing **title**\\ncontent format (backward compatible)"
  - "All archive sections marked visibility='public' (archive data is player-visible)"
  - "order field 0-5 for consistent section ordering across renderers"
metrics:
  duration: ~3 minutes
  completed: 2026-03-31
  tests_added: 7
  tests_modified: 5
  total_tests: 820 passed
---

# Phase D43 Plan 01: Activity-Ready Presentation Contracts Summary

**One-liner:** CardSection dataclass + CardRenderer protocol decouple archive data from Discord formatting, enabling reusable card sections for future Activity UI panels.

## Objective

Define presentation contracts (CardSection, CardRenderer) that decouple archive data from Discord-specific formatting, enabling reuse by future Discord Activity UI panels.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create CardSection dataclass, CardRenderer protocol, DiscordCardRenderer | 3a37394 | presentation.py, test_presentation.py |
| 2 | Refactor card_view() to return list[CardSection] | 4f4d3f2 | archive.py |
| 3 | Update commands.py to use DiscordCardRenderer | 772226e | commands.py, test_v18_archive_builder.py |

## Verification Results

- ✅ `uv run pytest tests/test_presentation.py -x` — 7 passed
- ✅ `uv run pytest tests/test_v18_archive_builder.py -x -q` — 21 passed
- ✅ `uv run pytest tests/coc/test_builder.py -x -q` — 7 passed
- ✅ `uv run pytest tests/test_discord_commands.py -x -q` — 10 passed
- ✅ `uv run python -m dm_bot.main smoke-check` — 820 passed
- ✅ `uv run pytest -q` — 820 passed

## Success Criteria

- [x] ACTIVITY-01: CardSection dataclass exists with title, content, visibility, order fields — not hardcoded to Discord embed format
- [x] ACTIVITY-01: CardRenderer protocol enables future ActivityCardRenderer without changing archive.py
- [x] ACTIVITY-01: card_view() returns list[CardSection] — reusable by any renderer
- [x] ACTIVITY-02: presentation.py defines only formatting contracts — no canonical state or data ownership
- [x] DiscordCardRenderer produces identical output to previous implementation (backward compatible)
- [x] All tests pass (uv run pytest -q) — 820 passed
- [x] Smoke check passes (uv run python -m dm_bot.main smoke-check) — 820 passed

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None. All CardSection fields are fully wired with real data from InvestigatorArchiveProfile.

## Self-Check: PASSED

- [x] src/dm_bot/coc/presentation.py exists
- [x] tests/test_presentation.py exists
- [x] Commits 3a37394, 4f4d3f2, 772226e exist in git log
- [x] All 820 tests pass
- [x] Smoke check passes
