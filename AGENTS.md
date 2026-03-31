<!-- GSD:project-start -->
## Project Overview

**Discord AI Keeper** — 本地模型驱动的 Call of Cthulhu 跑团系统

> **Note**: This project uses two distinct systems that are sometimes confused:
> - **oh-my-opencode (omo)**: OpenCode plugin providing built-in agents (`sisyphus`, `oracle`, `metis`, `librarian`, etc.)
> - **gsd-opencode (gsd)**: Workflow/project management system (`/gsd-plan-phase`, `/gsd-execute-phase`, `gsd-tools.cjs`, etc.)
>
> This file focuses on **GSD conventions**. For oh-my-opencode agents, refer to OpenCode's built-in documentation.

核心目标：

- 多个真人玩家在 Discord 里直接跑团
- AI 负责 Keeper 叙事、NPC 扮演、场景推进
- 规则、模组状态、线索揭露、后果链尽量由系统托管
- 模组不是纯提示词，而是可结构化、可迁移、可复用的数据
- 长期角色和模组内实例分离，方便跨模组持续使用

**Core Value:** Run real multiplayer Call of Cthulhu sessions in Discord where a local AI Keeper can narrate, roleplay NPCs, and enforce COC rules without constant manual bookkeeping.

### Project Structure

This project uses **multi-track workstreams** for parallel development:

| Workstream | Focus | Current Milestone |
|------------|-------|------------------|
| `track-b/` | Track B - 人物构建与管理层 | vB.1.5 (next) |
| `track-e/` | Track E - 运行控制与运维面板层 | vE.2.2 (in progress) |

**Current active workstream:** `track-b` (see `.planning/active-workstream`)

To check current state:
```bash
cat .planning/active-workstream                    # Which track is active
cat .planning/workstreams/<track>/ROADMAP.md       # Track roadmap
cat .planning/workstreams/<track>/STATE.md          # Track state
```

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

**⚠️ There are TWO types of GSD commands:**

1. **Slash Commands** (for OpenCode conversation):
   - `/gsd-quick`, `/gsd-debug`, `/gsd-plan-phase`, `/gsd-execute-phase`, etc.
   - These are invoked WITH the slash prefix in OpenCode

2. **CLI Commands** (for workflow scripts):
   - `node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" init <subcommand>`
   - These are used INSIDE workflow files and scripts
   - **Must use `init` prefix** — see section below for details

**Entry Points** (use these slash commands, not direct file edits):
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
- **GSD Tools CLI**: `node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs"` (see CLI section above)
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

### Command Reference (gsd-opencode v1.22.1)

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

**Two ways to run GSD phases:**

#### 1. Autonomous Mode (Recommended for milestones)
```
/gsd-autonomous                    # Run all remaining phases automatically
/gsd-autonomous --from E77         # Start from phase E77
```

#### 2. Manual Mode (Single phase, interactive)
```
/gsd-plan-phase E77 --skip-research   # Plan phase context
/gsd-execute-phase E77 --auto          # Execute: plan → verify → execute
```

**Subagent Invocation (for spawning GSD agents directly):**
```
Task(subagent_type="gsd-executor", prompt="...", description="...")   # Execute plans
Task(subagent_type="gsd-planner", prompt="...", description="...")     # Create plans
Task(subagent_type="gsd-verifier", prompt="...", description="...")    # Verify completion
```

**⚠️ Common Mistake:** Do NOT use `Task(tool="/gsd-plan-phase")` — this just sends the slash command text to a general agent without triggering the actual workflow.

**Plan-Phase Options:**
- `--prd <filepath>` — Generate CONTEXT.md directly from PRD file (express path)
- `--auto` — Chain plan → verify without user input
- `--skip-research` — Skip research step
- `--skip-verify` — Skip verification step
- `--gaps` — Find missing phases in roadmap

**Execute-Phase Options:**
- `--auto` — Continue executing without prompting between waves
- `--no-transition` — Skip transition animations (used in auto-chain)

### gsd-tools CLI Usage

**⚠️ IMPORTANT: The `init` prefix is required for workflow commands.**

All workflow initialization commands MUST be prefixed with `init`:

```bash
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" init <subcommand>
```

**Common `init` subcommands:**

