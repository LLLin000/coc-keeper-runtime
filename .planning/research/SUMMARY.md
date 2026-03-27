# Research Summary

**Project:** Discord AI DM  
**Synthesized:** 2026-03-27  
**Confidence:** MEDIUM-HIGH

## Executive Summary

The lowest-risk path is a Discord-first, Python-based modular monolith that runs a dual-model local AI stack behind a deterministic rules and state layer. The product should optimize for one thing first: a campaign-usable multiplayer Discord session loop with reliable combat, persistence, and multi-character DM performance. Mature ecosystems should be reused for rules data, Discord UX patterns, and character import ideas instead of rebuilding those layers from scratch.

## Recommended Product Shape

- Discord-native multiplayer play in one campaign channel or thread
- Hybrid gameplay style: normal DM-led narration with scene-based multi-character performance
- Heavy-rules support with deterministic authority for combat and resource state
- External character import or linking through one low-friction mature path in v1
- Text-first gameplay with persistence and resume before voice, maps, or deep long-term memory

## Recommended Technical Baseline

- `Python 3.12+` as the primary runtime
- `discord.py` as the Discord framework
- `Ollama` as the default local model host
- `qwen3:1.7b` as the router model
- `collective-v0.1-chinese-roleplay-8b` as the default Chinese narrator model
- `PostgreSQL` as the canonical data store
- `5e-srd-api` as the primary open rules/compendium source
- `Avrae` used as a reference for UX, combat flow, and import patterns rather than as a runtime dependency

## Key Product Requirements Confirmed By Research

- Multiplayer session orchestration inside Discord is table stakes
- Combat state management is the real credibility threshold for a heavy-rules DM system
- Character import/link is expected; full custom sheet management is not a good v1 investment
- Rules lookup is necessary but not sufficient; the system needs a real rules state kernel
- Persistence and interruption recovery are mandatory for real Discord play
- Multi-character performance is part of the core thesis, not a cosmetic add-on

## Architecture Recommendation

Use a modular monolith with campaign-scoped serialized turn processing:

- `discord-adapter`
- `turn-orchestrator`
- `router-engine`
- `tool-and-rules-gateway`
- `narration-engine`
- `state-store`
- `projection-read-models`

Critical rules:

- Single writer per campaign/thread
- Canonical state lives in typed code and storage, not in model text
- Event log is authoritative history
- Narration consumes state and tool results but does not mutate canonical rules state directly

## Main Risks

1. Discord interactions timing out while local inference runs
2. Letting the LLM act as the source of truth for combat and resource state
3. Mistaking SRD lookup for full heavy-rules support
4. Mixing incompatible rules baselines such as 2014 and 2024 content
5. Overbuilding v1 into an AI DM, VTT, and character platform at the same time

## Guardrails For v1

- Use asynchronous Discord interaction handling from the start
- Choose one rules baseline: `2014 SRD only`
- Choose one primary character import path first
- Keep rules authoritative and deterministic
- Keep narrator and router separated
- Store append-only turn/event history for replay and debugging
- Prefer slash commands and structured controls for state-changing actions

## Product Boundary For v1

### In scope

- Discord multiplayer session loop
- Character import/link through one mature path
- Dice and action resolution
- Combat automation with persistence and resume
- DM narration and multi-NPC performance

### Defer

- Voice/TTS
- VTT/maps
- Broad homebrew support
- Full custom sheet management
- Multi-platform chat support
- Custom model training/fine-tuning

## Bottom Line

The first release should behave like a reliable Discord D&D runtime with local AI narration, not like an all-purpose tabletop platform. The winning strategy is to keep the orchestration and rules core deterministic, use local models for routing and narration only where they are strongest, and borrow mature data and interaction patterns wherever possible.
