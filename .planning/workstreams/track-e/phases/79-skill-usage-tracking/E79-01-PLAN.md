---
phase: E79-skill-usage-tracking
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/orchestrator/skill_tracker.py
  - src/dm_bot/orchestrator/session_store.py
  - src/dm_bot/rules/coc/combat.py
  - src/dm_bot/testing/runtime_driver.py
  - tests/rules/coc/test_skill_tracking.py
  - tests/scenarios/acceptance/scen_skill_improvement.yaml
autonomous: true
requirements:
  - SKILL-TRACK-01
  - SKILL-TRACK-02
  - SKILL-TRACK-03
  - SKILL-TRACK-04

must_haves:
  truths:
    - "Combat system records each skill check attempt with skill name and result"
    - "Session state maintains skill usage history per character per encounter"
    - "Post-session improvement phase can query which skills were used (and succeeded)"
    - "E2E scenario validates combat → skill tracking → improvement flow"
  artifacts:
    - path: "src/dm_bot/orchestrator/skill_tracker.py"
      provides: "SkillUsageTracker class with record_usage, get_eligible_skills, clear methods"
      min_lines: 80
    - path: "src/dm_bot/orchestrator/session_store.py"
      provides: "Skill tracker integration in CampaignSession"
      exports: ["skill_tracker"]
    - path: "src/dm_bot/rules/coc/combat.py"
      provides: "Combat hooks that record skill usage"
      pattern: "skill_tracker.record_usage"
    - path: "tests/rules/coc/test_skill_tracking.py"
      provides: "Unit tests for skill tracking"
      min_lines: 60
  key_links:
    - from: "combat.py resolve_* functions"
      to: "SkillUsageTracker.record_usage"
      via: "session.skill_tracker"
    - from: "session_store.py"
      to: "SkillUsageTracker"
      via: "CampaignSession.skill_tracker field"
---

<objective>
Implement skill usage tracking during combat for post-session improvement.

Purpose: Enable COC 7e skill improvement mechanics by tracking which skills players use during combat encounters.
Output: SkillUsageTracker integrated with combat system and RuntimeTestDriver.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/workstreams/track-e/phases/79-skill-usage-tracking/E79-CONTEXT.md
@src/dm_bot/rules/coc/combat.py
@src/dm_bot/rules/coc/experience.py
@src/dm_bot/orchestrator/session_store.py
@src/dm_bot/testing/runtime_driver.py

## Key Types from Existing Code

From session_store.py:
```python
class CampaignSession(BaseModel):
    campaign_id: str
    member_ids: list[str]
    player_ready: dict[str, bool]
    session_phase: SessionPhase
    # ... other fields
```

From combat.py:
```python
class CombatCheckResult(BaseModel):
    action: CombatAction
    actor_name: str
    success: bool
    success_rank: str
    # ... other fields
```

From experience.py:
```python
def roll_skill_improvement(skill_key: str, current_value: int) -> SkillImprovementResult:
    """Roll 1d100 < current skill → +1d10 improvement"""
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create SkillUsageTracker class</name>
  <files>src/dm_bot/orchestrator/skill_tracker.py</files>
  <action>
Create SkillUsageTracker class in new file:

```python
from pydantic import BaseModel, Field

class SkillUsageTracker(BaseModel):
    """Tracks skill usage per player per session for COC 7e improvement."""
    
    # Map: player_id -> skill_name -> usage_count
    usage: dict[str, dict[str, int]] = Field(default_factory=dict)
    
    # Map: player_id -> skill_name -> success_count
    successes: dict[str, dict[str, int]] = Field(default_factory=dict)
    
    def record_usage(self, player_id: str, skill_name: str, success: bool = False) -> None:
        """Record that a player used a skill."""
        if player_id not in self.usage:
            self.usage[player_id] = {}
            self.successes[player_id] = {}
        
        self.usage[player_id][skill_name] = self.usage[player_id].get(skill_name, 0) + 1
        if success:
            self.successes[player_id][skill_name] = self.successes[player_id].get(skill_name, 0) + 1
    
    def get_eligible_skills(self, player_id: str) -> list[str]:
        """Get list of skills eligible for improvement (any usage counts)."""
        return list(self.usage.get(player_id, {}).keys())
    
    def get_usage_count(self, player_id: str, skill_name: str) -> int:
        """Get usage count for a specific skill."""
        return self.usage.get(player_id, {}).get(skill_name, 0)
    
    def get_success_count(self, player_id: str, skill_name: str) -> int:
        """Get success count for a specific skill."""
        return self.successes.get(player_id, {}).get(skill_name, 0)
    
    def clear(self) -> None:
        """Clear all usage data (call at session end/improvement phase)."""
        self.usage.clear()
        self.successes.clear()
    
    def export_state(self) -> dict:
        """Export tracker state for persistence."""
        return {
            "usage": dict(self.usage),
            "successes": dict(self.successes)
        }
    
    @classmethod
    def import_state(cls, payload: dict) -> "SkillUsageTracker":
        """Import tracker state from persistence."""
        tracker = cls()
        tracker.usage = payload.get("usage", {})
        tracker.successes = payload.get("successes", {})
        return tracker
