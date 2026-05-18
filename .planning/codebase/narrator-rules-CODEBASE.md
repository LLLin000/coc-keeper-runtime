# Narrator & Rules Package Analysis

**Generated:** 2026-04-25
**Packages:** `src/dm_bot/narrator/`, `src/dm_bot/rules/`

---

## 1. Package Purpose & Responsibilities

### `narrator/`

AI narrative generation client. Generates prose and roleplay text from state + results.

- **Responsibility:** Transform structured game state into natural language narration
- **Does NOT:** Modify state, compute rules, manage sessions

### `rules/`

Deterministic COC 7th Edition rules engine. Pure computation with no side effects.

- **Responsibility:** Dice, checks, combat, sanity, magic, derived attributes, experience
- **Does NOT:** State changes, persistence, narrative generation

---

## 2. Key Classes and Functions

### `narrator/client.py`

```python
class NarratorClient(Protocol):
    def generate(self, prompt: str) -> str: ...

class SimpleNarrator:
    def generate(self, prompt: str) -> str: str  # Placeholder
```

### `narrator/prompts.py`

```python
def scene_opening(scene_name: str, scene_desc: str, characters: list[str]) -> str
def action_ack(action_text: str, character_name: str) -> str
def scene_resolution(scene_name: str, actions_summary: str) -> str
```

### `rules/dice.py`

```python
# Type aliases
AdvantageMode = Literal["none", "advantage", "disadvantage"]
COCDifficulty = Literal["regular", "hard", "extreme"]

# Models
class DiceOutcome(BaseModel):
    expression: str; total: int; rendered: str

class PercentileOutcome(BaseModel):
    value: int; difficulty: COCDifficulty; rolled: int; success: bool
    success_rank: str; critical: bool; fumble: bool; ...

# Protocols
class DiceRoller(Protocol):
    def roll(self, expression: str, *, advantage: AdvantageMode = "none") -> DiceOutcome: ...
    def roll_percentile(self, *, value: int, difficulty: COCDifficulty = "regular",
                       bonus_dice: int = 0, penalty_dice: int = 0, pushed: bool = False) -> PercentileOutcome: ...

# Implementations
class SeededDiceRoller:
    def __init__(self, seed: int) -> None
    def roll(self, expression: str, *, advantage: AdvantageMode = "none") -> DiceOutcome
    def roll_percentile(self, *, value: int, ...) -> PercentileOutcome

class D20DiceRoller:
    def roll(self, expression: str, *, advantage: AdvantageMode = "none") -> DiceOutcome
    def roll_percentile(self, *, value: int, ...) -> PercentileOutcome

def seeded_dice_roller(seed: int) -> SeededDiceRoller
```

### `rules/coc/__init__.py`

Re-exports all public symbols from submodules.

### `rules/coc/derived.py`

```python
@dataclass
class COCAttributes:
    str: int = 50; con: int = 50; siz: int = 50; dex: int = 50
    app: int = 50; int: int = 50; pow: int = 50; edu: int = 50

class DerivedAttributes(BaseModel):
    luck: int; hp: int; hp_max: int; mp: int; mp_max: int
    san: int; san_max: int; move_rate: int; build: int
    damage_bonus: int; damage_bonus_str: str

# Calculation functions
def calculate_luck(pow_value: int) -> int
def calculate_hp(con_value: int, siz_value: int) -> int
def calculate_mp(pow_value: int) -> int
def calculate_sanity(pow_value: int) -> int
def calculate_move_rate(str_value: int, dex_value: int, siz_value: int, age: int = 0) -> int
def calculate_build(str_value: int, siz_value: int) -> int
def calculate_damage_bonus(str_value: int, siz_value: int) -> tuple[int, str]
def get_damage_bonus_dice_expression(str_value: int, siz_value: int) -> str
def calculate_all_derived_attributes(attributes: COCAttributes, age: int = 0) -> DerivedAttributes
def get_age_modifiers(age: int) -> dict[str, int]
def apply_age_modifiers(attributes: COCAttributes, age: int) -> COCAttributes
def roll_characteristic() -> int
def generate_characteristics() -> dict[str, int]
def spend_luck(current_luck: int, amount: int = 1) -> tuple[int, bool]
def recover_luck(max_luck: int, current_luck: int, rest_periods: int = 0) -> int
```

