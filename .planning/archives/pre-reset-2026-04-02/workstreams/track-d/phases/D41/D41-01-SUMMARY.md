---
phase: D41
plan: 01
status: complete
started: 2026-03-31
completed: 2026-03-31
---

# D41-01 Summary: Archive Card Redesign

## What Was Built

Added `card_view()` method to `InvestigatorArchiveProfile` that returns archive data as 6 visual sections with emoji stat indicators, replacing the plain text `detail_view()` dump in `/profile_detail`.

## Changes Made

### src/dm_bot/coc/archive.py
- Added `card_view()` method returning `list[tuple[str, str]]` — 6 sections:
  1. 📋 调查员档案 — header with name, occupation, age, status, **长期档案** label
  2. 🏷️ 身份 — concept, birthplace, residence, family, education
  3. 💼 人物 — occupation detail, specialty, career arc
  4. 🎭 塑造 — 13 personality/background fields
  5. 📊 数值 — 8 attributes + emoji stats: 🧠 SAN, ❤️ HP, 💧 MP, 🍀 LUCK
  6. 📚 技能与收束 — favored/occupation/interest skills, adjustments, rules note
- Each section under 1024 chars (Discord embed field limit)
- Existing `detail_view()` preserved unchanged for backward compatibility

### src/dm_bot/discord_bot/commands.py
- `profile_detail` handler now calls `profile.card_view()` instead of `profile.detail_view()`
- Sends each section as a separate ephemeral message (first via response, rest via followup)
- Section titles rendered as bold prefix: `**{title}**\n{content}`

### tests/test_v18_archive_builder.py
- Added 5 new tests:
  - `test_card_view_returns_six_sections` — verifies 6 (title, content) tuples
  - `test_card_view_sections_under_discord_limit` — all sections < 1024 chars
  - `test_card_view_has_emoji_stats` — ❤️ HP, 🧠 SAN, 💧 MP, 🍀 LUCK present
  - `test_card_view_has_archive_label` — "长期档案" in header
  - `test_card_view_preserves_detail_view` — detail_view unchanged
- Updated `test_profile_detail_command_renders_investigator_card_sections` to check all messages (response + followup)

## Requirements Addressed

| Requirement | Status |
|-------------|--------|
| PRESENT-01: card_view() with emoji indicators | ✅ |
| PRESENT-02: sections under 1024 chars | ✅ |
| PRESENT-03: 长期档案 label, campaign state separate | ✅ |

## Verification

- `uv run pytest -q` — 813 passed
- `uv run python -m dm_bot.main smoke-check` — passed
- All 5 new card_view tests pass
- All existing tests pass (no regressions)

## Design Notes

- `card_view()` returns `list[tuple[str, str]]`, not Discord-specific format — reusable by future Activity UI (D43 ACTIVITY-01)
- Campaign-local state (SAN, HP, MP, Luck from InvestigatorPanel) intentionally NOT included in card_view — shown separately via status_me / session panels per PRESENT-03
- `detail_view()` preserved for backward compatibility and admin/debug use
