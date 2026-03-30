"""COC 7th Edition Skill Resolution Service.

Provides skill check resolution with D20DiceRoller integration,
bonus/penalty dice handling, and push roll support.
"""

from dataclasses import dataclass

from dm_bot.rules.actions import COCDifficulty
from dm_bot.rules.dice import D20DiceRoller, PercentileOutcome


@dataclass
class SkillCheckResult:
    """Result of a skill check.

    Attributes:
        skill_name: Name of the skill checked
        skill_value: Character's skill value
        rolled: The dice roll result (00-99)
        success: Whether the check succeeded
        success_rank: "critical", "extreme", "hard", "regular", "failure", or "fumble"
        critical: True if rolled a 1 (critical success)
        fumble: True if rolled 100 or 96+ with value < 50 (critical failure)
        bonus_dice: Number of bonus dice
        penalty_dice: Number of penalty dice
        pushed: Whether this was a pushed roll
        difficulty: Check difficulty (regular, hard, extreme)
        rendered: Human-readable string like "08 / 50 (成功)"
        narrative_suggestion: AI narration hint
    """

    skill_name: str
    skill_value: int
    rolled: int
    success: bool
    success_rank: str
    critical: bool = False
    fumble: bool = False
    bonus_dice: int = 0
    penalty_dice: int = 0
    pushed: bool = False
    difficulty: COCDifficulty = "regular"
    rendered: str = ""
    narrative_suggestion: str = ""


class SkillResolutionService:
    """Service for resolving COC skill checks.

    Integrates with D20DiceRoller for percentile dice resolution
    and provides narrative suggestions for AI narration.
    """

    def __init__(self, dice_roller: D20DiceRoller | None = None):
        """Initialize the service.

        Args:
            dice_roller: Optional D20DiceRoller instance. Creates a new one if not provided.
        """
        self._dice_roller = dice_roller or D20DiceRoller()

    def check(
        self,
        character,  # CharacterRecord
        skill_name: str,
        *,
        difficulty: COCDifficulty = "regular",
        bonus_dice: int = 0,
        penalty_dice: int = 0,
        pushed: bool = False,
    ) -> SkillCheckResult:
        """Perform a skill check for a character.

        Args:
            character: CharacterRecord with skills list
            skill_name: Name of the skill to check
            difficulty: Check difficulty (regular, hard, extreme)
            bonus_dice: Number of bonus dice (picks minimum)
            penalty_dice: Number of penalty dice (picks maximum)
            pushed: Whether this is a pushed roll

        Returns:
            SkillCheckResult with the outcome

        Raises:
            ValueError: If skill not found or skill value <= 0
        """
        # Find skill on character
        from dm_bot.rules.skills import get_skill_by_name

        skill_entry = get_skill_by_name(character.skills, skill_name)
        if not skill_entry:
            raise ValueError(
                f"Skill '{skill_name}' not found on character {character.name}"
            )
        if skill_entry.value <= 0:
            raise ValueError(
                f"Skill '{skill_name}' has value {skill_entry.value}, must be > 0 for check"
            )

        # Call D20DiceRoller.roll_percentile()
        outcome = self._dice_roller.roll_percentile(
            value=skill_entry.value,
            difficulty=difficulty,
            bonus_dice=bonus_dice,
            penalty_dice=penalty_dice,
            pushed=pushed,
        )

        # Build result with narrative suggestion
        return SkillCheckResult(
            skill_name=skill_name,
            skill_value=skill_entry.value,
            rolled=outcome.rolled,
            success=outcome.success,
            success_rank=outcome.success_rank,
            critical=outcome.critical,
            fumble=outcome.fumble,
            bonus_dice=bonus_dice,
            penalty_dice=penalty_dice,
            pushed=pushed,
            difficulty=difficulty,
            rendered=outcome.rendered,
            narrative_suggestion=self._build_narrative(skill_name, outcome),
        )

    def push(
        self,
        character,  # CharacterRecord
        skill_name: str,
        luck_cost: int = 1,
    ) -> tuple[SkillCheckResult, int]:
        """Push a failed skill check by spending luck.

        Args:
            character: CharacterRecord with coc.luck
            skill_name: Name of the skill to push
            luck_cost: Amount of luck to spend (default 1)

        Returns:
            Tuple of (new_result, luck_spent)

        Raises:
            ValueError: If not enough luck
        """
        if character.coc is None or character.coc.luck < luck_cost:
            raise ValueError(
                f"Not enough luck. Have: {character.coc.luck if character.coc else 0}, need: {luck_cost}"
            )

        # Spend luck
        character.coc.luck -= luck_cost

        # Reroll with pushed=True
        result = self.check(character, skill_name, pushed=True)
        return result, luck_cost

    def _build_narrative(self, skill_name: str, outcome: PercentileOutcome) -> str:
        """Build AI narration suggestion based on outcome.

        Args:
            skill_name: Name of the skill
            outcome: PercentileOutcome from dice roller

        Returns:
            Chinese narrative string for AI narration
        """
        if outcome.critical:
            return f"【大成功】{skill_name}检定掷出{outcome.rolled}，大成功！"
        elif outcome.fumble:
            return f"【大失败】{skill_name}检定掷出{outcome.rolled}，大失败！"
        elif outcome.success_rank == "extreme":
            return f"【极限成功】{skill_name}检定掷出{outcome.rolled}，极限成功！"
        elif outcome.success_rank == "hard":
            return f"【困难成功】{skill_name}检定掷出{outcome.rolled}，困难成功！"
        elif outcome.success:
            return f"【成功】{skill_name}检定掷出{outcome.rolled}，成功。"
        else:
            return f"【失败】{skill_name}检定掷出{outcome.rolled}，失败。"


# Export public interface
__all__ = [
    "SkillResolutionService",
    "SkillCheckResult",
]
