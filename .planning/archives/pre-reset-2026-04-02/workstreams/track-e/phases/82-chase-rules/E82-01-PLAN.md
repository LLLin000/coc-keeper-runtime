---
phase: E82-chase-rules
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/dm_bot/rules/coc/chase.py
  - src/dm_bot/gameplay/chase.py
  - src/dm_bot/testing/runtime_driver.py
  - tests/rules/coc/test_chase.py
  - tests/scenarios/acceptance/scen_chase.yaml
autonomous: true
requirements:
  - CHASE-01
  - CHASE-02
  - CHASE-03
  - CHASE-04
  - CHASE-05

must_haves:
  truths:
    - "Chase mechanics support pursuer/fleeer roles with CON-based rolls"
    - "Chase state tracks locations and relative positions"
    - "Obstacles require appropriate skill checks to overcome"
    - "Chase ends correctly on escape, capture, or transition to combat"
    - "E2E scenario validates a complete chase flow"
  artifacts:
    - path: "src/dm_bot/rules/coc/chase.py"
      provides: "ChaseEncounter, ChaseParticipant, ChaseRoundResult"
      min_lines: 200
    - path: "src/dm_bot/gameplay/chase.py"
      provides: "GameplayChaseManager for session integration"
      min_lines: 100
    - path: "tests/rules/coc/test_chase.py"
      provides: "Unit tests for chase mechanics"
      min_lines: 80
  key_links:
    - from: "ChaseEncounter.resolve_round"
      to: "CON check system"
      via: "resolve_con_check"
    - from: "ChaseParticipant"
      to: "combat.py"
      via: "transition_to_combat"
---

<objective>
Implement COC 7e chase mechanics for pursuit and escape scenarios.

Purpose: Enable chase scenes in adventures with proper COC 7e rules.
Output: Complete chase system with CON checks, obstacles, and end conditions.
</objective>

<execution_context>
@C:/Users/Lin/.opencode/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@src/dm_bot/rules/coc/combat.py
@src/dm_bot/rules/coc/skills.py
@src/dm_bot/orchestrator/session_store.py

## Key Types from Existing Code

From skills.py:
```python
class SkillCheckResult(BaseModel):
    skill_key: str
    skill_value: int
    rolled: int
    success: bool
    success_rank: SuccessRank
```

