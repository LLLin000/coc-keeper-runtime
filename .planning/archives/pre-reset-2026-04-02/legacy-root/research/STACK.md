# Stack Research: Archive-Builder Normalization

**Domain:** Discord AI Keeper - Archive and Builder Data Contracts
**Researched:** 2026-03-28
**Confidence:** MEDIUM-HIGH

## Recommended Stack Additions

### Core Enhancement: Structured LLM Output

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `instructor` | 0.10.x | Structured output parsing from LLM responses | Directly addresses the AI summarization problem — transforms raw LLM output into validated Pydantic models. Works with Ollama's OpenAI-compatible API. |

### Existing Stack (Already Recommended)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.12+ | Main runtime | Lowest integration friction across Discord, AI, and database |
| `pydantic` + `pydantic-settings` | v2 line | Typed config and LLM I/O validation | Already in use — extends well for archive contracts |
| SQLAlchemy | 2.0.x | ORM for archive persistence | Already in use — JSONB handles flexible character data |
| PostgreSQL | 16/17 | Primary datastore | Already in use — JSONB for semi-structured archive fields |

## Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `instructor` | 0.10.x | Extract structured data from conversational builder responses | Use in builder flow when converting freeform interview answers to archive fields |
| `orjson` | current | Fast JSON serialization | Already in recommended set — use for archive JSONB serialization |
| `email-validator` | current | Email validation | Use for player/contact email fields in archive |
| `phonenumbers` | current | Phone validation | Optional — for contact fields if needed |

## Key Problem: AI Summarization in Builder Flow

The current issue: "AI just copies user input instead of summarizing into cohesive character attributes."

**Root cause:** Without structured output handling, the LLM returns freeform text that either:
- Gets copied verbatim (current behavior)
- Requires fragile regex/string parsing

**Solution:** Use `instructor` to define Pydantic models for each builder stage, then validate/normalize the LLM output:

```python
import instructor
from pydantic import BaseModel, Field
from typing import Optional

# Define what you want extracted from builder conversation
class CharacterBackground(BaseModel):
    backstory_summary: str = Field(description="2-3 sentence summary of character's history")
    key_motivation: str = Field(description="Primary motivation driving the investigator")
    significant_relationships: list[str] = Field(description="2-4 important relationships")
    trauma_or_loss: Optional[str] = Field(description="Any past trauma relevant to sanity")

# Use with Ollama (OpenAI-compatible)
client = instructor.from_ollama(base_url="http://localhost:11434", model="qwen3:4b")

normalized = client.chat.completions.create(
    model="qwen3:4b",
    messages=[{"role": "user", "content": user_input_from_builder}],
    response_model=CharacterBackground,
)
```

**Why instructor over alternatives:**
- Directly uses existing Pydantic v2 (already in stack)
- Automatic retry with validation failures
- Works with Ollama's OpenAI-compatible API
- Handles the "JSON in markdown" parsing problem automatically

## Alternative Approaches Considered

| Approach | Why Not | When It Makes Sense |
|----------|---------|---------------------|
| Custom regex/string parsing | Fragile, breaks with varied input, hard to maintain | Only if extremely simple fields |
| LangChain structured output | Heavy dependency, over-engineered for this use case | If you already use LangChain |
| Function calling only | Requires specific model support, not all local models support it well | When using GPT-4 API |
| Manual JSON parsing | Requires careful prompt engineering to get valid JSON | If you have full control over prompts |

## Archive Contract Patterns

### Pattern 1: Nested Pydantic Models for Character Sections

