---
phase: D41
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/coc/archive.py
  - src/dm_bot/discord_bot/commands.py
  - tests/test_v18_archive_builder.py
autonomous: true
requirements: [PRESENT-01, PRESENT-02, PRESENT-03]
user_setup: []

must_haves:
  truths:
    - "/profile_detail outputs card-like format with visual sections and emoji stat indicators"
    - "Long-lived archive sections clearly labeled as 长期档案"
    - "Each card section stays under 1024 characters (Discord embed field limit)"
    - "Campaign-local state (SAN, HP, MP, Luck from InvestigatorPanel) shown separately from archive stats"
  artifacts:
    - path: "src/dm_bot/coc/archive.py"
      provides: "card_view() method on InvestigatorArchiveProfile"
      contains: "def card_view"
    - path: "src/dm_bot/discord_bot/commands.py"
      provides: "profile_detail handler uses card_view()"
      contains: "card_view()"
    - path: "tests/test_v18_archive_builder.py"
      provides: "Tests for card_view format and Discord constraints"
      contains: "card_view"
  key_links:
    - from: "src/dm_bot/discord_bot/commands.py"
      to: "src/dm_bot/coc/archive.py"
      via: "profile.card_view() call in profile_detail handler"
      pattern: "profile\\.card_view\\(\\)"
    - from: "src/dm_bot/coc/archive.py"
      to: "Discord embed constraints"
      via: "Section length enforcement in card_view"
      pattern: "1024|card_view"
---

<objective>
Redesign archive profile display from plain text dump to investigator card format with emoji indicators, visual sections, and Discord-compliant sizing.

Purpose: Make /profile_detail feel like reading a physical investigator card, not a bot text dump. Long-lived archive data visually distinguished from campaign-local state.
Output: card_view() method on InvestigatorArchiveProfile, updated /profile_detail handler, tests for card format.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/workstreams/track-d/STATE.md
@.planning/workstreams/track-d/ROADMAP.md
@.planning/workstreams/track-d/REQUIREMENTS.md

@src/dm_bot/coc/archive.py
@src/dm_bot/discord_bot/commands.py
@tests/test_v18_archive_builder.py
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add card_view() method to InvestigatorArchiveProfile</name>
  <files>src/dm_bot/coc/archive.py, tests/test_v18_archive_builder.py</files>
  <behavior>
    - card_view() returns list of (section_title, section_content) tuples
    - Each section_content is under 1024 characters (Discord embed field limit)
    - Stats section uses emoji indicators: ❤️ HP, 🧠 SAN, 💧 MP, 🍀 LUCK
    - Archive sections labeled with "长期档案" marker
    - Sections: 调查员档案 (header), 身份, 人物, 塑造, 数值, 技能与收束
    - Existing detail_view() preserved (not replaced) for backward compatibility
  </behavior>
  <action>
    Add `card_view()` method to `InvestigatorArchiveProfile` in src/dm_bot/coc/archive.py.

    Design decisions:
    - Returns `list[tuple[str, str]]` — each tuple is (section_title, section_content)
    - This is presentation-layer only, not Discord-specific. Can be reused by future Activity UI (per ACTIVITY-01 in D43).
    - Each section_content MUST be under 1024 chars. If a section would exceed, truncate with "…" and note "（内容较长，仅显示摘要）".
    - Stats section uses emoji: ❤️ HP: {value}, 🧠 SAN: {value}, 💧 MP: {value}, 🍀 LUCK: {value}
    - Header section includes "长期档案" label to satisfy PRESENT-03
    - Keep existing detail_view() intact — card_view is additive

    Section structure:
    1. "📋 调查员档案" — name, occupation, age, status, "长期档案" label
    2. "🏷️ 身份" — concept, birthplace, residence, family, education
    3. "💼 人物" — occupation detail, specialty, career arc
    4. "🎭 塑造" — key_past_event, core_belief, life_goal, material_desire, weakness, trait_notes, important_person, significant_location, treasured_possession, fear_or_taboo, scars_and_injuries, phobias_and_manias, disposition
    5. "📊 数值" — 8 attributes with emoji, derived stats (SAN, HP, MP, LUCK, MOV, build, damage_bonus)
    6. "📚 技能与收束" — favored skills, occupation skills, interest skills, adjustments, rules_note

    Write tests first in tests/test_v18_archive_builder.py:
    - Test card_view returns list of tuples
    - Test each section under 1024 chars
    - Test emoji presence in stats section (❤️, 🧠, 💧, 🍀)
    - Test "长期档案" appears in header section
    - Test all 6 sections present
  </action>
  <verify>
    <automated>uv run pytest tests/test_v18_archive_builder.py -k "card_view" -x</automated>
  </verify>
  <done>card_view() returns 6 sections as list of (title, content) tuples, each under 1024 chars, with emoji stats and 长期档案 label. Tests pass.</done>
