<!-- GSD:project-start -->
## Project

**Discord AI Keeper**

本项目是一个运行在 Discord 里的、本地模型驱动的 **Call of Cthulhu Keeper 系统**。它不是单纯的聊天 bot，而是一个把 Discord、COC 规则、结构化模组运行时、长期角色档案和 AI 叙事层拼在一起的多人跑团框架。

核心目标：

- 多个真人玩家在 Discord 里直接跑团
- AI 负责 Keeper 叙事、NPC 扮演、场景推进
- 规则、模组状态、线索揭露、后果链尽量由系统托管
- 模组不是纯提示词，而是可结构化、可迁移、可复用的数据
- 长期角色和模组内实例分离，方便跨模组持续使用

**Core Value:** Run real multiplayer Call of Cthulhu sessions in Discord where a local AI Keeper can narrate, roleplay NPCs, and enforce COC rules without constant manual bookkeeping.

### Constraints

- **Platform**: Discord-first — the system must work naturally in Discord channels or threads because that is the chosen runtime surface.
- **Inference**: Local models — narration and control should run through local model infrastructure rather than a hosted LLM dependency.
- **Target Hardware**: Consumer local machine — the default stack should remain practical on `8GB`-class consumer GPUs with `32GB` system RAM.
- **Architecture**: Reuse mature projects first — stable existing tools, APIs, and datasets should be integrated before writing custom subsystems.
- **Rules Scope**: Heavy COC rules support in v1 — percentile checks, SAN, success grades, pushed rolls, and combat resolution are not optional side features.
- **Delivery**: First release should optimize for campaign-usable reliability over maximal scope — reducing integration and debugging cost is a priority.

### Product Tracks

项目按 4 条长期 Track 理解：

- **Track A: 模组与规则运行层** — COC 规则、模组 schema、room/scene/event graph、trigger、consequence、reveal policy
- **Track B: 人物构建与管理层** — builder、archive、profile lifecycle、campaign projection、管理员角色治理
- **Track C: Discord 交互层** — slash commands、频道职责、自然消息、ephemeral/DM、启动与交付检查
- **Track D: 游戏呈现层** — Keeper 风格呈现、提示边界、线索板/历史板/角色板的可读性和沉浸感

### Global Rules

1. 每个 milestone 必须有一个主 Track。
2. 数值真相、规则真相、状态真相不能只靠 prompt，必须来自本地规则书、确定性代码或显式模组特规。
3. 关键状态变化必须可持久化、可审计。
4. 宣称"可交付"前，至少要通过：`uv run pytest -q` 和 `uv run python -m dm_bot.main smoke-check`
5. 新功能优先做成可复用 runtime 能力，而不是单模组硬编码。
<!-- GSD:project-end -->

<!-- GSD:architecture-start -->
## Architecture

### System Diagram

```
Discord Users
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Discord Bot Layer                                      │
│  (slash commands / normal messages / streaming)        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Session Orchestrator                                   │
│  (campaign binding / channel roles / turn coordination) │
└───────┬─────────┬─────────┬─────────┬─────────────────┘
        │         │         │         │
        ▼         ▼         ▼         ▼
┌───────────┐ ┌─────────┐ ┌──────────┐ ┌────────────────┐
│ Adventure  │ │ COC     │ │ Model    │ │ Persistence &  │
│ Runtime    │ │Character│ │ Layer    │ │ Diagnostics   │
│            │ │ Layer   │ │          │ │               │
│(room graph │ │(archive │ │Router    │ │SQLite         │
│ scene graph│ │ builder │ │qwen3:1.7b│ │event log      │
│ trigger    │ │ panels) │ │          │ │session recovery│
│ tree       │ │         │ │Narrator  │ │               │
│            │ │         │ │qwen3:4b  │ │               │
└────────────┘ └─────────┘ └──────────┘ └───────────────┘
```

### Key Layers

