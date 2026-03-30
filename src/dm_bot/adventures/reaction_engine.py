from dataclasses import dataclass, field
from typing import Optional, Literal
from enum import Enum


class ReactionType(Enum):
    """All possible reaction types in the event graph runtime."""

    FEEDBACK = "feedback"
    CLARIFICATION = "clarification"
    ROLL = "roll"
    STATE_CHANGE = "state_change"
    CLUE_CHANGE = "clue_change"
    FOLLOW_ON = "follow_on"
    ENDING = "ending"


@dataclass
class EventReaction:
    """Base class for all reaction types."""

    reaction_id: str
    source_trigger_id: str
    reaction_type: ReactionType = ReactionType.FEEDBACK

    def __post_init__(self):
        # Ensure reaction_type is always set based on the actual subclass
        pass


@dataclass
class FeedbackReaction(EventReaction):
    """Direct feedback to player - renders immediately (non-blocking)."""

    message: str = ""

    def __post_init__(self):
        self.reaction_type = ReactionType.FEEDBACK


@dataclass
class ClarificationReaction(EventReaction):
    """Clarification request - blocks execution pending player response."""

    error_message: str = ""
    missing_prereq: Optional[str] = None
    suggested_correction: Optional[str] = None

    def __post_init__(self):
        self.reaction_type = ReactionType.CLARIFICATION


@dataclass
class RollReaction(EventReaction):
    """Roll request - blocks execution pending dice result."""

    skill_or_stat: str = ""
    difficulty: str = "regular"
    modifier: int = 0

    def __post_init__(self):
        self.reaction_type = ReactionType.ROLL


@dataclass
class StateChangeReaction(EventReaction):
    """State change (HP, SAN, inventory) - applies immediately (non-blocking)."""

    change_type: str = ""
    delta: int = 0
    reason: str = ""

    def __post_init__(self):
        self.reaction_type = ReactionType.STATE_CHANGE


@dataclass
class ClueChangeReaction(EventReaction):
    """Clue change (add/remove clues) - applies immediately (non-blocking)."""

    clue_id: str = ""
    action: str = "add"
    clue_text: Optional[str] = None

    def __post_init__(self):
        self.reaction_type = ReactionType.CLUE_CHANGE


@dataclass
class FollowOnReaction(EventReaction):
    """Follow-on trigger chain - queues next triggers (non-blocking)."""

    next_trigger_ids: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.reaction_type = ReactionType.FOLLOW_ON


@dataclass
class EndingReaction(EventReaction):
    """Ending evaluation — final state of the module."""

    ending_id: str = ""
    ending_type: str = ""  # "best", "good", "neutral", "bad", "worst"
    spine_alignment: float = 0.0  # 0.0-1.0
    summary: str = ""  # 1-2 sentence narrative summary

    def __post_init__(self):
        self.reaction_type = ReactionType.ENDING


@dataclass
class ReactionResult:
    """Aggregates all reactions from a trigger execution.

    Reactions are categorized by type for downstream processing:
    - Discord bot consumes: feedback_messages, clarifications (for display)
    - Rules engine consumes: roll_requests (for resolution)
    - Adventure state applies: state_changes, clue_changes
    - Trigger engine queues: follow_ons (for next triggers)
    """

    feedback_messages: list[str] = field(default_factory=list)
    clarifications: list[ClarificationReaction] = field(default_factory=list)
    roll_requests: list[RollReaction] = field(default_factory=list)
    state_changes: list[StateChangeReaction] = field(default_factory=list)
    clue_changes: list[ClueChangeReaction] = field(default_factory=list)
    follow_ons: list[FollowOnReaction] = field(default_factory=list)
    ending_reactions: list[EndingReaction] = field(default_factory=list)

    def add_reaction(self, reaction: EventReaction) -> None:
        """Add a reaction to the appropriate bucket."""
        if isinstance(reaction, FeedbackReaction):
            self.feedback_messages.append(reaction.message)
        elif isinstance(reaction, ClarificationReaction):
            self.clarifications.append(reaction)
        elif isinstance(reaction, RollReaction):
            self.roll_requests.append(reaction)
        elif isinstance(reaction, StateChangeReaction):
            self.state_changes.append(reaction)
        elif isinstance(reaction, ClueChangeReaction):
            self.clue_changes.append(reaction)
        elif isinstance(reaction, FollowOnReaction):
            self.follow_ons.append(reaction)
        elif isinstance(reaction, EndingReaction):
            self.ending_reactions.append(reaction)

    def apply_to_state(self, adventure_state: dict) -> None:
        """Apply state_changes and clue_changes to adventure state."""
        for change in self.state_changes:
            if change.change_type == "hp":
                adventure_state.setdefault("character", {})
                adventure_state["character"].setdefault("hp", 100)
                adventure_state["character"]["hp"] = max(
                    0, adventure_state["character"]["hp"] + change.delta
                )
            elif change.change_type == "san":
                adventure_state.setdefault("character", {})
                adventure_state["character"].setdefault("san", 100)
                adventure_state["character"]["san"] = max(
                    0, adventure_state["character"]["san"] + change.delta
                )
            elif change.change_type == "inventory":
                if change.delta > 0:
                    adventure_state.setdefault("character", {})
                    adventure_state["character"].setdefault("inventory", [])
                    adventure_state["character"]["inventory"].append(change.reason)
                else:
                    adventure_state.setdefault("character", {})
                    adventure_state["character"].setdefault("inventory", [])
                    if change.reason in adventure_state["character"]["inventory"]:
                        adventure_state["character"]["inventory"].remove(change.reason)

        for change in self.clue_changes:
            adventure_state.setdefault("clues", {})
            if change.action == "add":
                adventure_state["clues"][change.clue_id] = change.clue_text or ""
            elif change.action == "remove":
                adventure_state["clues"].pop(change.clue_id, None)

    def get_discord_messages(self) -> list[str]:
        """Get all feedback messages formatted for Discord."""
        return self.feedback_messages

    def has_blocking_reactions(self) -> bool:
        """Check if any reactions block execution."""
        return len(self.clarifications) > 0 or len(self.roll_requests) > 0


