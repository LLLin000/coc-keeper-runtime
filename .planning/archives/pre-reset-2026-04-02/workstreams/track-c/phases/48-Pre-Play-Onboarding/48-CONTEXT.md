# Phase 48: Pre-Play Onboarding - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning
**Source:** Discuss phase with user

<domain>
## Phase Boundary

Implement structured pre-play onboarding stage that runs automatically after /start-session and before first scene narration. Onboarding presents interactive guidance covering theme, rules, and tips with KP-customizable content.

**Requirements addressed:** ONBOARD-01, ONBOARD-02, ONBOARD-03

</domain>

<decisions>
## Implementation Decisions

### Onboarding Trigger & Flow
- **ONBOARD-01:** Onboarding starts automatically after `/start-session` command completes
- Transition from `AWAITING_ADMIN_START` → `ONBOARDING` phase
- After onboarding completes (all players confirm or timeout), transition to `SCENE_ROUND_OPEN`
- No manual trigger needed — automatic flow ensures consistency

### Content Delivery Format
- **ONBOARD-02:** Interactive Discord messages with buttons
- Use button components for "Got it", "Questions?" prompts
- Include reaction options for quick polls ("Any rules questions?")
- Multiple messages in sequence (theme → rules → tips → confirm)
- Rich embeds with clear sections and formatting

### Minimum-Rules Scope
- **ONBOARD-02:** Full quick-start content:
  - Dice mechanic: percentiles, success levels, bonus/penalty dice
  - Basic gameplay loop: investigate → roll → result → narrate
  - Character sheet overview: stats, skills, SAN, HP
  - Skill check types: opposed, regular, extreme, fumble
  - SAN checks and consequences
  - Investigation tips: on the fly, libraries, interviews
- Content is comprehensive but scannable (bullet points, highlights)

### Admin Customization
- **ONBOARD-03:** Full custom possible
- Adventure package can include custom onboarding content
- KP can override any section via adventure config
- Default fallback to system templates if adventure doesn't specify
- Structure: theme → rules → tips → confirm (KP can add/remove sections)

### the agent's Discretion
- Exact timeout duration for auto-advance if players don't confirm
- Whether to track onboarding completion per-player or session-wide
- Error handling if adventure package missing onboarding content

</decisions>

<canonical_refs>
## Canonical References

**From Track C:**
- `.planning/workstreams/track-c/REQUIREMENTS.md` — vC.1.2 ONBOARD requirements
- `.planning/workstreams/track-c/phases/47-Session-Phases/47-CONTEXT.md` — Session phase model
- `.planning/workstreams/track-c/phases/47-Session-Phases/47-01-SUMMARY.md` — Phase 47 implementation summary

**From Project:**
- `src/dm_bot/discord_bot/commands.py` — Existing command implementation
- `src/dm_bot/orchestrator/session_store.py` — Session phase state management

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- SessionPhase enum already includes `ONBOARDING` phase
- `/start-session` command already implemented
- Phase transition methods exist: `transition_to()`, `get_phase_context()`

### Established Patterns
- Discord rich embeds used in existing commands
- Button interactions available via discord.py
- Phase transitions logged with timestamps

### Integration Points
- Onboarding flow connects to session_store.py CampaignSession
- Content sourced from adventure package or defaults
- Uses existing Discord message delivery infrastructure

</code_context>

<specifics>
## Specific Ideas

- "Full quick-start" — comprehensive but scannable onboarding
- "Interactive" — use Discord buttons for engagement
- "Full custom possible" — adventure packages can override

</specifics>

<deferred>
## Deferred Ideas

- Scene round collection (ROUND-01, ROUND-02, ROUND-03) — Phase 49
- Message intent routing (INTENT-01, INTENT-02, INTENT-03) — Phase 50
- Campaign/adventure visibility (VIS-01, VIS-02, VIS-03) — Phase 51

</deferred>

---

*Phase: 48-Pre-Play-Onboarding*
*Context gathered: 2026-03-28*
