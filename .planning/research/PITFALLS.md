# Domain Pitfalls

**Domain:** Discord-native local-AI COC Keeper system
**Researched:** 2026-03-28
**Overall confidence:** MEDIUM-HIGH

---

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
**Consequences:** Silent corruption of combat state and arguments about what "really happened."
**Prevention:** Keep canonical game state in typed code and storage. The model proposes intents; deterministic services validate and apply them.
**Detection:** State mismatches between recap, pinned combat summary, and stored records; malformed tool payloads; frequent manual corrections.

### Pitfall 3: Treating "heavy rules support" as just SRD lookup
**What goes wrong:** The bot can quote spells and monsters but cannot run action economy, reactions, effect durations, targeting, or resource bookkeeping correctly.
**Why it happens:** Lookup data is much easier than adjudication. A usable DM assistant needs a rules state machine, not just a retrieval layer.
**Consequences:** Combat becomes slower than manual play and the product feels deceptive.
**Prevention:** Scope v1 around a narrow, testable rules kernel: initiative, turns, HP, conditions, concentration, death saves, and basic resource counters.
**Detection:** Sessions rely on DM override for most turns; combat takes more messages than manual play; edge-case rulings explode.

### Pitfall 4: Mixing incompatible rules/data baselines
**What goes wrong:** Characters, monsters, spells, and rulings disagree because different systems assume different rules vintages or content sets.
**Why it happens:** `5e-srd-api` is currently versioned around `/api/2014`, while teams often talk about "5e" loosely and accidentally mix 2014, 2024, SRD-only, and purchased-source content.
**Consequences:** Wrong modifiers, missing features, bad spell text, and impossible automation bugs.
**Prevention:** Choose one rules baseline for v1 and enforce it everywhere in prompts, imports, validation, and UI copy.
**Detection:** Frequent "why is my sheet missing X?" reports, unexplained stat mismatches, and ad hoc exceptions in adapters.

### Pitfall 5: Assuming external character sources are interchangeable
**What goes wrong:** Imports succeed for some players and fail or partially sync for others; updates do not flow back consistently.
**Why it happens:** D&D Beyond, Dicecloud, and Google Sheets have different sharing, auth, and sync semantics. Even Avrae documents source-specific behavior and delays.
**Consequences:** Support burden rises immediately and campaign state splits across systems.
**Prevention:** Support exactly one primary character path in v1, with import semantics clearly labeled as `snapshot` or `live sync`.
**Detection:** Re-import loops, "my HP here is wrong there," permission errors, and onboarding friction concentrated around sheet connection.

---

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

---

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

---

## Observability And Testing Risks

### Risk 1: No replayable event log
**What goes wrong:** You cannot explain why a ruling happened or reproduce a desync.
**Mitigation:** Persist every user action, model decision, tool call, state diff, and outbound Discord message under a single trace ID.

### Risk 2: Testing components in isolation only
**What goes wrong:** Unit tests pass while real sessions fail at the seams between Discord, orchestration, storage, and rules updates.
**Mitigation:** Build end-to-end replay tests from captured transcripts. Avrae's public repo is a good reference for mocking Discord interactions and asserting bot output plus database state.

### Risk 3: No adversarial structured-output tests
**What goes wrong:** Rare malformed JSON, wrong enum values, or partial tool payloads corrupt state in production.
**Mitigation:** Fuzz tool responses, replay failures, and hard-reject invalid actions rather than "best effort" applying them.

### Risk 4: Missing operator-facing diagnostics
**What goes wrong:** DMs cannot tell whether a failure came from Discord, model latency, source auth, or rules validation.
**Mitigation:** Expose a compact admin/debug view with queue depth, last model timings, source sync status, and latest rules errors.

---

## Archive And Builder Normalization Pitfalls (v2.3)

*These pitfalls specifically address the B1 milestone: tightening archive-builder mapping with better AI summarization during builder flow.*

