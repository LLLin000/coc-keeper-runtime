## OpenCode Agent Contract

这个仓库通过 OpenCode 中安装的 `get-shit-done` 运行。

把这份文件当成执行规约，不要当成资料说明书。它的目标只有三个：

- 先选对 GSD 入口
- 让 `.planning/` 始终和真实工作一致
- 禁止绕开 workflow 的随手改仓库行为

### Instruction Priority

1. Direct user request
2. This `AGENTS.md`
3. Installed GSD workflow and command files under `C:\Users\Lin\.config\opencode\get-shit-done`
4. General model defaults

If a user explicitly asks to bypass GSD for a one-off task, obey the user. Otherwise, follow GSD.

### System Boundary

这份文件只约束：

- OpenCode 命令使用方式
- GSD workflow 选择
- 本项目自己的交付门槛

不要混入别的 agent 系统。这个仓库只按 OpenCode + GSD 理解。

### Canonical GSD Installation

- Installed runtime: `C:\Users\Lin\.config\opencode\get-shit-done`
- Local source mirror for inspection: `D:\L\AI\get-shit-done-1.30.0`
- OpenCode command style: `/gsd-...`
- Do not use `/gsd:...` in this repository

### `CLAUDE.md` 与 `AGENTS.md` 的对应关系

GSD 源码、官方文档、agent 定义、workflow 提示词中，大量使用的是 `CLAUDE.md` 这个名字。

但在 OpenCode 运行时，这个角色应理解为当前仓库根目录的 `AGENTS.md`。

对本仓库，执行时按下面的映射理解：

- GSD 源码里写的 `./CLAUDE.md`
- 在 OpenCode 中等价于 `./AGENTS.md`

含义是：

- 当 GSD 官方文档说“读取 `CLAUDE.md` 中的项目约束”
- 对本仓库的 OpenCode agent 来说，应该读取并遵守 `AGENTS.md`

优先级上：

- OpenCode 运行时，以当前仓库 `AGENTS.md` 为准
- 不要因为源码里写了 `CLAUDE.md`，就以为这个仓库还需要并行维护第二套说明文件

### Golden Rules

1. Before any repo-changing work, choose and enter a GSD workflow.
2. In OpenCode, the normal entrypoint is always a slash command like `/gsd-quick` or `/gsd-plan-phase`.
3. Do not simulate a slash command by sending its text inside a generic `Task(...)`.
4. Do not treat internal workflow implementation details as user-facing entrypoints.
5. Keep `.planning/` as the canonical workflow state. Do not improvise parallel state tracking outside it.
6. Do not claim work is complete before running this project's verification gate.

### GSD 工作流模型

GSD 不是“一个命令直接做完所有事”，而是一个固定分层：

1. 用户调用 `/gsd-...` 命令
2. 对应 command 文件进入 workflow
3. workflow 作为薄编排器，只做：
   - 读取 `gsd-tools.cjs init ...` 上下文
   - 选择下一个 agent
   - 等待结果
   - 更新 `.planning/` 状态
   - 路由到下一步
4. 真正的研究、计划、执行、验证由专用 `gsd-*` subagent 完成
5. 产物落盘到 `.planning/` 后，才进入下一步

要点：

- command 是入口
- workflow 是编排器
- `gsd-*` subagent 是执行单元
- `.planning/` 是状态真相

### Fresh Context 原则

GSD 的核心设计之一是：每个专用 agent 都拿到一份新的上下文窗口。

因此：

- 不要把一个长对话线程硬扛到底
- 不要让 orchestrator 自己去做本该由 planner 或 executor 做的重活
- 不要试图在一个普通 agent 里“继续扮演”下一个 GSD 专用 agent

薄编排器负责衔接，专用 agent 负责干活。

### Subagent 边界

这是本文件最重要的补充规则。

#### 正常项目工作时

无论是 `/gsd-quick`、`/gsd-plan-phase`、`/gsd-execute-phase` 还是 `/gsd-debug`：

- 先进入对应 slash command
- 由 workflow 生成和调用正确的 `gsd-*` subagent
- subagent 完成自己的职责后，把结果返回给 orchestrator
- subagent 不再继续 spawn 另一个 subagent

一句话：

- 用户命令可以进入 workflow
- workflow 可以 spawn 专用 subagent
- 专用 subagent 默认不得继续 spawn subagent

#### 为什么要这么做

