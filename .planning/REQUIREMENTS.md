# Requirements

**Project:** Discord AI DM  
**Version:** v1 scope definition  
**Defined:** 2026-03-27

## v1 Requirements

### Discord Session Runtime

- [ ] **DISC-01**: Players can create or join a campaign session bound to a Discord channel or thread.
- [ ] **DISC-02**: Multiple human players can participate in the same active campaign session without corrupting turn or combat state.
- [ ] **DISC-03**: The bot acknowledges Discord interactions quickly and completes long-running work asynchronously through follow-up responses.
- [ ] **DISC-04**: The system supports a clear v1 session topology and validates required Discord permissions during setup.

### Gameplay Modes And Roleplay

- [ ] **PLAY-01**: The DM can run normal narration mode where the bot responds as the world-facing DM.
- [ ] **PLAY-02**: The system can switch into scene-based multi-character performance where the bot speaks as multiple NPCs or enemies with explicit speaker attribution.
- [ ] **PLAY-03**: The system can return from performance scenes to normal DM-led play without losing scene, combat, or actor context.
- [ ] **PLAY-04**: The narrator produces Chinese-first output suitable for storytelling, scene framing, and NPC dialogue.

### Character Data

- [ ] **CHAR-01**: A player can import or link a character from one mature external source through a clearly defined v1 path.
- [ ] **CHAR-02**: Imported character data is normalized into a local gameplay model that can power checks, attacks, saves, spell use, and resource tracking.
- [ ] **CHAR-03**: The system clearly labels whether character data is a snapshot import or a live sync path.
- [ ] **CHAR-04**: Character onboarding does not require building or managing a custom full-sheet editor inside Discord.

### Rules And Mechanical Resolution

- [ ] **RULE-01**: The system uses a deterministic rules layer as the canonical authority for state-changing mechanics.
- [ ] **RULE-02**: Players can trigger ability checks, skill checks, saving throws, attack rolls, and damage resolution from Discord.
- [ ] **RULE-03**: The system can resolve initiative, turn order, HP changes, conditions, concentration, death saves, and basic resource counters during combat.
- [ ] **RULE-04**: The system can perform rules, spell, monster, class, and equipment lookup using an open structured compendium source.
- [ ] **RULE-05**: The v1 rules baseline is explicitly constrained to `2014 SRD only`.
- [ ] **RULE-06**: The system rejects or flags malformed model actions instead of silently applying uncertain state mutations.

### Persistence And Recovery

- [ ] **PERS-01**: Campaign state persists across restarts and can be reloaded without reconstructing the game manually.
- [ ] **PERS-02**: The system stores enough canonical state to resume scenes, combat, resources, and party context after interruption.
- [ ] **PERS-03**: Every turn records a replayable event trail including user action, router decision, tool execution, state mutations, and outbound bot response.
- [ ] **PERS-04**: The system can generate prompt-ready summaries or projections from canonical state without using raw Discord history as the only source of truth.

### Orchestration And Models

- [ ] **ORCH-01**: The system uses a dual-model architecture with a small router model and a separate narrator model.
- [ ] **ORCH-02**: The router emits structured output that determines gameplay mode, tool usage, and state intents without generating final prose as its primary output.
- [ ] **ORCH-03**: The narrator consumes compact context and tool results to produce final DM/NPC output without directly mutating canonical state.
- [ ] **ORCH-04**: The default local model stack remains practical on a consumer machine in the class of `8GB` VRAM and `32GB` system RAM.

### Operations And Diagnostics

- [ ] **OPS-01**: Operators can inspect the health of Discord integration, model calls, tool execution, and recent rules failures from a compact debug surface or command.
- [ ] **OPS-02**: The system provides traceable identifiers that link one player action to routing, tool use, state changes, and final Discord output.
- [ ] **OPS-03**: The system exposes a basic health check workflow to verify setup, permissions, and service connectivity before running a live session.

## v2 Requirements

- [ ] **V2-01**: The DM can override or correct rules outcomes from an operator control path.
- [ ] **V2-02**: The system generates structured session recaps and campaign journals after play.
- [ ] **V2-03**: The narrator tracks richer NPC memory and relationship continuity across longer campaigns.
- [ ] **V2-04**: The platform supports async between-session play and downtime exchanges.
- [ ] **V2-05**: The system supports lightweight map or encounter visualization integrations.
- [ ] **V2-06**: The system supports broader homebrew content policies and overrides.
- [ ] **V2-07**: The platform adds optional voice/TTS delivery modes.

## Out Of Scope

- Full custom character builder or sheet manager in v1
- Full VTT features including maps, fog of war, token UI, and tactical positioning UI
- Multi-platform chat support outside Discord in v1
- Full support for multiple tabletop systems at launch
- Runtime dependence on `Avrae` as the core bot engine
- Dependence on `DND5E-MCP` as a required production core
- Custom model training or fine-tuning before product validation
- NSFW-specific model behavior in v1

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DISC-01 | Phase 1 | Pending |
| DISC-02 | Phase 1 | Pending |
| DISC-03 | Phase 1 | Pending |
| DISC-04 | Phase 1 | Pending |
| PLAY-01 | Phase 3 | Pending |
| PLAY-02 | Phase 3 | Pending |
| PLAY-03 | Phase 3 | Pending |
| PLAY-04 | Phase 3 | Pending |
| CHAR-01 | Phase 2 | Pending |
| CHAR-02 | Phase 2 | Pending |
| CHAR-03 | Phase 2 | Pending |
| CHAR-04 | Phase 2 | Pending |
| RULE-01 | Phase 2 | Pending |
| RULE-02 | Phase 3 | Pending |
| RULE-03 | Phase 3 | Pending |
| RULE-04 | Phase 2 | Pending |
| RULE-05 | Phase 2 | Pending |
| RULE-06 | Phase 2 | Pending |
| PERS-01 | Phase 4 | Pending |
| PERS-02 | Phase 4 | Pending |
| PERS-03 | Phase 4 | Pending |
| PERS-04 | Phase 4 | Pending |
| ORCH-01 | Phase 1 | Pending |
| ORCH-02 | Phase 1 | Pending |
| ORCH-03 | Phase 1 | Pending |
| ORCH-04 | Phase 1 | Pending |
| OPS-01 | Phase 4 | Pending |
| OPS-02 | Phase 4 | Pending |
| OPS-03 | Phase 1 | Pending |
