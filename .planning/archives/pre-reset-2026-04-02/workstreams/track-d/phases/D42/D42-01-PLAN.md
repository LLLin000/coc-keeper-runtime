---
phase: D42
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/coc/builder.py
  - src/dm_bot/narration/service.py
  - src/dm_bot/orchestrator/consequence_aggregator.py
  - src/dm_bot/discord_bot/commands.py
autonomous: true
requirements:
  - KEEPER-01
  - KEEPER-02
  - KEEPER-03
  - KEEPER-04

must_haves:
  truths:
    - "All builder prompts use consistent Keeper voice (verified from D40)"
    - "Model-guided system prompts use Keeper voice instead of generic '你是XX器'"
    - "Consequence output text uses narrative framing, not just mechanical labels"
    - "Narration system prompt reinforces Chinese Keeper style"
    - "System-facing messages use consistent Chinese tone"
  artifacts:
    - path: "src/dm_bot/coc/builder.py"
      provides: "Model-guided system prompts with Keeper voice"
      contains: "你是克苏鲁的呼唤 Keeper"
    - path: "src/dm_bot/narration/service.py"
      provides: "Narration system prompt with Chinese Keeper style"
      contains: "Chinese Call of Cthulhu Keeper"
    - path: "src/dm_bot/orchestrator/consequence_aggregator.py"
      provides: "Narrative consequence formatting"
      contains: "narrative framing for outcomes"
  key_links:
    - from: "src/dm_bot/coc/builder.py"
      to: "Model router"
      via: "ModelGuidedInterviewPlanner system_prompt"
      pattern: "system_prompt.*你是"
    - from: "src/dm_bot/narration/service.py"
      to: "Model narrator"
      via: "_build_model_request system_prompt"
      pattern: "system_prompt.*Keeper"
    - from: "src/dm_bot/orchestrator/consequence_aggregator.py"
      to: "Discord output"
      via: "_format_outcome returns narrative text"
      pattern: "_format_outcome"
---

<objective>
Polish all remaining Keeper voice across the system beyond builder prompts — model-guided system prompts, narration service, consequence formatting, and system messages.

Purpose: Ensure Keeper voice is consistent everywhere the player sees text, not just the builder interview. D40 handled the builder; D42 handles everything else.
Output: Updated system prompts in builder.py, narration/service.py, consequence_aggregator.py, and commands.py.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
@C:/Users/Lin/.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/workstreams/track-d/ROADMAP.md
@.planning/workstreams/track-d/REQUIREMENTS.md
@.planning/workstreams/track-d/STATE.md
@.planning/workstreams/track-d/phases/D40/D40-01-SUMMARY.md
@src/dm_bot/coc/builder.py
@src/dm_bot/narration/service.py
@src/dm_bot/orchestrator/consequence_aggregator.py
@src/dm_bot/discord_bot/commands.py
</context>

<interfaces>
<!-- Key types and contracts the executor needs. Extracted from codebase. -->

From src/dm_bot/coc/builder.py — Model-guided system prompts to polish:
```python
# ModelGuidedInterviewPlanner (line 231-236):
system_prompt=(
    "你是克苏鲁的呼唤建卡采访器。"
    "基于已知角色信息，选择下一条最有价值的追问。"
    ...
)

# ModelGuidedArchiveSemanticExtractor (line 284-292):
system_prompt=(
    "你是克苏鲁的呼唤人物档案归档器。"
    ...
)

# ModelGuidedCharacterSheetSynthesizer (line 360-366):
system_prompt=(
    "你是克苏鲁的呼唤角色卡整理器。"
    ...
)
```

From src/dm_bot/narration/service.py — Narration system prompt:
```python
system_prompt=(
    "You are the Chinese Call of Cthulhu Keeper. Produce final Discord-ready prose only. "
    "Write like a practical tabletop Keeper: eerie but concise sensory framing, clear actionable details, "
    ...
)
```

From src/dm_bot/orchestrator/consequence_aggregator.py — Outcome formatting:
```python
def _format_outcome(self, outcome: dict[str, Any]) -> str:
    # Currently: "技能检定: 成功 (roll)", "SAN检定: 失败 (损失 X)", "伤害: X"
    # Target: narrative framing like "检定通过，你勉强躲过了这一劫" or "理智的裂缝又扩大了一分"
```

From src/dm_bot/discord_bot/commands.py — System messages:
```python
# Mixed English/Chinese messages like:
# "no campaign bound to this channel"
# "gameplay is not configured"
# "combat not active"
# "returned to DM mode"
# "scene mode enabled for..."
# "loaded adventure..."
# Target: consistent Chinese with subtle Keeper tone where player-facing
```
</interfaces>

<tasks>