### Pitfall AB1: AI Summarization Invents Non-COC Data
**What goes wrong:** The AI summarization during builder flow generates character attributes, skills, or background elements that do not exist in COC rules (e.g., invented skills, non-existent occupations, house-rule modifications).
**Why it happens:** Local models are creative by nature; without explicit COC bounds in the summarization prompt, the AI may "improve" character details by adding non-canonical content.
**Consequences:** Characters become unplayable in official COC modules; campaign projection contains invalid data; player trust erodes when AI-generated claims cannot be verified against rules.
**Prevention:** 
- Embed COC 7e occupation list, skill list, and characteristic bounds explicitly in summarization prompts
- Use structured output schemas that constrain values to COC-legal ranges
- Add post-processing validation: occupation must match COC occupation list, skills must be from COC skill list
**Detection:** 
- Invalid occupation names in archive
- Skill point totals exceeding COC caps
- Backstory references to non-existent COC mechanics

### Pitfall AB2: Builder-to-Archive Contract Breakage
**What goes wrong:** New normalized fields in the archive schema do not map correctly from builder interview answers; existing profiles become partially migrated or have null values.
**Why it happens:** Schema changes add new fields without migration strategy; builder flow assumes all fields exist; legacy profiles lack new normalization data.
**Consequences:** 
- `/profile_detail` shows incomplete data for older characters
- Builder flow fails when encountering missing normalized fields
- Campaign projection uses fallback heuristics inconsistently
**Prevention:** 
- Treat archive schema as append-only for v1; add new normalized fields as optional with sensible defaults
- Implement schema versioning in archive metadata
- Create migration path: fill new fields with derived values from existing fields where possible
- Test builder flow against both new profiles and legacy profiles from previous milestones
**Detection:** 
- Null values in new archive fields for pre-v2.3 profiles
- Inconsistent field population between new and old profiles

### Pitfall AB3: Archive-Campaign Projection Desync
**What goes wrong:** Normalized archive fields update but campaign projection retains old values, or vice versa; players see different stats depending on which view they access.
**Why it happens:** The separation between archive (long-term truth) and campaign projection (instance-specific state) becomes unclear when adding normalization; updates to one do not automatically propagate to the other.
**Consequences:** 
- Confusion about which data is "real"
- Stat discrepancies between `/sheet` and in-campaign display
- Potential rule violations if campaign projection uses non-normalized values
**Prevention:** 
- Explicitly define update semantics: when archive normalizes, does campaign projection auto-update or require manual refresh?
- Document the archive-projection contract in `ArchiveProfile` and `CampaignProjection` schemas
- Add diagnostic command to show sync status between archive and projection
**Detection:** 
- `/profile_detail` and in-campaign stats disagree
- Players report "my points changed" after archive normalization

### Pitfall AB4: Semantic Normalization Overwrites User Intent
**What goes wrong:** AI-suggested normalization changes character details that players explicitly chose (occupation backstory, motivation, bond); players feel their character is being rewritten.
**Why it happens:** Aggressive normalization "corrects" freeform input to standard forms without preserving the user's specific intent; no user confirmation step exists.
**Consequences:** 
- Player frustration with "the bot changed my character"
- Loss of unique character identity
- Players may abandon builder flow
**Prevention:** 
- Distinguish between "derived" fields (stats calculated from rules) and "intent" fields (backstory, motivation, personality)
- Apply AI summarization only to semantic coherence, not to override explicit player choices
- Add confirmation step for normalization that affects player-authored content
**Detection:** 
- Players explicitly complain about character changes
- Backstory differs significantly between builder input and stored archive

### Pitfall AB5: Schema Migration Breaks Single Active Profile Governance
**What goes wrong:** Schema changes to archive disrupt the existing single-active-profile governance; players can activate multiple profiles, or activation fails entirely.
**Why it happens:** Profile activation logic depends on specific archive fields; new fields may create validation conflicts or bypass existing activation guards.
**Consequences:** 
- Multiple active profiles per player (governance violation)
- Players stuck in unactivatable state
- Campaign state corruption from wrong profile binding
**Prevention:** 
- Audit all profile activation paths after schema changes
- Add integration test: activate profile -> schema migrate -> verify still only one active
- Preserve existing activation guards (one-active-per-player) in migration code
**Detection:** 
- Player has two active profiles simultaneously
- Activation command fails with cryptic error

