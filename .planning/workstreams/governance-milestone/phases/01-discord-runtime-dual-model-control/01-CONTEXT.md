# Phase 1: Discord Runtime & Dual-Model Control - Context

**Gathered:** 2026-03-27 (auto mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the Discord-facing runtime surface, asynchronous interaction flow, and local dual-model orchestration needed to run one campaign session safely on consumer local hardware. This phase creates the shell that later rules, character import, combat, and persistence work will plug into. It does not yet deliver full gameplay automation.

</domain>

<decisions>
## Implementation Decisions

### Discord session surface
- **D-01:** v1 will use a single supported session topology: one campaign bound to one Discord text channel or thread, with slash commands and structured interactions as the primary control surface.
- **D-02:** Freeform message parsing may exist as flavor input later, but Phase 1 treats explicit slash-command or interaction-driven entry points as the canonical way to create, join, and manage sessions.
- **D-03:** The runtime must validate Discord permissions and channel/thread binding during setup instead of failing implicitly during play.

### Interaction timing and turn control
- **D-04:** All stateful Discord actions must acknowledge quickly and continue asynchronously through follow-up responses to avoid Discord timeout failures.
- **D-05:** Turn handling will be serialized per campaign or thread so multiple players can participate without overlapping canonical state mutations.
- **D-06:** Every inbound action should carry or derive a stable trace or command identifier so later phases can attach tool calls, state changes, and responses to the same turn.

### Dual-model orchestration
- **D-07:** The router and narrator remain separate services: `qwen3:1.7b` is the structured router and `collective-v0.1-chinese-roleplay-8b` is the Chinese narrator.
- **D-08:** The router's primary output is structured mode, tool, and state intent data rather than prose.
- **D-09:** The narrator consumes compact context plus router and tool results and must not directly mutate canonical state.

### Runtime shape
- **D-10:** Phase 1 should be implemented as a single Python service with hard internal module boundaries rather than multiple deployable services.
- **D-11:** The initial module boundaries are `discord-adapter`, `turn-orchestrator`, `router-engine`, `narration-engine`, and runtime health/config surfaces.
- **D-12:** The default local runtime target is a consumer machine in the class of `8GB` VRAM and `32GB` system RAM, so the stack should prefer practical local defaults over larger higher-latency models.

### the agent's Discretion
- Exact slash command names, provided they clearly separate setup, session, and health flows
- Internal package layout inside the Python service
- How to present deferred/follow-up Discord messages as long as the async contract remains intact

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope and requirements
- `.planning/PROJECT.md` — Product thesis, fixed platform choice, model split, and hardware constraints
- `.planning/REQUIREMENTS.md` — Phase-relevant requirements `DISC-01..04`, `ORCH-01..04`, and `OPS-03`
- `.planning/ROADMAP.md` — Phase 1 goal, dependencies, and success criteria
- `.planning/STATE.md` — Current project status and phase focus

### Research guidance
- `.planning/research/SUMMARY.md` — Consolidated product and architecture guidance
- `.planning/research/STACK.md` — Recommended stack, runtime choices, and reuse boundaries
- `.planning/research/ARCHITECTURE.md` — Recommended module boundaries and single-writer campaign model
- `.planning/research/PITFALLS.md` — Discord timing, state authority, and orchestration failure risks

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- No application code exists yet; this phase starts from planning artifacts only.

### Established Patterns
- The project has already committed to a coarse 4-phase roadmap and a strong preference for mature external dependencies over bespoke infrastructure.
- The narration and routing boundary is already fixed at the project level and should not be revisited during planning.

### Integration Points
- Phase 1 creates the initial Python service skeleton and Discord/model interfaces that Phase 2 rules and character import work will build on.
- Health and setup workflows created here become the operator entry point for later phases.

</code_context>

<specifics>
## Specific Ideas

- Keep Phase 1 pragmatic and coarse rather than over-splitting infrastructure into tiny phases or plans.
- Optimize for a responsive local Discord runtime first, not for abstract architecture purity.
- Prefer proven patterns from Avrae and Discord app-command workflows, but do not embed Avrae itself.

</specifics>

<deferred>
## Deferred Ideas

- Character import specifics belong to Phase 2.
- Deterministic combat and broader gameplay flow belong to Phase 3.
- Persistence, replay, and operator diagnostics beyond a basic health workflow belong to Phase 4.
- Telegram support, NSFW model behavior, VTT features, and custom character tooling remain out of scope for this phase.

</deferred>

---

*Phase: 01-discord-runtime-dual-model-control*
*Context gathered: 2026-03-27*
