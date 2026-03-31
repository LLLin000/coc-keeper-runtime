---
phase: D40
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/coc/builder.py
  - src/dm_bot/discord_bot/commands.py
autonomous: true
requirements:
  - PRIVATE-01
  - PRIVATE-02
  - PRIVATE-03

must_haves:
  truths:
    - "/start_builder sends first question to user's DM, not archive channel"
    - "Archive channel shows only a brief '建卡中...' indicator"
    - "Archive channel guidance text explains builder flow vs profile viewing"
    - "All builder prompts read like a Keeper shaping a person, not a form"
  artifacts:
    - path: "src/dm_bot/coc/builder.py"
      provides: "Keeper-voiced question constants and finalization prompt"
      contains: "INTRO_QUESTION with Keeper tone"
    - path: "src/dm_bot/discord_bot/commands.py"
      provides: "DM-routed start_character_builder and archive channel indicator"
      exports: ["start_character_builder"]
  key_links:
    - from: "src/dm_bot/discord_bot/commands.py"
      to: "src/dm_bot/coc/builder.py"
      via: "character_builder.start() returns first question"
      pattern: "character_builder\\.start\\("
    - from: "src/dm_bot/discord_bot/commands.py"
      to: "Discord DM channel"
      via: "interaction.user.create_dm() then send"
      pattern: "create_dm|user\\.send"
---

<objective>
Route character builder to DM by default, add archive channel guidance, and rewrite all builder prompts with Keeper voice.

Purpose: Make character creation feel like a private Keeper-guided interview rather than a public bot interaction.
Output: Modified commands.py with DM routing, modified builder.py with Keeper-voiced prompts.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/workstreams/track-d/ROADMAP.md
@.planning/workstreams/track-d/REQUIREMENTS.md
@.planning/workstreams/track-d/STATE.md
@src/dm_bot/coc/builder.py
@src/dm_bot/discord_bot/commands.py
</context>

<interfaces>
<!-- Key types and contracts the executor needs. Extracted from codebase. -->

From src/dm_bot/coc/builder.py:
```python
class ConversationalCharacterBuilder:
    INTRO_QUESTION = "先给这位调查员起个名字。"
    CONCEPT_QUESTION = "用一句短话描述这个人的人物骨架，例如\"38岁的落魄临床医生\"。"

    def start(self, *, user_id: str, visibility: str = "private") -> str:
        # Returns first question string
        ...

    async def answer(self, *, user_id: str, answer: str) -> tuple[str, InvestigatorArchiveProfile | None]:
        # Returns (next_question_or_finalization, profile_or_none)
        ...
```

From src/dm_bot/discord_bot/commands.py:
```python
async def start_character_builder(self, interaction, *, visibility: str = "private") -> None:
    # Currently: sends prompt in-channel with ephemeral=True
    # Target: send first question to DM, post indicator in archive channel
    ...

async def builder_reply(self, interaction, *, answer: str) -> None:
    # Currently: responds in-channel with ephemeral=True
    # May need update if builder is DM-based
    ...
```

Key Discord API patterns from codebase:
- `interaction.user.create_dm()` — creates DM channel with user
- `user.send(message)` — sends message to user's DM
- `interaction.response.send_message(msg, ephemeral=True)` — ephemeral response in channel
- `interaction.followup.send(msg)` — follow-up message
</interfaces>

<tasks>

<task type="auto">
  <name>Task 1: Rewrite builder prompts with Keeper voice (PRIVATE-03)</name>
  <files>src/dm_bot/coc/builder.py</files>
  <action>
Rewrite all question constants and helper functions in builder.py to use Keeper voice. Changes:

1. **INTRO_QUESTION** (line 441): Replace "先给这位调查员起个名字。" with:
   "让我先了解一下这位即将踏入黑暗的调查员。请先告诉我他的名字。"

2. **CONCEPT_QUESTION** (line 442): Replace "用一句短话描述这个人的人物骨架，例如"38岁的落魄临床医生"。" with:
   "告诉我，这是个什么样的人？用一句话勾勒他的轮廓——比如'38岁的落魄临床医生'，或者'被过去追逐的退伍老兵'。"

3. **Age question** in `_next_question()` (line 509): Replace "他的年龄是多少？" with:
   "这位调查员看起来有多大？岁月在他身上留下了什么痕迹？"

4. **Occupation question** in `_next_question()` (line 511): Replace "他的职业是什么？尽量用 COC 里能落地的现实职业描述。" with:
   "在成为调查员之前，他以什么为生？"

5. **`_past_event_question()`** (line 634-643): Already has good Keeper voice — keep as is, it's already contextual.

6. **HeuristicInterviewPlanner questions** (lines 201-218): Already have Keeper voice — keep as is.

7. **`_build_finalization_prompt()`** (line 789-796): Rewrite to feel like Keeper summarizing:
   Replace with:
   ```python
   def _build_finalization_prompt(session: BuilderSession) -> str:
       return (
           f"{session.portrait_summary}\n\n"
           "访谈到此告一段落。这就是你即将带入黑暗的调查员。\n"
           "如果这份人物画像没问题，回复 `定卡` 或 `按人物来`。\n"
           "如果你想直接指定这人最擅长的 2-4 项技能，直接回复技能名并用逗号分隔。\n"
           "如果你还想补一笔人物信息，直接回复那一句，我会先更新人物画像。"
       )
   ```

