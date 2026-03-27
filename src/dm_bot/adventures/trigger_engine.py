from dataclasses import dataclass, field


@dataclass
class TriggerRuntimeEvent:
    event_type: str
    payload: dict[str, object]


@dataclass
class TriggerResolution:
    matched_trigger_ids: list[str] = field(default_factory=list)
    table_summaries: list[str] = field(default_factory=list)
    gm_summaries: list[str] = field(default_factory=list)
    events: list[TriggerRuntimeEvent] = field(default_factory=list)

    def merged_table_summary(self) -> str:
        return "\n".join(item for item in self.table_summaries if item)


class TriggerEngine:
    def execute(self, *, package, adventure_state: dict[str, object], event: dict[str, object], trigger_ids: list[str] | None = None) -> TriggerResolution:
        resolution = TriggerResolution()
        seen: set[str] = set()
        queue = list(trigger_ids or self._matching_trigger_ids(package=package, adventure_state=adventure_state, event=event))
        while queue:
            trigger_id = queue.pop(0)
            if trigger_id in seen:
                continue
            seen.add(trigger_id)
            trigger = package.trigger_by_id(trigger_id)
            if not self._matches(trigger=trigger, adventure_state=adventure_state, event=event):
                continue
            resolution.matched_trigger_ids.append(trigger.id)
            self._apply_effects(trigger=trigger, package=package, adventure_state=adventure_state, resolution=resolution)
            if trigger.table_summary:
                resolution.table_summaries.append(trigger.table_summary)
            if trigger.gm_summary:
                resolution.gm_summaries.append(trigger.gm_summary)
            queue.extend(trigger.next_trigger_ids)
        return resolution

    def _matching_trigger_ids(self, *, package, adventure_state: dict[str, object], event: dict[str, object]) -> list[str]:
        matched: list[str] = []
        for trigger in package.triggers:
            if trigger.event_kind != event.get("kind"):
                continue
            if trigger.event_kind == "action" and trigger.action_id and trigger.action_id != event.get("action_id"):
                continue
            if trigger.event_kind == "roll":
                if trigger.pending_roll_id and trigger.pending_roll_id != event.get("pending_roll_id"):
                    continue
                if trigger.roll_action and trigger.roll_action != event.get("roll_action"):
                    continue
            if self._matches(trigger=trigger, adventure_state=adventure_state, event=event):
                matched.append(trigger.id)
        return matched

    def _matches(self, *, trigger, adventure_state: dict[str, object], event: dict[str, object]) -> bool:
        conditions = trigger.conditions
        if conditions.location_id and conditions.location_id != adventure_state.get("location_id"):
            return False
        if conditions.pending_roll_id and conditions.pending_roll_id != event.get("pending_roll_id"):
            return False
        module_state = dict(adventure_state.get("module_state", {}))
        for key, value in conditions.state_matches.items():
            if module_state.get(key) != value:
                return False
        clues = set(adventure_state.get("clues_found", []))
        if any(clue not in clues for clue in conditions.required_clues):
            return False
        if any(clue in clues for clue in conditions.absent_clues):
            return False
        total = event.get("roll_total")
        if conditions.min_total is not None and (total is None or int(total) < conditions.min_total):
            return False
        if conditions.max_total is not None and (total is None or int(total) > conditions.max_total):
            return False
        return True

    def _apply_effects(self, *, trigger, package, adventure_state: dict[str, object], resolution: TriggerResolution) -> None:
        module_state = dict(adventure_state.get("module_state", {}))
        location_state = dict(adventure_state.get("location_state", {}))
        for effect in trigger.effects:
            if effect.kind == "set_module_state":
                module_state[effect.key] = effect.value
                resolution.events.append(TriggerRuntimeEvent("trigger.effect_applied", {"trigger_id": trigger.id, "effect": effect.kind, "key": effect.key, "value": effect.value}))
            elif effect.kind == "increment_module_state":
                module_state[effect.key] = int(module_state.get(effect.key, 0)) + int(effect.amount)
                resolution.events.append(TriggerRuntimeEvent("trigger.effect_applied", {"trigger_id": trigger.id, "effect": effect.kind, "key": effect.key, "amount": effect.amount}))
            elif effect.kind == "set_location_state":
                target_location = effect.location_id or str(adventure_state.get("location_id", ""))
                bucket = dict(location_state.get(target_location, {}))
                bucket[effect.key] = effect.value
                location_state[target_location] = bucket
                resolution.events.append(TriggerRuntimeEvent("trigger.effect_applied", {"trigger_id": trigger.id, "effect": effect.kind, "location_id": target_location, "key": effect.key, "value": effect.value}))
            elif effect.kind == "add_clue":
                clues = list(adventure_state.get("clues_found", []))
                if effect.clue_id and effect.clue_id not in clues:
                    clues.append(effect.clue_id)
                    adventure_state["clues_found"] = clues
                resolution.events.append(TriggerRuntimeEvent("trigger.effect_applied", {"trigger_id": trigger.id, "effect": effect.kind, "clue_id": effect.clue_id}))
            elif effect.kind == "move_location":
                location = package.location_by_id(effect.location_id)
                adventure_state["location_id"] = location.id
                adventure_state["scene_id"] = location.scene_id
                resolution.events.append(TriggerRuntimeEvent("trigger.effect_applied", {"trigger_id": trigger.id, "effect": effect.kind, "location_id": location.id}))
            elif effect.kind == "set_pending_roll":
                adventure_state["pending_roll"] = {
                    "id": effect.roll_id,
                    "action": effect.roll_action,
                    "label": effect.roll_label,
                    "prompt": effect.prompt,
                }
                resolution.events.append(TriggerRuntimeEvent("trigger.effect_applied", {"trigger_id": trigger.id, "effect": effect.kind, "roll_id": effect.roll_id, "roll_action": effect.roll_action}))
            elif effect.kind == "clear_pending_roll":
                adventure_state.pop("pending_roll", None)
                resolution.events.append(TriggerRuntimeEvent("trigger.effect_applied", {"trigger_id": trigger.id, "effect": effect.kind}))
        adventure_state["module_state"] = module_state
        adventure_state["location_state"] = location_state
