from dataclasses import dataclass, field
from typing import Optional, Literal


@dataclass
class Entity:
    """Represents a target entity referenced in player action."""

    entity_type: str  # e.g., "door", "safe", "character", "location"
    reference: str  # player's reference: "那扇门", "保险箱", "NPC"
    resolved_id: Optional[str] = None  # resolved scene entity ID after validation


@dataclass
class ActionIntent:
    """Semi-structured action intent parsed from player text.

    Fields:
        action_type: Broad category like "lock_interaction", "search", "move", "combat"
        intent: Original player intent text preserved for reference
        target: Target entity if identified, None if no specific target
        modifiers: List of action modifiers like ["quietly", "forcefully", "stealth"]
    """

    action_type: str
    intent: str
    target: Optional[Entity] = None
    modifiers: list[str] = field(default_factory=list)


@dataclass
class IntentParseResult:
    """Result of parsing player action text into intents."""

    intents: list[ActionIntent]  # Ordered list of intents (compound actions)
    parse_method: Literal["rule", "llm", "hybrid"]  # How parsing was done


@dataclass
class ValidationResult:
    """Result of validating an ActionIntent against scene context."""

    valid: bool
    errors: list[str] = field(default_factory=list)  # Chinese error messages
    clarification_needed: bool = False


@dataclass
class ClarificationReaction:
    """Reaction emitted when validation fails and player needs to clarify."""

    error_message: str  # Chinese: "找不到目标「X」"
    missing_prerequisite: Optional[str] = None  # e.g., "需要先完成「调查房间」"
    suggested_correction: Optional[str] = None  # e.g., "你想撬开哪个锁？"
