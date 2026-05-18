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
                       ┌───────────────────────────────────────┐
                       │           Discord Users               │
                       └──────────────┬────────────────────────┘
                                      │ slash commands / messages
                                      ▼
                       ┌───────────────────────────────────────┐
                       │    discord_bot / commands.py          │
                       │    /start /begin_module /action       │
                       │    /roll /sheet /end_round /status    │
                       └──────┬──────────┬──────────┬──────────┘
                              │          │          │
         ┌────────────────────┘          │          └──────────────────┐
         │                               │                            │
         ▼                               ▼                            ▼
 ┌───────────────┐            ┌──────────────────┐       ┌──────────────────┐
 │ surface/      │            │ scene/ round.py   │       │ narrator/        │
 │ SessionBoard  │            │ WAITING→COLLECTING│       │ SimpleNarrator   │
 │ SceneBoard    │            │ →RESOLVING→NARRATE│       │ (placeholder)    │
 │ BlockerBoard  │            └──────┬───────────┘       └──────────────────┘
 │ Consequence   │                   │
 │ Board         │                   │ fires TriggerEvent
 │ ClueBoard     │                   ▼
 │ Character     │            ┌────────────────────────────────┐
 │ CardBoard     │            │ trigger/ engine.py             │
 │ CharListBoard │            │ TriggerEngine                  │
 │ Board (ABC)   │            │ → match event_type             │
 └───────────────┘            │ → collect reactions            │
                              │ → sort by priority             │
                              │ → create TriggerChain          │
                              │ → record audit trail            │
                              │ → persist to Store             │
                              │ → resume / recover chains      │
                              └──────────┬─────────────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │                                         │
                    ▼                                         ▼
       ┌──────────────────────┐              ┌──────────────────────┐
       │ reveal/ checker.py   │              │ publish/             │
       │ RevealChecker        │              │ Publisher            │
       │ is_clue_visible()    │              │ 6 typed event models │
       │ gate + knowledge     │              │ visibility filtering  │
       │ enforcement          │              │ RendererContract ABC │
       └──────────────────────┘              └──────────────────────┘
                    │                                         │
                    └────────────────┬────────────────────────┘
                                     │
                                     ▼
                    ┌───────────────────────────────────────────┐
                    │           character/                      │
                    │   CharacterSheet (COC stats + skills)     │
                    │   CharacterArchive (versioned wrapper)    │
                    │   CharacterBuilder (conversational)       │
                    │   FullPathBuilder (heuristic fallback)    │
                    │   SessionCheckpoint (post-session)        │
                    │   AdventureLog (structured history)       │
                    │   Importer (JSON paste import)            │
                    │   Validation (COC legality rules)          │
                    └───────────────────────────────────────────┘
                                     │
                                     ▼
                    ┌───────────────────────────────────────────┐
                    │           rules/                          │
                    │   dice.py         ─── 百分骰系统          │
                    │   coc/skills.py   ─── 80+ 技能/检定       │
                    │   coc/combat.py   ─── 格斗/射击/摔跤/闪避 │
                    │   coc/sanity.py   ─── SAN/疯狂/运气       │
                    │   coc/derived.py  ── 衍生属性计算          │
                    │   coc/experience.py ── 技能提升/成长       │
                    └───────────────────────────────────────────┘
                                     │
                                     ▼
                    ┌───────────────────────────────────────────┐
                    │           store / db.py                   │
                    │   SQLite: sessions, characters, blockers, │
                    │   trigger_chains, audit_entries,          │
                    │   reveal_gates, schema_version            │
                    │   soft delete, integrity check            │
                    └───────────────────────────────────────────┘