# Constants for cycle prevention
MAX_FOLLOW_ON_DEPTH = 10


class ReactionEngine:
    """Executes reactions and manages follow-on trigger chains.

    Execution model (per R-02):
    - Non-blocking: feedback, state_change, clue_change, follow_on
    - Blocking: clarification (waits for player), roll (waits for dice)

    Cycle prevention (per R-04):
    - Depth limit: MAX_FOLLOW_ON_DEPTH (10)
    - Visited set: prevents re-triggering same trigger
    """

    def __init__(self, trigger_engine):
        """Initialize with TriggerEngine reference for follow-on execution."""
        self.trigger_engine = trigger_engine

    def execute_reaction(self, reaction: EventReaction, adventure_state: dict) -> None:
        """Execute a single reaction based on its type.

        Non-blocking reactions execute immediately.
        Blocking reactions set pending state on adventure_state.
        """
        if isinstance(reaction, FeedbackReaction):
            # Non-blocking - feedback rendered immediately
            # Discord bot will pick this up from ReactionResult
            pass

        elif isinstance(reaction, ClarificationReaction):
            # Blocking - set pending clarification state
            adventure_state["pending_clarification"] = {
                "reaction_id": reaction.reaction_id,
                "error_message": reaction.error_message,
                "suggested_correction": reaction.suggested_correction,
            }

        elif isinstance(reaction, RollReaction):
            # Blocking - set pending roll state
            adventure_state["pending_roll"] = {
                "reaction_id": reaction.reaction_id,
                "skill_or_stat": reaction.skill_or_stat,
                "difficulty": reaction.difficulty,
                "modifier": reaction.modifier,
            }

        elif isinstance(reaction, StateChangeReaction):
            # Non-blocking - apply to state immediately
            # Apply directly here for simplicity
            self._apply_state_change(reaction, adventure_state)

        elif isinstance(reaction, ClueChangeReaction):
            # Non-blocking - apply to state immediately
            self._apply_clue_change(reaction, adventure_state)

        elif isinstance(reaction, FollowOnReaction):
            # Non-blocking - triggers queued for next execution
            # Follow-on chain handled by execute_follow_on_chain
            pass

    def _apply_state_change(
        self, change: StateChangeReaction, adventure_state: dict
    ) -> None:
        """Apply a state change to adventure state."""
        if change.change_type == "hp":
            adventure_state.setdefault("character", {})
            adventure_state["character"].setdefault("hp", 100)
            adventure_state["character"]["hp"] = max(
                0, adventure_state["character"]["hp"] + change.delta
            )
        elif change.change_type == "san":
            adventure_state.setdefault("character", {})
            adventure_state["character"].setdefault("san", 100)
            adventure_state["character"]["san"] = max(
                0, adventure_state["character"]["san"] + change.delta
            )
        elif change.change_type == "inventory":
            if change.delta > 0:
                adventure_state.setdefault("character", {})
                adventure_state["character"].setdefault("inventory", [])
                adventure_state["character"]["inventory"].append(change.reason)
            else:
                adventure_state.setdefault("character", {})
                adventure_state["character"].setdefault("inventory", [])
                if change.reason in adventure_state["character"]["inventory"]:
                    adventure_state["character"]["inventory"].remove(change.reason)

    def _apply_clue_change(
        self, change: ClueChangeReaction, adventure_state: dict
    ) -> None:
        """Apply a clue change to adventure state."""
        adventure_state.setdefault("clues", {})
        if change.action == "add":
            adventure_state["clues"][change.clue_id] = change.clue_text or ""
        elif change.action == "remove":
            adventure_state["clues"].pop(change.clue_id, None)

    def execute_follow_on_chain(
        self,
        initial_trigger_ids: list[str],
        package,
        adventure_state: dict,
        event: dict,
    ) -> ReactionResult:
        """Execute follow-on trigger chain with cycle prevention.

        Uses depth limit (10) + visited set to prevent infinite loops.

        Args:
            initial_trigger_ids: Starting trigger IDs to execute
            package: AdventurePackage for trigger lookup
            adventure_state: Current game state
            event: Event that triggered this chain

        Returns:
            ReactionResult aggregating all reactions from the chain
        """
        result = ReactionResult()
        depth = 0
        visited: set[str] = set()
        pending = list(initial_trigger_ids)

        while pending and depth < MAX_FOLLOW_ON_DEPTH:
            trigger_id = pending.pop(0)

            # Cycle prevention: skip already-visited triggers
            if trigger_id in visited:
                continue

            visited.add(trigger_id)

            # Execute trigger via TriggerEngine
            resolution = self.trigger_engine.execute(
                package=package,
                adventure_state=adventure_state,
                event=event,
                trigger_ids=[trigger_id],
            )

            # Spine tracking: record first-triggered path as spine (D-01)
            # First time a trigger fires becomes the spine - no explicit marker needed
            if trigger_id not in adventure_state.get("spine_history", []):
                adventure_state.setdefault("spine_history", []).append(trigger_id)
                adventure_state["spine_progress"] = len(
                    adventure_state["spine_history"]
                )

            # Branch tracking: track player deviation from spine (D-02)
            # Initialize branch_state if not present
            if "branch_state" not in adventure_state:
                adventure_state["branch_state"] = {
                    "is_off_spine": False,
                    "off_spine_triggers": [],
                    "branch_depth": 0,
                    "return_attempts": 0,
                }

            # Check if current trigger is off-spine
            is_off_spine = trigger_id not in adventure_state.get("spine_history", [])
            branch_state = adventure_state["branch_state"]

            if is_off_spine:
                # Track off-spine trigger
                if trigger_id not in branch_state["off_spine_triggers"]:
                    branch_state["off_spine_triggers"].append(trigger_id)
                branch_state["branch_depth"] += 1
                branch_state["is_off_spine"] = True
            else:
                # On spine - reset branch depth if returning from off-spine
                if branch_state["branch_depth"] > 0:
                    branch_state["return_attempts"] += 1
                branch_state["branch_depth"] = 0
                branch_state["is_off_spine"] = False

            # Process all events from this trigger
            for rt_event in resolution.events:
                reaction = self._event_to_reaction(rt_event)
                if reaction:
                    result.add_reaction(reaction)

                    # Queue follow-ons for next iteration
                    if isinstance(reaction, FollowOnReaction):
                        pending.extend(reaction.next_trigger_ids)

            # Check for ending triggers after each trigger execution
            trigger = package.trigger_by_id(trigger_id)
            if trigger.event_kind == "ending":
                ending = self.trigger_engine._check_ending_conditions(
                    trigger, adventure_state, event
                )
                if ending:
                    result.ending_reactions.append(ending)
                    # Don't continue chain after ending - endings are terminal
                    break

            depth += 1

        return result

    def _event_to_reaction(self, rt_event) -> Optional[EventReaction]:
        """Convert TriggerRuntimeEvent to appropriate EventReaction.

        This is a bridge between the old TriggerRuntimeEvent pattern
        and the new EventReaction types.
        """
        event_type = rt_event.event_type
        payload = rt_event.payload

        reaction_id = payload.get("reaction_id", f"rx_{id(rt_event)}")
        source_trigger_id = payload.get("trigger_id", "unknown")

        if event_type == "feedback":
            return FeedbackReaction(
                reaction_id=reaction_id,
                source_trigger_id=source_trigger_id,
                message=payload.get("message", ""),
            )
        elif event_type == "clarification":
            return ClarificationReaction(
                reaction_id=reaction_id,
                source_trigger_id=source_trigger_id,
                error_message=payload.get("error_message", ""),
                missing_prereq=payload.get("missing_prereq"),
                suggested_correction=payload.get("suggested_correction"),
            )
        elif event_type == "roll":
            return RollReaction(
                reaction_id=reaction_id,
                source_trigger_id=source_trigger_id,
                skill_or_stat=payload.get("skill_or_stat", ""),
                difficulty=payload.get("difficulty", "regular"),
                modifier=payload.get("modifier", 0),
            )
        elif event_type == "state_change":
            return StateChangeReaction(
                reaction_id=reaction_id,
                source_trigger_id=source_trigger_id,
                change_type=payload.get("change_type", ""),
                delta=payload.get("delta", 0),
                reason=payload.get("reason", ""),
            )
        elif event_type == "clue_change":
            return ClueChangeReaction(
                reaction_id=reaction_id,
                source_trigger_id=source_trigger_id,
                clue_id=payload.get("clue_id", ""),
                action=payload.get("action", "add"),
                clue_text=payload.get("clue_text"),
            )
        elif event_type == "follow_on":
            return FollowOnReaction(
                reaction_id=reaction_id,
                source_trigger_id=source_trigger_id,
                next_trigger_ids=payload.get("next_trigger_ids", []),
            )

        return None