| Subcommand | Purpose | Example |
|------------|---------|---------|
| `init plan-phase <N>` | Initialize phase planning context | `init plan-phase 5` |
| `init execute-phase <N>` | Initialize phase execution context | `init execute-phase 5` |
| `init new-milestone` | Initialize new milestone workflow | `init new-milestone` |
| `init new-project` | Initialize new project workflow | `init new-project` |
| `init quick <desc>` | Initialize quick task workflow | `init quick "fix bug"` |
| `init progress` | Initialize progress check | `init progress` |
| `init resume` | Initialize resume workflow | `init resume` |
| `init verify-work <N>` | Initialize verification workflow | `init verify-work 5` |
| `init todos [area]` | Initialize todo workflow | `init todos api` |

**How `init manager` works:**

1. Reads `.planning/active-workstream` to determine current workstream
2. Reads `.planning/workstreams/<workstream>/STATE.md` to get current milestone
3. Reads `.planning/workstreams/<workstream>/ROADMAP.md` to list phases
4. Returns JSON with phases, status, and recommendations

**⚠️ Important:** `STATE.md` frontmatter must have correct `milestone` field matching ROADMAP:
```yaml
---
milestone: vE.3.1          # Must match milestone name in ROADMAP
milestone_name: "Character Lifecycle E2E"
status: in_progress        # or "complete"
---
```

If `milestone` is wrong (e.g., `v1.0`), `init manager` will show phases from ALL non-shipped milestones instead of just the current one.

**Other useful commands:**

```bash
# Roadmap operations
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" roadmap analyze
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" roadmap get-phase <N>
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" phase-plan-index <N>

# State operations
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" state load
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" state-snapshot

# Phase operations
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" phase complete <N>
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" phase add "<description>"
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" phase remove <N>

# Commit
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" commit "<message>" --files <files>
```

**Common mistakes to avoid:**

```bash
# ❌ WRONG - "new-milestone" is not a standalone command
node gsd-tools.cjs new-milestone "v1.0"

# ✅ CORRECT - must use "init" prefix
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" init new-milestone

# ❌ WRONG - "plan-phase" alone is not valid
node gsd-tools.cjs plan-phase 5

# ✅ CORRECT - must use "init" prefix
node "$HOME/.config/opencode/get-shit-done/bin/gsd-tools.cjs" init plan-phase 5
```

### Subagent Type

**Always use**: `task(subagent_type="general", ...)`  
**Never use**: `task(subagent_type="task", ...)` (deprecated v1.20.5)

### GSD Subagent Types

When spawning GSD workflow agents directly (not via slash commands), use these specific subagent types:

| Subagent Type | Purpose | When to Use |
|-------------|---------|-------------|
| `gsd-planner` | Create phase plans | Planning a phase programmatically |
| `gsd-executor` | Execute plans | Executing phase plans |
| `gsd-verifier` | Verify completion | Verifying phase goals |
| `gsd-debugger` | Debug issues | Investigating bugs |

**Example:**
```python
# Correct - spawn planner directly
Task(
    description="Plan phase E78",
    subagent_type="gsd-planner",
    prompt="Create PLAN.md for phase E78..."
)

# Incorrect - spawning general agent
Task(
    description="Plan phase E78",
    prompt="You should spawn a gsd-planner..."  # Don't do this!
)
```

### Do NOT

- Make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it
- Use colon prefix `/gsd:` — use hyphen prefix `/gsd-` instead
- Suppress type errors with `as any` or `@ts-ignore`
- Use empty catch blocks
- Delete failing tests to "pass"
- Leave code in broken state after failures
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## System Clarification

| System | What It Is | When to Use |
|--------|------------|-------------|
| **oh-my-opencode (omo)** | OpenCode plugin providing built-in agents | Use when you need: `sisyphus`, `oracle`, `metis`, `momus`, `explore`, `librarian` agents |
| **gsd-opencode (gsd)** | Workflow/project management system | Use for: `/gsd-plan-phase`, `/gsd-execute-phase`, `/gsd-quick`, milestone planning, roadmap management |

### Key Differences

