# Phase E82 Context: Chase Rules Implementation

## Goal
Implement COC 7e chase mechanics including pursuer/fleeer roles, CON rolls, and obstacle resolution.

## Background

### Current State
- Combat system exists but no chase mechanics
- Skill check system exists
- Need to implement COC 7e Chapter 6 chase rules

### COC 7e Chase Rules Summary

**Core Concepts:**
1. **Chase Participants**: Divided into Fleeers (trying to escape) and Pursuers (trying to catch)
2. **Locations**: Chase happens across multiple locations (cards/spaces)
3. **CON Rolls**: Each round, participants roll CON to avoid penalties
4. **Obstacles**: Barriers requiring skill checks to overcome
5. **Resolution**: Escape, capture, or transition to combat

**Chase Flow:**
1. Determine roles (fleeer/pursuer)
2. Set up locations
3. Each round:
   - CON roll (failure = -1 MOV for round)
   - Fleeers move first (DEX order)
   - Pursuers move (try to close distance)
   - Resolve obstacles
4. Check end conditions

**Obstacles:**
- Physical barriers (Jump, Climb, Swim)
- Hazards (Dodge, Drive)
- Mental (Spot Hidden to find path)
- Failure = fall behind or take damage

## Design Decisions

### 1. Chase State Model

**Decision**: Pydantic model with round-by-round tracking

```python
class ChaseEncounter(BaseModel):
    """A chase encounter."""
    
    # Participants
    fleeers: list[ChaseParticipant]
    pursuers: list[ChaseParticipant]
    
    # Locations
    locations: list[ChaseLocation]
    
    # State
    current_round: int = 1
    active: bool = True
    
    def resolve_round(self) -> ChaseRoundResult:
        """Resolve one round of chase."""
        # CON checks
        # Movement
        # Obstacles
        # Check end conditions
```

### 2. Participant Model

```python
class ChaseParticipant(BaseModel):
    """A participant in a chase."""
    
    character_id: str
    role: Literal["fleeer", "pursuer"]
    current_location: int  # Index in locations list
    mov: int
    con: int
    dex: int
    
    # State
    exhausted: bool = False  # Failed CON check
    conditions: list[str] = []  # From obstacle failures
```

### 3. Obstacle Model

```python
class ChaseObstacle(BaseModel):
    """An obstacle in a chase location."""
    
    name: str
    skill_required: str  # e.g., "jump", "climb", "dodge"
    difficulty: int  # Skill value needed
    failure_effect: str  # "fall_back", "damage", "stuck"
    description: str
```

### 4. Integration Points

**Combat Integration:**
- Chase can transition to combat if pursuer catches fleeer
- Combat can transition to chase if someone flees

**Skill System:**
- Use existing skill check resolution
- Track skill usage for improvement

**RuntimeTestDriver:**
- Methods to start/resolve chases
- Assertions for chase state

## Implementation Requirements

### CHASE-01: Chase Data Models
- ChaseEncounter, ChaseParticipant, ChaseLocation
- ChaseObstacle, ChaseRoundResult
- State transitions

### CHASE-02: CON Check System
- CON roll each round
- Exhaustion on failure
- MOV penalty when exhausted

### CHASE-03: Movement System
- Fleeers move first (DEX order)
- Pursuers move to close distance
- Relative position tracking

### CHASE-04: Obstacle Resolution
- Skill checks for obstacles
- Failure consequences
- Multiple obstacle types

### CHASE-05: End Conditions
- Escape (fleeer reaches end)
- Capture (pursuer catches fleeer)
- Transition to combat
- E2E scenario validation

## Files to Create/Modify

- `src/dm_bot/rules/coc/chase.py` - Core chase system
- `src/dm_bot/gameplay/chase.py` - Gameplay integration
- `src/dm_bot/testing/runtime_driver.py` - Test access
- `tests/rules/coc/test_chase.py` - Unit tests
- `tests/scenarios/acceptance/scen_chase.yaml` - E2E

## Success Criteria

- [ ] Chase mechanics support pursuer/fleeer roles
- [ ] CON rolls each round with exhaustion
- [ ] Movement based on DEX order
- [ ] Obstacles require skill checks
- [ ] End conditions: escape, capture, combat
- [ ] Integration with combat system
- [ ] Unit tests for all mechanics
- [ ] E2E scenario validates chase flow
