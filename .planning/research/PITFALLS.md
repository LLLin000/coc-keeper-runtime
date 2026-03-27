# Domain Pitfalls

**Domain:** Discord-native local-AI D&D DM system
**Researched:** 2026-03-27
**Overall confidence:** MEDIUM-HIGH

## Top Failure Modes

### Pitfall 1: Blocking Discord interactions on local inference
**What goes wrong:** Commands stall, Discord shows failures, or users retry and create duplicate actions.
**Why it happens:** Discord requires an initial interaction response within 3 seconds, while local narration plus routing plus tool use can easily exceed that budget.
**Consequences:** Double turns, duplicate spell casts, confused players, and broken trust in the bot.
**Prevention:** Acknowledge immediately, push all real work to an async job, and make every state-changing action idempotent with a command/event ID.
**Detection:** Repeated retries from players, duplicated combat actions, rising deferred-response counts, or missing followups.

### Pitfall 2: Letting the LLM be the source of truth for rules state
**What goes wrong:** HP, initiative, conditions, spell slots, concentration, and durations drift from what the model narrates.
**Why it happens:** Tool calling and structured outputs exist in local stacks, but reliability is still model-dependent; narrative models are not a deterministic rules engine.
**Consequences:** Silent corruption of combat state and arguments about what “really happened.”
**Prevention:** Keep canonical game state in typed code and storage. The model proposes intents; deterministic services validate and apply them.
**Detection:** State mismatches between recap, pinned combat summary, and stored records; malformed tool payloads; frequent manual corrections.

### Pitfall 3: Treating “heavy rules support” as just SRD lookup
**What goes wrong:** The bot can quote spells and monsters but cannot run action economy, reactions, effect durations, targeting, or resource bookkeeping correctly.
**Why it happens:** Lookup data is much easier than adjudication. A usable DM assistant needs a rules state machine, not just a retrieval layer.
**Consequences:** Combat becomes slower than manual play and the product feels deceptive.
**Prevention:** Scope v1 around a narrow, testable rules kernel: initiative, turns, HP, conditions, concentration, death saves, and basic resource counters.
**Detection:** Sessions rely on DM override for most turns; combat takes more messages than manual play; edge-case rulings explode.

### Pitfall 4: Mixing incompatible rules/data baselines
**What goes wrong:** Characters, monsters, spells, and rulings disagree because different systems assume different rules vintages or content sets.
**Why it happens:** `5e-srd-api` is currently versioned around `/api/2014`, while teams often talk about “5e” loosely and accidentally mix 2014, 2024, SRD-only, and purchased-source content.
**Consequences:** Wrong modifiers, missing features, bad spell text, and impossible automation bugs.
**Prevention:** Choose one rules baseline for v1 and enforce it everywhere in prompts, imports, validation, and UI copy.
**Detection:** Frequent “why is my sheet missing X?” reports, unexplained stat mismatches, and ad hoc exceptions in adapters.

### Pitfall 5: Assuming external character sources are interchangeable
**What goes wrong:** Imports succeed for some players and fail or partially sync for others; updates do not flow back consistently.
**Why it happens:** D&D Beyond, Dicecloud, and Google Sheets have different sharing, auth, and sync semantics. Even Avrae documents source-specific behavior and delays.
**Consequences:** Support burden rises immediately and campaign state splits across systems.
**Prevention:** Support exactly one primary character path in v1, with import semantics clearly labeled as `snapshot` or `live sync`.
**Detection:** Re-import loops, “my HP here is wrong there,” permission errors, and onboarding friction concentrated around sheet connection.

## Integration Traps

### Trap 1: Message-content-first UX
**What goes wrong:** The bot is built around reading freeform channel messages, then loses access or behaves inconsistently in larger deployments.
**Why it happens:** `MESSAGE_CONTENT` is a privileged intent and unapproved apps receive empty values for affected fields.
**Mitigation:** Make slash commands, buttons, selects, and modals the primary control surface. Treat freeform parsing as optional augmentation, not the backbone.

### Trap 2: Thread/channel permission blind spots
**What goes wrong:** Sessions fail in threads, private threads, or mixed channel setups even though the bot works in a test server.
**Why it happens:** Discord thread participation depends on thread-specific permissions and visibility rules.
**Mitigation:** Design one supported session topology for v1, verify permissions explicitly during setup, and provide a `/healthcheck` command.

### Trap 3: Tool-call fanout without backpressure
**What goes wrong:** One player action triggers multiple retrievals, rule checks, memory lookups, and narration passes; latency spikes and order becomes nondeterministic.
**Why it happens:** Dual-model orchestration encourages overcomposition.
**Mitigation:** Use a strict action pipeline: parse intent -> validate -> mutate state -> narrate. Do not let narration recursively trigger more stateful tools.

