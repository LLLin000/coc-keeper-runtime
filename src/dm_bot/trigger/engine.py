"""Trigger event processing pipeline."""

from dm_bot.trigger.models import Trigger, TriggerEvent, Reaction


class TriggerEngine:
    """Matches events to triggers and executes reactions in priority order."""

    def __init__(self) -> None:
        self._triggers: dict[str, Trigger] = {}

    @property
    def triggers(self) -> dict[str, Trigger]:
        return dict(self._triggers)

    def register_trigger(self, trigger: Trigger) -> None:
        self._triggers[trigger.trigger_id] = trigger

    def unregister(self, trigger_id: str) -> None:
        self._triggers.pop(trigger_id, None)

    def fire_event(self, event: TriggerEvent) -> list[Reaction]:
        """Fire an event, match triggers, and execute reactions ordered."""
        matched = self._find_matching_triggers(event)
        if not matched:
            return []
        reactions = self._collect_reactions(matched)
        ordered = sorted(reactions, key=lambda r: r.priority)
        self._execute_reactions(ordered)
        return ordered

    def _find_matching_triggers(self, event: TriggerEvent) -> list[Trigger]:
        return [t for t in self._triggers.values() if t.event_type == event.event_type]

    def _collect_reactions(self, triggers: list[Trigger]) -> list[Reaction]:
        return [r for t in triggers for r in t.reactions]

    def _execute_reactions(self, reactions: list[Reaction]) -> None:
        for reaction in reactions:
            self._execute_single(reaction)

    def _execute_single(self, reaction: Reaction) -> None:
        pass  # concrete effect execution deferred to higher layers
