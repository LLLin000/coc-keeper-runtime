# Project Research Summary

**Project:** Discord AI Keeper (COC Archive-Builder Normalization)
**Domain:** Discord-native local-AI Call of Cthulhu Keeper system — character management layer
**Researched:** 2026-03-28
**Confidence:** MEDIUM-HIGH

## Executive Summary

This research addresses the critical gap in v2.3 Track B: **AI summarization during the character builder flow merely copies or paraphrases user input instead of synthesizing cohesive character attributes**. The current system records interview transcripts but fails to transform them into usable archive profiles that read like a Keeper crafted them.

The recommended solution introduces a **synthesis-first architecture** using `instructor` (structured output parsing) to transform raw builder answers into normalized COC 7e character sheet sections. Key architectural changes include adding `AnswerNormalizer`, `CharacterSheetSynthesizer`, and `SectionNormalizer` components while maintaining the existing archive-campaign separation pattern.

The primary risk is that local models may generate non-COC content during synthesis. Mitigation requires embedding explicit COC occupation/skill lists in prompts and validating all synthesis output against COC rules before persisting. The architecture is sound but adds ~1-2 seconds per character creation — acceptable for v1 scale.

## Key Findings

### Recommended Stack

**Core addition for v2.3:**
- `instructor` 0.10.x — transforms raw LLM output into validated Pydantic models, solving the core "AI just copies" problem. Works with Ollama's OpenAI-compatible API.

**Already in stack (verified):**
- Python 3.12+ — main runtime
- pydantic v2 + pydantic-settings — typed config and LLM I/O validation
- SQLAlchemy 2.0.x + PostgreSQL — archive persistence with JSONB for flexible fields
- Ollama (local models) — qwen3:1.7b (router) + qwen3:4b (narrator)

**Supporting libraries:**
- `orjson` — fast JSON serialization for archive JSONB
- `email-validator` — player contact validation if needed

### Expected Features

**Must have (table stakes):**
- Core COC 7e attributes (STR, CON, SIZ, DEX, INT, POW, APP, EDU) — already working
- Derived statistics (HP, MP, SAN, Idea, Luck, Know, Move Rate, Build, Damage Bonus) — deterministic COC math, already working
- Occupation with skill allocation — partially working
- Archive-campaign separation — already implemented correctly in v1.8+

**Should have (differentiators):**
- **AI Summarization Synthesis** — THE KEY GAP to fix. Must synthesize user interview responses into cohesive profile text. Currently AI copies verbatim.
- Archive field normalization — align existing "life goal/weakness/key past event" with standard COC backstory sections
- Adaptive conversational builder — already built in v1.9, needs refinement in synthesis quality

**Defer (v2+):**
- Rich UI panels beyond Discord message format
- Character sheet PDF export
- Multi-era support (1920s, Modern, Dark Ages)
- Pulp Cthulhu rules variant

### Architecture Approach

The proposed architecture adds three new components between builder and archive:

1. **AnswerNormalizer** — cleans raw user input to canonical slot format (handles Chinese variations)
2. **CharacterSheetSynthesizer** — transforms normalized answers into cohesive narrative using structured output (instructor + Pydantic)
3. **SectionNormalizer** — maps synthesis output to COC 7e character sheet sections with validation

**Major components:**
1. Builder Interview Layer — unchanged BuilderSession, updated InterviewPlanner
2. AI Summarization Synthesis Layer (NEW) — synthesizer + normalizer + contracts
3. Archive Contract Layer (NEW) — enhanced ArchiveProfile with normalized COC 7e sections
4. Campaign Projection — unchanged from current architecture

### Critical Pitfalls

1. **AI Summarization Invents Non-COC Data** — local models add invented skills/occupations without COC bounds. Prevention: embed explicit COC lists in prompts + post-processing validation.

2. **Builder-to-Archive Contract Breakage** — new schema fields don't map from builder, legacy profiles have nulls. Prevention: schema versioning + append-only new fields + migration path.

3. **Archive-Campaign Projection Desync** — normalization updates archive but not projection. Prevention: explicit update semantics, diagnostic command for sync status.

4. **Semantic Normalization Overwrites User Intent** — AI "corrects" explicit player choices. Prevention: distinguish derived vs. intent fields, add confirmation step.

