from typing import Literal

from pydantic import BaseModel, Field


class ActionResult(BaseModel):
    """结算后的单个行动结果"""

    success: bool
    success_rank: str = "failure"  # critical, extreme, hard, regular, failure
    rolled_value: int = 0
    san_change: int = 0
    discovered_clues: list[str] = Field(default_factory=list)
    extra_info: str = ""


class Action(BaseModel):
    """玩家提交的行动"""

    user_id: str = Field(min_length=1)
    character_id: str = Field(min_length=1)
    action_text: str = Field(min_length=1)
    visibility: Literal["public", "private"] = "public"
    dex_value: int = 50  # DEX 决定行动顺序，默认 50
    result: ActionResult | None = None
