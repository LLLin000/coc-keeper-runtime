# Architecture Patterns

**Domain:** Discord-native local-AI D&D DM
**Researched:** 2026-03-27
**Confidence:** MEDIUM-HIGH

## Recommendation

Use a **modular monolith with campaign-scoped turn workers**, not microservices and not a giant bot process. One deployable is the right starting point for a local-AI Discord system, but inside that deployable the boundaries should be hard:

1. `discord-adapter`
2. `turn-orchestrator`
3. `router-engine`
4. `tool-and-rules-gateway`
5. `narration-engine`
6. `state-store`
7. `projection-read-models`

This avoids a monolith in the important sense: Discord I/O, model reasoning, rule lookup, and persistence are isolated behind contracts. It also avoids premature distributed-systems overhead for a single-node local inference stack.

## Recommended Boundaries

| Module | Responsibility | Must Not Own |
|--------|----------------|--------------|
| `discord-adapter` | Receive Discord events, defer responses within Discord's interaction window, send followups, map channels/threads to campaign IDs | Game rules, prompt building, state mutation logic |
| `turn-orchestrator` | Serialize turns per campaign/thread, load state, invoke router, tools, narration, commit results | Discord API details, direct model prompting details |
| `router-engine` | Fast model that classifies intent, picks mode, requests tools, emits structured `TurnPlan` JSON | Final prose, DB writes, external API calls |
| `tool-and-rules-gateway` | Execute dice, rule lookup, condition/initiative actions, compendium reads via adapters | Discord formatting, narrative decisions |
| `narration-engine` | Large local model for DM voice, NPC dialogue, scene framing, result explanation | Tool selection, canonical rules state |
| `state-store` | Canonical persistence for campaigns, scenes, combat state, message/event log, imported character refs | Prompt-ready summaries, Discord delivery state beyond IDs |
| `projection-read-models` | Build prompt context, summaries, combat views, player-facing recaps from canonical events | Canonical writes |

## One Discord Turn

```text
Discord event
  -> discord-adapter validates + persists raw ingress
  -> immediate defer/ack
  -> enqueue turn keyed by campaign_id
  -> turn-orchestrator loads campaign snapshot + recent event log
  -> router-engine returns TurnPlan
  -> tool-and-rules-gateway executes required actions/lookups
  -> state mutations are validated and appended as domain events
  -> narration-engine receives compact context + tool results + speaking plan
  -> discord-adapter sends/edit followup messages
  -> projection-read-models refresh summaries/combat views
```

The important constraint is **single-writer per campaign**. A Discord campaign thread should process one authoritative turn at a time. That prevents race conditions when two players post simultaneously, especially once initiative, HP, conditions, and resources become canonical.

## State Model Boundaries

Keep state in three layers:

| State Layer | Examples | Owner |
|-------------|----------|-------|
| `canonical game state` | Campaign, channel/thread binding, party roster, scene, combatants, initiative, HP, conditions, clocks, inventory/resource counters, event log | `state-store` |
| `derived operational state` | Prompt summaries, turn digests, semantic recall snippets, pinned combat summary, unread queue state | `projection-read-models` |
| `external source of truth` | Character sheets from D&D Beyond/Dicecloud/Sheets, SRD compendium data, MCP lookup caches | External adapters |

Rules:

- Never let the narration model write canonical state directly.
- Never treat imported character sheets as fully owned local state; store references plus normalized snapshots.
- Persist **events first**, then rebuild prompt summaries and combat views from projections.
- Store raw Discord message IDs and interaction IDs, but not Discord message text as the only canonical history; the campaign event log is the authoritative history.

## Integration Boundaries

Use mature external projects as **read/execute adapters**, not as your core domain model.

| External Project | Recommended Boundary |
|------------------|----------------------|
| `dnd-mcp` | Optional lookup/verification adapter for fuzzy rules questions and structured compendium access. Useful as a sidecar or internal tool bridge, but not the source of combat truth. |
| `5e-srd-api` / `dnd5eapi` | Read-only compendium adapter for SRD classes, spells, monsters, equipment, and features. Mirror/cache locally for reliability. |
| `Avrae` | Reference implementation for Discord UX, combat affordances, and character import surfaces. Do not embed it as the runtime core. Copy proven interaction patterns, not its whole command architecture. |
| Character providers | Wrap D&D Beyond, Dicecloud, and Sheets behind `character-source` ports so combat and narration consume one normalized character model. |

The architecture should assume these external systems can be unavailable, slow, or schema-unstable. Cache reads, normalize responses, and keep your own canonical combat/campaign state independent.

## Extensibility Points

Design these interfaces now:

```ts
type TurnPlan = {
  mode: "dm" | "scene" | "combat";
  toolCalls: ToolCall[];
  stateIntents: StateIntent[];
  speakerPlan: SpeakerPlan[];
};
```

```ts
interface RulesAdapter {
  lookup(query: RulesQuery): Promise<RulesResult>;
  execute(action: MechanicalAction, state: GameState): Promise<ActionResult>;
}
```

```ts
interface CharacterSourceAdapter {
  import(ref: CharacterRef): Promise<NormalizedCharacter>;
  refresh(ref: CharacterRef): Promise<NormalizedCharacter>;
}
```

That gives you clean insertion points for:

- a real combat engine with initiative phases, reactions, legendary actions, and effect durations
- richer character sync/import from D&D Beyond, Dicecloud, or sheets
- alternate narration models
- stricter rule adjudication policies per campaign

## Recommended Shape

Start with:

- one process for `discord-adapter` + `turn-orchestrator`
- one local database, preferably PostgreSQL
- one background worker loop keyed by `campaign_id`
- local model runners behind two ports: `router-engine` and `narration-engine`
- adapter packages for compendium/rules/character integrations

Do **not** start with:

- separate services for each module
- direct model access from Discord handlers
- a shared mutable in-memory campaign object
- tool adapters writing canonical state behind the orchestrator's back

## Why This Is Best

This gives the project the right balance:

- **Discord-native:** fast defer/followup flow matches Discord interactions and channel/thread play.
- **Local-AI friendly:** router and narrator remain independent model ports.
- **Rules-heavy without rewrite risk:** compendium and character systems stay replaceable.
- **Persistent multiplayer-safe:** campaign-scoped serialization prevents state corruption.
- **Non-monolithic in practice:** the hard boundaries are at module and data ownership lines, which matters more than splitting into many processes too early.

## Sources

- Discord interactions docs: https://docs.discord.com/developers/interactions/receiving-and-responding
- `dnd-mcp` repository README: https://github.com/procload/dnd-mcp
- D&D 5e API homepage/docs: https://www.dnd5eapi.co/
- Avrae getting started: https://avrae.readthedocs.io/en/latest/cheatsheets/get_started.html
- Avrae DM combat guide: https://avrae.readthedocs.io/en/stable/cheatsheets/dm_combat.html
- Avrae D&D Beyond integration: https://avrae.readthedocs.io/en/latest/ddb.html