```

## 模块说明

| Package       | Responsibility                                           |
| ------------- | -------------------------------------------------------- |
| `discord_bot` | Discord I/O：7 slash commands、消息路由                    |
| `scene`       | 回合状态机：WAITING → COLLECTING → RESOLVING → NARRATING |
| `adventure`   | 模组数据：Adventure / Scene / NPC / Clue / TriggerRef    |
| `trigger`     | 触发器引擎：TriggerEvent 匹配、Reaction 排序、Blocker 检查点 |
| `reveal`      | 揭露门系统：RevealGate、KnowledgeState、RevealChecker    |
| `publish`     | 发布事件：6 种结构化事件（Action/Clue/Scene/Blocker/...） |
| `surface`     | Discord 信息面板：7 个 Board + SessionContext            |
| `character`   | 角色系统：CharacterSheet / Archive / Builder / Checkpoint |
| `narrator`    | AI 叙事层（接入 ollama 前为 placeholder）                 |
| `rules`       | d100 规则：骰子、技能、战斗、SAN、成长                    |
| `store`       | SQLite 持久化层：10 个表，schema 版本管理，完整性检查      |

## Project Layout

```
src/dm_bot/
  discord_bot/       commands.py — 7 slash commands
  scene/             state.py / action.py / round.py
  adventure/         models.py / loader.py (JSON file loading)
  trigger/           models.py / engine.py (chain lifecycle, audit, resume)
  reveal/            models.py / checker.py (gate visibility enforcement)
  publish/           models.py / publisher.py / contract.py
  surface/           board.py / session_board / scene_board / blocker_board /
                     consequence_board / clue_board / character_board /
                     session_context / view_payload / discord_formatter
  character/         sheet.py / archive.py / builder.py / checkpoint.py /
                     adventure_log.py / importer.py / validation.py
  narrator/          client.py / prompts.py
  rules/             dice.py + coc/ (skills, combat, sanity, experience)
  store/             db.py (11 tables, schema versioning, integrity checks)
  config.py          Settings (Pydantic, .env)
  main.py            Entry: preflight / run-bot / smoke-check
```

## Setup

```powershell
# 1. 复制环境变量
cp .env.example .env

# 2. 填写 .env
DM_BOT_DISCORD_TOKEN=your_token_here
DM_BOT_DISCORD_GUILD_ID=your_guild_id

# 3. 安装依赖
uv sync

# 4. 确保 Ollama 已拉好模型（可选）
ollama pull qwen3:4b-instruct-2507-q4_K_M

# 5. 启动前检查
uv run python -m dm_bot.main preflight
uv run python -m dm_bot.main smoke-check

# 6. 启动 bot
uv run python -m dm_bot.main run-bot
```

## Discord Commands

**角色管理（私密）：**
- `/start` — 对话式建卡
- `/sheet` — 查看角色卡
- `/roll <技能>` — 技能检定

**游戏流程（公开）：**
- `/begin_module <模组名>` — 开始模组（支持 .json 文件）
- `/action <描述>` — 私密行动提交
- 普通消息 → 公开行动
- `/end_round` — 结算当前回合（DEX 排序 + 触发引擎）
- `/status` — 查看 session/场景/拦截点/线索 状态

## Round Flow

```
1. /begin_module → Round 进入 COLLECTING
2. 玩家提交行动（公开消息或 /action）
   → submit_action() fires TriggerEvent("action.submit")
   → TriggerEngine 匹配触发器 → 创建 TriggerChain → 审计
3. /end_round 或所有玩家已行动
   → resolve():
     a. DEX 降序 + user_id asc 排序（确定性）
     b. 按序执行规则检定
     c. fires TriggerEvent("round.resolve")
     d. 私密结果 DM 玩家，公开结算发送大厅
4. 下一轮 COLLECTING
```

## 当前状态 (2026-05-19)

**已实现（187 个测试，全部通过）：**
- S2 触发器系统：事件匹配、反应排序、Blocker 检查点
- S3 可恢复链 + 审计：TriggerChain 生命周期、Store 持久化、进程重启恢复
- S4 揭露门：RevealGate 条件控制、KnowledgeState 玩家独立知识
- S5 发布事件：6 种类型事件、可见性标记（全员/KP/私密）
- S6 运行时硬化：Schema 版本管理、AdventureLoader JSON 加载、完整性检查
- S7 信息面板：SessionBoard / SceneBoard / BlockerBoard / ConsequenceBoard
- S8 线索面板 + 视图分离：ViewPayload → DiscordFormatter 解耦
- S9 角色面板：CharacterCardBoard / CharacterListBoard / Session 角色绑定
- S11 角色档案：CharacterArchive 版本包装、Store CRUD、双路径建卡
- S12 数据生命周期：JSON 导入、软/硬删除、COC 合法性校验
- S13 会话集成：SessionCheckpoint 技能提升、AdventureLog 结构化日志
- S14 Ops：增强 preflight、smoke-check 区分模块/存储失败

**待完成：**
- S10 交互式 UI：按钮/选择菜单/Activity UI（需要视觉验证）
- S15 诊断：测试场景标准化、故障诊断
- 接入真实 ollama 模型替换 SimpleNarrator
- /roll 真实调用 rules 系统
- Discord 消息路由（玩家大厅文字 → trigger 引擎）

## Commands Reference

```powershell
uv run python -m dm_bot.main preflight      # 详细系统诊断
uv run python -m dm_bot.main smoke-check    # 模块 + 存储检查
uv run python -m dm_bot.main run-bot        # 启动 Discord bot
```