<task type="auto">
  <name>Task 1: Polish model-guided system prompts with Keeper voice (KEEPER-01, KEEPER-02, KEEPER-03)</name>
  <files>src/dm_bot/coc/builder.py</files>
  <action>
Rewrite the three model-guided system prompts in builder.py to use consistent Keeper voice instead of generic "XX器" framing. These are system prompts sent to the router model, so they need to be clear about the task while maintaining Keeper atmosphere.

1. **ModelGuidedInterviewPlanner** (line ~231): Replace system prompt:
   FROM: "你是克苏鲁的呼唤建卡采访器。基于已知角色信息，选择下一条最有价值的追问。一次只能问一个问题。不要重复已知信息，不要谈属性数值，不要输出解释。只返回 JSON，键为 slot 和 question。slot 必须是这些候选之一: ..."
   TO: "你是克苏鲁的呼唤的 Keeper，正在引导一位新调查员完成建卡访谈。基于已知的人物信息，选择下一条最有价值的追问。一次只问一个问题，像 Keeper 了解角色那样自然地提问——不要重复已知信息，不要谈属性数值，不要输出解释。只返回 JSON，键为 slot 和 question。slot 必须是这些候选之一: ..."

2. **ModelGuidedArchiveSemanticExtractor** (line ~284): Replace system prompt:
   FROM: "你是克苏鲁的呼唤人物档案归档器。根据采访答案，提取适合长期档案保存的人物语义字段。不要编造采访里完全不存在的事实。可以做适度归纳，但必须忠于原意。只返回 JSON，不要解释。..."
   TO: "你是克苏鲁的呼唤的 Keeper，正在为刚刚完成访谈的调查员整理长期档案。根据采访答案，提取适合长期档案保存的人物语义字段。不要编造采访里完全不存在的事实。可以做适度归纳，但必须忠于原意。只返回 JSON，不要解释。..."

3. **ModelGuidedCharacterSheetSynthesizer** (line ~360): Replace system prompt:
   FROM: "你是克苏鲁的呼唤角色卡整理器。根据采访答案和已有语义字段，把人物整理为更连贯的长期档案。不要编造采访里没有的具体事实，不要发明新职业，不要改动明确给出的年龄和职业。输出必须是 JSON，对每个字段给出简洁中文；不确定就留空。favored_skills 必须是字符串数组。"
   TO: "你是克苏鲁的呼唤的 Keeper，正在将一位新调查员的访谈内容整理为完整的角色档案。根据采访答案和已有语义字段，把人物整理为更连贯的长期档案。不要编造采访里没有的具体事实，不要发明新职业，不要改动明确给出的年龄和职业。输出必须是 JSON，对每个字段给出简洁中文；不确定就留空。favored_skills 必须是字符串数组。"

Do NOT change any logic, data structures, or normalization functions. Only change system prompt text strings.
  </action>
  <verify>
    <automated>uv run pytest tests/coc/test_builder.py -x -q</automated>
  </verify>
  <done>All three model-guided system prompts use Keeper voice ("你是克苏鲁的呼唤的 Keeper，正在..."); no logic changes; tests pass.</done>
</task>

<task type="auto">
  <name>Task 2: Polish consequence formatting with narrative framing (KEEPER-04 extension)</name>
  <files>src/dm_bot/orchestrator/consequence_aggregator.py</files>
  <action>
Rewrite the _format_outcome method in consequence_aggregator.py to use narrative Keeper-style framing instead of raw mechanical labels. This is the text that eventually reaches players.

Current output examples:
- "技能检定: 成功 (45/60)" → should feel like "检定通过——你勉强做到了"
- "SAN检定: 失败 (损失 1d6)" → should feel like "理智的防线出现裂痕"
- "伤害: 7" → should feel like "伤口比你预想的更深"
- "weapon攻击: 命中" → should feel like "攻击命中"

New _format_outcome implementation:

```python
def _format_outcome(self, outcome: dict[str, Any]) -> str:
    """Format a rule outcome into Keeper-style narrative text."""
    action = outcome.get("action", "unknown")
    if action == "coc_skill_check":
        label = outcome.get("label", "技能检定")
        success = outcome.get("success", False)
        roll = outcome.get("roll", "")
        grade = outcome.get("grade", "")
        if success:
            if grade == "extreme":
                return f"{label}：大成功——你做到了远超预期的事情（{roll}）"
            elif grade == "hard":
                return f"{label}：困难成功——你完成得相当漂亮（{roll}）"
            else:
                return f"{label}：检定通过——你勉强做到了（{roll}）"
        else:
            return f"{label}：检定失败——事情没有按你的预期发展（{roll}）"
    elif action == "coc_sanity_check":
        san_loss = outcome.get("san_loss", "0")
        success = outcome.get("success", False)
        if success:
            return f"SAN检定：你稳住了心神，但那一幕已刻入记忆（损失 {san_loss}）"
        else:
            return f"SAN检定：理智的防线出现裂痕（损失 {san_loss}）"
    elif action == "attack_roll":
        hit = outcome.get("hit", False)
        weapon = outcome.get("weapon", "武器")
        if hit:
            return f"{weapon}攻击命中"
        else:
            return f"{weapon}攻击落空"
    elif action == "damage_roll":
        total = outcome.get("total", 0)
        if total > 0:
            return f"造成 {total} 点伤害"
        return "未造成伤害"
    else:
        return str(outcome)
```