5. **Adaptive Builder Interview Breaks with New Normalization** — schema changes break interview flow. Prevention: treat builder schema and archive schema as coupled contracts.

## Implications for Roadmap

Based on research, suggested phase structure for v2.3:

### Phase 1: Foundation (Week 1)
**Rationale:** Must establish contracts before building synthesis logic — prevents integration breakage later.
**Delivers:** 
- `synthesis/contracts.py` with Pydantic schemas for synthesis I/O
- `AnswerNormalizer` with basic slot cleaning
- Updated `BuilderSession` to store normalized answers alongside raw
**Addresses:** Archive field normalization baseline
**Avoids:** Pitfall AB6 (builder-schema coupling), Pitfall AB2 (contract breakage)

### Phase 2: Core Synthesis (Week 2)
**Rationale:** This is the main value add — fixing AI summarization is why v2.3 exists.
**Delivers:**
- `CharacterSheetSynthesizer` with narrative synthesis prompt using instructor
- `SectionNormalizer` with basic COC 7e section mapping
- `ArchiveProfileFactory` to construct profiles from synthesis
**Uses:** `instructor` 0.10.x for structured output
**Implements:** CharacterSheetSynthesizer component
**Avoids:** Pitfall AB1 (non-COC data) — embed COC lists in synthesis prompts

### Phase 3: Integration (Week 3)
**Rationale:** Must integrate new components with existing builder and archive.
**Delivers:**
- Updated `ConversationalCharacterBuilder` to use new synthesis flow
- Backward compatibility layer for existing archive fields
- Fallback from synthesis to heuristic extraction (for robustness)
**Implements:** Full builder-to-archive flow
**Avoids:** Pitfall AB4 (overwrites intent), Pitfall AB3 (projection desync)

### Phase 4: Polish (Week 4)
**Rationale:** Validate with real playtest data before declaring done.
**Delivers:**
- Expand COC 7e sections based on playtesting feedback
- Validation rules for occupation skills and attributes
- Optimize synthesis prompt based on character quality evaluation
**Avoids:** Pitfall AB7 (COC section misalignment)

### Phase Ordering Rationale

- Foundation first: contracts prevent integration breakage
- Synthesis second: core value proposition
- Integration third: must connect to existing systems
- Polish last: requires playtest feedback

This order avoids the critical pitfalls: AB2 (contract breakage) by starting with contracts, AB1 (non-COC data) by embedding rules in synthesis prompts, and AB3 (desync) by explicitly defining update semantics in integration phase.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (Core Synthesis):** Prompt engineering for synthesis quality — may need iteration to get cohesive narrative output
- **Phase 3 (Integration):** Archive-projection update semantics — need to define explicit contract

Phases with standard patterns (skip research-phase):
- **Phase 1 (Foundation):** Pydantic contracts are well-understood patterns
- **Phase 4 (Polish):** Validation rules follow COC 7e character sheet structure

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | `instructor` verified working with Ollama; existing stack stable |
| Features | HIGH | Based on existing v1.8-v1.9 implementation, COC 7e character sheet reference |
| Architecture | HIGH | Synthesis-first pattern well-documented; components clearly bounded |
| Pitfalls | MEDIUM-HIGH | Derived from Track B patterns + COC rules; mitigation strategies align with schema migration best practices |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Synthesis prompt quality:** Initial prompts may not produce optimal character synthesis — plan for iteration based on playtest feedback
- **Model selection:** Current qwen3 models not benchmarked specifically for synthesis tasks — may need alternative models if quality insufficient
- **Chinese language synthesis:** Prompts optimized for English COC terminology — may need refinement for Chinese character names and concepts

## Sources

### Primary (HIGH confidence)
- Context7 /pydantic/pydantic — field_validator, model_validator, computed_field patterns
- Context7 /instructor-ai/instructor — structured output extraction with Pydantic
- Ollama OpenAI compatibility docs — confirmed instructor works with local Ollama
- COC 7e character sheet (Chaosium official) — section structure reference

### Secondary (MEDIUM confidence)
- cthulhuclub.com character sheet generator — Chinese community reference
- Project's existing v1.8-v1.9 builder implementation — current architecture patterns

### Tertiary (LOW confidence)
- `DND5E-MCP` — noted as too new to anchor stack; not recommended as dependency

---

*Research completed: 2026-03-28*
*Ready for roadmap: yes*
