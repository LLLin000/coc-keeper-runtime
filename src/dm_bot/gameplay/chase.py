"""Gameplay integration for chase system."""

from dm_bot.rules.coc.chase import (
    ChaseEncounter,
    ChaseParticipant,
    ChaseRole,
    ChaseObstacle,
    ChaseLocation,
)


class GameplayChaseManager:
    """Manages chases within a gameplay session."""

    def __init__(self) -> None:
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
                    "role": p.role.value if hasattr(p.role, "value") else p.role,
                    "location": p.current_location,
                    "status": p.status.value
                    if hasattr(p.status, "value")
                    else p.status,
                    "exhausted": p.exhausted,
                }
                for pid, p in chase.participants.items()
            },
            "locations": [
                {"Name": loc.name_cn, "is_end": loc.is_end} for loc in chase.locations
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
            status_val = (
                participant.status.value
                if hasattr(participant.status, "value")
                else participant.status
            )
            if status_val == "escaped":
                result["winners"].append(pid)
            elif status_val == "captured":
                result["captured"].append(pid)

        self.active_chase = None
        return result