因为 GSD 官方架构就是：

- thin orchestrators
- fresh context per agent
- artifacts written to disk
- orchestrator 再决定下一步

如果让 subagent 再继续 spawn subagent，会破坏：

- 上下文边界
- 状态可追踪性
- checkpoint / continuation 机制
- workflow 的可恢复性

#### 唯一例外

只有你在维护 `get-shit-done` 自己时，才可以讨论或修改内部的 subagent wiring，例如：

- workflow 文件本身
- command 到 workflow 的路由
- installer 转换逻辑
- GSD 内部 agent 定义

那是“维护 GSD 本身”，不是“用 GSD 跑这个项目”。

### Hard Prohibitions

Never do these unless the user explicitly requests a bypass:

- edit repo files directly without first entering a GSD workflow
- paste `/gsd-plan-phase ...`, `/gsd-execute-phase ...`, `/gsd-quick ...` into a generic spawned agent as plain text
- use `/gsd:...` colon syntax
- invent new workflow entrypoints that are not installed in GSD
- ignore `.planning/active-workstream` and work against the wrong track by default
- mark a phase or task done without updating the workflow artifacts that GSD expects

### 常见工作流怎么走

#### `/gsd-quick`

默认流程是：

1. 解析任务描述
2. `init quick`
3. 必要时进入 discuss 或 research
4. workflow spawn `gsd-planner`
5. planner 产出 `.planning/quick/.../PLAN.md`
6. workflow spawn `gsd-executor`
7. executor 执行、提交、写 `SUMMARY.md`
8. workflow 更新 `STATE.md`
9. 如使用 `--full`，再走 verifier

#### `/gsd-plan-phase <phase>`

默认流程是：

1. `init plan-phase`
2. 读取 phase、state、requirements、context
3. 必要时先 research
4. workflow spawn `gsd-phase-researcher`
5. workflow spawn `gsd-planner`
6. planner 产出 `PLAN.md`
7. workflow spawn `gsd-plan-checker`
8. 如不通过，回到 planner 修订，最多有限轮次
9. 通过后由 orchestrator 给出下一步 `/gsd-execute-phase`

#### `/gsd-execute-phase <phase>`

默认流程是：

1. `init execute-phase`
2. 发现该 phase 下所有 plan
3. 按依赖分 wave
4. orchestrator 按 wave spawn `gsd-executor`
5. executor 各自执行 plan、写 `SUMMARY.md`
6. wave 完成后，orchestrator 汇总并进入下一 wave
7. 所有 plan 完成后，workflow spawn `gsd-verifier`
8. verifier 写 `VERIFICATION.md`
9. orchestrator 更新 `ROADMAP.md` / `STATE.md` 并给出后续动作

#### `/gsd-debug`

默认流程是：

1. 进入 debug workflow
2. workflow spawn `gsd-debugger`
3. debugger 负责收集证据、形成假设、验证、记录
4. 如遇 checkpoint，由 orchestrator 呈现给用户
5. continuation 是 orchestrator 生成新的 continuation agent，不是旧 agent 无限续命

### What Counts As The Correct Entry Point

Use this decision table first.

| Situation | Required entrypoint |
|---|---|
| Small fix, doc tweak, ad-hoc task, narrow refactor | `/gsd-quick` |
| Bug investigation, flaky behavior, failing tests, unclear root cause | `/gsd-debug` |
| New roadmap phase needs planning | `/gsd-plan-phase <phase>` |
| Planned phase implementation | `/gsd-execute-phase <phase>` |
| Need to clarify phase scope before planning | `/gsd-discuss-phase <phase>` |
| Need conversational validation of completed phase behavior | `/gsd-verify-work <phase>` |
| Need roadmap surgery | `/gsd-add-phase`, `/gsd-insert-phase`, `/gsd-remove-phase`, `/gsd-plan-milestone-gaps` |
| Need current-state recovery or handoff | `/gsd-pause-work`, `/gsd-resume-work`, `/gsd-progress`, `/gsd-next` |
| Need codebase understanding before planning | `/gsd-map-codebase` |
| Need autonomous milestone execution | `/gsd-autonomous` |

### Required Workflow By Task Type

#### 1. Ad-hoc work

Use `/gsd-quick` when the user asks for:

- a focused bugfix
- a small feature
- a docs update
- a test adjustment
- a contained cleanup

