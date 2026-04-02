---
phase: D43
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/coc/presentation.py
  - src/dm_bot/coc/archive.py
  - src/dm_bot/discord_bot/commands.py
  - tests/test_v18_archive_builder.py
autonomous: true
requirements: [ACTIVITY-01, ACTIVITY-02]
user_setup: []

must_haves:
  truths:
    - "CardSection type exists with title, content, visibility, order fields"
    - "card_view() returns list[CardSection] instead of list[tuple[str, str]]"
    - "CardRenderer protocol exists, allowing swappable renderers (Discord, Activity, etc.)"
    - "DiscordCardRenderer converts CardSections to Discord message format"
    - "No canonical state or data ownership defined in presentation layer"
  artifacts:
    - path: "src/dm_bot/coc/presentation.py"
      provides: "CardSection dataclass, CardRenderer protocol, DiscordCardRenderer"
      exports: ["CardSection", "CardRenderer", "DiscordCardRenderer"]
    - path: "src/dm_bot/coc/archive.py"
      provides: "card_view() returning list[CardSection]"
      contains: "list[CardSection]"
    - path: "src/dm_bot/discord_bot/commands.py"
      provides: "profile_detail handler using CardRenderer"
      contains: "DiscordCardRenderer|CardRenderer"
    - path: "tests/test_v18_archive_builder.py"
      provides: "Tests for CardSection, CardRenderer, refactored card_view"
      contains: "CardSection|CardRenderer"
  key_links:
    - from: "src/dm_bot/coc/archive.py"
      to: "src/dm_bot/coc/presentation.py"
      via: "card_view imports and returns CardSection"
      pattern: "from.*presentation.*import.*CardSection"
    - from: "src/dm_bot/discord_bot/commands.py"
      to: "src/dm_bot/coc/presentation.py"
      via: "commands import and use DiscordCardRenderer"
      pattern: "DiscordCardRenderer|CardRenderer"
    - from: "src/dm_bot/coc/presentation.py"
      to: "src/dm_bot/coc/archive.py"
      via: "CardRenderer.render consumes list[CardSection]"
      pattern: "render.*CardSection|sections.*CardSection"
---

<objective>
Define presentation contracts (CardSection, CardRenderer) that decouple archive data from Discord-specific formatting, enabling reuse by future Discord Activity UI panels.

Purpose: ACTIVITY-01 requires reusable sections not hardcoded to Discord embed format. ACTIVITY-02 requires presentation layer to never redefine canonical state. This plan creates the abstraction boundary between data (Track B) and presentation (Track D).
Output: CardSection dataclass, CardRenderer protocol, DiscordCardRenderer implementation, refactored card_view(), updated commands.py.
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
@src/dm_bot/coc/panels.py
@src/dm_bot/discord_bot/commands.py
@tests/test_v18_archive_builder.py
</context>

<interfaces>
<!-- Key types and contracts the executor needs. Extracted from codebase. -->

From src/dm_bot/coc/archive.py:
```python
class InvestigatorArchiveProfile(BaseModel):
    # ... many fields ...
    def card_view(self) -> list[tuple[str, str]]:
        """Returns list of (section_title, section_content) tuples."""
        # Currently returns 6 sections as raw strings

class ArchiveFinishingRecommendation(BaseModel):
    recommended_occupation_skills: list[str]
    recommended_interest_skills: list[str]
    allowed_adjustments: list[str]
    rules_note: str
```

From src/dm_bot/coc/panels.py:
```python
class InvestigatorPanel(BaseModel):
    user_id: str
    name: str
    role: str = "investigator"
    occupation: str = ""
    san: int = 50
    hp: int = 10
    mp: int = 10
    luck: int = 50
    skills: dict[str, int]
    journal: list[str]
    module_flags: dict[str, str | int | bool]

    def summary(self, *, knowledge_titles: list[str]) -> str: ...
```

