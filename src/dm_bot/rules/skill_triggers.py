"""COC 7th Edition Skill Trigger Parsing.

Hybrid parsing: exact keyword match first, fuzzy/LLM fallback for ambiguous cases.
"""

import re
from dataclasses import dataclass

from dm_bot.rules.actions import COCDifficulty


# Chinese + English trigger keywords mapping to skill names
SKILL_TRIGGERS: dict[str, str] = {
    # PERCEPTION
    "侦查": "侦查",
    "侦察": "侦查",
    "spot": "侦查",
    "search": "搜索",
    "搜索": "搜索",
    "listen": "聆听",
    "聆听": "聆听",
    "感知": "感知",
    "sense": "感知",
    # COMMUNICATION
    "说服": "说服",
    "persuade": "说服",
    "char": "魅惑",
    "魅惑": "魅惑",
    "charm": "魅惑",
    "威胁": "胁迫",
    "胁迫": "胁迫",
    "intimidate": "胁迫",
    "话术": "话术",
    "fast talk": "话术",
    # COMBAT
    "战斗": "Brawl",
    "fight": "Brawl",
    "格斗": "Brawl",
    "射击": "Shooting (Handgun)",
    "shoot": "Shooting (Handgun)",
    "闪避": "Dodge",
    "dodge": "Dodge",
    "躲避": "Dodge",
    # KNOWLEDGE
    "潜行": "Stealth",
    "stealth": "Stealth",
    "潜行": "Stealth",
    "聆听": "Listen",
    "搜索": "Search",
    "侦查": "Spot Hidden",
    "侦察": "Spot Hidden",
    # SKILL CHECK PHRASES
    "检定": "",  # Strip suffix like "侦查检定"
    "roll": "",  # Strip "roll" prefix
    "骰": "",  # Strip dice suffix
}


@dataclass
class SkillTriggerIntent:
    """Parsed skill trigger from player action text.

    Attributes:
        skill_name: Exact skill name if matched, None if fuzzy/LLM needed
        bonus_dice: Number of bonus dice (0 if none)
        penalty_dice: Number of penalty dice (0 if none)
        difficulty: Check difficulty (regular, hard, extreme)
        push_requested: Whether player requested a pushed roll
        confidence: "exact" if matched, "fuzzy" if ambiguous
        raw_text: Original input text
    """

    skill_name: str | None = None
    bonus_dice: int = 0
    penalty_dice: int = 0
    difficulty: COCDifficulty = "regular"
    push_requested: bool = False
    confidence: str = "exact"
    raw_text: str = ""


def parse_skill_trigger(
    text: str,
    character,  # CharacterRecord
) -> SkillTriggerIntent:
    """Parse player action text into skill check intent.

    Hybrid approach:
    1. Try exact keyword match on skill triggers dict
    2. Try exact match against character skill names
    3. If no exact match → return with confidence="fuzzy" for LLM fallback

    Args:
        text: Player action text (e.g., "我想侦查这个房间", "roll 侦查")
        character: CharacterRecord with skills list

    Returns:
        SkillTriggerIntent with matched skill or None if no match
    """
    text_stripped = text.strip()
    text_lower = text_stripped.lower()

    # Remove common suffixes
    for suffix in ["检定", "roll", "骰"]:
        if text_lower.endswith(suffix):
            text_lower = text_lower[: -len(suffix)].strip()
            text_stripped = text_stripped[: -len(suffix)].strip()

    # 1. Try exact keyword match
    for keyword, skill_name in SKILL_TRIGGERS.items():
        if skill_name and (keyword in text_lower or keyword in text_stripped):
            return SkillTriggerIntent(
                skill_name=skill_name,
                bonus_dice=_extract_bonus(text),
                penalty_dice=_extract_penalty(text),
                difficulty=_extract_difficulty(text),
                push_requested="推动" in text or "push" in text_lower,
                confidence="exact",
                raw_text=text,
            )

    # 2. Try exact match against character skill names
    for skill in character.skills:
        if skill.name in text or skill.name.lower() in text_lower:
            return SkillTriggerIntent(
                skill_name=skill.name,
                bonus_dice=_extract_bonus(text),
                penalty_dice=_extract_penalty(text),
                difficulty=_extract_difficulty(text),
                push_requested="推动" in text or "push" in text_lower,
                confidence="exact",
                raw_text=text,
            )

        # Also match specializations
        if skill.specialization and (
            skill.specialization.lower() in text_lower or skill.specialization in text
        ):
            return SkillTriggerIntent(
                skill_name=skill.name,
                bonus_dice=_extract_bonus(text),
                penalty_dice=_extract_penalty(text),
                difficulty=_extract_difficulty(text),
                push_requested="推动" in text or "push" in text_lower,
                confidence="exact",
                raw_text=text,
            )

    # 3. No match → fuzzy for LLM
    return SkillTriggerIntent(
        skill_name=None,
        bonus_dice=_extract_bonus(text),
        penalty_dice=_extract_penalty(text),
        difficulty=_extract_difficulty(text),
        push_requested="推动" in text or "push" in text_lower,
        confidence="fuzzy",
        raw_text=text,
    )