- **Discord 层** — slash commands、普通消息监听、分频道职责、流式输出
- **Session / Orchestrator 层** — campaign 绑定、turn 协调、角色投影、模式切换、消息路由
- **Adventure Runtime 层** — 模组结构、room graph、scene/event graph、trigger tree、reveal policy、结局条件
- **Rules 层** — COC 骰子、成功等级、SAN、明确的规则结算
- **Character / Archive 层** — 长期调查员档案、对话建卡、调查员面板、模组实例投影
- **Model 层** — `router` 负责结构化判断，`narrator` 负责叙事和角色表演
- **Persistence / Diagnostics 层** — SQLite、事件日志、状态恢复、调试摘要

### Local Models

- **Router**: `qwen3:1.7b` — 快、稳定、结构化判断
- **Narrator**: `qwen3:4b-instruct-2507-q4_K_M` — 中文稳、适合 Keeper 叙事

### Project Layout

```
src/dm_bot/
  adventures/      structured modules, graphs, triggers, extraction
  characters/      import sources and base character models
  coc/             archive, builder, panels, COC asset handling
  diagnostics/     runtime summaries and debug output
  discord_bot/     Discord client, commands, streaming transport
  gameplay/        combat and scene presentation helpers
  models/          Ollama/OpenAI-compatible client and model schemas
  narration/       narrator prompt and response shaping
  orchestrator/    turn pipeline, session runtime, gameplay integration
  persistence/     SQLite-backed state store
  router/          structured turn routing contracts and service
  rules/           dice, COC checks, deterministic rule resolution
  runtime/         app health, startup checks, smoke check
```

### Design Principles

- **状态真相不交给模型** — AI 可以说话、提问、总结，但 canonical truth 必须落在结构化状态、规则结算和触发器执行里
- **模组优先结构化** — 模组应该有 room/scene/event graph、trigger tree、state fields、reveal gates
- **规则和叙事分离** — 规则层决定能不能、发生了什么；叙事层决定怎么把这件事说得像 Keeper
- **长期角色和模组实例分离** — 玩家档案是长期资产；模组里的 SAN、秘密、入口身份、临时状态是实例状态
- **优先复用成熟方案** — 骰子、Discord 调度、TRPG 交互模式优先参考成熟项目
<!-- GSD:architecture-end -->

<!-- GSD:conventions-start -->
## Conventions

### Code Conventions

- **Python**: Follow `uv` + Pydantic v2 + SQLAlchemy 2.0 stack
- **Type Safety**: Never suppress type errors with `as any`, `@ts-ignore`, `@ts-expect-error`
- **Error Handling**: Never use empty catch blocks `catch(e) {}`
- **Testing**: Never delete failing tests to "pass" — fix root causes instead
- **Bugfix Rule**: Fix minimally. NEVER refactor while fixing.

### Git Conventions

- Branch naming: `codex/<feature-name>`
- Commit message format: `type: description` (e.g., `feat: add character archive`)
- Primary Track must be declared in commit messages for cross-track changes
- Run `uv run pytest -q` and `uv run python -m dm_bot.main smoke-check` before pushing

### GSD Workflow Conventions

- **Entry Points** (use these commands, not direct file edits):
  - `/gsd-quick` — small fixes, doc updates, ad-hoc tasks
  - `/gsd-debug` — investigation and bug fixing
  - `/gsd-plan-phase` — plan a new phase
  - `/gsd-execute-phase` — execute a planned phase
  - `/gsd-discuss-phase` — clarify phase scope and approach
  - `/gsd-verify-work` — verify completed work
  - `/gsd-map-codebase` — understand codebase structure
  - `/gsd-add-phase`, `/gsd-insert-phase`, `/gsd-remove-phase` — manage roadmap
  - `/gsd-plan-milestone-gaps` — find missing phases
  - `/gsd-pause-work`, `/gsd-resume-work` — pause/resume work sessions
  - `/gsd-new-milestone` — create new milestone
  - `/gsd-audit-milestone`, `/gsd-complete-milestone` — milestone lifecycle
  - `/gsd-set-profile`, `/gsd-set-model` — agent configuration
  - `/gsd-settings` — view current settings

