# Architecture Research

**Domain:** COC Character Archive/Builder Integration with AI Summarization
**Researched:** 2026-03-28
**Confidence:** HIGH

## Executive Summary

This research addresses how improved archive-builder contracts and AI summarization integrate with existing Track B architecture. The current system has a functional but fragile mapping between conversational builder answers and archive fields. The key problems are:

1. **AI summarization merely copies/paraphrases** rather than synthesizing cohesive character attributes
2. **Character sheet sections are not normalized** to standard COC 7e layout
3. **Builder-to-archive contracts use heuristic fallbacks** that produce inconsistent results

This document proposes a synthesis-first architecture that transforms raw interview answers into canonical COC character sheet sections while maintaining the existing archive/projection separation.

## Current Architecture (Track B)

### Existing Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CHARACTER LAYER (Track B)                        │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐    ┌──────────────────────────────────┐  │
│  │ Conversational      │    │ ArchiveRepository                 │  │
│  │ CharacterBuilder   │───▶│ (InvestigatorArchiveProfile)      │  │
│  │                     │    │                                    │  │
│  │ - BuilderSession   │    │ - Long-lived identity truth       │  │
│  │ - InterviewPlanner │    │ - Semantic fields (name, occupation│  │
│  │ - SemanticExtractor│    │   background, persona, etc.)      │  │
│  └──────────┬──────────┘    │ - COCInvestigatorProfile (stats)  │  │
│             │               └──────────────────────────────────┘  │
│             │                           ▲                          │
│             ▼                           │                          │
│  ┌─────────────────────┐    ┌──────────────────────────────────┐  │
│  │ ArchiveSemantic     │    │ CampaignProjection               │  │
│  │ Extractor          │    │ (per-campaign mutable instances)  │  │
│  │ (Protocol)         │    │ - SAN, HP, conditions            │  │
│  │                     │    │ - Module-specific state          │  │
│  │ - Heuristic        │    │ - Session transcripts            │  │
│  │ - ModelGuided      │    │ (not yet implemented)            │  │
│  └─────────────────────┘    └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Current Data Flow

```
User Answer → BuilderSession.answers[slot] → SemanticExtractor.extract()
                                                    ↓
                                            Heuristic OR ModelGuided
                                                    ↓
                                    create_profile() → ArchiveRepository
```

### Current Problems

1. **ModelGuidedArchiveSemanticExtractor** currently receives raw answers and returns them almost verbatim — it paraphrases but doesn't synthesize
2. **No normalized character sheet sections** — archive fields don't map cleanly to COC 7e character sheet sections
3. **Heuristic fallbacks are brittle** — keyword matching produces inconsistent results

## Proposed Architecture: Synthesis-First Builder

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENHANCED CHARACTER LAYER (Track B v2.3)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    BUILDER INTERVIEW LAYER                          │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │   │
│  │  │ BuilderSession  │  │ InterviewPlanner│  │ AnswerNormalizer   │ │   │
│  │  │ (unchanged)     │  │ (unchanged)     │  │ (NEW: normalizes   │ │   │
│  │  │                 │  │                 │  │  raw answers to    │ │   │
│  │  │                 │  │                 │  │  canonical slots)  │ │   │
│  │  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘ │   │
│  └───────────┼───────────────────┼──────────────────────┼────────────┘   │
│              │                   │                      │                  │
│              ▼                   ▼                      ▼                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                 AI SUMMARIZATION SYNTHESIS LAYER (NEW)             │   │
│  │                                                                     │   │
│  │  ┌───────────────────────┐    ┌─────────────────────────────────┐  │   │
│  │  │ CharacterSheetSynthesizer│  │ SectionNormalizer              │  │   │
│  │  │                        │    │                                 │  │   │
│  │  │ - Receives normalized │    │ - Maps synthesis output to     │  │   │
│  │  │   interview answers    │    │   COC 7e character sheet       │  │   │
│  │  │ - Synthesizes into    │    │   sections                     │  │   │
│  │  │   cohesive narrative  │    │ - Validates against COC rules  │  │   │
│  │  │ - Returns structured  │    │                                 │  │   │
│  │  │   synthesis result   │    │                                 │  │   │
│  │  └───────────┬───────────┘    └──────────────┬──────────────────┘  │   │
│  └──────────────┼────────────────────────────────┼────────────────────┘   │
│                 │                                 │                       │
│                 ▼                                 ▼                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    ARCHIVE CONTRACT LAYER                           │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │ ArchiveProfile (ENHANCED)                                    │  │   │
│  │  │                                                             │  │   │
│  │  │ EXISTING:          │  NEW COC 7e NORMALIZED SECTIONS:        │  │   │
│  │  │ - name             │  - portrait_summary                    │  │   │
│  │  │ - occupation      │  - character_concept (from synthesis)   │  │   │
│  │  │ - background      │  - backstory_narrative                  │  │   │
│  │  │ - persona fields │  - mental_disorders                     │  │   │
│  │  │ - COC stats       │  - injuries_scars                       │  │   │
│  │  │                   │  - phobias_manias                      │  │   │
│  │  │                   │  - significant_characters               │  │   │
│  │  │                   │  - possessions_assets                   │  │   │
│  │  │                   │  - income_spending                      │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Implementation Approach |
|-----------|----------------|------------------------|
| `AnswerNormalizer` | Normalizes raw user input to canonical slot format | Regex + keyword extraction, handles variations in Chinese input |
| `CharacterSheetSynthesizer` | Transforms normalized answers into cohesive character narrative | Model-guided with structured output schema |
| `SectionNormalizer` | Maps synthesis output to COC 7e character sheet sections | Rule-based mapping with validation |
| `ArchiveProfile` (enhanced) | Stores both legacy fields and new normalized sections | Backward-compatible Pydantic model extension |