```

Add combat skills constant:
```python
COMBAT_SKILLS = ["fighting", "shooting", "brawl", "grapple", "dodge", "throw"]
```
  </action>
  <verify>
    <automated>python -c "from dm_bot.orchestrator.skill_tracker import SkillUsageTracker; t = SkillUsageTracker(); t.record_usage('p1', 'fighting', True); print('OK')"</automated>
  </verify>
  <done>SkillUsageTracker class created with all required methods</done>
</task>

<task type="auto">
  <name>Task 2: Integrate tracker into SessionStore</name>
  <files>src/dm_bot/orchestrator/session_store.py</files>
  <action>
Add skill_tracker field to CampaignSession:

1. Import SkillUsageTracker at top of file:
```python
from dm_bot.orchestrator.skill_tracker import SkillUsageTracker
```

2. Add skill_tracker field to CampaignSession class (after existing fields):
```python
class CampaignSession(BaseModel):
    # ... existing fields ...
    
    # Skill usage tracking for COC 7e improvement
    skill_tracker: SkillUsageTracker = Field(default_factory=SkillUsageTracker)
```

3. Update export_state method to include skill_tracker:
```python
def export_state(self) -> dict[str, object]:
    return {
        # ... existing fields ...
        "skill_tracker": self.skill_tracker.export_state(),
    }
```

4. Update load method to restore skill_tracker:
```python
@classmethod
def load(cls, payload: dict[str, object]) -> "CampaignSession":
    session = cls(...)
    # ... existing loading ...
    if "skill_tracker" in payload:
        session.skill_tracker = SkillUsageTracker.import_state(payload["skill_tracker"])
    return session
```

Note: Check actual SessionStore implementation and adapt accordingly.
  </action>
  <verify>
    <automated>python -c "from dm_bot.orchestrator.session_store import CampaignSession; s = CampaignSession(campaign_id='test', channel_id='c1', guild_id='g1', owner_id='o1'); s.skill_tracker.record_usage('p1', 'fighting'); print('OK')"</automated>
  </verify>
  <done>CampaignSession has skill_tracker field with persistence support</done>
</task>

<task type="auto">
  <name>Task 3: Add combat hooks to record skill usage</name>
  <files>src/dm_bot/rules/coc/combat.py</files>
  <action>
Add skill usage recording to combat resolution functions.

Modify resolve_fighting_attack to accept optional skill_tracker parameter:

```python
def resolve_fighting_attack(
    attacker: CombatantStats,
    defender: CombatantStats,
    attacker_roll: int,
    defender_roll: int,
    skill_tracker: SkillUsageTracker | None = None,
    attacker_id: str | None = None,
) -> CombatCheckResult:
    """Resolve a Fighting attack vs Dodge.
    
    Args:
        # ... existing args ...
        skill_tracker: Optional tracker to record skill usage
        attacker_id: Player ID for tracking
    """
    # ... existing resolution logic ...
    result = CombatCheckResult(...)  # existing
    
    # Record skill usage
    if skill_tracker and attacker_id:
        skill_tracker.record_usage(
            player_id=attacker_id,
            skill_name="fighting",
            success=result.success
        )
        if defender.dodge > 0:
            skill_tracker.record_usage(
                player_id=defender.name,  # or defender_id if available
                skill_name="dodge",
                success=not result.success  # dodge succeeds if attack fails
            )
    
    return result