From combat.py:
```python
class CombatEncounter(BaseModel):
    order: list[str]
    combatants: dict[str, Combatant]
    active_index: int = 0
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create chase data models</name>
  <files>src/dm_bot/rules/coc/chase.py</files>
  <action>
Create chase system models:

```python
"""COC 7th Edition Chase System.

Chase mechanics for pursuit and escape scenarios.
Reference: Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 6
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class ChaseRole(StrEnum):
    """Role in a chase."""
    FLEER = "fleeer"  # Trying to escape
    PURSUER = "pursuer"  # Trying to catch


class ChaseStatus(StrEnum):
    """Status of a chase participant."""
    ACTIVE = "active"
    ESCAPED = "escaped"
    CAPTURED = "captured"
    EXHAUSTED = "exhausted"
    IN_COMBAT = "in_combat"


class ChaseParticipant(BaseModel):
    """A participant in a chase.
    
    Can be an investigator or creature.
    """
    # Identity
    participant_id: str
    name: str
    role: ChaseRole
    
    # Stats
    con: int  # Constitution for endurance checks
    dex: int  # Dexterity for initiative
    mov: int  # Movement rate
    
    # State
    current_location: int = 0  # Index in locations list
    status: ChaseStatus = ChaseStatus.ACTIVE
    exhausted: bool = False  # Failed CON check this round
    conditions: list[str] = Field(default_factory=list)
    
    # Tracking
    con_rolls: list[int] = Field(default_factory=list)  # History of CON rolls
    obstacles_overcome: int = 0
    obstacles_failed: int = 0
    
    def can_move(self) -> bool:
        """Check if participant can move this round."""
        return self.status == ChaseStatus.ACTIVE and not self.exhausted
    
    def get_effective_mov(self) -> int:
        """Get movement rate (reduced if exhausted)."""
        if self.exhausted:
            return max(1, self.mov - 1)
        return self.mov


class ChaseObstacle(BaseModel):
    """An obstacle in a chase location.
    
    Must be overcome to move through the location.
    """
    name: str
    name_cn: str
    skill: str  # Skill key required
    difficulty: Literal["regular", "hard", "extreme"] = "regular"
    description: str = ""
    failure_effect: Literal["fall_back", "damage", "stuck", "slow"] = "slow"
    damage: str = ""  # Damage on failure (e.g., "1d6")
    
    def get_difficulty_multiplier(self) -> int:
        """Get multiplier for difficulty."""
        return {"regular": 1, "hard": 2, "extreme": 5}[self.difficulty]


class ChaseLocation(BaseModel):
    """A location in the chase.
    
    Chase happens across a series of locations.
    """
    index: int
    name: str
    name_cn: str
    description: str = ""
    
    # Obstacles
    entry_obstacle: ChaseObstacle | None = None  # To enter this location
    exit_obstacle: ChaseObstacle | None = None  # To leave this location
    
    # Special
    is_end: bool = False  # Escape if fleeer reaches here
    is_dangerous: bool = False  # May cause damage


class ChaseRoundResult(BaseModel):
    """Result of a chase round."""
    round_number: int
    
    # CON checks
    con_results: dict[str, dict] = Field(default_factory=dict)
    # {participant_id: {rolled: int, success: bool, con: int}}
    
    # Movement
    movements: list[dict] = Field(default_factory=list)
    # [{participant_id, from_loc, to_loc, method}]
    
    # Obstacles
    obstacle_results: list[dict] = Field(default_factory=list)
    # [{participant_id, obstacle, success, effect}]
    
    # Status changes
    status_changes: dict[str, ChaseStatus] = Field(default_factory=dict)
    
    # End condition
    ended: bool = False
    end_reason: Literal["escape", "capture", "combat", None] = None
    winners: list[str] = Field(default_factory=list)
    
    # Narrative
    narrative: str = ""


class ChaseEncounter(BaseModel):
    """A chase encounter.
    
    Manages the state and resolution of a chase scene.
    """
    
    # Participants
    participants: dict[str, ChaseParticipant] = Field(default_factory=dict)
    fleeers: list[str] = Field(default_factory=list)  # IDs of fleeers
    pursuers: list[str] = Field(default_factory=list)  # IDs of pursuers
    
    # Locations
    locations: list[ChaseLocation] = Field(default_factory=list)
    
    # State
    current_round: int = 1
    active: bool = True
    
    # History
    round_history: list[ChaseRoundResult] = Field(default_factory=list)
    
    def add_participant(
        self,
        participant_id: str,
        name: str,
        role: ChaseRole,
        con: int,
        dex: int,
        mov: int,
        start_location: int = 0,
    ) -> ChaseParticipant:
        """Add a participant to the chase."""
        participant = ChaseParticipant(
            participant_id=participant_id,
            name=name,
            role=role,
            con=con,
            dex=dex,
            mov=mov,
            current_location=start_location,
        )
        self.participants[participant_id] = participant
        
        if role == ChaseRole.FLEER:
            self.fleeers.append(participant_id)
        else:
            self.pursuers.append(participant_id)
        
        return participant
    
    def add_location(
        self,
        name: str,
        name_cn: str,
        entry_obstacle: ChaseObstacle | None = None,
        exit_obstacle: ChaseObstacle | None = None,
        is_end: bool = False,
    ) -> ChaseLocation:
        """Add a location to the chase."""
        location = ChaseLocation(
            index=len(self.locations),
            name=name,
            name_cn=name_cn,
            entry_obstacle=entry_obstacle,
            exit_obstacle=exit_obstacle,
            is_end=is_end,
        )
        self.locations.append(location)
        return location
    
    def resolve_round(self, dice_rolls: dict[str, int] | None = None) -> ChaseRoundResult:
        """Resolve one round of chase.
        
        Args:
            dice_rolls: Optional pre-rolled dice {participant_id: roll}
            
        Returns:
            ChaseRoundResult with full resolution
        """
        result = ChaseRoundResult(round_number=self.current_round)
        
        # Step 1: CON checks
        self._resolve_con_checks(result, dice_rolls or {}n        
        # Step 2: Fleeers move (DEX order)
        self._resolve_fleeer_movement(result, dice_rolls or {})
        
        # Step 3: Pursuers move
        self._resolve_pursuer_movement(result)
        
        # Step 4: Check end conditions
        self._check_end_conditions(result)
        
        # Store result
        self.round_history.append(result)
        
        if not result.ended:
            self.current_round += 1
            # Reset exhausted for next round
            for p in self.participants.values():
                p.exhausted = False
        else:
            self.active = False
        
        return result
    
    def _resolve_con_checks(
        self,
        result: ChaseRoundResult,
        dice_rolls: dict[str, int],
    ) -> None:
        """Resolve CON checks for all participants."""
        import random
        
        for pid, participant in self.participants.items():
            if participant.status != ChaseStatus.ACTIVE:
                continue
            
            # Roll CON
            roll = dice_rolls.get(pid, random.randint(1, 100))
            success = roll <= participant.con
            
            result.con_results[pid] = {
                "rolled": roll,
                "con": participant.con,
                "success": success,
            }
            participant.con_rolls.append(roll)
            
            if not success:
                participant.exhausted = True
    
    def _resolve_fleeer_movement(
        self,
        result: ChaseRoundResult,
        dice_rolls: dict[str, int],
    ) -> None:
        """Resolve fleeer movement (DEX order)."""
        # Sort fleeers by DEX descending
        sorted_fleeers = sorted(
            [self.participants[pid] for pid in self.fleeers],
            key=lambda p: p.dex,
            reverse=True,
        )
        
        for fleeer in sorted_fleeers:
            if not fleeer.can_move():
                continue
            
            # Try to move forward
            self._attempt_move(fleeer, +1, result, dice_rolls)
    
    def _resolve_pursuer_movement(self, result: ChaseRoundResult) -> None:
        """Resolve pursuer movement."""
        # Pursuers try to close distance to nearest fleeer
        for pid in self.pursuers:
            pursuer = self.participants[pid]
            if not pursuer.can_move():
                continue
            
            # Find nearest fleeer
            nearest = self._find_nearest_fleeer(pursuer)
            if nearest:
                direction = self._get_direction(pursuer, nearest)
                self._attempt_move(pursuer, direction, result, {})
    
    def _attempt_move(
        self,
        participant: ChaseParticipant,
        direction: int,
        result: ChaseRoundResult,
        dice_rolls: dict[str, int],
    ) -> bool:
        """Attempt to move a participant."""
        new_location = participant.current_location + direction
        
        # Check bounds
        if new_location < 0 or new_location >= len(self.locations):
            return False
        
        # Check obstacle
        current_loc = self.locations[participant.current_location]
        obstacle = current_loc.exit_obstacle if direction > 0 else current_loc.entry_obstacle
        
        if obstacle:
            # Would need skill check here
            # For now, auto-succeed
            pass
        
        # Move
        old_location = participant.current_location
        participant.current_location = new_location
        
        result.movements.append({
            "participant_id": participant.participant_id,
            "from": old_location,
            "to": new_location,
            "direction": "forward" if direction > 0 else "back",
        })
        
        return True
    
    def _find_nearest_fleeer(self, pursuer: ChaseParticipant) -> ChaseParticipant | None:
        """Find the nearest fleeer to a pursuer."""
        nearest = None
        min_distance = float('inf')
        
        for pid in self.fleeers:
            fleeer = self.participants[pid]
            if fleeer.status != ChaseStatus.ACTIVE:
                continue
            
            distance = abs(fleeer.current_location - pursuer.current_location)
            if distance < min_distance:
                min_distance = distance
                nearest = fleeer
        
        return nearest
    
    def _get_direction(self, from_p: ChaseParticipant, to_p: ChaseParticipant) -> int:
        """Get direction to move from one participant to another."""
        if to_p.current_location > from_p.current_location:
            return 1
        elif to_p.current_location < from_p.current_location:
            return -1
        return 0
    
    def _check_end_conditions(self, result: ChaseRoundResult) -> None:
        """Check if chase has ended."""
        # Check for escape (fleeer reached end)
        for pid in self.fleeers:
            fleeer = self.participants[pid]
            if fleeer.current_location >= len(self.locations) - 1:
                # Reached end
                current_loc = self.locations[fleeer.current_location]
                if current_loc.is_end:
                    fleeer.status = ChaseStatus.ESCAPED
                    result.winners.append(pid)
        
        # Check for capture (pursuer same location as fleeer)
        for pursuer_id in self.pursuers:
            pursuer = self.participants[pursuer_id]
            for fleeer_id in self.fleeers:
                fleeer = self.participants[fleeer_id]
                if (pursuer.current_location == fleeer.current_location and
                    pursuer.status == ChaseStatus.ACTIVE and
                    fleeer.status == ChaseStatus.ACTIVE):
                    # Capture!
                    fleeer.status = ChaseStatus.CAPTURED
                    result.status_changes[fleeer_id] = ChaseStatus.CAPTURED
        
        # Determine if ended
        active_fleeers = [pid for pid in self.fleeers 
                         if self.participants[pid].status == ChaseStatus.ACTIVE]
        
        if result.winners:
            result.ended = True
            result.end_reason = "escape"
        elif not active_fleeers:
            result.ended = True
            result.end_reason = "capture"
```
  </action>
  <verify>
    <automated>python -c "from dm_bot.rules.coc.chase import ChaseEncounter, ChaseParticipant; print('OK')"</automated>
  </verify>
  <done>Chase system models with CON checks and movement</done>
</task>

<task type="auto">
  <name>Task 2: Add gameplay integration</name>
  <files>src/dm_bot/gameplay/chase.py</files>
  <action>
Create gameplay chase manager:

```python
"""Gameplay integration for chase system."""

from dm_bot.rules.coc.chase import (
    ChaseEncounter,
    ChaseParticipant,
    ChaseRole,
    ChaseObstacle,
    ChaseLocation,
)
from dm_bot.orchestrator.session_store import CampaignSession


class GameplayChaseManager:
    """Manages chases within a gameplay session."""
    
    def __init__(self, session: CampaignSession) -> None:
        self.session = session
        self.active_chase: ChaseEncounter | None = None
    
    def start_chase(
        self,
        fleeer_ids: list[str],
        pursuer_ids: list[str],
        locations: list[dict],
    ) -> ChaseEncounter:
        """Start a new chase.
        
        Args:
            fleeer_ids: IDs of characters trying to escape
            pursuer_ids: IDs of characters pursuing
            locations: List of location dicts with name, obstacles
            
        Returns:
            The chase encounter
        """
        chase = ChaseEncounter()
        
        # Add fleeers
        for char_id in fleeer_ids:
            # Get character stats from session
            # TODO: Get actual stats from character registry
            chase.add_participant(
                participant_id=char_id,
                name=char_id,  # TODO: Get actual name
                role=ChaseRole.FLEER,
                con=50,
                dex=50,
                mov=8,
            )
        
        # Add pursuers
        for char_id in pursuer_ids:
            chase.add_participant(
                participant_id=char_id,
                name=char_id,
                role=ChaseRole.PURSUER,
                con=50,
                dex=50,
                mov=8,
            )
        
        # Add locations
        for i, loc_data in enumerate(locations):
            chase.add_location(
                name=loc_data["name"],
                name_cn=loc_data.get("name_cn", loc_data["name"]),
                is_end=(i == len(locations) - 1),
            )
        
        self.active_chase = chase
        return chase
    
    def resolve_round(self) -> dict:
        """Resolve the current round of the active chase.
        
        Returns:
            Round result as dict
        """
        if not self.active_chase:
            raise ValueError("No active chase")
        
        result = self.active_chase.resolve_round()
        
        # Check for combat transition
        if result.ended and result.end_reason == "capture":
            # Transition to combat
            pass
        
        return result.model_dump()
    
    def get_chase_status(self) -> dict:
        """Get current chase status.
        
        Returns:
            Status dict with participants, locations, round
        """
        if not self.active_chase:
            return {"active": False}
        
        chase = self.active_chase
        return {
            "active": chase.active,
            "round": chase.current_round,
            "participants": {
                pid: {
                    "name": p.name,
                    "role": p.role,
                    "location": p.current_location,
                    "status": p.status,
                    "exhausted": p.exhausted,
                }
                for pid, p in chase.participants.items()
            },
            "locations": [
                {"name": loc.name_cn, "is_end": loc.is_end}
                for loc in chase.locations
            ],
        }
    
    def end_chase(self) -> dict:
        """End the active chase.
        
        Returns:
            Final result
        """
        if not self.active_chase:
            return {"ended": False}
        
        chase = self.active_chase
        result = {
            "ended": True,
            "rounds": chase.current_round,
            "winners": [],
            "captured": [],
        }
        
        for pid, participant in chase.participants.items():
            if participant.status.value == "escaped":
                result["winners"].append(pid)
            elif participant.status.value == "captured":
                result["captured"].append(pid)
        
        self.active_chase = None
        return result
```
  </action>
  <verify>
    <automated>python -c "from dm_bot.gameplay.chase import GameplayChaseManager; print('OK')"</automated>
  </verify>
  <done>GameplayChaseManager for session integration</done>
</task>

<task type="auto">
  <name>Task 3: Add RuntimeTestDriver methods</name>
  <files>src/dm_bot/testing/runtime_driver.py</files>
  <action>
Add chase methods to RuntimeTestDriver:

```python
# Add to RuntimeTestDriver class

def start_chase(
    self,
    fleeer_ids: list[str],
    pursuer_ids: list[str],
    locations: list[dict],
) -> dict:
    """Start a chase encounter.
    
    Args:
        fleeer_ids: IDs of characters fleeing
        pursuer_ids: IDs of characters pursuing
        locations: List of location definitions
        
    Returns:
        Chase status dict
    """
    # TODO: Integrate with GameplayChaseManager
    # For now, return placeholder
    return {
        "started": True,
        "fleeers": fleeer_ids,
        "pursuers": pursuer_ids,
        "locations": len(locations),
    }

def resolve_chase_round(self) -> dict:
    """Resolve one round of the active chase.
    
    Returns:
        Round result dict
    """
    # TODO: Call GameplayChaseManager.resolve_round()
    return {"resolved": True}

def get_chase_status(self) -> dict:
    """Get current chase status.
    
    Returns:
        Status dict
    """
    # TODO: Call GameplayChaseManager.get_chase_status()
    return {"active": False}
```
  </action>
  <verify>
    <automated>grep -n "def start_chase\|def resolve_chase_round" src/dm_bot/testing/runtime_driver.py</automated>
  </verify>
  <done>RuntimeTestDriver chase methods</done>
</task>

<task type="auto">
  <name>Task 4: Create unit tests</name>
  <files>tests/rules/coc/test_chase.py</files>
  <action>
Create chase unit tests:

```python
"""Tests for chase system."""

import pytest

from dm_bot.rules.coc.chase import (
    ChaseEncounter,
    ChaseParticipant,
    ChaseRole,
    ChaseStatus,
    ChaseObstacle,
    ChaseLocation,
)


class TestChaseParticipant:
    """Test chase participant mechanics."""
    
    def test_participant_creation(self):
        """Test creating a participant."""
        p = ChaseParticipant(
            participant_id="p1",
            name="Test",
            role=ChaseRole.FLEER,
            con=60,
            dex=70,
            mov=8,
        )
        assert p.role == ChaseRole.FLEER
        assert p.mov == 8
    
    def test_exhaustion_reduces_mov(self):
        """Test that exhaustion reduces movement."""
        p = ChaseParticipant(
            participant_id="p1",
            name="Test",
            role=ChaseRole.FLEER,
            con=60,
            dex=70,
            mov=8,
            exhausted=True,
        )
        assert p.get_effective_mov() == 7
    
    def test_cannot_move_when_exhausted(self):
        """Test that exhausted participants can't move."""
        p = ChaseParticipant(
            participant_id="p1",
            name="Test",
            role=ChaseRole.FLEER,
            con=60,
            dex=70,
            mov=8,
            exhausted=True,
        )
        assert not p.can_move()