```python
from pydantic import BaseModel, Field, computed_field
from typing import Optional

class InvestigatorCharacteristics(BaseModel):
    """Section 1: Core COC attributes (STR, CON, SIZ, DEX, INT, POW, APP, EDU)"""
    strength: int = Field(ge=0, le=100, description="STR - Strength")
    constitution: int = Field(ge=0, le=100, description="CON - Constitution")
    size: int = Field(ge=0, le=100, description="SIZ - Size")
    dexterity: int = Field(ge=0, le=100, description="DEX - Dexterity")
    intelligence: int = Field(ge=0, le=100, description="INT - Intelligence")
    power: int = Field(ge=0, le=100, description="POW - Power")
    appearance: int = Field(ge=0, le=100, description="APP - Appearance")
    education: int = Field(ge=0, le=100, description="EDU - Education")

    @computed_field
    @property
    def hp_max(self) -> int:
        return (self.constitution + self.size) // 10

    @computed_field
    @property
    def sanity_max(self) -> int:
        return self.power

class InvestigatorSkills(BaseModel):
    """Section 2: Skill points and specializations"""
    accounting: int = Field(default=0, ge=0, le=100)
    anthropology: int = Field(default=0, ge=0, le=100)
    appraise: int = Field(default=0, ge=0, le=100)
    archaeology: int = Field(default=0, ge=0, le=100)
    # ... complete COC skill list

class InvestigatorProfile(BaseModel):
    """Full archive profile contract"""
    name: str = Field(min_length=1, max_length=100)
    occupation: str
    age: int = Field(ge=16, le=90)
    sex: str
    residence: str
    birthplace: str
    
    characteristics: InvestigatorCharacteristics
    skills: InvestigatorSkills
    
    # Narrative fields that benefit from AI summarization
    backstory: str = Field(description="Character history summary")
    description: str = Field(description="Physical description")
    ideology_or_beliefs: Optional[str] = None
    significant_people: list[str] = Field(default_factory=list)
    meaningful_locations: list[str] = Field(default_factory=list)
    treasured_possessions: list[str] = Field(default_factory=list)
    injuries_scars: Optional[str] = None
    phobias_manias: Optional[str] = None
    encounters_with_strange: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Dr. Eleanor Vance",
                "occupation": "Professor of Anthropology",
                "age": 34,
                "sex": "F",
                "residence": "Arkham, Massachusetts",
                "birthplace": "Salem, Massachusetts"
            }
        }
```

### Pattern 2: Builder Stage Contracts

Each builder interview stage gets its own Pydantic model:

```python
class BuilderStageIdentity(BaseModel):
    """Stage 1: Basic identity"""
    name: str
    occupation: str
    age: int
    sex: str

class BuilderStageCharacteristics(BaseModel):
    """Stage 2: Roll characteristics"""
    rolls: dict[str, int]  # {"STR": 65, "CON": 50, ...}

class BuilderStageBackground(BaseModel):
    """Stage 3: Narrative backstory (uses instructor for summarization)"""
    backstory_summary: str
    key_motivation: str
    significant_relationships: list[str]
```

## JSON Schema for API Contracts

Pydantic v2 generates JSON Schema automatically — useful for archive API contracts:

```python
from pydantic import model_json_schema

schema = model_json_schema(InvestigatorProfile)
# Returns JSON Schema dict for FastAPI documentation
```

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Additional database (MongoDB, etc.) | PostgreSQL JSONB already handles flexible character data | Enhance existing SQLAlchemy models |
| Full-text search library (Elasticsearch) | Overkill for character archive | PostgreSQL text search or simple LIKE |
| Character sheet UI library | Discord is the primary surface | Focus on data contracts first |
| Live character sync with D&D Beyond | Not the target — local-first | Import adapters for static character data |

## Installation

```bash
# Core addition for v2.3
uv add instructor

# Already in recommended set - verify installed
uv add orjson email-validator pydantic pydantic-settings
```

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| instructor 0.10.x | pydantic v2, openai SDK, httpx | Works with Ollama OpenAI-compatible API |
| pydantic v2.10+ | FastAPI, SQLAlchemy, instructor | Already in current stack |
| SQLAlchemy 2.0+ | PostgreSQL, asyncpg, Alembic | Already in current stack |

## Sources

- Context7 /pydantic/pydantic — field_validator, model_validator, computed_field patterns
- Context7 /instructor-ai/instructor — structured output extraction with Pydantic
- Pydantic v2 docs — JSON Schema generation
- Ollama OpenAI compatibility — confirmed instructor works with local Ollama
- COC 7th Ed character sheet sections — Chaosium official, cthulhuclub.com reference

---

*Stack research for: Archive-Builder Normalization v2.3*
*Researched: 2026-03-28*
