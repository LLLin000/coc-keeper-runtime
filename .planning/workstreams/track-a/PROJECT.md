# Track A: 模组与规则运行层

## What This Is

Track A 负责 COC 规则权威和模组运行时真相。

## Core Value

Owns canonical play truth:
- COC rules authority
- module schema
- room/scene/event graphs
- trigger trees and consequence chains
- reveal policy, private knowledge, endings

## Typical Work

- complex module runtime
- reusable module authoring contracts
- rule resolution and state mutation

## Out of Scope

- Discord UX polish as the main goal
- archive UI as the main goal
- prose quality polish as the main goal

## vA.1.1 Scope

基于 PR #1 贡献者 tanlearner123 的工作：

- `sad_carnival.json` - 凄夜的游乐场结构化模组
- `mad_mansion.json` - 疯狂之馆触发器增强 + 结局扩展
- `fuzhe.json` - 覆辙模组结构化完善

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| 模组 JSON 格式 | 使用结构化 schema 包含 room graph, triggers, endings |
| 触发器系统 | 支持条件触发和后果链 |
| 地点扩展 | 支持多地点场景图 |

---

_See main PROJECT.md for full project context._