- **Subagent Invocation**: Use `task(subagent_type="general", ...)` NOT `subagent_type="task"`
- **GSD Tools CLI**: `node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs"`
- **Do NOT** spawn `gsd-planner` via Task subagent — use `/gsd-plan-phase` CLI command directly. Nesting Task agents causes runtime hangs.

### Cross-Track Change Convention

When a change impacts multiple tracks, commit/PR descriptions must state:
- `Primary Track`
- `Secondary Impact`
- `Contracts Changed`
- `Migration Notes`

### Delivery Gate

Before claiming any work is complete:
1. Run `uv run pytest -q` — all tests must pass
2. Run `uv run python -m dm_bot.main smoke-check` — must pass
3. Diagnostics must be clean on all changed files
4. Evidence before assertions — verify before claiming success
<!-- GSD:conventions-end -->

<!-- GSD:workflow-start -->
## GSD Workflow Enforcement

**Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.**

### Command Reference (gsd-opencode v1.22.4)

| Command | Purpose |
|---------|---------|
| `/gsd-quick` | Small fixes, doc updates, ad-hoc tasks |
| `/gsd-debug` | Investigation and bug fixing |
| `/gsd-plan-phase` | Plan a new phase (supports `--prd`, `--auto`, `--skip-research`, `--skip-verify`) |
| `/gsd-execute-phase` | Execute a planned phase (wave-based, checkpoint handling) |
| `/gsd-discuss-phase` | Clarify phase scope and approach |
| `/gsd-verify-work` | Verify completed work against phase goals |
| `/gsd-map-codebase` | Understand codebase structure |
| `/gsd-add-phase` | Add phase to roadmap |
| `/gsd-insert-phase` | Insert phase at specific position |
| `/gsd-remove-phase` | Remove phase from roadmap |
| `/gsd-plan-milestone-gaps` | Find missing phases in roadmap |
| `/gsd-pause-work` | Pause current work session |
| `/gsd-resume-work` | Resume paused work session |
| `/gsd-new-milestone` | Create new milestone |
| `/gsd-audit-milestone` | Audit milestone completeness |
| `/gsd-complete-milestone` | Complete and archive milestone |
| `/gsd-set-profile` | Set agent developer profile |
| `/gsd-set-model` | Set agent model |
| `/gsd-settings` | View current settings |
| `/gsd-help` | Show available commands |
| `/gsd-update` | Update gsd-opencode |
| `/gsd-whats-new` | Show what's new |

### Phase Planning Flow

```
1. /gsd-plan-phase E## --prd <roadmap-file>   # Load phase context from roadmap
2. [Optional] /gsd-discuss-phase              # Clarify scope before planning
3. /gsd-execute-phase --auto                  # Auto-chain: plan → verify → execute
```

**Plan-Phase Options:**
- `--prd <filepath>` — Generate CONTEXT.md directly from PRD file (express path)
- `--auto` — Chain plan → verify without user input
- `--skip-research` — Skip research step
- `--skip-verify` — Skip verification step
- `--gaps` — Find missing phases in roadmap

**Execute-Phase Options:**
- `--auto` — Continue executing without prompting between waves
- `--no-transition` — Skip transition animations (used in auto-chain)

### Key gsd-tools Commands

```bash
# Initialize plan phase
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" init plan-phase "$PHASE"

# Initialize execute phase  
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" init execute-phase

# Get current phase plan index
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" phase-plan-index

# Mark phase complete
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" phase complete "$PHASE_NUMBER"
```

### Subagent Type

**Always use**: `task(subagent_type="general", ...)`  
**Never use**: `task(subagent_type="task", ...)` (deprecated v1.20.5)

### Do NOT

- Make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it
- Use colon prefix `/gsd:` — use hyphen prefix `/gsd-` instead
- Suppress type errors with `as any` or `@ts-ignore`
- Use empty catch blocks
- Delete failing tests to "pass"
- Leave code in broken state after failures
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-set-profile` to generate your developer profile.
> This section is managed by `generate-claude-profile` — do not edit manually.
<!-- GSD:profile-end -->