### Pitfall AB6: Adaptive Builder Interview Breaks with New Normalization
**What goes wrong:** The adaptive builder interview flow assumes certain archive fields exist; new normalization adds fields that builder does not ask about, or removes fields it expected.
**Why it happens:** Builder interview logic and archive schema are loosely coupled; changes to one break the other without warning.
**Consequences:** 
- Builder flow produces incomplete profiles
- Interview questions become irrelevant or confusing
- New fields remain null because builder never populates them
**Prevention:** 
- Treat builder interview schema and archive schema as coupled contracts
- Add integration test: complete builder flow -> verify all archive fields populated
- Document which archive fields require builder population vs. post-hoc derivation
**Detection:** 
- New archive fields remain null after builder completion
- Builder asks about deprecated fields

### Pitfall AB7: COC Character Sheet Section Misalignment
**What goes wrong:** Archive fields do not align with standard COC character sheet sections (Personal Data, Characteristics, Skills, Equipment, Background, etc.); display becomes confusing or incomplete.
**Why it happens:** Normalization focuses on internal data structure without considering how fields map to COC character sheet presentation.
**Consequences:** 
- `/profile_detail` shows non-standard layout
- Players cannot find expected information
- Incompatibility with external COC character sheets
**Prevention:** 
- Reference COC 7e character sheet structure during normalization design
- Map each archive field to explicit COC character sheet section
- Test `/profile_detail` output against reference character sheets (e.g., cthulhuclub.com generator)
**Detection:** 
- Profile display missing expected COC sections
- Field organization does not match COC conventions

---

## Recommended Guardrails

- Pick one v1 rules baseline: `2014 SRD only` is the cleanest current choice because `5e-srd-api` currently exposes `/api/2014`.
- Pick one v1 character path: import from a single mature source first; call it `snapshot import` unless you can prove safe live sync.
- Make the rules engine authoritative and the LLM non-authoritative.
- Make Discord interactions asynchronous by default.
- Store append-only event history so session recovery is possible after crashes or bad generations.
- Treat freeform chat as flavor input; require explicit structured commands for state-changing actions.

### v2.3 Specific Guardrails

- **COC bounds in all AI output**: Embed explicit COC occupation list, skill list, and characteristic ranges in every summarization prompt.
- **Schema versioning**: Add version field to archive schema; migrate gracefully.
- **Archive-projection explicit contract**: Document when normalization updates propagate to campaign projection.
- **Builder-contract coupling**: Test builder output against full archive schema on every change.
- **User intent preservation**: Distinguish AI-suggested normalization from player-explicit choices; confirm before overwriting.

---

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
- Call of Cuthulhu 7e character creation: occupation-based skill point allocation, SAN as core characteristic, percentile system. https://www.rpgstack.com/systems/coc7e/character-creation
- COC character sheet structure reference: Personal Data, Characteristics (STR, CON, SIZ, INT, POW, DEX, APP), Skills, Equipment, Background. https://www.cthulhuclub.com/charSheetGenerator/
- Schema migration best practices: nullable columns with defaults, versioning, backward compatibility. https://hoop.dev/blog/how-to-safely-add-a-new-column-to-a-database-schema-27/

---

## Confidence Notes

- **HIGH:** Discord interaction, intent, thread, and rate-limit pitfalls.
- **HIGH:** SRD/open-content boundary and 2014-versus-2024 data-version risk.
- **MEDIUM:** Local-model orchestration failure patterns. Official docs confirm capability, but some operational risk statements are inference from those capabilities plus Discord constraints.
- **MEDIUM:** External character sync pitfalls. Verified through Avrae's documented behaviors, but exact failure frequency will depend on the chosen source.
- **MEDIUM-HIGH:** Archive-builder normalization pitfalls. Derived from existing Track B architecture patterns and COC character creation rules; tested mitigation strategies align with standard schema migration practices.