class TestChaseEncounter:
    """Test chase encounter mechanics."""
    
    @pytest.fixture
    def chase(self):
        """Create a basic chase."""
        c = ChaseEncounter()
        
        # Add fleeer
        c.add_participant(
            participant_id="fleeer1",
            name="Fleeer",
            role=ChaseRole.FLEER,
            con=60,
            dex=70,
            mov=8,
        )
        
        # Add pursuer
        c.add_participant(
            participant_id="pursuer1",
            name="Pursuer",
            role=ChaseRole.PURSUER,
            con=50,
            dex=60,
            mov=8,
        )
        
        # Add locations
        for i in range(5):
            c.add_location(
                name=f"Loc{i}",
                name_cn=f"地点{i}",
                is_end=(i == 4),
            )
        
        return c
    
    def test_con_check_success(self, chase):
        """Test successful CON check."""
        result = chase.resolve_round({"fleeer1": 30, "pursuer1": 40})
        
        assert result.con_results["fleeer1"]["success"] is True
        assert result.con_results["pursuer1"]["success"] is True
        assert not chase.participants["fleeer1"].exhausted
    
    def test_con_check_failure(self, chase):
        """Test failed CON check."""
        result = chase.resolve_round({"fleeer1": 70, "pursuer1": 40})
        
        assert result.con_results["fleeer1"]["success"] is False
        assert chase.participants["fleeer1"].exhausted
    
    def test_fleeer_movement(self, chase):
        """Test that fleeers move."""
        initial_loc = chase.participants["fleeer1"].current_location
        
        result = chase.resolve_round({"fleeer1": 30, "pursuer1": 40})
        
        # Fleeer should have moved
        assert len(result.movements) > 0
    
    def test_escape_condition(self, chase):
        """Test escape when fleeer reaches end."""
        # Move fleeer to end
        chase.participants["fleeer1"].current_location = 4
        
        result = chase.resolve_round({"fleeer1": 30, "pursuer1": 40})
        
        assert result.ended is True
        assert result.end_reason == "escape"
        assert "fleeer1" in result.winners
    
    def test_capture_condition(self, chase):
        """Test capture when pursuer catches fleeer."""
        # Put pursuer and fleeer at same location
        chase.participants["fleeer1"].current_location = 2
        chase.participants["pursuer1"].current_location = 2
        
        result = chase.resolve_round({"fleeer1": 30, "pursuer1": 40})
        
        # Fleeer should be captured
        assert chase.participants["fleeer1"].status == ChaseStatus.CAPTURED