Escalate from `/gsd-quick` to phase workflow if the task is clearly milestone-sized, cross-cutting, or should produce durable planning artifacts for future phases.

#### 2. Planned phase work

Use:

1. `/gsd-discuss-phase <phase>` when scope is ambiguous or contains meaningful tradeoffs
2. `/gsd-plan-phase <phase>` to create executable plan artifacts
3. `/gsd-execute-phase <phase>` to implement them
4. `/gsd-verify-work <phase>` when user-facing or behavioral validation is needed

Do not jump straight to editing files for a numbered phase unless the user explicitly says to bypass GSD.

#### 3. Debugging

Use `/gsd-debug` for:

- failures with unclear cause
- repeated regressions
- scenario or integration breakage
- bugs that need persistent evidence tracking

Do not treat debugging as a normal quick task when the failure mode is still unknown.

#### 4. Resume and continuity

When the user says:

- continue
- resume
- what's next
- where were we

prefer `/gsd-resume-work` or `/gsd-progress` instead of guessing from memory.

### Subagent Rules

这是旧版最容易把 agent 带偏的地方，必须严格执行。

#### 用户态规则

对正常仓库工作，不要手动把第一步写成：

- `gsd-planner`
- `gsd-executor`
- `gsd-verifier`
- `gsd-debugger`
- 其他 `gsd-*` 专用 subagent

第一步应该是 slash command，不是专用 subagent。

#### 编排规则

允许的调用链只有这类：

- 用户 / 主 agent → `/gsd-...`
- `/gsd-...` command → workflow orchestrator
- workflow orchestrator → 一个或多个 `gsd-*` subagent
- `gsd-*` subagent → 返回结果给 orchestrator

正常项目工作里，不允许：

- 普通 agent 伪装成 workflow
- subagent 再继续 spawn subagent
- 把 workflow 内部的 subagent 例子拿来当用户态入口

#### 内部实现例外

只有在维护 GSD 自己时，才允许直接处理 `Task(subagent_type="gsd-*", ...)`：

- 编辑 GSD workflow 文件
- 修 command wiring
- 修 installer / runtime conversion
- 修 agent 定义

那属于 GSD 内部实现，不属于仓库日常开发。

#### 普通 generic task 规则

如果因为非 GSD 原因必须开一个普通 task：

- 用 `subagent_type="general"`
- 不要用废弃的 `subagent_type="task"`
- 不要把 slash command 文本丢进去假装命令执行了

### CLI Rules

GSD workflow initialization commands use:

```bash
node "C:\Users\Lin\.config\opencode\get-shit-done\bin\gsd-tools.cjs" init <subcommand>
```

Important:

- `init` is required for workflow initialization commands
- this is workflow plumbing, not the normal user-facing entrypoint
- prefer slash commands in conversation; use the CLI form only when workflow implementation or low-level inspection actually requires it

Common valid forms:

```bash
node "C:\Users\Lin\.config\opencode\get-shit-done\bin\gsd-tools.cjs" init quick "fix X"
node "C:\Users\Lin\.config\opencode\get-shit-done\bin\gsd-tools.cjs" init plan-phase E93
node "C:\Users\Lin\.config\opencode\get-shit-done\bin\gsd-tools.cjs" init execute-phase E93
node "C:\Users\Lin\.config\opencode\get-shit-done\bin\gsd-tools.cjs" init resume
node "C:\Users\Lin\.config\opencode\get-shit-done\bin\gsd-tools.cjs" init verify-work E93
```

Common invalid forms:

```bash
node gsd-tools.cjs plan-phase E93
node gsd-tools.cjs quick "fix X"
node gsd-tools.cjs new-milestone
```

### Workstream And Planning State Rules

This project uses multi-track workstreams. Always inspect the active workstream before phase work.

Canonical files:

- active workstream: `.planning/active-workstream`
- track roadmap: `.planning/workstreams/<track>/ROADMAP.md`
- track state: `.planning/workstreams/<track>/STATE.md`

Current-state lookup order:

1. Read `.planning/active-workstream`
2. Read `.planning/workstreams/<active>/STATE.md`
3. Read `.planning/workstreams/<active>/ROADMAP.md`
4. Reconcile conflicts before planning or execution

Repository-specific caution:

- if a non-active track's `STATE.md` disagrees with `.planning/active-workstream`, trust the active-workstream pointer first and treat the mismatch as workflow-state drift

