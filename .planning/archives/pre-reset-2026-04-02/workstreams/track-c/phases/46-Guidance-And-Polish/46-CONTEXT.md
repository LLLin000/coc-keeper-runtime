# Phase 46: Guidance & Polish - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning
**Mode:** Auto-generated (proceeding with existing plan)

<domain>
## Phase Boundary

Add user guidance and reduce command clutter in game halls.

Purpose: Improve user experience with better onboarding and cleaner channel usage.
Output: Welcome messages, command output improvements, and diagnostics channel discipline.

</domain>

<decisions>
## Implementation Decisions

### Execution Mode
Proceeding with existing detailed plan (46-01-PLAN.md) which contains:
- Task 1: Welcome message with channel structure
- Task 2: Long outputs ephemeral mode
- Task 3: Diagnostic commands channel discipline  
- Task 4: Gameplay narration channel enforcement

### the agent's Discretion
All implementation choices are guided by the existing plan tasks and verification criteria.

</decisions>

<code_context>
## Existing Code Insights

From PLAN.md context references:
- src/dm_bot/discord_bot/commands.py
- src/dm_bot/discord_bot/client.py

Key files to modify:
- commands.py: ephemeral mode checks, channel discipline
- client.py: welcome message / setup guidance

</code_context>

<specifics>
## Specific Requirements

From REQUIREMENTS.md:
- GUIDE-03: New users get welcome message with channel structure
- CLUTTER-01: Long command outputs use ephemeral mode
- CLUTTER-02: Diagnostic commands prefer trace/admin channels
- CLUTTER-03: Gameplay narration stays in game halls

</specifics>

<deferred>
## Deferred Ideas

None - all requirements addressed in current plan.

</deferred>
