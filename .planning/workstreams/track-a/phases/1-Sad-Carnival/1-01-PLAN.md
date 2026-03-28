---
phase: 1-Sad-Carnival
plan: '01'
type: execute
wave: '1'
depends_on: []
files_modified:
  - src/dm_bot/adventures/sad_carnival.json
autonomous: true
requirements:
  - MOD-01
  - MOD-02
  - MOD-03

must_haves:
  truths:
    - 凄夜的游乐场模组以结构化 JSON 格式存在
    - 包含 room graph 定义
    - 包含触发器系统
    - 包含结局条件
  artifacts:
    - added: src/dm_bot/adventures/sad_carnival.json (+702 行)
---

<objective>
迁移「凄夜的游乐场」为结构化 COC 模组格式
</objective>

<context>
@src/dm_bot/adventures/sad_carnival.json (新增文件)
</context>

<tasks>

<task type="auto">
  <name>Task 1: 创建 sad_carnival.json 结构化模组</name>
  <files>src/dm_bot/adventures/sad_carnival.json</files>
  <action>
    创建新模组文件，包含：
    - 模组元数据 (title, description, difficulty)
    - room graph (地点节点和连接)
    - 触发器系统
    - 结局条件定义
  </action>
  <verify>
    <manual>检查模组文件是否包含完整结构</manual>
  </verify>
  <done>sad_carnival.json 创建完成</done>
</task>

</tasks>

<verification>
- [ ] sad_carnival.json 文件存在
- [ ] 包含 room graph 定义
- [ ] 包含触发器系统
- [ ] 包含结局条件
</verification>

<success_criteria>
1. MOD-01: 凄夜的游乐场模组包含完整的 room graph
2. MOD-02: 凄夜的游乐场模组支持触发器系统
3. MOD-03: 凄夜的游乐场模组定义结局条件
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-a/phases/1-Sad-Carnival/1-01-SUMMARY.md`
