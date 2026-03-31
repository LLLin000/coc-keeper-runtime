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

    def resolve_round(
        self, dice_rolls: dict[str, int] | None = None
    ) -> ChaseRoundResult:
        """Resolve one round of chase.

        Args:
            dice_rolls: Optional pre-rolled dice {participant_id: roll}

        Returns:
            ChaseRoundResult with full resolution
        """
        import random

        result = ChaseRoundResult(round_number=self.current_round)

        # Step 1: CON checks
        self._resolve_con_checks(result, dice_rolls or {})

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
        obstacle = (
            current_loc.exit_obstacle if direction > 0 else current_loc.entry_obstacle
        )

        if obstacle:
            # Would need skill check here
            # For now, auto-succeed
            pass

        # Move
        old_location = participant.current_location
        participant.current_location = new_location

        result.movements.append(
            {
                "participant_id": participant.participant_id,
                "from": old_location,
                "to": new_location,
                "direction": "forward" if direction > 0 else "back",
            }
        )

        return True

    def _find_nearest_fleeer(
        self, pursuer: ChaseParticipant
    ) -> ChaseParticipant | None:
        """Find the nearest fleeer to a pursuer."""
        nearest = None
        min_distance = float("inf")

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
                if (
                    pursuer.current_location == fleeer.current_location
                    and pursuer.status == ChaseStatus.ACTIVE
                    and fleeer.status == ChaseStatus.ACTIVE
                ):
                    # Capture!
                    fleeer.status = ChaseStatus.CAPTURED
                    result.status_changes[fleeer_id] = ChaseStatus.CAPTURED

        # Determine if ended
        active_fleeers = [
            pid
            for pid in self.fleeers
            if self.participants[pid].status == ChaseStatus.ACTIVE
        ]

        if result.winners:
            result.ended = True
            result.end_reason = "escape"
        elif not active_fleeers:
            result.ended = True
            result.end_reason = "capture"
