# Phase E79 Context: Skill Usage Tracking & Combat Integration

## Goal
Implement skill usage tracking during combat for post-session improvement.

## Background

### Current State
- **Combat System** (`combat.py`): Fully functional with Fighting, Shooting, Brawl, Grapple, Dodge
- **Experience System** (`experience.py`): Skill improvement mechanics exist (1d100 < skill → +1d10)
- **Gap**: Combat doesn't track which skills were used, so players can't improve skills based on usage

### COC 7e Rules Reference
- Skills improve through "experience checks" at the end of a session
- Skills that were "used successfully" during the session can be rolled for improvement
- A skill is considered "used" if the player made a skill check (regardless of success/failure)

## Design Decisions

### 1. Where to Track Skills

**Decision**: Store in `SessionStore` as part of session state

**Rationale**:
- SessionStore already tracks campaign state, members, and phases
- Skill usage is session-scoped (resets each session)
- Easy access from TurnRunner and RuntimeTestDriver
- Can be persisted to SQLite if needed

**Data Structure**:
```python
class SkillUsageTracker(BaseModel):
    """Tracks skill usage per player per session."""
    
    # Map: player_id -> skill_name -> usage_count
    usage: dict[str, dict[str, int]] = Field(default_factory=dict)
    
    # Map: player_id -> skill_name -> success_count
    successes: dict[str, dict[str, int]] = Field(default_factory=dict)
    
    def record_usage(self, player_id: str, skill_name: str, success: bool = False):
        """Record that a player used a skill."""
        if player_id not in self.usage:
            self.usage[player_id] = {}
            self.successes[player_id] = {}
        
        self.usage[player_id][skill_name] = self.usage[player_id].get(skill_name, 0) + 1
        if success:
            self.successes[player_id][skill_name] = self.successes[player_id].get(skill_name, 0) + 1
    
    def get_eligible_skills(self, player_id: str) -> list[str]:
        """Get list of skills eligible for improvement."""
        return list(self.usage.get(player_id, {}).keys())
    
    def clear(self):
        """Clear all usage data (call at session end)."""
        self.usage.clear()
        self.successes.clear()
```

### 2. What Counts as "Skill Usage"

**Decision**: All skill attempts count, but track success separately

**Rationale**:
- COC 7e says "used successfully" but Keeper discretion applies
- Tracking both gives flexibility
- Failed attempts still represent practice/learning

**Combat Skills to Track**:
- `fighting` - Fighting attacks
- `shooting` - Shooting attacks
- `brawl` - Brawl attacks
- `grapple` - Grapple attempts
- `dodge` - Dodge attempts
- `throw` - Thrown weapon attacks

### 3. When Does Improvement Happen

**Decision**: Explicit "improvement phase" triggered by KP

**Rationale**:
- COC 7e has specific "downtime" for improvement
- Automatic improvement at session end might be jarring
- KP control allows narrative pacing
- Can be triggered via command: `/improvement_phase` or similar

**Flow**:
1. Combat ends (or session reaches appropriate point)
2. KP triggers improvement phase
3. System rolls 1d100 for each eligible skill
4. If roll < current skill, add 1d10
5. Clear usage tracker

### 4. Integration Points

#### Combat Resolution Hook
Modify combat resolution functions to record skill usage:

```python
# In combat.py
from dm_bot.orchestrator.session_store import get_session_store

def resolve_fighting_attack(
    attacker_id: str,
    target_id: str,
    weapon_skill: int,
    # ... other params
) -> FightingResult:
    # ... existing resolution logic ...
    
    # Record skill usage
    session = get_session_store()
    if session and session.skill_tracker:
        session.skill_tracker.record_usage(
            player_id=attacker_id,
            skill_name="fighting",
            success=result.success
        )
    
    return result
```

#### RuntimeTestDriver Access
Add methods to RuntimeTestDriver:

```python
# In runtime_driver.py
class RuntimeTestDriver:
    # ... existing methods ...
    
    def get_skill_usage(self, player_id: str) -> dict[str, int]:
        """Get skill usage for a player (for test assertions)."""
        session = self.session_store
        if session and session.skill_tracker:
            return session.skill_tracker.usage.get(player_id, {})
        return {}
    
    def trigger_improvement_phase(self) -> ImprovementResult:
        """Trigger skill improvement phase."""
        # ... implementation ...
        pass
```

#### Scenario Assertions
Add new assertion types for scenarios:

```yaml
assertions:
  skill_usage:
    player_id: "u_p1"
    expected:
      fighting: 3  # Used fighting 3 times
      dodge: 1     # Used dodge 1 time
  
  improvement_eligible:
    player_id: "u_p1"
    expected_skills: ["fighting", "dodge"]
```

### 5. Testing Strategy

**Unit Tests**:
- Test SkillUsageTracker record/clear/get methods
- Test combat resolution hooks record usage
- Test improvement phase logic

**Integration Tests**:
- Test skill tracking through full combat encounter
- Test improvement phase triggers correctly
- Test usage clears after improvement

**E2E Scenario**:
Update `scen_skill_improvement_lifecycle.yaml`:
```yaml
steps:
  # ... existing combat steps ...
  
  - actor: kp
    action: command
    name: trigger_improvement_phase
    args: {}

assertions:
  skill_usage:
    u_p1:
      fighting: 2
      dodge: 1
  
  improvement_rolls:
    u_p1:
      fighting: "1d100 < 50 → +1d10"  # Document expected roll
```

## Open Questions

1. **Should non-combat skills be tracked?**
   - Currently out of scope (focus on combat integration)
   - Could extend later via skill check hooks

2. **How to handle multiple combat encounters per session?**
   - Usage accumulates across encounters
   - Cleared only at improvement phase

3. **What about NPC skill usage?**
   - Not tracked (only player characters)
   - NPCs don't improve skills

## Implementation Plan

### Wave 1: Core Tracking
1. Create `SkillUsageTracker` class
2. Add to `SessionStore`
3. Hook into combat resolution functions

### Wave 2: Improvement Phase
1. Create improvement phase command
2. Implement skill improvement rolls
3. Add clear/reset logic

### Wave 3: Testing
1. Unit tests for tracker
2. Integration tests for combat hooks
3. Update E2E scenario with assertions

### Wave 4: Documentation
1. Update combat system docs
2. Add skill improvement guide
3. Document scenario assertions

## Files to Modify

- `src/dm_bot/orchestrator/session_store.py` - Add SkillUsageTracker
- `src/dm_bot/rules/coc/combat.py` - Add usage recording hooks
- `src/dm_bot/testing/runtime_driver.py` - Add test access methods
- `tests/rules/coc/test_combat_and_insanity.py` - Add usage tests
- `tests/scenarios/acceptance/scen_skill_improvement_lifecycle.yaml` - Update assertions

## Success Criteria

- [ ] Skill usage tracked during combat
- [ ] Improvement phase can be triggered
- [ ] Skills improve based on usage
- [ ] Usage clears after improvement
- [ ] Tests verify tracking accuracy
- [ ] E2E scenario validates full flow