### Trap 4: Importing non-SRD or purchased content by implication
**What goes wrong:** The system depends on content it is not clearly licensed or technically entitled to use.
**Why it happens:** SRD/open APIs are available, but players expect full D&D Beyond parity. Those are not the same thing.
**Mitigation:** Build v1 on SRD/open content only unless you have an explicit licensed path. State this boundary in product copy.

## Scope Traps

### Trap 1: Building a full DM instead of a campaign-usable runtime
**What goes wrong:** The team tries to solve world simulation, perfect improvisation, every subclass, every spell edge case, voice, maps, and long-term memory at once.
**Mitigation:** Optimize for one-shots and short campaigns first. Combat reliability and recovery matter more than broad fantasy.

### Trap 2: Recreating mature automation ecosystems
**What goes wrong:** Time disappears into custom aliasing, dice parsing, and content plumbing that existing projects already solved.
**Mitigation:** Reuse mature references for interaction and test design. Copy proven patterns before inventing abstractions.

### Trap 3: Overpromising multiplayer scene performance
**What goes wrong:** Multi-NPC performance scenes become unreadable, slow, or hard to attribute in Discord text.
**Mitigation:** Limit concurrent bot speakers, enforce speaker labels, and switch to summary mode when scene density rises.

## Observability And Testing Risks

### Risk 1: No replayable event log
**What goes wrong:** You cannot explain why a ruling happened or reproduce a desync.
**Mitigation:** Persist every user action, model decision, tool call, state diff, and outbound Discord message under a single trace ID.

### Risk 2: Testing components in isolation only
**What goes wrong:** Unit tests pass while real sessions fail at the seams between Discord, orchestration, storage, and rules updates.
**Mitigation:** Build end-to-end replay tests from captured transcripts. Avrae’s public repo is a good reference for mocking Discord interactions and asserting bot output plus database state.

### Risk 3: No adversarial structured-output tests
**What goes wrong:** Rare malformed JSON, wrong enum values, or partial tool payloads corrupt state in production.
**Mitigation:** Fuzz tool responses, replay failures, and hard-reject invalid actions rather than “best effort” applying them.

### Risk 4: Missing operator-facing diagnostics
**What goes wrong:** DMs cannot tell whether a failure came from Discord, model latency, source auth, or rules validation.
**Mitigation:** Expose a compact admin/debug view with queue depth, last model timings, source sync status, and latest rules errors.

## Recommended Guardrails

- Pick one v1 rules baseline: `2014 SRD only` is the cleanest current choice because `5e-srd-api` currently exposes `/api/2014`.
- Pick one v1 character path: import from a single mature source first; call it `snapshot import` unless you can prove safe live sync.
- Make the rules engine authoritative and the LLM non-authoritative.
- Make Discord interactions asynchronous by default.
- Store append-only event history so session recovery is possible after crashes or bad generations.
- Treat freeform chat as flavor input; require explicit structured commands for state-changing actions.

## Sources

- Discord Interactions docs: initial response required within 3 seconds; interaction tokens valid for 15 minutes for followups. https://docs.discord.com/developers/interactions/receiving-and-responding
- Discord Gateway docs: `MESSAGE_CONTENT` is privileged; unapproved apps receive empty message-content fields. https://docs.discord.com/developers/events/gateway
- Discord Threads docs: thread messaging depends on thread-specific permissions and visibility. https://docs.discord.com/developers/topics/threads
- Discord Gateway docs: gateway send-rate limits and connection constraints. https://docs.discord.com/developers/docs/topics/gateway
- Ollama blog: tool calling support. https://ollama.com/blog/tool-support
- Ollama blog: structured outputs with JSON schema, plus reliability tips such as schema use and temperature 0. https://ollama.com/blog/structured-outputs
- 5e SRD API repo: current API versioning notes show `/api/2014` is available and `/api/2024` is next. https://github.com/5e-bits/5e-srd-api
- Wizards / D&D Beyond: SRD 5.1 made available under Creative Commons; this does not imply access to all commercial D&D content. https://www.dndbeyond.com/posts/1439-ogl-1-0a-creative-commons
- Avrae docs: supported import sources include D&D Beyond, Dicecloud, and Google Sheets; source-specific sync/sharing behavior exists. https://avrae.readthedocs.io/en/latest/cheatsheets/get_started.html
- Avrae docs: D&D Beyond link recognition may take up to 15 minutes; linked-account behavior is source-specific. https://avrae.readthedocs.io/en/latest/ddb.html
- Avrae repo: public test suite includes mocked Discord interactions and end-to-end tests across user input, bot output, and database state. https://github.com/avrae/avrae

## Confidence Notes

- **HIGH:** Discord interaction, intent, thread, and rate-limit pitfalls.
- **HIGH:** SRD/open-content boundary and 2014-versus-2024 data-version risk.
- **MEDIUM:** Local-model orchestration failure patterns. Official docs confirm capability, but some operational risk statements are inference from those capabilities plus Discord constraints.
- **MEDIUM:** External character sync pitfalls. Verified through Avrae’s documented behaviors, but exact failure frequency will depend on the chosen source.