### `rules/coc/combat.py`

```python
class CombatAction(StrEnum): FIGHT; SHOOT; BRAWL; DODGE; GRAPPLE; ...
class WeaponType(StrEnum): MELEE; RANGED; THROWN

class CombatantStats(BaseModel):
    name: str; dex: int; fighting: int; shooting: int; brawl: int; dodge: int; ...
    hp: int; hp_max: int; armor: int; build: int; damage_bonus: int; ...

class CombatCheckResult(BaseModel):
    action: CombatAction; actor_name: str; target_name: str; rolled: int
    success: bool; success_rank: str; critical: bool; fumble: bool
    damage: int; final_damage: int; impale: bool; major_wound: bool; ...

def roll_initiative(dex_value: int) -> int
def get_initiative_order(combatants: list[tuple[str, int]]) -> list[tuple[str, int, int]]
def resolve_fighting_attack(attacker, defender, attacker_roll, defender_roll, ...) -> CombatCheckResult
def resolve_shooting_attack(attacker, defender, attacker_roll, range_modifier=0, ...) -> CombatCheckResult
def resolve_brawl_attack(attacker, defender, attacker_roll, defender_roll, ...) -> CombatCheckResult
def resolve_grapple_attack(attacker, defender, attacker_roll, defender_roll, ...) -> CombatCheckResult
def calculate_build(str_value: int, siz_value: int) -> int
def calculate_damage_bonus(str_value: int, siz_value: int) -> int
def get_damage_bonus_string(str_value: int, siz_value: int) -> str
RANGE_MODIFIERS: dict[str, int]
def get_range_modifier(weapon_range: str, actual_distance: int) -> int
```

### `rules/coc/sanity.py`

```python
class SanityLossType(StrEnum): UNKNOWN; SEEN; COMBAT; DEATH; MYTHOS
class InsanityType(StrEnum): NONE; TEMPORARY; INDEFINITE

COMMON_PHOBIAS: list[str]
COMMON_MANIAS: list[str]

class SanityCheckResult(BaseModel):
    actor_name: str; current_san: int; max_san: int; rolled: int
    success: bool; success_rank: str; sanity_loss: int; mythos_gain: int
    insanity_triggered: InsanityType; ...

class InsanityBreakResult(BaseModel):
    actor_name: str; insanity_type: InsanityType; trigger_event: str
    acute_response: str; duration_rounds: int; ...

def get_mythos_gain_for_encounter(encounter_type: str) -> int
def get_sanity_loss_for_encounter(encounter_type: str, rolled_loss: int | None = None) -> int
def roll_insanity_break(actor_name, current_san, max_san, trigger_event) -> InsanityBreakResult
def resolve_sanity_check(actor_name, current_san, max_san, rolled, ...,
                          loss_on_success: int = 0, loss_on_failure: int = 0, ...) -> SanityCheckResult
def calculate_sanity_recovery(current_san, max_san, rest_periods=0, ...) -> int
def spend_luck_for_sanity(actor_name, current_san, max_san, luck_available, ...) -> tuple[int, int, str]
```

### `rules/coc/skills.py`

```python
class SkillCategory(StrEnum): COMBAT; LANGUAGE; KNOWLEDGE; INTERPERSONAL; OBSERVATION; PRACTICAL; CRAFT; MAGIC; ...

class SkillDefinition(BaseModel):
    name: str; name_cn: str; category: SkillCategory; base_points: int
    occupational: bool; interest: bool; specialized: bool; subtypes: list[str]

COC_SKILLS: dict[str, SkillDefinition]  # 80+ skills

class SuccessRank(StrEnum): CRITICAL; EXTREME; HARD; REGULAR; FAILURE; FUMBLE

class SkillCheckResult(BaseModel):
    skill_key: str; skill_name_cn: str; skill_value: int; rolled: int
    success: bool; success_rank: SuccessRank; critical: bool; fumble: bool; ...

def resolve_skill_check(skill_key, skill_value, rolled,
                        bonus_dice=0, penalty_dice=0,
                        difficulty: Literal["regular","hard","extreme"] = "regular",
                        pushed: bool = False) -> SkillCheckResult
def get_skills_by_category(category: SkillCategory) -> dict[str, SkillDefinition]
def get_skill_categories() -> list[SkillCategory]
def is_specialized_skill(skill_key: str) -> bool
def expand_specialized_skill(skill_key: str, specialization: str | None = None) -> str
def get_skill_display_name(skill_key: str, specialization: str | None = None) -> str

OCCUPATIONAL_SKILL_POINTS: dict[int, int]
INTEREST_SKILL_POINTS: dict[int, int]
IMPROVEMENT_SKILL_POINTS: dict[int, int]
```

