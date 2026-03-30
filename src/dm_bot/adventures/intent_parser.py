import re
from typing import Optional

from .action_intent import ActionIntent, Entity, IntentParseResult


# Common COC action patterns for rule-based matching
ACTION_PATTERNS = [
    # Lock interaction
    (r"(撬锁?|开锁?|pick\s*lock)", "lock_interaction"),
    (r"(锁|锁头)", "lock_interaction"),
    # Search
    (r"(搜索?|搜查?|找|寻?找)", "search"),
    (r"(翻|检查?|查看?)", "search"),
    # Move
    (r"(移动?|走去?|走到?|go\s*to|move)", "move"),
    (r"(进入?|进去?|出来?|出来|exit|enter)", "move"),
    # Combat
    (r"(攻击?|打|砍|射|开火)", "combat"),
    (r"(战斗?|打架)", "combat"),
    # Observation
    (r"(观察?|查看?|看|瞧|看一?下)", "observe"),
    (r"(注意?|察觉?|发现?)", "observe"),
    # Interaction
    (r"(交谈?|对话?|说话?|跟.*说)", "interact"),
    (r"(问|询问?|打听?)", "interact"),
    # Stealth
    (r"(潜行?|偷偷摸摸|悄悄)", "stealth"),
    # Skill use
    (r"(使用?|运用?)", "skill_use"),
]

# Modifiers
MODIFIER_PATTERNS = [
    (r"(悄悄|偷偷|安静|静悄悄)", "quietly"),
    (r"(用力|使劲|暴力)", "forcefully"),
    (r"(小心|谨慎|仔细)", "carefully"),
    (r"(快速|快|赶紧)", "quickly"),
    (r"(偷偷|秘密|暗中)", "secretly"),
]

# Compound action separators
COMPOUND_SEPARATORS = [
    r"[,，、]\s*",  # "搜索房间，撬锁"
    r"(?:并且|然后|接着|再|之后)\s*",  # "搜索房间然后撬锁"
    r"(?:和|与|以及)\s*",  # "搜索房间和撬锁"
]


class IntentParser:
    """Hybrid parser: rule-based fast path + LLM fallback.

    Strategy:
    1. Try rule-based parsing first (fast, deterministic)
    2. If rules don't match or input is complex, use LLM fallback
    3. Compound actions split by separators, parsed individually
    """

    def __init__(self, llm_client: Optional[object] = None):
        """Initialize parser with optional LLM client for fallback."""
        self.llm_client = llm_client

    def parse(self, player_text: str) -> IntentParseResult:
        """Parse player action text into list of ActionIntents.

        Args:
            player_text: Raw player input like "我想搜索房间并撬开保险箱"

        Returns:
            IntentParseResult with ordered list of intents and parse method used
        """
        if not player_text or not player_text.strip():
            return IntentParseResult(intents=[], parse_method="rule")

        # Step 1: Split compound actions
        segments = self._split_compound(player_text)

        # Step 2: Parse each segment
        intents: list[ActionIntent] = []
        all_rule_parsed = True

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            intent = self._parse_single(segment)
            if intent:
                intents.append(intent)
                if intent.action_type == "unknown":
                    all_rule_parsed = False
            else:
                # Rule parsing failed, try LLM
                llm_intent = self._parse_with_llm(segment)
                if llm_intent:
                    intents.append(llm_intent)
                    all_rule_parsed = False

        # Determine parse method
        if all_rule_parsed:
            parse_method = "rule"
        elif self.llm_client and any(i.action_type != "unknown" for i in intents):
            parse_method = "hybrid"
        else:
            parse_method = "llm" if self.llm_client else "rule"

        return IntentParseResult(intents=intents, parse_method=parse_method)

    def _split_compound(self, text: str) -> list[str]:
        """Split compound actions into individual segments.

        "搜索房间并撬锁" -> ["搜索房间", "撬锁"]
        """
        pattern = "|".join(COMPOUND_SEPARATORS)
        segments = re.split(pattern, text)
        return segments if segments else [text]

    def _parse_single(self, text: str) -> Optional[ActionIntent]:
        """Parse a single action segment using rules."""
        text_lower = text.lower()

        # Find action type
        action_type = "unknown"
        for pattern, action in ACTION_PATTERNS:
            if re.search(pattern, text_lower):
                action_type = action
                break

        # Extract modifiers
        modifiers: list[str] = []
        for pattern, mod in MODIFIER_PATTERNS:
            if re.search(pattern, text_lower):
                modifiers.append(mod)

        # Extract potential target (simple heuristic: longest noun phrase)
        target = self._extract_target(text)

        return ActionIntent(
            action_type=action_type,
            intent=text,
            target=target,
            modifiers=modifiers,
        )

    def _extract_target(self, text: str) -> Optional[Entity]:
        """Extract potential target entity from text.

        This is a simple heuristic - full resolution happens in validation.
        """
        # Common target patterns
        target_patterns = [
            r"(保险箱?|保险柜)",
            r"(门|窗户?|窗)",
            r"(桌子|椅子|柜子|书架)",
            r"(尸体?|死人|骨骸?)",
            r"(那(?:个|扇|个)?(?:门|锁|窗|保险箱?|柜子))",
            r"(这个?|这儿|这里)",
        ]

        for pattern in target_patterns:
            match = re.search(pattern, text)
            if match:
                entity_text = match.group(0)
                entity_type = self._infer_entity_type(entity_text)
                return Entity(
                    entity_type=entity_type,
                    reference=entity_text,
                    resolved_id=None,  # Resolved during validation
                )

        return None

    def _infer_entity_type(self, reference: str) -> str:
        """Infer entity type from reference text."""
        reference_lower = reference.lower()
        if any(word in reference_lower for word in ["门", "窗"]):
            return "door_or_window"
        if any(word in reference_lower for word in ["保险箱", "保险柜"]):
            return "safe"
        if any(word in reference_lower for word in ["柜子", "书架", "桌子"]):
            return "furniture"
        if any(word in reference_lower for word in ["尸体", "死人", "骨骸"]):
            return "corpse"
        return "unknown"

    def _parse_with_llm(self, text: str) -> Optional[ActionIntent]:
        """Fallback to LLM for complex/unknown inputs."""
        if not self.llm_client:
            return None

        # Simple LLM prompt - in production, use more sophisticated prompting
        prompt = f"""解析玩家动作文本为结构化意图。

文本: "{text}"

输出格式 (JSON):
{{
    "action_type": "动作类型，如 search, move, combat, lock_interaction, observe, interact",
    "intent": "原始意图文本",
    "target_type": "目标类型，如 door, safe, character, location 或 null",
    "target_reference": "玩家对目标的引用，如 "那扇门" 或 null",
    "modifiers": ["修饰词列表，如 quietly, forcefully"]
}}

只输出 JSON，不要其他文字。"""

        try:
            response = self.llm_client.chat(prompt)
            import json

            data = json.loads(response)
            target = None
            if data.get("target_reference"):
                target = Entity(
                    entity_type=data.get("target_type", "unknown"),
                    reference=data["target_reference"],
                    resolved_id=None,
                )

            return ActionIntent(
                action_type=data.get("action_type", "unknown"),
                intent=data.get("intent", text),
                target=target,
                modifiers=data.get("modifiers", []),
            )
        except Exception:
            return None