From src/dm_bot/discord_bot/commands.py (line ~489-500):
```python
sections = profile.card_view()
first_title, first_content = sections[0]
await interaction.response.send_message(f"**{first_title}**\n{first_content}", ephemeral=True)
for title, content in sections[1:]:
    await interaction.followup.send(f"**{title}**\n{content}", ephemeral=True)
```
</interfaces>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Create CardSection dataclass, CardRenderer protocol, and DiscordCardRenderer</name>
  <files>src/dm_bot/coc/presentation.py, tests/test_presentation.py</files>
  <behavior>
    - CardSection has fields: title (str), content (str), visibility (str), order (int)
    - visibility accepts: "public", "private", "group", "keeper"
    - CardRenderer protocol defines render(sections: list[CardSection]) -> list[str]
    - DiscordCardRenderer implements CardRenderer, formats as "**title**\ncontent" per section
    - CardSection is a dataclass, not a Pydantic model (lightweight, no validation overhead)
    - Protocol-based design allows future ActivityCardRenderer without changing archive.py
  </behavior>
  <action>
    Create new file src/dm_bot/coc/presentation.py with:

    1. CardSection dataclass:
    ```python
    from dataclasses import dataclass
    from typing import Literal, Protocol

    Visibility = Literal["public", "private", "group", "keeper"]

    @dataclass
    class CardSection:
        title: str
        content: str
        visibility: Visibility = "public"
        order: int = 0
    ```

    Design notes:
    - Uses dataclass (not Pydantic) — this is a presentation contract, not a data model per ACTIVITY-02
    - Visibility type Literal ensures type safety for future Activity panel routing
    - order field enables consistent sorting across renderers

    2. CardRenderer protocol:
    ```python
    class CardRenderer(Protocol):
        def render(self, sections: list[CardSection]) -> list[str]: ...
    ```

    Design notes:
    - Protocol (structural subtyping) allows any class with render() method
    - Returns list[str] — each string is one rendered message/panel
    - This is the abstraction boundary: archive produces CardSections, renderer formats them

    3. DiscordCardRenderer implementation:
    ```python
    class DiscordCardRenderer:
        def render(self, sections: list[CardSection]) -> list[str]:
            return [f"**{s.title}**\n{s.content}" for s in sections]
    ```

    Design notes:
    - Matches current commands.py behavior: bold title + newline + content
    - Could add Discord-specific logic later (embed formatting, character limits, etc.)
    - Does NOT modify or own any canonical state — purely formatting per ACTIVITY-02

    Write tests first in tests/test_presentation.py:
    - Test CardSection creation with all fields
    - Test CardSection defaults (visibility="public", order=0)
    - Test DiscordCardRenderer renders sections correctly
    - Test CardRenderer protocol accepts DiscordCardRenderer
    - Test visibility type enforcement (invalid visibility rejected by type checker)
  </action>
  <verify>
    <automated>uv run pytest tests/test_presentation.py -x</automated>
  </verify>
  <done>CardSection dataclass, CardRenderer protocol, DiscordCardRenderer all exist with tests passing. presentation.py exports all three.</done>
</task>

<task type="auto">
  <name>Task 2: Refactor card_view() to return list[CardSection]</name>
  <files>src/dm_bot/coc/archive.py</files>
  <action>
    Refactor InvestigatorArchiveProfile.card_view() in src/dm_bot/coc/archive.py:

    Current signature: `def card_view(self) -> list[tuple[str, str]]`
    New signature: `def card_view(self) -> list[CardSection]`

    Changes:
    1. Add import: `from dm_bot.coc.presentation import CardSection`
    2. Replace each `sections.append((title, content))` with `sections.append(CardSection(title=title, content=content, visibility="public", order=i))`
    3. Assign order values 0-5 for the 6 sections (consistent ordering)
    4. Set visibility="public" for all sections (archive data is player-visible)
    5. Keep detail_view() unchanged for backward compatibility

    Section mapping:
    - order=0: "📋 调查员档案" (header)
    - order=1: "🏷️ 身份"
    - order=2: "💼 人物"
    - order=3: "🎭 塑造"
    - order=4: "📊 数值"
    - order=5: "📚 技能与收束"

    Design notes:
    - This is the data producer side of the contract — archive provides structured sections
    - No canonical state is added or modified — only the return type changes (per ACTIVITY-02)
    - The content strings remain identical to D41's implementation — only the wrapper changes
  </action>
  <verify>
    <automated>uv run pytest tests/test_v18_archive_builder.py -k "card_view" -x</automated>
  </verify>
  <done>card_view() returns list[CardSection] with correct order and visibility values. All existing card_view tests pass (updated for new return type).</done>
