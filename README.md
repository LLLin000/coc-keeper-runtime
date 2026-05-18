# Discord AI Keeper

本地模型驱动的 **d100 horror investigation** 跑团系统。多个真人玩家在 Discord 里跑团，AI 扮演 Keeper 叙事、NPC 扮演、规则结算。

## 核心目标

- 多个真人玩家在 Discord 里直接跑团
- AI 负责 Keeper 叙事、NPC 扮演、场景推进
- d100 规则由本地代码托管（确定性结算）
- 模组结构化，可迁移、可复用
- 长期角色档案和模组实例状态分离

## Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │              Discord Users                  │
                    └──────────────────┬────────────────────────┘
                                       │ slash commands / messages
                                       ▼
                    ┌─────────────────────────────────────────────┐
                    │           discord_bot / commands.py          │
                    │   /start  /begin_module  /action  /roll    │
                    │   /sheet  /end_round  /status               │
                    └──────┬──────────┬──────────────┬────────────┘
                           │          │              │
           ┌───────────────┘          │              └──────────────┐
           │                          ▼                                  │
           │         ┌──────────────────────────────┐                  │
           │         │         scene / round.py       │                  │
           │         │  WAITING → COLLECTING        │                  │
           │         │  → RESOLVING → NARRATING     │                  │
           │         └──────────────┬───────────────┘                  │
           │                        │                                    │
           ▼                        ▼                                    ▼
┌─────────────────────┐  ┌──────────────────┐  ┌─────────────────────────────────┐
│   character /       │  │   adventure /    │  │          narrator /             │
│   builder.py        │  │   loader.py     │  │          client.py               │
│                     │  │                  │  │                                 │
│  Conversational     │  │  Adventure       │  │  SimpleNarrator (placeholder)    │
│  character          │  │  Scene / NPC /   │  │ 接入 qwen3:4b 后替换             │
│  creation           │  │  Clue models     │  │                                 │
│                     │  │                  │  │                                 │
│  → CharacterSheet   │  │  → Adventure     │  │  → 场景叙事                      │
│                     │  │                  │  │  → 行动结算描述                  │
└─────────────────────┘  └──────────────────┘  │  → NPC 对话                      │
                                                └─────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────────┐
                    │                 rules /                    │
                    │                                          │
                    │  dice.py   ──── 百分骰系统               │
                    │  coc/skills.py ─── 80+ 技能定义/检定    │
                    │  coc/combat.py ─── 格斗/射击/摔跤/闪避  │
                    │  coc/sanity.py ─── SAN/疯狂/运气        │
                    │  coc/derived.py ── 衍生属性计算         │
                    │                                          │
                    └──────────────────┬───────────────────────┘
                                       │
                    ┌──────────────────┴───────────────────────┐
                    │               store / db.py               │
                    │                                          │
                    │  SQLite: sessions, characters 表         │
                    └─────────────────────────────────────────┘
```

## 7 Package Design

| Package       | Responsibility                                    |
| ------------- | ------------------------------------------------- |
| `discord_bot` | Discord I/O：slash commands、消息路由、DM 推送     |
| `scene`       | 回合状态机：WAITING → COLLECTING → RESOLVING → NARRATING |
| `adventure`   | 模组数据：Adventure / Scene / NPC / Clue 模型     |
| `character`   | 角色卡：CharacterSheet、对话建卡 CharacterBuilder   |
| `narrator`   | AI 叙事层（接入 ollama 前为 placeholder）          |
| `rules`       | d100 规则：骰子、技能、战斗、SAN、衍生属性       |
| `store`       | SQLite 持久化：sessions、characters 表              |

### Design Principles

- **规则和叙事分离** — `rules/` 决定"能不能、发生了什么"，`narrator/` 决定"怎么讲得像 Keeper"
- **状态真相不交给模型** — canonical truth 在结构化状态、规则结算、模组数据里
- **模组结构化** — 模组是 Scene/NPC/Clue 数据，不是整篇剧本塞给模型
- **长期角色和模组实例分离** — 玩家档案是长期资产，模组内 SAN/秘密/临时状态是实例状态

## Project Layout

```
src/dm_bot/
  discord_bot/
    __init__.py
    commands.py       # 7 slash commands: /start /begin_module /action /roll /sheet /end_round /status
  scene/
    __init__.py
    state.py         # SceneState enum: WAITING / COLLECTING / RESOLVING / NARRATING
    action.py        # Action, ActionResult models
    round.py         # Round class: submit_action() / resolve() / get_private_results()
  adventure/
    __init__.py
    models.py        # Adventure / Scene / NPC / Clue Pydantic models
    loader.py        # AdventureLoader (目前返回空模组，待接入 JSON/YAML)
  character/
    __init__.py
    sheet.py         # CharacterSheet: 8 base attributes, HP/MP/SAN, skills dict
    builder.py       # CharacterBuilder: conversational creation flow
  narrator/
    __init__.py
    client.py        # NarratorClient protocol + SimpleNarrator placeholder
    prompts.py       # 场景叙事/行动确认/结算叙事 prompt 模板
  rules/
    __init__.py
    dice.py          # 百分骰: SeededDiceRoller, D20DiceRoller, COCDifficulty
    coc/
      __init__.py
      derived.py     # COCAttributes, 衍生属性计算, 年龄修正
      skills.py      # 80+ 技能定义, SkillCheckResult, resolve_skill_check()
      combat.py      # CombatantStats, 格斗/射击/摔跤/闪避, damage bonus
      sanity.py      # SAN check, 疯狂, 运气消耗
      magic.py       # 魔法 (占位)
      chase.py       # 追逐 (占位)
      experience.py  # 经验值 (占位)
  store/
    __init__.py
    db.py            # SQLite Store: sessions / characters 表
  config.py          # Settings: discord_token, ollama_base_url, narrator_model
  logging.py         # 日志配置
  main.py            # 入口: preflight / run-bot / smoke-check
  testing/           # 测试工具