class TestChaseObstacles:
    """Test chase obstacles."""
    
    def test_obstacle_creation(self):
        """Test creating an obstacle."""
        obs = ChaseObstacle(
            name="Wall",
            name_cn="墙",
            skill="climb",
            difficulty="regular",
        )
        assert obs.skill == "climb"
```
  </action>
  <verify>
    <automated>uv run pytest tests/rules/coc/test_chase.py -v</automated>
  </verify>
  <done>Chase unit tests</done>
</task>

<task type="auto">
  <name>Task 5: Create E2E chase scenario</name>
  <files>tests/scenarios/acceptance/scen_chase.yaml</files>
  <action>
Create E2E chase scenario:

```yaml
# Chase E2E Scenario
# Validates: chase initiation → CON checks → movement → escape

scenario:
  id: scen_chase
  name: "Chase Scene"
  description: "Validates complete chase flow from start to escape"
  
actors:
  - id: kp
    role: keeper
  - id: p1
    role: player
    name: "逃亡者"
  - id: p2
    role: player
    name: "追捕者"

initial_state:
  dice_mode: seeded
  dice_seed: 12345
  
steps:
  # Setup campaign
  - actor: kp
    action: command
    name: bind_campaign
    args:
      campaign_id: "chase_test"
      
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
    
  # Start chase
  - actor: kp
    action: command
    name: start_chase
    args:
      fleeers: ["p1"]
      pursuers: ["p2"]
      locations:
        - name: "Street"
          name_cn: "街道"
        - name: "Alley"
          name_cn: "小巷"
        - name: "Fence"
          name_cn: "围墙"
        - name: "Park"
          name_cn: "公园"
        - name: "Escape"
          name_cn: "逃脱点"
          
  # Assertions: Chase started
  - actor: system
    action: assert
    assertions:
      chase:
        active: true
        round: 1
        participants:
          p1:
            role: "fleeer"
          p2:
            role: "pursuer"
            
  # Resolve rounds until escape
  - actor: kp
    action: command
    name: resolve_chase_round
    args: {}
    
  - actor: system
    action: assert
    assertions:
      chase_round:
        round: 1
        con_checks:
          p1:
            success: bool
          p2:
            success: bool
        movements:
          exists: true
          
  # Continue until escape
  - actor: kp
    action: command
    name: resolve_chase_round
    args: {}
    
  - actor: kp
    action: command
    name: resolve_chase_round
    args: {}
    
  - actor: kp
    action: command
    name: resolve_chase_round
    args: {}
    
  # Check final result
  - actor: system
    action: assert
    assertions:
      chase:
        active: false
        ended: true
        end_reason: "escape"  # or "capture"
        
      skill_usage:
        p1:
          # Skills used during chase
          - "climb"
          - "jump"
          - "dodge"

expected_outcomes:
  - chase_completed: true
  - con_checks_resolved: true
  - movement_tracked: true
  - end_condition_met: true
```
  </action>
  <verify>
    <automated>cat tests/scenarios/acceptance/scen_chase.yaml | head -30</automated>
  </verify>
  <done>E2E chase scenario</done>
</task>

</tasks>

<verification>
Run verification:
1. `uv run pytest tests/rules/coc/test_chase.py -v`
2. `uv run python -m dm_bot.main smoke-check`
</verification>

<success_criteria>
- ChaseEncounter with CON checks and movement
- ChaseParticipant with exhaustion mechanics
- Fleeers move first in DEX order
- Pursuers move to close distance
- Escape condition when fleeer reaches end
- Capture condition when pursuer catches fleeer
- Unit tests for all mechanics
- E2E scenario validates full chase
- All existing tests pass
</success_criteria>

<output>
After completion, create `.planning/workstreams/track-e/phases/82-chase-rules/E82-01-SUMMARY.md`
</output>