Also update _format_trigger_effect to be slightly more narrative:
FROM: `"[触发器] {effect.event_type}"` or `"[触发器事件]"`
TO: `"【事件触发】{effect.event_type}"` or `"【事件触发】"`

Do NOT change the aggregation logic, grouping, or sorting. Only change the formatting methods.
  </action>
  <verify>
    <automated>uv run pytest tests/ -k "consequence" -x -q</automated>
  </verify>
  <done>_format_outcome returns Keeper-style narrative text; _format_trigger_effect uses 【事件触发】 format; tests pass.</done>
</task>

<task type="auto">
  <name>Task 3: Polish system messages in commands.py to consistent Chinese (KEEPER-01, KEEPER-02)</name>
  <files>src/dm_bot/discord_bot/commands.py</files>
  <action>
Replace all English system messages in commands.py with consistent Chinese. These are player-facing error/status messages that currently break immersion by switching to English. Focus on messages the player actually sees — internal debug strings can stay English.

Messages to replace (player-facing only):

1. Line ~186: `"campaign \`{campaign_id}\` bound to channel \`{interaction.channel_id}\`"`
   → `"战役 \`{campaign_id}\` 已绑定到频道 \`{interaction.channel_id}\`"`

2. Line ~384: `"left campaign \`{session.campaign_id}\`"`
   → `"已离开战役 \`{session.campaign_id}\`"`

3. Line ~391: `"gameplay is not configured"`
   → `"游戏系统尚未配置"`

4. Line ~637: `"no campaign bound to this channel"`
   → `"当前频道没有绑定战役"`

5. Line ~726: `"scene mode enabled for {', '.join(parsed)}"`
   → `"场景模式已启用，发言者：{', '.join(parsed)}"`

6. Line ~739: `"returned to DM mode"`
   → `"已返回常规模式"`

7. Line ~766: `"combat started; active turn: {encounter.active_combatant.name}"`
   → `"战斗开始；当前行动者：{encounter.active_combatant.name}"`

8. Line ~790: `"combat not active"`
   → `"当前没有进行中的战斗"`

9. Line ~815: `"loaded adventure \`{adventure.title}\`"`
   → Already has Chinese follow-up on line 820, but line 815 response is English. Change to: `"模组 \`{adventure.title}\` 已加载。"`

10. Line ~239: `"session store is not configured"` (appears multiple times)
    → `"会话系统尚未配置"`

11. Line ~419: `"character builder is not configured"`
    → `"建卡系统尚未配置"`

12. Line ~479: `"archive repository is not configured"`
    → `"档案系统尚未配置"`

Do NOT change:
- Log messages or internal strings
- Variable names or function names
- The actual command logic or flow
- Messages that are already in Chinese

This is a text-only change — no logic modifications.
  </action>
  <verify>
    <automated>uv run pytest tests/test_discord_commands.py -x -q</automated>
  </verify>
  <done>All player-facing system messages use consistent Chinese; no logic changes; tests pass.</done>
</task>

</tasks>

<verification>
- Builder tests pass: `uv run pytest tests/coc/test_builder.py -x -q`
- Discord command tests pass: `uv run pytest tests/test_discord_commands.py -x -q`
- Consequence tests pass: `uv run pytest tests/ -k "consequence" -x -q`
- Smoke check passes: `uv run python -m dm_bot.main smoke-check`
- Full test suite: `uv run pytest -q`
- No English player-facing messages remain in commands.py: `grep -n "await interaction.*send_message.*\"" src/dm_bot/discord_bot/commands.py | grep -v "中文\|建卡\|战役\|调查员\|档案\|游戏\|场景\|战斗\|模组\|会话\|角色\|技能\|检定\|理智\|伤害\|攻击\|事件\|发言\|常规\|尚未"`
</verification>

<success_criteria>
1. All three model-guided system prompts in builder.py use "你是克苏鲁的呼唤的 Keeper" instead of "你是XX器"
2. Consequence formatting uses narrative Keeper-style text instead of mechanical labels
3. All player-facing system messages in commands.py use consistent Chinese
4. Narration service prompt remains solid (no changes needed — already good)
5. All tests pass
6. Smoke check passes
7. No regression in builder prompt quality (D40's work preserved)
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-d/phases/D42/D42-01-SUMMARY.md`
</output>
