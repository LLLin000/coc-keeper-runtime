# Phase 3: Gameplay Loop & Combat Play - Context

**Gathered:** 2026-03-27 (auto mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Use the runtime, character import, and deterministic rules foundations from Phases 1 and 2 to deliver playable gameplay inside Discord: DM-led narration, multi-character performance scenes, and heavy-rules combat flow.

</domain>

<decisions>
## Implementation Decisions

- **D-01:** Gameplay remains Discord-native and continues to use the existing structured command surface rather than freeform chat as the only canonical path.
- **D-02:** Combat state changes must still go through the deterministic rules layer introduced in Phase 2.
- **D-03:** Multi-character performance should use explicit speaker attribution so NPC and enemy dialogue stays readable in Discord.
- **D-04:** Scene mode and combat mode are router-selected but runtime-enforced; narration does not become the state authority.
- **D-05:** Phase 3 should deliver a real playable loop before adding richer persistence or diagnostics work from Phase 4.

</decisions>

<canonical_refs>
## Canonical References

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md` — `PLAY-01..04`, `RULE-02`, `RULE-03`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/02-character-import-rules-authority/02-03-SUMMARY.md`
- `.planning/research/FEATURES.md`
- `.planning/research/ARCHITECTURE.md`
- `.planning/research/PITFALLS.md`

</canonical_refs>

<specifics>
## Specific Ideas

- Keep the gameplay layer compact: one clear combat loop, one scene-mode speaker format, one DM-led narration path.
- Prefer explicit commands and deterministic state updates over ambitious natural-language parsing.
- Use the existing router contracts and extend them only where combat or speaker control demands it.

</specifics>

---

*Phase: 03-gameplay-loop-combat-play*
*Context gathered: 2026-03-27*