</task>

<task type="auto">
  <name>Task 2: Update /profile_detail handler to use card_view()</name>
  <files>src/dm_bot/discord_bot/commands.py</files>
  <action>
    Update the profile_detail handler in src/dm_bot/discord_bot/commands.py (line ~492-505).

    Current behavior: calls profile.detail_view() and sends as single ephemeral message.
    New behavior: calls profile.card_view() and sends each section as a separate message.

    Implementation:
    - Replace `profile.detail_view()` with `profile.card_view()`
    - Loop through sections and send each as a separate message
    - First message uses interaction.response.send_message, subsequent messages use interaction.followup.send
    - All messages remain ephemeral=True
    - Add section title as bold prefix: f"**{title}**\n{content}"
    - If only one section, send normally (no followup needed)

    Per PRESENT-03: The card_view shows ONLY long-lived archive data. Campaign-local state (SAN, HP, MP, Luck from InvestigatorPanel) is NOT included — that's shown separately via status_me / session panels. This keeps the visual distinction clear.
  </action>
  <verify>
    <automated>uv run pytest tests/test_v18_archive_builder.py -k "profile_detail_command" -x</automated>
  </verify>
  <done>/profile_detail sends card sections as multiple ephemeral messages with bold section titles. Existing test updated and passes.</done>
</task>

<task type="auto">
  <name>Task 3: Update existing tests and add card_view-specific tests</name>
  <files>tests/test_v18_archive_builder.py</files>
  <action>
    Update existing test_profile_detail_command_renders_investigator_card_sections (line ~663) to expect card_view output format instead of detail_view.

    Add new tests:
    1. test_card_view_returns_sections — verifies card_view returns list of 6 tuples
    2. test_card_view_sections_under_discord_limit — verifies each section content < 1024 chars
    3. test_card_view_has_emoji_stats — verifies ❤️ HP, 🧠 SAN, 💧 MP, 🍀 LUCK in stats section
    4. test_card_view_has_archive_label — verifies "长期档案" in header section
    5. test_card_view_preserves_detail_view — verifies detail_view still works unchanged

    Run full test suite to ensure no regressions.
  </action>
  <verify>
    <automated>uv run pytest tests/test_v18_archive_builder.py -x -q</automated>
  </verify>
  <done>All archive builder tests pass, including new card_view tests. detail_view preserved and tested.</done>
</task>

</tasks>

<verification>
- uv run pytest tests/test_v18_archive_builder.py -x -q — all tests pass
- uv run python -m dm_bot.main smoke-check — smoke check passes
- Manual check: card_view sections all under 1024 chars
- Manual check: emoji indicators present in stats section
- Manual check: "长期档案" label visible in header
</verification>

<success_criteria>
1. PRESENT-01: card_view() exists with visual sections and emoji stat indicators (❤️ HP, 🧠 SAN, 💧 MP, 🍀 LUCK)
2. PRESENT-02: All sections under 1024 characters, compact but scannable format
3. PRESENT-03: "长期档案" label clearly visible, campaign-local state not mixed into card
4. /profile_detail handler uses card_view, sends sections as separate messages
5. Existing detail_view() preserved for backward compatibility
6. All tests pass (uv run pytest -q)
7. Smoke check passes (uv run python -m dm_bot.main smoke-check)
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-d/phases/D41/D41-01-SUMMARY.md`
</output>
