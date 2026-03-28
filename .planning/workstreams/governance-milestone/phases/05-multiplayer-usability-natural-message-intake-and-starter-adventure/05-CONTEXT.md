# Phase 5: Multiplayer usability, natural message intake, and starter adventure - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn the existing playable Discord runtime into a usable table workflow by letting players act through normal channel messages, tightening multiplayer state and combat gating, improving Chinese DM voice, and packaging one starter adventure plus operator docs.

</domain>

<decisions>
## Implementation Decisions

- **D-01:** Normal channel messages become the default gameplay input in a bound campaign channel; slash commands remain for setup, state transitions, and diagnostics.
- **D-02:** Message intake should ignore obvious OOC and mention-heavy social chatter rather than blindly treating every message as a turn.
- **D-03:** Combat remains runtime-enforced; natural messages from non-active combatants must be rejected or redirected cleanly.
- **D-04:** Narration should sound like a practical Chinese DM, not a generic prose narrator.
- **D-05:** The first adventure package should be a single ready-to-run one-shot rather than a general campaign authoring system.
- **D-06:** Reference mature products such as Avrae and RPG Sessions for command and table-flow patterns, but keep the project's DM-first narration architecture.

</decisions>

<canonical_refs>
## Canonical References

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `docs/superpowers/specs/2026-03-27-multiplayer-dm-usability-design.md`
- `.planning/phases/03-gameplay-loop-combat-play/03-CONTEXT.md`
- `.planning/phases/04-persistence-recovery-diagnostics/04-CONTEXT.md`

</canonical_refs>

<specifics>
## Specific Ideas

- Keep `/turn` as a fallback and test hook, but no longer require it for ordinary play.
- Add a lightweight filter layer for natural messages so `//` OOC and obvious social chatter are ignored.
- Add command and runtime helpers that make multiplayer combat readable: show combat, next turn, enter/end scene, leave campaign.
- Ship a starter one-shot in a structured format plus a human-readable operator guide.
- Update README into a practical “how to actually run a session” document.

</specifics>

---

*Phase: 05-multiplayer-usability-natural-message-intake-and-starter-adventure*
*Context gathered: 2026-03-27*