```

Similarly update:
- resolve_shooting_attack (track "shooting")
- resolve_brawl_attack (track "brawl")
- resolve_grapple_attack (track "grapple")

For each function:
1. Add skill_tracker and attacker_id/defender_id parameters
2. After resolution, record usage for attacker skill
3. Record defender dodge usage if applicable
4. Pass success=True/False based on result
  </action>
  <verify>
    <automated>grep -n "skill_tracker.record_usage" src/dm_bot/rules/coc/combat.py | wc -l</automated>
  </verify>
  <done>All combat resolution functions record skill usage</done>
</task>

<task type="auto">
  <name>Task 4: Add RuntimeTestDriver access methods</name>
  <files>src/dm_bot/testing/runtime_driver.py</files>
  <action>
Add methods to RuntimeTestDriver for skill tracking access:

```python
def get_skill_usage(self, player_id: str) -> dict[str, int]:
    """Get skill usage counts for a player (for test assertions).
    
    Args:
        player_id: The player/user ID
        
    Returns:
        Dict mapping skill_name -> usage_count
    """
    if self._session_store is None:
        return {}
    
    for session in self._session_store._sessions.values():
        return session.skill_tracker.usage.get(player_id, {})
    return {}

def get_skill_successes(self, player_id: str) -> dict[str, int]:
    """Get skill success counts for a player.
    
    Args:
        player_id: The player/user ID
        
    Returns:
        Dict mapping skill_name -> success_count
    """
    if self._session_store is None:
        return {}
    
    for session in self._session_store._sessions.values():
        return session.skill_tracker.successes.get(player_id, {})
    return {}

def get_eligible_skills(self, player_id: str) -> list[str]:
    """Get list of skills eligible for improvement.
    
    Args:
        player_id: The player/user ID
        
    Returns:
        List of skill names that were used
    """
    if self._session_store is None:
        return []
    
    for session in self._session_store._sessions.values():
        return session.skill_tracker.get_eligible_skills(player_id)
    return []

def clear_skill_tracking(self) -> None:
    """Clear skill tracking (simulates improvement phase completion)."""
    if self._session_store is None:
        return
    
    for session in self._session_store._sessions.values():
        session.skill_tracker.clear()
```
  </action>
  <verify>
    <automated>grep -n "def get_skill_usage\|def get_eligible_skills\|def clear_skill_tracking" src/dm_bot/testing/runtime_driver.py</automated>
  </verify>
  <done>RuntimeTestDriver has skill tracking query methods</done>
</task>

<task type="auto">
  <name>Task 5: Create unit tests for skill tracking</name>
  <files>tests/rules/coc/test_skill_tracking.py</files>
  <action>
Create comprehensive unit tests:

```python
"""Tests for skill usage tracking system."""

import pytest

from dm_bot.orchestrator.skill_tracker import SkillUsageTracker, COMBAT_SKILLS


