"""Message intent classification for Discord COC Keeper runtime.

This module provides intent classification to route messages appropriately
based on the message's purpose (OOC discussion, in-character social action,
player action, rules query, or admin command).
"""

from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class MessageIntent(str, Enum):
    """Classification of message intent in a COC session.

    OOC - Out of Character: Discussion not meant to be in-game
    SOCIAL_IC - Social In-Character: Non-action in-character communication
    PLAYER_ACTION - Player's game action requiring resolution
    RULES_QUERY - Player asking about game rules
    ADMIN_ACTION - Administrative command (admin only)
    UNKNOWN - Unable to determine intent (defaults to safe handling)
    """

    OOC = "ooc"
    SOCIAL_IC = "social_ic"
    PLAYER_ACTION = "player_action"
    RULES_QUERY = "rules_query"
    ADMIN_ACTION = "admin_action"
    UNKNOWN = "unknown"


class IntentClassificationRequest(BaseModel):
    """Request for classifying a message's intent."""

    trace_id: str = Field(description="Unique trace identifier")
    campaign_id: str = Field(description="Campaign identifier")
    channel_id: str = Field(description="Discord channel identifier")
    user_id: str = Field(description="User who sent the message")
    content: str = Field(description="Message content to classify")
    session_phase: str = Field(description="Current session phase")
    is_admin: bool = Field(default=False, description="Whether user has admin role")


class IntentClassificationResult(BaseModel):
    """Result of intent classification."""

    intent: MessageIntent
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence")
    reasoning: str = Field(description="Brief reasoning for classification")
    timestamp: datetime = Field(default_factory=datetime.now)


class MessageIntentMetadata(BaseModel):
    """Metadata stored with each message for debugging and logging."""

    intent: MessageIntent
    classification_reasoning: str
    classified_at: datetime = Field(default_factory=datetime.now)
    handling_decision: str = Field(
        description="What the system decided to do with this message"
    )
    was_buffered: bool = Field(
        default=False, description="Whether message was buffered"
    )
    phase_at_classification: str = Field(description="Session phase when classified")


class IntentHandlingResult(BaseModel):
    """Result of intent handling."""

    should_process: bool
    should_buffer: bool
    feedback_message: str | None = None
    deferred_content: str | None = None


# Default intent when classification fails
DEFAULT_INTENT = MessageIntent.UNKNOWN

# Intent handling priorities per session phase
# Format: phase -> list of (intent, priority) - higher priority = handled first
INTENT_PRIORITY_BY_PHASE = {
    "onboarding": [
        (MessageIntent.RULES_QUERY, 10),
        (MessageIntent.ADMIN_ACTION, 9),
        (MessageIntent.OOC, 7),
        (MessageIntent.SOCIAL_IC, 5),
        (MessageIntent.PLAYER_ACTION, 3),
        (MessageIntent.UNKNOWN, 1),
    ],
    "lobby": [
        (MessageIntent.ADMIN_ACTION, 10),
        (MessageIntent.OOC, 8),
        (MessageIntent.SOCIAL_IC, 6),
        (MessageIntent.RULES_QUERY, 5),
        (MessageIntent.PLAYER_ACTION, 3),
        (MessageIntent.UNKNOWN, 1),
    ],
    "awaiting_ready": [
        (MessageIntent.ADMIN_ACTION, 10),
        (MessageIntent.OOC, 8),
        (MessageIntent.RULES_QUERY, 6),
        (MessageIntent.SOCIAL_IC, 5),
        (MessageIntent.PLAYER_ACTION, 3),
        (MessageIntent.UNKNOWN, 1),
    ],
    "scene_round_open": [
        (MessageIntent.PLAYER_ACTION, 10),
        (MessageIntent.SOCIAL_IC, 7),
        (MessageIntent.ADMIN_ACTION, 9),
        (MessageIntent.OOC, 4),
        (MessageIntent.RULES_QUERY, 3),
        (MessageIntent.UNKNOWN, 1),
    ],
    "scene_round_resolving": [
        (MessageIntent.ADMIN_ACTION, 10),
        (MessageIntent.PLAYER_ACTION, 5),
        (MessageIntent.OOC, 2),
        (MessageIntent.SOCIAL_IC, 2),
        (MessageIntent.RULES_QUERY, 2),
        (MessageIntent.UNKNOWN, 1),
    ],
    "combat": [
        (MessageIntent.PLAYER_ACTION, 10),
        (MessageIntent.ADMIN_ACTION, 9),
        (MessageIntent.SOCIAL_IC, 2),
        (MessageIntent.OOC, 1),
        (MessageIntent.RULES_QUERY, 1),
        (MessageIntent.UNKNOWN, 1),
    ],
    "paused": [
        (MessageIntent.ADMIN_ACTION, 10),
        (MessageIntent.OOC, 7),
        (MessageIntent.SOCIAL_IC, 5),
        (MessageIntent.RULES_QUERY, 4),
        (MessageIntent.PLAYER_ACTION, 2),
        (MessageIntent.UNKNOWN, 1),
    ],
}


def get_intent_priority(intent: MessageIntent, session_phase: str) -> int:
    """Get the handling priority for an intent in a given session phase.

    Args:
        intent: The message intent
        session_phase: The current session phase

    Returns:
        Priority value (higher = more important to handle now)
    """
    phase_priorities = INTENT_PRIORITY_BY_PHASE.get(
        session_phase, INTENT_PRIORITY_BY_PHASE["lobby"]
    )
    for intent_type, priority in phase_priorities:
        if intent_type == intent:
            return priority
    return 1  # Default lowest priority


def should_buffer_intent(intent: MessageIntent, session_phase: str) -> bool:
    """Determine if an intent should be buffered (delayed) in the current phase.

    Args:
        intent: The message intent
        session_phase: The current session phase

    Returns:
        True if the message should be buffered until phase ends
    """
    if session_phase == "scene_round_resolving":
        return intent not in {MessageIntent.ADMIN_ACTION}

    if session_phase == "combat":
        return intent not in {MessageIntent.ADMIN_ACTION, MessageIntent.PLAYER_ACTION}

    return False


def get_handling_decision(intent: MessageIntent, session_phase: str) -> str:
    """Get a human-readable explanation of how a message will be handled.

    Args:
        intent: The classified intent
        session_phase: The current session phase

    Returns:
        Explanation string for the user
    """
    if should_buffer_intent(intent, session_phase):
        return f"Message buffered until {session_phase} phase ends"

    priority = get_intent_priority(intent, session_phase)
    if priority >= 9:
        return "Message will be processed immediately"
    elif priority >= 5:
        return "Message will be processed with normal priority"
    else:
        return "Message will be processed when higher priority items complete"