### `rules/coc/magic.py`

```python
class SpellSchool(StrEnum): CONJURATION; DIVINATION; ENCHANTMENT; EVOCATION; NECROMANCY; TRANSMUTATION; GENERAL
class SpellType(StrEnum): SPELL; RITUAL; SUMMONING; BINDING; SUMMONING_BINDING

class SpellDefinition(BaseModel):
    name: str; name_cn: str; school: SpellSchool; spell_type: SpellType
    casting_time: str; mp_cost: int; mp_cost_percent: bool; sanity_loss: int
    difficulty: Literal["regular","hard","extreme"]; creature_type: str; ...

COC_SPELLS: dict[str, SpellDefinition]

class SpellCastResult(BaseModel): ...
class SpellbookEntry(BaseModel): spell_key: str; learned: bool; casting_threshold_override: int; notes: str
class Spellbook(BaseModel):
    entries: dict[str, SpellbookEntry]
    def add_spell(self, spell_key: str, notes: str = "") -> bool: ...
    def remove_spell(self, spell_key: str) -> bool: ...
    def has_spell(self, spell_key: str) -> bool: ...
    def get_spell_cost(self, spell_key: str, caster_max_mp: int) -> int: ...

def resolve_spell_cast(spell_key, caster_name, caster_int, caster_pow, ...,
                       rolled: int, bonus_dice=0, penalty_dice=0) -> SpellCastResult
def calculate_mp(pow_value: int) -> int
def get_mp_for_level(pow_value: int, level: int) -> int
```

### `rules/coc/chase.py`

```python
class ChaseRole(StrEnum): FLEER; PURSUER
class ChaseStatus(StrEnum): ACTIVE; ESCAPED; CAPTURED; EXHAUSTED; IN_COMBAT

class ChaseParticipant(BaseModel): ...
class ChaseObstacle(BaseModel): ...
class ChaseLocation(BaseModel): ...
class ChaseRoundResult(BaseModel): ...
class ChaseEncounter(BaseModel):
    participants: dict[str, ChaseParticipant]; fleeers: list[str]; pursuers: list[str]
    locations: list[ChaseLocation]; current_round: int; active: bool
    def add_participant(...): ...
    def add_location(...): ...
    def resolve_round(dice_rolls: dict[str, int] | None = None) -> ChaseRoundResult: ...
```

### `rules/coc/experience.py`

```python
CREDIT_RATING_OCCUPATIONAL_POINTS: dict[int, int]
INT_INTEREST_POINTS: dict[int, int]

class SkillImprovementResult(BaseModel): ...

def roll_skill_improvement(skill_key, current_value, improvement_roll=None) -> SkillImprovementResult
def roll_all_skill_improvements(skills_used, current_skills, ...) -> list[SkillImprovementResult]
def calculate_new_session_skill_points(credit_rating, int_value) -> NewSessionSkillPoints
def spend_occupational_point(current_skills, skill_key, points) -> tuple[dict, bool]
def spend_interest_point(current_skills, skill_key, points) -> tuple[dict, bool]
def calculate_build_points_spent(characteristics) -> int
def generate_standard_characteristics() -> dict[str, int]
OCCUPATION_SKILL_SUGGESTIONS: dict[str, list[str]]
def get_occupation_skills(occupation: str) -> list[str]
```

---

## 3. How Narrator and Rules Interact