## Recommended Project Structure

```
src/dm_bot/coc/
├── __init__.py
├── archive.py              # EXISTING: InvestigatorArchiveProfile, Repository
├── builder.py              # EXISTING: ConversationalCharacterBuilder
├── assets.py               # EXISTING: COC asset loading
├── panels.py               # EXISTING: Character panel display
├── models.py               # EXISTING: COCInvestigatorProfile, COCAttributes
│
├── synthesis/              # NEW: AI Summarization Layer
│   ├── __init__.py
│   ├── synthesizer.py      # CharacterSheetSynthesizer
│   ├── normalizer.py       # SectionNormalizer for COC 7e
│   ├── contracts.py        # Pydantic contracts for synthesis I/O
│   └── prompts.py          # Synthesis prompt templates
│
├── contracts/              # NEW: Archive-Builder Contract Layer
│   ├── __init__.py
│   ├── archive_profile.py  # Enhanced ArchiveProfile with normalized sections
│   ├── builder_session.py  # Updated BuilderSession with normalized answers
│   └── profile_factory.py  # Creates profiles from synthesis results
│
└── normalization/          # NEW: Answer Normalization
    ├── __init__.py
    ├── answer_normalizer.py
    └── slot_mapping.py
```

### Structure Rationale

- **`synthesis/`:** Isolates AI summarization logic — keeps model interaction patterns separate from business logic
- **`contracts/`:** Centralizes data structure definitions — ensures archive-builder communication has explicit schemas
- **`normalization/`:** Isolates input preprocessing — separates "how we clean user input" from "how we synthesize character"

## Architectural Patterns

### Pattern 1: Synthesis-First Semantic Extraction

**What:** Instead of extracting semantic fields directly from raw interview answers, first synthesize the answers into a cohesive character narrative, then extract canonical fields from that synthesis.

**When to use:** When AI summarization tends to merely copy/paraphrase rather than synthesize.

**Trade-offs:**
- Pros: Produces more cohesive characters; separates "what the user said" from "what the character is"
- Cons: Adds an extra LLM call; requires careful prompt design to avoid hallucination

**Example:**
```python
class CharacterSheetSynthesizer:
    async def synthesize(self, answers: dict[str, str]) -> CharacterSynthesisResult:
        # Step 1: Synthesize cohesive narrative from raw answers
        narrative = await self._synthesize_narrative(answers)
        
        # Step 2: Extract canonical fields from synthesis
        extracted = await self._extract_fields(narrative)
        
        return CharacterSynthesisResult(
            narrative=narrative,
            character_concept=extracted.character_concept,
            backstory_narrative=extracted.backstory,
            # ... normalized COC 7e sections
        )
```

### Pattern 2: COC 7e Section Normalization

**What:** Map all character information to standard COC 7e character sheet sections, with explicit validation.

**When to use:** When character data needs to be exportable or compatible with standard COC tools.

**Trade-offs:**
- Pros: Standard compliance; easier integration with external tools
- Cons: May require field expansion for non-standard character concepts

**Example:**
```python
class SectionNormalizer:
    COC7E_SECTIONS = [
        "personal_data",           # name, age, occupation, residence
        "character_concept",       # one-line concept
        "backstory_narrative",     # long-form backstory
        "mental_disorders",        # disorders (if any)
        "injuries_scars",          # physical marks
        "phobias_manias",          # fears and obsessions
        "significant_characters",  # important NPCs
        "possessions_assets",      # gear and money
        "income_spending",         # cash flow
    ]
    
    def normalize(self, synthesis: CharacterSynthesisResult) -> COC7eProfileSections:
        # Map synthesis output to canonical sections
        # Validate against COC rules (e.g., occupation skill limits)
        pass
```

### Pattern 3: Contract-Driven Archive Creation