</task>

<task type="auto">
  <name>Task 3: Update commands.py to use DiscordCardRenderer and update tests</name>
  <files>src/dm_bot/discord_bot/commands.py, tests/test_v18_archive_builder.py</files>
  <action>
    Update profile_detail handler in src/dm_bot/discord_bot/commands.py (line ~489-500):

    Current:
    ```python
    sections = profile.card_view()
    first_title, first_content = sections[0]
    await interaction.response.send_message(f"**{first_title}**\n{first_content}", ephemeral=True)
    for title, content in sections[1:]:
        await interaction.followup.send(f"**{title}**\n{content}", ephemeral=True)
    ```

    New:
    ```python
    from dm_bot.coc.presentation import DiscordCardRenderer

    renderer = DiscordCardRenderer()
    sections = profile.card_view()
    rendered = renderer.render(sections)
    await interaction.response.send_message(rendered[0], ephemeral=True)
    for message in rendered[1:]:
        await interaction.followup.send(message, ephemeral=True)
    ```

    Design notes:
    - The renderer handles the formatting — commands.py just sends the strings
    - This decouples the command from the section structure — if CardSection changes, only renderer needs updating
    - Per ACTIVITY-02: commands.py does not define any canonical state, only presentation

    Update tests in tests/test_v18_archive_builder.py:
    - Update test_profile_detail_command_renders_investigator_card_sections to work with CardSection return type
    - Update any tests that unpack card_view() as tuples
    - Add test that verifies DiscordCardRenderer produces same output as before (backward compatibility)
    - Run full test suite to ensure no regressions
  </action>
  <verify>
    <automated>uv run pytest tests/test_v18_archive_builder.py -x -q</automated>
  </verify>
  <done>profile_detail handler uses DiscordCardRenderer. All tests pass. Output format identical to before (backward compatible).</done>
</task>

</tasks>

<verification>
- uv run pytest tests/test_presentation.py -x — CardSection, CardRenderer, DiscordCardRenderer tests pass
- uv run pytest tests/test_v18_archive_builder.py -x -q — all archive tests pass with CardSection return type
- uv run python -m dm_bot.main smoke-check — smoke check passes
- CardSection has title, content, visibility, order fields (ACTIVITY-01)
- card_view() returns list[CardSection], not tuple (ACTIVITY-01)
- CardRenderer protocol allows swappable renderers (ACTIVITY-01)
- No canonical state defined in presentation.py (ACTIVITY-02)
</verification>

<success_criteria>
1. ACTIVITY-01: CardSection protocol/dataclass exists with title, content, visibility, order — not hardcoded to Discord embed format
2. ACTIVITY-01: CardRenderer protocol enables future ActivityCardRenderer without changing archive.py
3. ACTIVITY-01: card_view() returns list[CardSection] — reusable by any renderer
4. ACTIVITY-02: presentation.py defines only formatting contracts — no canonical state or data ownership
5. DiscordCardRenderer produces identical output to previous implementation (backward compatible)
6. All tests pass (uv run pytest -q)
7. Smoke check passes (uv run python -m dm_bot.main smoke-check)
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-d/phases/D43/D43-01-SUMMARY.md`
</output>