def _extract_bonus(text: str) -> int:
    """Extract bonus dice count from text like '有奖励骰', '+2 dice', etc.

    Args:
        text: Input text to parse

    Returns:
        Number of bonus dice (0 if none found)
    """
    text_lower = text.lower()

    # Chinese patterns
    patterns = [
        r"奖励(\d+)",  # "奖励2"
        r"有(\d+)个?奖励骰",  # "有2个奖励骰"
        r"奖励(\d+)个?骰",  # "奖励2个骰"
    ]
    for p in patterns:
        m = re.search(p, text_lower)
        if m:
            return int(m.group(1))

    # English patterns
    patterns_en = [
        r"bonus\s*(\d+)",  # "bonus 2"
        r"\+(\d+).*dice",  # "+2 dice"
    ]
    for p in patterns_en:
        m = re.search(p, text_lower)
        if m:
            return int(m.group(1))

    # Simple "bonus dice" without number = 1
    if "奖励骰" in text or "bonus dice" in text_lower:
        return 1

    return 0


def _extract_penalty(text: str) -> int:
    """Extract penalty dice count from text like '-1惩罚骰', etc.

    Args:
        text: Input text to parse

    Returns:
        Number of penalty dice (0 if none found)
    """
    text_lower = text.lower()

    # Chinese patterns
    patterns = [
        r"惩罚(\d+)",  # "惩罚2"
        r"有(\d+)个?惩罚骰",  # "有2个惩罚骰"
    ]
    for p in patterns:
        m = re.search(p, text_lower)
        if m:
            return int(m.group(1))

    # English patterns
    patterns_en = [
        r"penalty\s*(\d+)",  # "penalty 2"
        r"-(\d+).*dice",  # "-2 dice"
        r"disadvantage",  # "disadvantage" = 1 penalty die
    ]
    for p in patterns_en:
        m = re.search(p, text_lower)
        if m:
            if m.lastindex:
                return int(m.group(1))
            return 1

    # Simple "penalty dice" without number = 1
    if "惩罚骰" in text or "penalty dice" in text_lower:
        return 1

    return 0


def _extract_difficulty(text: str) -> COCDifficulty:
    """Extract difficulty from text.

    Args:
        text: Input text to parse

    Returns:
        COCDifficulty: "regular", "hard", or "extreme"
    """
    text_lower = text.lower()

    if "极限" in text or "extreme" in text_lower:
        return "extreme"
    if "困难" in text or "hard" in text_lower:
        return "hard"

    return "regular"


# Export public interface
__all__ = [
    "SkillTriggerIntent",
    "parse_skill_trigger",
    "SKILL_TRIGGERS",
]