class TestSkillUsageTracker:
    """Test SkillUsageTracker functionality."""
    
    def test_record_usage_basic(self):
        """Test basic usage recording."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting")
        
        assert tracker.get_usage_count("player1", "fighting") == 1
        assert tracker.get_eligible_skills("player1") == ["fighting"]
    
    def test_record_usage_multiple_skills(self):
        """Test recording multiple skills."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting")
        tracker.record_usage("player1", "dodge")
        tracker.record_usage("player1", "fighting")
        
        assert tracker.get_usage_count("player1", "fighting") == 2
        assert tracker.get_usage_count("player1", "dodge") == 1
        assert set(tracker.get_eligible_skills("player1")) == {"fighting", "dodge"}
    
    def test_record_usage_success_tracking(self):
        """Test tracking successful vs failed uses."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting", success=True)
        tracker.record_usage("player1", "fighting", success=False)
        tracker.record_usage("player1", "fighting", success=True)
        
        assert tracker.get_usage_count("player1", "fighting") == 3
        assert tracker.get_success_count("player1", "fighting") == 2
    
    def test_multiple_players(self):
        """Test tracking for multiple players."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting")
        tracker.record_usage("player2", "shooting")
        
        assert tracker.get_eligible_skills("player1") == ["fighting"]
        assert tracker.get_eligible_skills("player2") == ["shooting"]
    
    def test_clear(self):
        """Test clearing tracker."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting")
        tracker.record_usage("player1", "dodge")
        
        tracker.clear()
        
        assert tracker.get_eligible_skills("player1") == []
        assert tracker.get_usage_count("player1", "fighting") == 0
    
    def test_export_import(self):
        """Test state export and import."""
        tracker = SkillUsageTracker()
        tracker.record_usage("player1", "fighting", success=True)
        tracker.record_usage("player1", "dodge")
        
        state = tracker.export_state()
        new_tracker = SkillUsageTracker.import_state(state)
        
        assert new_tracker.get_usage_count("player1", "fighting") == 1
        assert new_tracker.get_success_count("player1", "fighting") == 1
        assert new_tracker.get_usage_count("player1", "dodge") == 1


class TestCombatSkills:
    """Test combat skill constants."""
    
    def test_combat_skills_defined(self):
        """Test that combat skills are defined."""
        assert "fighting" in COMBAT_SKILLS
        assert "shooting" in COMBAT_SKILLS
        assert "dodge" in COMBAT_SKILLS
```
  </action>
  <verify>
    <automated>uv run pytest tests/rules/coc/test_skill_tracking.py -v</automated>
  </verify>
  <done>All skill tracking unit tests pass</done>
</task>

<task type="auto">
  <name>Task 6: Create E2E scenario for skill improvement</name>
  <files>tests/scenarios/acceptance/scen_skill_improvement.yaml</files>
  <action>
Create E2E scenario validating skill tracking and improvement:

```yaml
# Skill Improvement Lifecycle E2E Scenario
# Validates: combat → skill tracking → improvement flow

scenario:
  id: scen_skill_improvement
  name: "Skill Improvement Lifecycle"
  description: "Validates skill usage tracking during combat and improvement phase"
  
actors:
  - id: kp
    role: keeper
  - id: p1
    role: player
    name: "调查员A"
  - id: p2
    role: player
    name: "调查员B"

initial_state:
  dice_mode: seeded
  dice_seed: 12345
  
steps:
  # Setup: Create campaign and join players
  - actor: kp
    action: command
    name: bind_campaign
    args:
      campaign_id: "test_campaign"
      
  - actor: p1
    action: command
    name: join
    args: {}
    
  - actor: p2
    action: command
    name: join
    args: {}
    
  - actor: p1
    action: command
    name: ready
    args: {}
    
  - actor: p2
    action: command
    name: ready
    args: {}
    
  - actor: kp
    action: command
    name: start_session
    args: {}
    
  # Combat: Players use skills
  - actor: p1
    action: message
    text: "我用格斗攻击敌人"
    
  - actor: p2
    action: message
    text: "我闪避攻击"
    
  - actor: p1
    action: message
    text: "我再射击一次"
    
  # Assertions: Verify skill tracking
  - actor: system
    action: assert
    assertions:
      skill_usage:
        p1:
          fighting: ">= 1"
          shooting: ">= 1"
        p2:
          dodge: ">= 1"
      
  # Improvement phase
  - actor: kp
    action: command
    name: trigger_improvement_phase
    args: {}
    
  # Assertions: Verify improvement occurred
  - actor: system
    action: assert
    assertions:
      skill_improvement:
        p1:
          eligible_skills:
            contains: ["fighting", "shooting"]
        p2:
          eligible_skills:
            contains: ["dodge"]
      
  # Clear tracking
  - actor: kp
    action: command
    name: clear_skill_tracking
    args: {}
    
  # Assertions: Verify cleared
  - actor: system
    action: assert
    assertions:
      skill_usage_cleared:
        p1: {}
        p2: {}

expected_outcomes:
  - skill_usage_tracked: true
  - improvement_phase_triggered: true
  - tracking_cleared: true
```
  </action>
  <verify>
    <automated>uv run python -m dm_bot.main run-scenario --scenario tests/scenarios/acceptance/scen_skill_improvement.yaml --dry-run</automated>
  </verify>
  <done>E2E scenario file created and validated</done>
</task>

</tasks>

<verification>
Run full verification suite:
1. `uv run pytest tests/rules/coc/test_skill_tracking.py -v` - Unit tests
2. `uv run pytest tests/rules/coc/test_combat_and_insanity.py -v` - Combat integration
3. `uv run python -m dm_bot.main smoke-check` - Smoke check
</verification>

<success_criteria>
- SkillUsageTracker class exists with all methods
- CampaignSession integrates skill_tracker field
- Combat resolution records skill usage
- RuntimeTestDriver provides skill tracking access
- Unit tests pass (100% coverage of tracker)
- E2E scenario validates full flow
- All existing tests still pass
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-e/phases/79-skill-usage-tracking/E79-01-SUMMARY.md`
</output>
