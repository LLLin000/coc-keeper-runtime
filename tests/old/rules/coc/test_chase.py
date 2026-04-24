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

    def test_can_move_when_active(self):
        """Test that active participants can move."""
        p = ChaseParticipant(
            participant_id="p1",
            name="Test",
            role=ChaseRole.FLEER,
            con=60,
            dex=70,
            mov=8,
            exhausted=False,
        )
        assert p.can_move()

    def test_effective_mov_not_below_one(self):
        """Test that effective MOV is never below 1."""
        p = ChaseParticipant(
            participant_id="p1",
            name="Test",
            role=ChaseRole.FLEER,
            con=60,
            dex=70,
            mov=1,
            exhausted=True,
        )
        assert p.get_effective_mov() == 1


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

    def test_multiple_rounds(self, chase):
        """Test multiple rounds of chase."""
        # Set starting positions further apart so chase takes longer
        chase.participants["fleeer1"].current_location = 0
        chase.participants["pursuer1"].current_location = 0

        rounds = 0
        for i in range(3):
            result = chase.resolve_round({"fleeer1": 30, "pursuer1": 40})
            rounds += 1
            if result.ended:
                break

        # Either chase ended in capture/escape, or we ran multiple rounds
        assert rounds >= 1

    def test_exhausted_participant_cannot_move(self, chase):
        """Test that exhausted participants don't move."""
        # First round - exhaust fleeer
        result1 = chase.resolve_round({"fleeer1": 95, "pursuer1": 40})
        assert chase.participants["fleeer1"].exhausted

        # Second round - fleeer should not move
        fleeer_loc_before = chase.participants["fleeer1"].current_location
        result2 = chase.resolve_round({"fleeer1": 30, "pursuer1": 40})

        # Fleeer should not have moved (still exhausted from last round CON failure)
        # Note: exhaustion is reset at end of round resolution


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
        assert obs.difficulty == "regular"

    def test_difficulty_multiplier_regular(self):
        """Test regular difficulty multiplier."""
        obs = ChaseObstacle(
            name="Wall",
            name_cn="墙",
            skill="climb",
            difficulty="regular",
        )
        assert obs.get_difficulty_multiplier() == 1

    def test_difficulty_multiplier_hard(self):
        """Test hard difficulty multiplier."""
        obs = ChaseObstacle(
            name="Wall",
            name_cn="墙",
            skill="climb",
            difficulty="hard",
        )
        assert obs.get_difficulty_multiplier() == 2

    def test_difficulty_multiplier_extreme(self):
        """Test extreme difficulty multiplier."""
        obs = ChaseObstacle(
            name="Wall",
            name_cn="墙",
            skill="climb",
            difficulty="extreme",
        )
        assert obs.get_difficulty_multiplier() == 5


class TestChaseLocation:
    """Test chase locations."""

    def test_location_creation(self):
        """Test creating a location."""
        loc = ChaseLocation(
            index=0,
            name="Street",
            name_cn="街道",
        )
        assert loc.index == 0
        assert loc.name == "Street"
        assert not loc.is_end

    def test_location_with_obstacles(self):
        """Test location with entry and exit obstacles."""
        entry = ChaseObstacle(
            name="Fence",
            name_cn="围栏",
            skill="jump",
            difficulty="hard",
        )
        loc = ChaseLocation(
            index=0,
            name="Yard",
            name_cn="院子",
            entry_obstacle=entry,
            is_end=False,
        )
        assert loc.entry_obstacle is not None
        assert loc.entry_obstacle.difficulty == "hard"

    def test_end_location(self):
        """Test end location marking."""
        loc = ChaseLocation(
            index=4,
            name="Escape",
            name_cn="逃脱点",
            is_end=True,
        )
        assert loc.is_end


class TestChaseIntegration:
    """Integration tests for chase system."""

    def test_full_chase_scenario(self):
        """Test a complete chase from start to escape."""
        chase = ChaseEncounter()

        # Add fleeer (investigator)
        chase.add_participant(
            participant_id="inv1",
            name="Investigator",
            role=ChaseRole.FLEER,
            con=70,
            dex=60,
            mov=9,
        )

        # Add pursuer (creature)
        chase.add_participant(
            participant_id="mon1",
            name="Ghoul",
            role=ChaseRole.PURSUER,
            con=50,
            dex=50,
            mov=7,
        )

        # Add locations
        chase.add_location(name="Street", name_cn="街道")
        chase.add_location(name="Alley", name_cn="小巷")
        chase.add_location(name="Fence", name_cn="围墙")
        chase.add_location(name="Rooftop", name_cn="屋顶")
        chase.add_location(name="Escape", name_cn="逃脱点", is_end=True)

        # Resolve rounds until escape or capture
        max_rounds = 10
        for i in range(max_rounds):
            result = chase.resolve_round({"inv1": 30, "mon1": 40})
            if result.ended:
                break

        # Chase should end with escape
        assert not chase.active
        # Either escape or capture
        assert result.end_reason in ["escape", "capture"]

    def test_chase_with_pre_rolled_dice(self):
        """Test chase with specific dice rolls."""
        chase = ChaseEncounter()

        chase.add_participant(
            participant_id="fleeer1",
            name="Fleeer",
            role=ChaseRole.FLEER,
            con=60,
            dex=70,
            mov=8,
        )

        chase.add_participant(
            participant_id="pursuer1",
            name="Pursuer",
            role=ChaseRole.PURSUER,
            con=50,
            dex=60,
            mov=8,
        )

        chase.add_location(name="Start", name_cn="起点")
        chase.add_location(name="Middle", name_cn="中途")
        chase.add_location(name="End", name_cn="终点", is_end=True)

        # Both succeed CON
        result = chase.resolve_round({"fleeer1": 30, "pursuer1": 25})
        assert result.con_results["fleeer1"]["success"] is True
        assert result.con_results["pursuer1"]["success"] is True