```

## Setup

```powershell
# 1. 复制环境变量
cp .env.example .env

# 2. 填写 .env
DM_BOT_DISCORD_TOKEN=your_token_here

# 3. 安装依赖
uv sync

# 4. 确保 Ollama 已拉好模型（可选，接入 AI 叙事之前 bot 可以跑占位符）
ollama pull qwen3:4b

# 5. 启动前检查
uv run python -m dm_bot.main preflight
uv run python -m dm_bot.main smoke-check

# 6. 启动 bot
uv run python -m dm_bot.main run-bot
```

## Discord Usage

推荐双频道模式：

**DM Bot（私密）**
- `/start` — 开始创建调查员（对话式建卡）
- `/sheet` — 查看当前角色卡
- `/roll <技能>` — 手动技能检定

**游戏大厅（公开）**
- `/begin_module <模组名>` — 开始一个模组，AI 发出开场叙事
- 普通消息 → 视为公开行动提交
- `/action <行动描述>` — 私密行动（其他玩家看不到）
- `/end_round` — 强制结算当前回合
- `/status` — 查看当前状态

## Round Flow

```
1. /begin_module         → Round 进入 COLLECTING，AI 发出开场叙事
2. 玩家提交行动
   - 普通消息 → 公开行动 (visibility=public)
   - /action text → 私密行动 (visibility=private)
3. /end_round 或所有玩家已行动
   → Round.resolve():
     a. DEX 降序排序，DEX 相同则 user_id 升序（确定性）
     b. 按序执行规则检定
     c. 私密结果 DM 玩家
     d. 公开结算发送大厅
4. 进入下一轮 COLLECTING
```

## Local Models

| 用途       | 默认模型                  |
| --------- | ------------------------ |
| Narrator  | `qwen3:4b-instruct-2507-q4_K_M` |

Narrator 目前为 `SimpleNarrator` placeholder，接入 ollama 后替换 `narrator/client.py`。

## 当前状态

**已实现：**
- 7 包架构（discord_bot / scene / adventure / character / narrator / rules / store）
- d100 完整规则（骰子/技能/战斗/SAN/衍生属性）
- 对话式建卡流程
- 回合状态机（COLLECTING → RESOLVING → NARRATING）
- 确定性排序（DEX desc + user_id asc）
- 49 个测试，`smoke-check` 通过

**待完成（P0 阻塞）：**
- 接入 ollama 替换 SimpleNarrator placeholder
- Round.resolve() 真实调用 rules 系统
- Discord 消息路由（玩家大厅文字 → handle_response）
- AdventureLoader 接入真实模组 JSON/YAML 数据
- /roll 命令实现

**交付前检查：**
```powershell
uv run pytest -q
uv run python -m dm_bot.main smoke-check
```

## Commands Reference

```powershell
uv run python -m dm_bot.main preflight      # 查看配置状态
uv run python -m dm_bot.main smoke-check    # 冒烟测试
uv run python -m dm_bot.main run-bot        # 启动 bot
```