Implications:

1. Default to the track named in `.planning/active-workstream` unless the user explicitly switches tracks.
2. If a phase number or milestone does not match the active workstream, stop and reconcile before planning or executing.
3. If `STATE.md` frontmatter is inconsistent with the roadmap, treat that as workflow-state drift and repair the state before relying on manager-style logic.

### Delivery Gate

Before claiming implementation work is complete, run all required project checks:

1. `uv run pytest -q`
2. `uv run python -m dm_bot.main smoke-check`

Required behavior:

- do not say "done" before these pass
- if they fail, report the failing gate plainly
- if a failure is unrelated but blocks the claim, say so explicitly
- if you changed workflow or planning files only, still avoid implying product behavior is verified unless the checks ran

### Git And Commit Conventions

- branch naming: `codex/<feature-name>`
- commit message format: `type: description`
- for cross-track changes, explicitly state:
  - `Primary Track`
  - `Secondary Impact`
  - `Contracts Changed`
  - `Migration Notes`

Do not make workflow state harder to audit:

- do not silently change `.planning/` without explaining why
- do not leave execution artifacts half-written if a workflow was supposed to own them

<!-- GSD:project-start -->
## Project Overview

**Discord AI Keeper** — 本地模型驱动的 Call of Cthulhu 跑团系统

核心目标：

- 多个真人玩家在 Discord 里直接跑团
- AI 负责 Keeper 叙事、NPC 扮演、场景推进
- 规则、模组状态、线索揭露、后果链尽量由系统托管
- 模组不是纯提示词，而是可结构化、可迁移、可复用的数据
- 长期角色和模组内实例分离，方便跨模组持续使用

**Core Value:** Run real multiplayer Call of Cthulhu sessions in Discord where a local AI Keeper can narrate, roleplay NPCs, and enforce COC rules without constant manual bookkeeping.

### Constraints

- **Platform:** Discord-first
- **Inference:** local models
- **Target Hardware:** consumer local machine, practical for `8GB`-class GPU and `32GB` RAM
- **Architecture:** prefer mature integrations before custom subsystems
- **Rules Scope:** COC rules support is required in v1
- **Delivery:** optimize for campaign-usable reliability, not maximal surface area

### Product Tracks

- **Track A:** 模组与规则运行层
- **Track B:** 人物构建与管理层
- **Track C:** Discord 交互层
- **Track D:** 游戏呈现层
- **Track E:** 运行控制与运维面板层

### Track Context

This repository uses workstreams under `.planning/workstreams/`.

Always derive the current track and phase from:

1. `.planning/active-workstream`
2. `.planning/workstreams/<active>/STATE.md`
3. `.planning/workstreams/<active>/ROADMAP.md`
<!-- GSD:project-end -->

<!-- GSD:architecture-start -->
## Architecture

### System Layers

- **Discord layer** — slash commands, normal message intake, streaming output
- **Session / orchestrator layer** — campaign binding, turn coordination, mode switching, routing
- **Adventure runtime** — structured modules, room or scene graphs, triggers, reveal policy, ending conditions
- **Rules layer** — deterministic COC dice, success grades, SAN, combat and checks
- **Character / archive layer** — long-lived investigator profiles and campaign projections
- **Model layer** — router for structured decisions, narrator for prose and roleplay
- **Persistence / diagnostics layer** — SQLite, event log, recovery, debug summaries

### Local Models

- **Router:** `qwen3:1.7b`
- **Narrator:** `qwen3:4b-instruct-2507-q4_K_M`

### Project Layout

```text
src/dm_bot/
  adventures/
  characters/
  coc/
  diagnostics/
  discord_bot/
  gameplay/
  models/
  narration/
  orchestrator/
  persistence/
  router/
  rules/
  runtime/
```

### Design Principles

- canonical state must not live only in prompts
- rules and narration are separate concerns
- module content should be structured, not only prompt-authored prose
- long-lived character truth and module-instance truth must remain separate
- critical state changes must be persistent and auditable
<!-- GSD:architecture-end -->

<!-- GSD:conventions-start -->
## Conventions

### Code Conventions

- Python stack: `uv` + Pydantic v2 + SQLAlchemy 2.0
- Never suppress type errors with `as any`, `@ts-ignore`, `@ts-expect-error`
- Never use empty catch blocks
- Never delete failing tests to make the suite pass
- For bugfixes: fix minimally, do not refactor opportunistically