### Data Flow (per Architecture Spec)

```
scene.round.resolve()
    |
    +-- rules.checks.skill_roll()     # skill checks via coc/skills.py
    +-- rules.combat.resolve()         # combat via coc/combat.py
    +-- rules.sanity.check()           # horror/SAN via coc/sanity.py
    |
    v
scene.round.generate_resolution()
    |
    v
narrator.generate(prompt)            # narrative text
```

### Interaction Points

| From | To | Purpose |
|------|-----|---------|
| `scene/` | `rules.dice.SeededDiceRoller` | Roll dice with seed for determinism |
| `scene/` | `rules.coc.*` | Resolve checks, combat, SAN |
| `scene/` | `narrator.prompts.*` | Build prompts from results |
| `scene/` | `narrator.client.NarratorClient` | Generate narrative |

### Key Design Constraint

- **Rules produce data; Narrator consumes data**
- Rules (`coc/*`) return Pydantic models with `rendered: str` fields (human-readable summaries)
- Narrator receives structured results + renders them into prose

---

## 4. Design Patterns Used

### Protocol/Impl Pattern (Dice)
```python
class DiceRoller(Protocol): ...        # Interface
class SeededDiceRoller: ...            # Deterministic impl
class D20DiceRoller: ...               # Standard impl
```
Allows swapping roller implementations without changing call sites.

### Factory Pattern (Dice)
```python
def seeded_dice_roller(seed: int) -> SeededDiceRoller
```

### Data-Driven Rules
Skills (`COC_SKILLS`), Spells (`COC_SPELLS`), and constants are defined as module-level dicts, not hardcoded logic.

### Rich Models with `rendered` Field
Every `*Result` Pydantic model includes a `rendered: str` field containing pre-formatted Chinese output, enabling both structured consumption and human readability.

### Separation of Concerns
- **Pure functions** for all rule calculations (no side effects)
- **State** is held by caller (`scene/`), not within rules
- **Narrator** is side-effect free - generates text only

---

## 5. Dependencies

### External Imports

| Package | Source | Used By |
|---------|--------|---------|
| `d20` | `pip` | `rules/dice.py`, `rules/coc/combat.py` - dice expression parsing |
| `pydantic` | `pip` | All `*Result`, `*Definition` models |
| `random` | stdlib | `SeededDiceRoller` internally, `D20DiceRoller` |

### Internal Dependencies

| From | To | Reason |
|------|-----|--------|
| `rules.coc.*` | `rules/dice.py` | Uses `DiceRoller` Protocol |
| `rules/cice.py` | `rules/coc/skills.py` | Imports `COC_SKILLS` |
| `rules/coc/combat.py` | `rules/coc/derived.py` | `calculate_build`, `calculate_damage_bonus` |
| `rules/coc/sanity.py` | `rules/coc/skills.py` | Skill check resolution |
| `rules/coc/magic.py` | `rules/coc/skills.py` | Spell requirements |

### Narrator Dependencies

| From | To | Reason |
|------|-----|--------|
| `narrator/client.py` | (none yet) | Protocol only, placeholder impl |
| `narrator/prompts.py` | (none) | Pure functions |

---

## 6. File Structure Summary

```
src/dm_bot/
├── narrator/
│   ├── __init__.py
│   ├── client.py         # NarratorClient Protocol, SimpleNarrator placeholder
│   └── prompts.py        # scene_opening, action_ack, scene_resolution
└── rules/
    ├── __init__.py
    ├── dice.py           # DiceRoller Protocol + SeededDiceRoller + D20DiceRoller
    └── coc/
        ├── __init__.py   # Re-exports all public symbols
        ├── derived.py     # COCAttributes, DerivedAttributes, calculators
        ├── combat.py      # Combat resolution (Fight/Shoot/Brawl/Grapple)
        ├── sanity.py      # SAN checks, insanity, recovery
        ├── skills.py      # 80+ skills, SkillCheckResult
        ├── magic.py       # Spells, Spellbook, casting
        ├── chase.py       # Chase system
        └── experience.py  # Skill improvement, character advancement
```

---

*End of analysis*
