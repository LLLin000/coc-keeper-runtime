"""Trigger event processing pipeline with chain lifecycle and audit trail."""

from dm_bot.trigger.models import (
    Trigger, TriggerEvent, Reaction,
    TriggerChain, AuditEntry,
)
from dm_bot.store.db import Store


class TriggerEngine:
    """Matches events to triggers with persisted chains and auditable trail."""

    def __init__(self, store: Store | None = None) -> None:
        self._triggers: dict[str, Trigger] = {}
        self._chains: list[TriggerChain] = []
        self._audit: list[AuditEntry] = []
        self._store = store
        self.recover_chains()

    @property
    def triggers(self) -> dict[str, Trigger]:
        return dict(self._triggers)

    @property
    def chains(self) -> list[TriggerChain]:
        return list(self._chains)

    def register_trigger(self, trigger: Trigger) -> None:
        self._triggers[trigger.trigger_id] = trigger

    def unregister(self, trigger_id: str) -> None:
        self._triggers.pop(trigger_id, None)

    def fire_event(self, event: TriggerEvent) -> list[Reaction]:
        matched = self._find_matching_triggers(event)
        if not matched:
            return []

        all_reactions: list[Reaction] = []
        for trigger in matched:
            chain = TriggerChain(
                event_id=event.event_id,
                event_type=event.event_type,
                trigger_id=trigger.trigger_id,
            )
            self._chains.append(chain)

            self._record_audit(chain.chain_id, "event.fire", {
                "event_id": event.event_id,
                "event_type": event.event_type,
            })
            self._record_audit(chain.chain_id, "trigger.match", {
                "trigger_id": trigger.trigger_id,
            })

            reactions = self._collect_ordered_reactions(trigger)
            all_reactions.extend(reactions)

            for reaction in reactions:
                self._record_audit(chain.chain_id, "reaction.exec", {
                    "reaction_id": reaction.reaction_id,
                    "effect_type": reaction.effect_type,
                })
                self._execute_single(reaction)

            chain.complete()
            self._persist_chain(chain)

        return all_reactions

    def resume_chain(self, chain: TriggerChain) -> None:
        chain.status = "running"
        self._chains.append(chain)
        self._record_audit(chain.chain_id, "chain.resume", {
            "trigger_id": chain.trigger_id,
            "event_type": chain.event_type,
        })
        self._persist_chain(chain)

    def recover_chains(self, store: Store | None = None) -> None:
        s = store or self._store
        if s is None:
            return
        loaded_ids = {c.chain_id for c in self._chains}
        for status in ("running", "blocked"):
            for chain in s.list_chains_by_status(status):
                if chain.chain_id not in loaded_ids:
                    self.resume_chain(chain)
                    loaded_ids.add(chain.chain_id)

    def list_running_chains(self) -> list[TriggerChain]:
        return [c for c in self._chains if c.status == "running"]

    def _find_matching_triggers(self, event: TriggerEvent) -> list[Trigger]:
        return [t for t in self._triggers.values() if t.event_type == event.event_type]

    def _collect_ordered_reactions(self, trigger: Trigger) -> list[Reaction]:
        return sorted(trigger.reactions, key=lambda r: r.priority)

    def _execute_single(self, reaction: Reaction) -> None:
        pass

    def _record_audit(self, chain_id: str, step: str, detail: dict) -> None:
        entry = AuditEntry(chain_id=chain_id, step=step, detail=detail)
        self._audit.append(entry)
        if self._store:
            self._store.save_audit_entry(entry)

    def _persist_chain(self, chain: TriggerChain) -> None:
        if self._store:
            self._store.save_chain(chain)

    def get_audit_trail(self, chain_id: str | None = None) -> list[AuditEntry]:
        if chain_id:
            return [e for e in self._audit if e.chain_id == chain_id]
        return list(self._audit)
