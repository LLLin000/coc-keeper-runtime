class DiagnosticsService:
    def __init__(self, store) -> None:
        self._store = store

    def recent_summary(self, campaign_id: str) -> str:
        events = self._store.list_events(campaign_id)
        lines: list[str] = []

        state = self._store.load_campaign_state(campaign_id)
        adventure_state = dict(state.get("adventure_state", {}))
        if adventure_state:
            module_state = dict(adventure_state.get("module_state", {}))
            lines.append(f"scene={adventure_state.get('scene_id', 'unknown')}")
            if adventure_state.get("location_id"):
                lines.append(f"location={adventure_state['location_id']}")
            onboarding = dict(adventure_state.get("onboarding", {}))
            if onboarding:
                ready = onboarding.get("ready_user_ids", [])
                lines.append(f"onboarding={onboarding.get('status', 'unknown')} ready={len(ready)}")
            if adventure_state.get("objectives"):
                lines.append(f"objectives={', '.join(adventure_state['objectives'])}")
            if adventure_state.get("clues_found"):
                lines.append(f"clues={', '.join(adventure_state['clues_found'])}")
            if "time_remaining" in module_state:
                lines.append(f"time_remaining={module_state['time_remaining']}")
            if "blood_collected" in module_state and "blood_required" in module_state:
                lines.append(f"blood={module_state['blood_collected']}/{module_state['blood_required']}")
            if "san_pressure" in module_state:
                lines.append(f"san_pressure={module_state['san_pressure']}")
            if "danger_level" in module_state:
                lines.append(f"danger_level={module_state['danger_level']}")
            if "pending_push" in module_state:
                lines.append(f"pending_push={module_state['pending_push']}")
            pending_roll = dict(adventure_state.get("pending_roll", {}))
            if pending_roll:
                lines.append(f"pending_roll={pending_roll.get('id', 'unknown')} action={pending_roll.get('action', 'unknown')}")
            if adventure_state.get("ending_id"):
                lines.append(f"ending={adventure_state['ending_id']}")

        if events:
            last = events[-5:]
            lines.extend(f"{event['trace_id']} {event['event_type']}" for event in last)

        return "\n".join(lines) if lines else "no events"
