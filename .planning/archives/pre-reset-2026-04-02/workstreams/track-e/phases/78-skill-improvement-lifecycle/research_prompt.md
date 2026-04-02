<objective>
Research how to implement Phase E78: Skill Improvement + Full Lifecycle Scenario
Answer: "What do I need to know to PLAN this phase well?"
</objective>

<files_to_read>
- .planning/workstreams/track-e/phases/78-skill-improvement-lifecycle/78-CONTEXT.md
- .planning/workstreams/track-e/REQUIREMENTS.md
- .planning/workstreams/track-e/STATE.md
- tests/scenarios/acceptance/scen_combat_san.yaml
- tests/scenarios/acceptance/scen_character_creation.yaml
- tests/rules/coc/test_experience_and_skill_catalog.py
- src/dm_bot/rules/coc/experience.py
- src/dm_bot/testing/runtime_driver.py
</files_to_read>

<additional_context>
**Phase description:** Phase E78 — Skill Improvement + Full Lifecycle Scenario. Goal: Create an end-to-end scenario that validates the complete character lifecycle: character creation → combat → SAN loss → skill improvement → next round. Integrates all previous COC tests (attributes, combat, SAN, skills) into one comprehensive scenario.

**Phase requirement IDs (MUST address):** None specified (TBD)

**Project instructions:** Read ./AGENTS.md if exists — follow project-specific guidelines
**Project skills:** Check .claude/skills/ or .agents/skills/ directory (if either exists) — read SKILL.md files, research should account for project skill patterns
</additional_context>

<output>
Write to: .planning/workstreams/track-e/phases/78-skill-improvement-lifecycle/78-RESEARCH.md
</output>
