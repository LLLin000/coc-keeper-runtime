# GSD Workflow Issues Debug Report

**Date:** 2026-03-31
**Status:** RESOLVED - AGENTS.md fixed
**Resolved:** 2026-03-31

---

## Issue 1: init manager reads wrong ROADMAP

### Summary
`init manager` is reading phases 40, 60, 61, etc. (old phases from vE.1.1 and vE.2.1) instead of the current vE.3.1 phases (E73-E78).

### Root Cause Analysis

**The Problem:**
The `cmdInitManager` function in `init.cjs` (line 765-1010) uses `extractCurrentMilestone()` to filter the ROADMAP content, but this function has a critical flaw in how it determines the "current milestone."

**Evidence from Code:**

1. **In `core.cjs` lines 803-870**, `extractCurrentMilestone()` tries to find the current milestone by:
   - First: Reading `milestone:` from STATE.md frontmatter
   - Second: Looking for 🚧 in-progress marker in ROADMAP.md
   - Fallback: Returning all non-shipped milestones

2. **The STATE.md frontmatter issue:**
   Looking at `track-e/STATE.md`:
   ```yaml
   ---
   gsd_state_version: 1.0
   milestone: v1.0          <-- PROBLEM: This is WRONG!
   milestone_name: milestone
   status: Milestone complete
   ```

   The STATE.md has `milestone: v1.0` which doesn't match the actual current milestone `vE.3.1`. This causes `extractCurrentMilestone()` to fail to find a matching section in the ROADMAP.

3. **The fallback behavior:**
   When no matching milestone is found, `extractCurrentMilestone()` falls back to `stripShippedMilestones()`, which returns ALL non-shipped milestone sections. This includes:
   - vE.1.1 phases (40-43)
   - vE.2.1 phases (60-68)
   - vE.2.2 phases (69-72)
   - vE.3.1 phases (73-78) - the actual current milestone

4. **The phase pattern matching:**
   In `init.cjs` line 784, the regex `/#{2,4}\s*Phase\s+(\d+[A-Z]?(?:\.\d+)*)\s*:\s*([^\n]+)/gi` matches ALL phases from ALL non-shipped milestones, not just the current one.

### Why This Happens

The STATE.md frontmatter has an incorrect `milestone: v1.0` value that doesn't match the actual workstream milestone naming convention (`vE.3.1`). When `extractCurrentMilestone()` can't find a section matching "v1.0", it returns all non-shipped content.

### Recommended Fix

**Option A: Fix STATE.md frontmatter (Immediate)**
Update `.planning/workstreams/track-e/STATE.md` frontmatter:
```yaml
---
gsd_state_version: 1.0
milestone: vE.3.1          # Change from v1.0 to vE.3.1
milestone_name: "Character Lifecycle E2E"
status: in_progress        # Change from "Milestone complete"
---
```

**Option B: Improve extractCurrentMilestone() (Long-term)**
In `core.cjs`, enhance the milestone detection to:
1. Check for workstream-prefixed milestone names (vE.X.X, vB.X.X)
2. Use the `active-workstream` file to derive the expected milestone prefix
3. Look for 🚧 marker BEFORE reading STATE.md (prioritize explicit markers)

**Option C: Add workstream-aware milestone detection**
The `extractCurrentMilestone()` function should accept the workstream name and use it to filter milestone sections (e.g., if workstream is "track-e", look for milestones matching `vE.*`).

---

## Issue 2: plan phase spawns general instead of gsd-planner

### Summary
When the manager workflow dispatches a plan phase action, it spawns a `general` subagent instead of the `gsd-planner` subagent.

### Root Cause Analysis

**The Problem:**
The manager workflow (`manager.md`) uses `Task()` to spawn background agents for plan/execute phases, but it's spawning a generic agent rather than the specific GSD subagent types.

**Evidence from Code:**

1. **In `manager.md` lines 209-234**, the Plan Phase handler spawns a background Task:
   ```markdown
   Task(
     description="Plan phase {N}: {phase_name}",
     run_in_background=true,
     prompt="You are running the GSD plan-phase workflow for phase {N}...
     
     ...
     
     5. Spawn a gsd-planner subagent via Task() to create the plans.
     6. If plan-checker is enabled, spawn a gsd-plan-checker subagent to verify.
     ..."
   )
   ```

2. **The prompt instructs the spawned agent to spawn gsd-planner**, but the Task itself doesn't specify `subagent_type`.

3. **According to AGENTS.md conventions**, the correct subagent types are:
   - `gsd-planner` — Creates detailed plans from phase scope
   - `gsd-plan-checker` — Reviews plan quality before execution
   - `gsd-executor` — Executes GSD plans
   - `gsd-verifier` — Verifies phase goal achievement

4. **The manager workflow is spawning a generic Task agent**, which then needs to spawn the actual GSD subagent. This is an extra layer of indirection that shouldn't be necessary.

### Why This Happens

The manager workflow was designed to spawn a "coordinator" agent that would then spawn the actual planner/executor. But this:
- Adds unnecessary complexity
- Loses the specific subagent context and capabilities
- Makes debugging harder
- Goes against the GSD convention of spawning specialized agents directly

### Recommended Fix

**Update `manager.md` to spawn the correct subagent types directly:**

For Plan Phase (lines 209-234), change from:
```markdown
Task(
  description="Plan phase {N}: {phase_name}",
  run_in_background=true,
  prompt="You are running the GSD plan-phase workflow...
  
  5. Spawn a gsd-planner subagent via Task() to create the plans."
)
```

To:
```markdown
Task(
  description="Plan phase {N}: {phase_name}",
  subagent_type="gsd-planner",
  run_in_background=true,
  prompt="You are the GSD planner for phase {N}...
  
  Create detailed PLAN.md files for this phase following the plan-phase workflow.
  Read the workflow at: C:/Users/Lin/.opencode/get-shit-done/workflows/plan-phase.md
  Run: node \"C:/Users/Lin/.opencode/get-shit-done/bin/gsd-tools.cjs\" init plan-phase {N}"
)
```

Similarly for Execute Phase (lines 244-278), spawn `gsd-executor` directly.

---

## Summary Table

| Issue | Root Cause | Fix Location | Priority |
|-------|-----------|--------------|----------|
| Wrong ROADMAP read | STATE.md has incorrect `milestone: v1.0` instead of `vE.3.1` | `.planning/workstreams/track-e/STATE.md` | High |
| Wrong ROADMAP read | `extractCurrentMilestone()` fallback returns all non-shipped milestones | `core.cjs` lines 803-870 | Medium |
| General agent spawned | Manager workflow spawns generic Task instead of specific subagent | `manager.md` lines 209-278 | High |

---

## Files Changed

1. `.planning/workstreams/track-e/STATE.md` - Fix frontmatter milestone field
2. `C:/Users/Lin/.opencode/get-shit-done/workflows/manager.md` - Update Task spawning to use correct subagent_type
3. `C:/Users/Lin/.opencode/get-shit-done/bin/lib/core.cjs` (optional) - Improve milestone detection

---

## Verification Steps

After applying fixes:

1. **Test init manager:**
   ```bash
   node "C:/Users/Lin/.opencode/get-shit-done/bin/gsd-tools.cjs" init manager
   ```
   Should show only phases E73-E78, not 40-72.

2. **Test plan-phase dispatch:**
   Run `/gsd-manager` and select a "Plan Phase" action.
   Should spawn `gsd-planner` subagent directly (visible in logs).

3. **Verify active workstream:**
   ```bash
   cat .planning/active-workstream
   ```
   Should output: `track-e`
