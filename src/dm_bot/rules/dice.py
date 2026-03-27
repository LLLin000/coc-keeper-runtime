import random
from typing import Protocol

import d20
from pydantic import BaseModel, Field

from dm_bot.rules.actions import AdvantageMode, COCDifficulty


class DiceOutcome(BaseModel):
    expression: str = Field(min_length=1)
    total: int
    rendered: str = Field(min_length=1)


class PercentileOutcome(BaseModel):
    value: int
    difficulty: COCDifficulty = "regular"
    rolled: int
    success: bool
    success_rank: str
    critical: bool = False
    fumble: bool = False
    bonus_dice: int = 0
    penalty_dice: int = 0
    pushed: bool = False
    rendered: str = Field(min_length=1)


class DiceRoller(Protocol):
    def roll(self, expression: str, *, advantage: AdvantageMode = "none") -> DiceOutcome: ...
    def roll_percentile(
        self,
        *,
        value: int,
        difficulty: COCDifficulty = "regular",
        bonus_dice: int = 0,
        penalty_dice: int = 0,
        pushed: bool = False,
    ) -> PercentileOutcome: ...


class D20DiceRoller:
    _ADVANTAGE_MAP = {
        "none": d20.AdvType.NONE,
        "advantage": d20.AdvType.ADV,
        "disadvantage": d20.AdvType.DIS,
    }

    def roll(self, expression: str, *, advantage: AdvantageMode = "none") -> DiceOutcome:
        try:
            result = d20.roll(expression, advantage=self._ADVANTAGE_MAP[advantage])
        except Exception as exc:  # pragma: no cover - d20 exception types vary
            raise ValueError(str(exc)) from exc
        return DiceOutcome(expression=expression, total=int(result.total), rendered=str(result))

    def roll_percentile(
        self,
        *,
        value: int,
        difficulty: COCDifficulty = "regular",
        bonus_dice: int = 0,
        penalty_dice: int = 0,
        pushed: bool = False,
    ) -> PercentileOutcome:
        ones = random.randint(0, 9)
        tens_pool = [random.randint(0, 9) for _ in range(max(1, 1 + bonus_dice + penalty_dice))]
        if bonus_dice and not penalty_dice:
            tens = min(tens_pool)
        elif penalty_dice and not bonus_dice:
            tens = max(tens_pool)
        else:
            tens = tens_pool[0]
        rolled = 100 if tens == 0 and ones == 0 else tens * 10 + ones
        thresholds = {
            "regular": value,
            "hard": value // 2,
            "extreme": value // 5,
        }
        success = rolled <= thresholds[difficulty]
        success_rank = "failure"
        if rolled == 1:
            success = True
            success_rank = "critical"
        elif success:
            if rolled <= thresholds["extreme"]:
                success_rank = "extreme"
            elif rolled <= thresholds["hard"]:
                success_rank = "hard"
            else:
                success_rank = "regular"
        critical = rolled == 1
        fumble = rolled == 100 or (value < 50 and rolled >= 96)
        rendered = f"{rolled:02d} / {value} ({'成功' if success else '失败'})"
        return PercentileOutcome(
            value=value,
            difficulty=difficulty,
            rolled=rolled,
            success=success,
            success_rank=success_rank,
            critical=critical,
            fumble=fumble,
            bonus_dice=bonus_dice,
            penalty_dice=penalty_dice,
            pushed=pushed,
            rendered=rendered,
        )