### Repository Conventions

- prefer reusable runtime capabilities over module-specific hardcoding
- keep rules truth deterministic
- keep important changes auditable
- preserve existing track and phase artifacts unless intentionally updating them through workflow

### Workflow Conventions

- slash commands are the default OpenCode interface
- `gsd-tools.cjs init ...` is workflow plumbing, not the normal conversational interface
- phase work should leave plan, summary, verification, and state artifacts coherent
<!-- GSD:conventions-end -->

<!-- GSD:workflow-start -->
## Workflow Enforcement

Before using any file-changing tool, start with the correct GSD entrypoint unless the user explicitly asks to bypass it.

Use these defaults:

- `/gsd-quick` for small fixes and ad-hoc work
- `/gsd-debug` for investigation and bug fixing
- `/gsd-discuss-phase <phase>` when phase scope needs clarification
- `/gsd-plan-phase <phase>` for planning
- `/gsd-execute-phase <phase>` for implementation
- `/gsd-verify-work <phase>` for conversational UAT and follow-up gaps
- `/gsd-resume-work` or `/gsd-progress` for session recovery

Do not:

- make direct repo edits outside a GSD workflow by default
- use `/gsd:...` syntax
- send slash commands into generic tasks
- use internal GSD subagent examples as the first user-facing action
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-set-profile` or `/gsd-profile-user` if you want GSD-managed interaction preferences.
> This section is intentionally lightweight here; workflow compliance matters more than personalization.
<!-- GSD:profile-end -->

## Common Failure Modes

These are the mistakes this file is specifically trying to prevent.

### 1. Fake workflow execution

Wrong:

```python
Task(subagent_type="general", prompt="/gsd-plan-phase E93")
```

Why wrong:

- the command text is not actually executed as a slash command
- planning artifacts may never be created
- the agent will often hallucinate workflow progress

Correct:

- run `/gsd-plan-phase E93` in OpenCode

### 2. Mixing internal and external interfaces

Wrong:

- seeing `gsd-planner` in GSD source code and deciding to call it directly for normal project work

Correct:

- use `/gsd-plan-phase E93`
- let the workflow decide whether to spawn `gsd-planner`

### 2.5. Subagent 继续套娃

Wrong:

- workflow 已经 spawn 了 `gsd-planner`
- `gsd-planner` 里又继续手动 spawn `gsd-plan-checker` 或别的 `gsd-*`

Why wrong:

- 破坏 GSD 的薄编排器模型
- 让状态更新和 checkpoint 脱离 workflow
- 破坏 fresh-context 分层

Correct:

- planner 只完成 planner 自己的职责
- checker 由 workflow orchestrator 再决定是否生成

### 3. Wrong command syntax

Wrong:

- `/gsd:quick`
- `/gsd:plan-phase`

Correct:

- `/gsd-quick`
- `/gsd-plan-phase`

### 4. Trusting stale track state over active-workstream

Wrong:

- reading a stale `track-b` milestone value and planning there by default

Correct:

- honor `.planning/active-workstream`
- reconcile state drift before phase execution

### 5. Declaring success without the repo gate

Wrong:

- "done" after edits
- "tests look fine" without running them

Correct:

- run `uv run pytest -q`
- run `uv run python -m dm_bot.main smoke-check`
- then report the actual result

## Canonical Command Reference

Use these exact forms in OpenCode:

```text
/gsd-quick <task>
/gsd-debug <problem>
/gsd-discuss-phase <phase>
/gsd-plan-phase <phase>
/gsd-execute-phase <phase>
/gsd-verify-work <phase>
/gsd-map-codebase
/gsd-progress
/gsd-resume-work
/gsd-add-phase
/gsd-insert-phase <phase>
/gsd-remove-phase <phase>
/gsd-plan-milestone-gaps
/gsd-autonomous
/gsd-settings
```

If uncertain which workflow to use, prefer:

1. `/gsd-progress` to inspect state
2. `/gsd-discuss-phase <phase>` if the work is a numbered phase but still ambiguous
3. `/gsd-quick` if the task is truly narrow and ad-hoc

## Final Rule

When in doubt, optimize for workflow integrity over speed.

This repository is not harmed most by slow planning. It is harmed most by agents bypassing GSD, editing directly, and leaving `.planning/` in a state that no longer matches the real work.