**What:** Use explicit Pydantic contracts for all archive-builder communication, with clear schemas for input and output.

**When to use:** When the system needs to be maintainable and testable.

**Trade-offs:**
- Pros: Type safety; explicit interfaces; easier testing
- Cons: More upfront schema design work

## Data Flow

### New Builder Flow

```
1. User provides answer
       ↓
2. BuilderSession.answers[slot] = answer
       ↓
3. AnswerNormalizer.normalizeslot → canonical_format
       ↓
4. InterviewPlanner.next_question → next user prompt
       ↓ (when builder complete)
5. CharacterSheetSynthesizer.synthesize(all_normalized_answers)
       ↓
6. SectionNormalizer.normalize(synthesis_result)
       ↓
7. ArchiveProfileFactory.create_profile(normalized_sections)
       ↓
8. ArchiveRepository.create_profile() → persistent archive
```

### Key Data Transformations

| Stage | Input | Output | Purpose |
|-------|-------|--------|---------|
| `AnswerNormalizer` | `"我叫张建国，是个落魄的医生"` | `{name: "张建国", occupation: "医生", concept: "落魄的医生"}` | Clean input variations |
| `CharacterSheetSynthesizer` | Normalized answers | `{character_concept: "...", backstory: "..."}` | Synthesize cohesive narrative |
| `SectionNormalizer` | Synthesis result | `COC7eProfileSections` | Map to COC 7e standard |
| `ArchiveProfileFactory` | COC7e sections | `InvestigatorArchiveProfile` | Create persistent archive |

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Builder → Synthesis | `CharacterSheetSynthesizer.synthesize()` | Called once at builder completion |
| Synthesis → Archive | `ArchiveProfileFactory.create_profile()` | Creates profile from synthesis |
| Archive → Projection | Standard projection flow | Unchanged from current architecture |

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Local Model (Ollama) | OpenAI-compatible API | Used for synthesis; router model for structured output |
| COC Rules Data | 5e-srd-api style endpoint | For occupation skills, rules lookup |

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-10 concurrent builders | Current architecture fine; synthesis adds ~1-2s per character |
| 10-100 concurrent builders | Consider caching synthesis prompts; add synthesis request queue |
| 100+ concurrent builders | Consider pre-computing common occupation templates |

### Scaling Priorities

1. **First bottleneck:** Model inference time for synthesis — mitigate with timeout handling and fallback to heuristic extraction
2. **Second bottleneck:** Archive creation serialization — already handled by current in-memory repository

## Anti-Patterns

### Anti-Pattern 1: Synthesis Without Validation

**What people do:** Pass synthesis output directly to archive without validating against COC rules.

**Why it's wrong:** AI can suggest invalid occupation skills or impossible attribute combinations.

**Do this instead:** Always validate synthesis output through `SectionNormalizer` with COC rule checks.

### Anti-Pattern 2: Replacing Heuristics Entirely

**What people do:** Remove all heuristic fallbacks and rely entirely on model-guided extraction.

**Why it's wrong:** Model can fail silently; no graceful degradation.

**Do this instead:** Keep heuristic extractors as fallback — use model-guided as primary with heuristic as safety net.

### Anti-Pattern 3: Premature Section Expansion

**What people do:** Add many COC 7e sections before validating the core synthesis flow works.

**Why it's wrong:** Complexity explodes; hard to debug.

**Do this instead:** Implement core synthesis first, then add sections incrementally.

## Build Order Recommendation

### Phase 1: Foundation (Week 1)

1. Create `synthesis/contracts.py` with Pydantic schemas for synthesis I/O
2. Implement `AnswerNormalizer` with basic slot cleaning
3. Update `BuilderSession` to store normalized answers alongside raw answers

### Phase 2: Core Synthesis (Week 2)

1. Implement `CharacterSheetSynthesizer` with narrative synthesis prompt
2. Add `SectionNormalizer` with basic COC 7e section mapping
3. Create `ArchiveProfileFactory` to construct profiles from synthesis

### Phase 3: Integration (Week 3)

1. Update `ConversationalCharacterBuilder` to use new synthesis flow
2. Add backward compatibility layer for existing archive fields
3. Implement fallback from synthesis to heuristic extraction

### Phase 4: Polish (Week 4)

1. Expand COC 7e sections based on playtesting feedback
2. Add validation rules for occupation skills and attributes
3. Optimize synthesis prompt based on character quality evaluation

## Sources

- Current archive implementation: `src/dm_bot/coc/archive.py`
- Current builder implementation: `src/dm_bot/coc/builder.py`
- Current COC models: `src/dm_bot/characters/models.py`
- Track B roadmap: `.planning/ROADMAP.md` Track B section
- COC 7e character sheet reference: Chaosium official character sheets

---

*Architecture research for: Archive/Builder Normalization with AI Summarization*
*Researched: 2026-03-28*