**oh-my-opencode Agents:**
- `sisyphus` — Main orchestrating agent (this project's primary agent)
- `oracle` — Architecture and deep technical consultation
- `metis` — Pre-planning analysis and requirements clarification
- `momus` — Work plan review and evaluation
- `explore` — Codebase search and pattern finding
- `librarian` — External documentation and reference lookup

**gsd Commands:**
- `/gsd-plan-phase` — Create execution plans for a roadmap phase
- `/gsd-execute-phase` — Execute plans in wave-based parallelization
- `/gsd-quick` — Execute small, ad-hoc tasks with GSD guarantees
- `/gsd-discuss-phase` — Clarify phase scope before planning
- `/gsd-verify-work` — Validate built features through UAT

### GSD Subagents

GSD 系统定义了 17 个 subagents，它们通过 GSD 命令和工作流间接调用：

**⚠️ Important:** When using the `/gsd-manager` command or manager workflow, it will automatically spawn the correct subagent types. However, if you need to spawn GSD subagents directly via `Task()`, you must specify the correct `subagent_type` as shown in the table above.

#### Planning & Research
| Agent | Purpose |
|-------|---------|
| `gsd-planner` | Creates executable phase plans with task breakdown, dependency analysis, goal-backward verification |
| `gsd-plan-checker` | Verifies plans will achieve phase goal before execution (goal-backward analysis) |
| `gsd-phase-researcher` | Researches how to implement a phase before planning (produces RESEARCH.md) |
| `gsd-project-researcher` | Researches domain ecosystem before roadmap creation (4 dimensions: stack, features, architecture, pitfalls) |
| `gsd-research-synthesizer` | Synthesizes outputs from 4 parallel researcher agents into SUMMARY.md |

#### Execution & Verification
| Agent | Purpose |
|-------|---------|
| `gsd-executor` | Executes GSD plans with atomic commits, deviation handling, checkpoint protocols |
| `gsd-verifier` | Verifies phase goal achievement through goal-backward analysis (creates VERIFICATION.md) |
| `gsd-integration-checker` | Verifies cross-phase integration and E2E flows |
| `gsd-nyquist-auditor` | Fills Nyquist validation gaps by generating tests and verifying coverage |

#### Roadmap & Discussion
| Agent | Purpose |
|-------|---------|
| `gsd-roadmapper` | Creates project roadmaps with phase breakdown, requirement mapping, success criteria |
| `gsd-assumptions-analyzer` | Deeply analyzes codebase for a phase, returns structured assumptions with evidence |
| `gsd-advisor-researcher` | Researches a single gray area decision, returns comparison table with rationale |

#### UI/Frontend (Frontend phases only)
| Agent | Purpose |
|-------|---------|
| `gsd-ui-researcher` | Produces UI-SPEC.md design contract for frontend phases |
| `gsd-ui-checker` | Validates UI-SPEC.md against 6 quality dimensions (BLOCK/FLAG/PASS verdicts) |
| `gsd-ui-auditor` | Retroactive 6-pillar visual audit of implemented frontend code |

#### Utilities
| Agent | Purpose |
|-------|---------|
| `gsd-codebase-mapper` | Explores codebase and writes structured analysis documents (STACK, ARCHITECTURE, CONVENTIONS, CONCERNS) |
| `gsd-debugger` | Investigates bugs using scientific method, manages debug sessions, handles checkpoints |
| `gsd-user-profiler` | Analyzes session messages across 8 behavioral dimensions to produce developer profile |

**Note:** 这些 agents 通过 GSD 命令（如 `/gsd-plan-phase`）和工作流间接调用，不是直接通过 `task(subagent_type="...")` 调用。

### Common Mistakes

```bash
# ❌ WRONG - mixing up systems
task(subagent_type="sisyphus", ...)  # sisyphus is not a category!
task(subagent_type="gsd-planner", ...)  # Don't call GSD agents directly!

# ✅ CORRECT - use GSD slash commands
/gsd-plan-phase 5    # Plans phase through the full GSD workflow
/gsd-execute-phase 5  # Executes through the GSD orchestrator
```

## Developer Profile

> Profile not yet configured. Run `/gsd-set-profile` to generate your developer profile.
> This section is managed by `generate-claude-profile` — do not edit manually.
<!-- GSD:profile-end -->