Do NOT change any logic, data structures, or normalization functions. Only change question text strings.
  </action>
  <verify>
    <automated>uv run pytest tests/coc/test_builder.py -x -q</automated>
  </verify>
  <done>INTRO_QUESTION, CONCEPT_QUESTION, age/occupation questions, and finalization prompt all use Keeper voice; no logic changes; tests pass.</done>
</task>

<task type="auto">
  <name>Task 2: Route /start_builder to DM and add archive channel guidance (PRIVATE-01, PRIVATE-02)</name>
  <files>src/dm_bot/discord_bot/commands.py</files>
  <action>
Modify `start_character_builder` method (line ~407-424) to:

1. **Send first question to user's DM** instead of in-channel:
   - After `self._character_builder.start(...)`, create DM channel via `await interaction.user.create_dm()`
   - Send the first question to the DM: `await dm_channel.send(prompt)`
   - If DM creation fails (user has DMs disabled), fall back to ephemeral in-channel with a note

2. **Post "建卡中..." indicator in archive channel**:
   - After sending to DM, send a brief message to the current channel: "🕯️ 建卡访谈已在私信中开始。完成建卡后档案将出现在这里。"
   - Use `await interaction.channel.send(...)` for the indicator (not ephemeral, so others can see someone is building)

3. **Add archive channel guidance** to `_build_channel_guidance()` (line ~76):
   - In the #角色档案 section, add a guidance line: "建卡请用 `/start_builder`，访谈将在私信中进行"
   - Ensure `/profiles` and `/profile_detail` are clearly documented as profile viewing commands

Updated `_build_channel_guidance` section for #角色档案:
```
1. **#角色档案** - 档案管理命令
   建卡请用 `/start_builder`，访谈将在私信中进行
   查看档案：`/profiles`（列表）, `/profile_detail`（详情）
   管理档案：`/select_profile`, `/archive_profile`, `/activate_profile`
```

Also update `_default_channel_guidance()` (line ~145) with the same guidance text.

For `builder_reply` method (line ~426): Keep as-is for now — it already uses ephemeral=True which works for in-channel replies during the interview flow. The DM routing is handled by the initial start; subsequent replies from the user in the archive channel will still work via the existing ephemeral flow. If the user is replying in a DM context, the interaction channel will be the DM channel, which is fine.

IMPORTANT: Handle the case where DM creation fails gracefully — user may have DMs disabled for the server. In that case, fall back to ephemeral in-channel with a message like "无法发送私信（你可能关闭了服务器私信）。建卡访谈将在当前频道以私密方式进行。"
  </action>
  <verify>
    <automated>uv run pytest tests/test_discord_commands.py -x -q</automated>
  </verify>
  <done>/start_builder sends first question to DM, archive channel shows indicator, guidance text updated, DM-failure fallback works.</done>
</task>

<task type="auto">
  <name>Task 3: Update builder_reply to handle DM context (PRIVATE-01 follow-up)</name>
  <files>src/dm_bot/discord_bot/commands.py</files>
  <action>
The `builder_reply` method currently uses `interaction.response.send_message()` which works for slash command follow-ups. However, when the builder is in DM mode, the user's replies come via normal messages in the DM channel, not via slash commands.

Check if there's an existing message handler for builder replies (not slash command). Look for how normal messages are routed to the builder in the message handling flow.

If there IS a message handler that routes to builder:
- Ensure it sends responses to the DM channel (which it already does if the interaction is in a DM)
- No changes needed

If there is NO message handler for builder DM replies:
- The current `builder_reply` slash command approach still works — user can use `/builder_reply answer:xxx` in the archive channel
- This is acceptable for vD.1.1; full DM message handling can be a future improvement
- Add a note in the DM's first message: "回答时直接在私信中回复即可，或在档案频道使用 `/builder_reply answer:你的回答`"

Search for message handling that routes to character_builder:
```bash
grep -rn "character_builder" src/dm_bot/ --include="*.py" | grep -v "commands.py" | grep -v "__pycache__"
```

Based on findings, make minimal changes to ensure the builder flow works end-to-end in DM context.
  </action>
  <verify>
    <automated>uv run pytest tests/test_discord_commands.py tests/coc/test_builder.py -x -q</automated>
  </verify>
  <done>Builder reply flow works in both DM and in-channel contexts; user knows how to reply.</done>
</task>

</tasks>

<verification>
- All builder tests pass: `uv run pytest tests/coc/test_builder.py -x -q`
- All command tests pass: `uv run pytest tests/test_discord_commands.py -x -q`
- Smoke check passes: `uv run python -m dm_bot.main smoke-check`
- Full test suite: `uv run pytest -q`
</verification>

<success_criteria>
1. `/start_builder` sends first question to user's DM (not archive channel)
2. Archive channel shows "🕯️ 建卡访谈已在私信中开始..." indicator
3. Archive channel guidance includes "建卡请用 `/start_builder`，访谈将在私信中进行"
4. INTRO_QUESTION opens with Keeper tone: "让我先了解一下这位即将踏入黑暗的调查员..."
5. CONCEPT_QUESTION asks in Keeper character
6. All follow-up questions maintain Keeper voice
7. Finalization prompt feels like Keeper summarizing
8. DM failure falls back gracefully to ephemeral in-channel
9. All tests pass
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-d/phases/D40/D40-01-SUMMARY.md`
</output>
