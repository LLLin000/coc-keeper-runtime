from dm_bot.gameplay.combat import CombatEncounter, Combatant
from dm_bot.gameplay.modes import GameModeState
from dm_bot.adventures.trigger_engine import TriggerEngine
from dm_bot.characters.models import CharacterRecord
from dm_bot.router.contracts import TurnPlan
from dm_bot.rules.actions import LookupAction, RuleAction, StatBlock
from dm_bot.adventures.models import AdventureLocationConnection, AdventurePackage


class CharacterRegistry:
    def __init__(self) -> None:
        self._characters: dict[str, CharacterRecord] = {}

    def put(self, user_id: str, character: CharacterRecord) -> None:
        self._characters[user_id] = character

    def get(self, user_id: str) -> CharacterRecord | None:
        return self._characters.get(user_id)


class GameplayOrchestrator:
    def __init__(self, *, importer, registry: CharacterRegistry, rules_engine) -> None:
        self._importer = importer
        self.registry = registry
        self._rules_engine = rules_engine
        self.mode_state = GameModeState()
        self.combat: CombatEncounter | None = None
        self.adventure: AdventurePackage | None = None
        self.adventure_state: dict[str, object] = {}
        self._trigger_engine = TriggerEngine()
        self._pending_trigger_events: list[dict[str, object]] = []

    def import_character(self, *, user_id: str, provider: str, external_id: str) -> CharacterRecord:
        character = self._importer.import_character(provider, external_id)
        self.registry.put(user_id, character)
        return character

    def enter_scene(self, *, speakers: list[str]) -> None:
        self.mode_state.enter_scene(speakers=speakers)

    def enter_dm(self) -> None:
        self.mode_state.enter_dm()

    def start_combat(self, *, combatants: list[Combatant]) -> CombatEncounter:
        encounter = CombatEncounter()
        encounter.start(combatants)
        self.combat = encounter
        self.mode_state.mode = "combat"
        return encounter

    def end_scene(self) -> None:
        self.mode_state.enter_dm()

    def next_combat_turn(self) -> CombatEncounter | None:
        if self.combat is None:
            return None
        self.combat.advance_turn()
        return self.combat

    def active_combatant_name(self) -> str | None:
        if self.combat is None:
            return None
        return self.combat.active_combatant.name

    def combat_summary(self) -> str:
        if self.combat is None:
            return "combat not active"
        return self.combat.summary()

    def load_adventure(self, adventure: AdventurePackage) -> None:
        self.adventure = adventure
        self.adventure_state = {
            "adventure_slug": adventure.slug,
            "scene_id": adventure.start_scene_id,
            "location_id": adventure.start_location_id or adventure.start_scene_id,
            "clues_found": [],
            "objectives": list(adventure.objectives),
            "module_state": adventure.state_defaults(),
            "location_state": {},
            "ending_id": None,
            "onboarding": {
                "status": "awaiting_ready",
                "ready_user_ids": [],
                "opening_sent": False,
            },
        }

    def adventure_snapshot(self) -> dict[str, object]:
        if self.adventure is None:
            return {}
        scene_id = self._current_scene_id()
        scene = self.adventure.scene_by_id(scene_id)
        location = self._current_location()
        module_state = dict(self.adventure_state.get("module_state", {}))
        return {
            "public": {
                "slug": self.adventure.slug,
                "title": self.adventure.title,
                "current_scene": scene.model_dump(),
                "current_location": location.model_dump(),
                "reachable_locations": [connection.model_dump() for connection in location.connections],
                "objectives": list(self.adventure_state.get("objectives", [])),
                "state": self.adventure.public_state(module_state),
                "guidance": self.adventure_guidance_snapshot(),
            },
            "gm": {
                "premise": self.adventure.premise,
                "state": self.adventure.gm_state(module_state),
                "endings": [ending.model_dump() for ending in self.adventure.endings],
                "pending_roll": dict(self.adventure_state.get("pending_roll", {})),
            },
        }

    def adventure_guidance_snapshot(self) -> dict[str, object]:
        if self.adventure is None:
            return {}
        scene = self.adventure.scene_by_id(self._current_scene_id())
        return {
            "ambient_focus": list(scene.guidance.ambient_focus),
            "light_hint": scene.guidance.light_hint,
            "rescue_hint": scene.guidance.rescue_hint,
            "known_clues": list(self.adventure_state.get("clues_found", [])),
            "pending_roll": dict(self.adventure_state.get("pending_roll", {})),
        }

    def scene_frame_text(self, *, scene_id: str | None = None) -> str:
        if self.adventure is None:
            return ""
        resolved_scene_id = scene_id or self._current_scene_id()
        scene = self.adventure.scene_by_id(resolved_scene_id)
        lines = [f"【{scene.title}】", scene.summary]
        if scene.presentation.entry_text:
            lines.append(scene.presentation.entry_text)
        if scene.presentation.pressure_text:
            lines.append(scene.presentation.pressure_text)
        if scene.presentation.choice_prompt:
            lines.append(scene.presentation.choice_prompt)
        elif scene.guidance.ambient_focus:
            lines.append(f"现在最值得留意的是：{'、'.join(scene.guidance.ambient_focus)}。")
        return "\n".join(line for line in lines if line)

    def set_adventure_scene(self, scene_id: str) -> None:
        if self.adventure is None:
            raise RuntimeError("adventure not loaded")
        self.adventure.scene_by_id(scene_id)
        self.adventure_state["scene_id"] = scene_id
        if self.adventure.locations:
            for location in self.adventure.locations:
                if location.scene_id == scene_id:
                    self.adventure_state["location_id"] = location.id
                    break

    def set_adventure_location(self, location_id: str) -> None:
        if self.adventure is None:
            raise RuntimeError("adventure not loaded")
        location = self.adventure.location_by_id(location_id)
        self.adventure_state["location_id"] = location.id
        self.adventure_state["scene_id"] = location.scene_id

    def record_adventure_clue(self, clue_id: str) -> None:
        clues = list(self.adventure_state.get("clues_found", []))
        if clue_id not in clues:
            clues.append(clue_id)
        self.adventure_state["clues_found"] = clues

    def update_adventure_state(self, **changes: object) -> None:
        module_state = dict(self.adventure_state.get("module_state", {}))
        module_state.update(changes)
        self.adventure_state["module_state"] = module_state

    def set_adventure_ending(self, ending_id: str) -> None:
        if self.adventure is None:
            raise RuntimeError("adventure not loaded")
        if ending_id not in {ending.id for ending in self.adventure.endings}:
            raise KeyError(ending_id)
        self.adventure_state["ending_id"] = ending_id

    def adventure_onboarding(self) -> dict[str, object]:
        return dict(self.adventure_state.get("onboarding", {}))

    def mark_adventure_ready(self, *, user_id: str) -> dict[str, object]:
        onboarding = self.adventure_onboarding()
        ready_user_ids = list(onboarding.get("ready_user_ids", []))
        if user_id not in ready_user_ids:
            ready_user_ids.append(user_id)
        onboarding["ready_user_ids"] = ready_user_ids
        self.adventure_state["onboarding"] = onboarding
        return onboarding

    def begin_adventure(self) -> None:
        onboarding = self.adventure_onboarding()
        onboarding["status"] = "in_progress"
        onboarding["opening_sent"] = True
        self.adventure_state["onboarding"] = onboarding

    def adventure_opening_text(self, *, active_characters: dict[str, str]) -> str:
        if self.adventure is None:
            raise RuntimeError("adventure not loaded")
        roster = [name for name in active_characters.values() if name]
        roster_line = f"已就位调查员：{', '.join(roster)}。" if roster else "已就位调查员：未命名调查员。"
        return (
            f"《{self.adventure.title}》开始。\n"
            f"{self.adventure.premise}\n"
            f"{roster_line}\n"
            f"{self.scene_frame_text()}\n"
            "先描述你们第一轮的观察、站位或试探动作。"
        )

    def onboarding_block_message(self) -> str | None:
        onboarding = self.adventure_onboarding()
        if onboarding and onboarding.get("status") == "awaiting_ready":
            return "模组已加载，先用 `/ready` 完成就位；如未导入角色，可在 `/ready` 里填写角色名。"
        return None

    def evaluate_scene_action(self, content: str) -> dict[str, object]:
        if self.adventure is None:
            return {"kind": "none"}
        scene = self.adventure.scene_by_id(self._current_scene_id())
        location = self._current_location()
        lowered = content.lower()
        connection_result = self._evaluate_location_connections(content=content, lowered=lowered, location=location)
        if connection_result is not None:
            return connection_result
        scored_matches: list[tuple[int, object]] = []
        for interactable in scene.interactables:
            score = sum(1 for keyword in interactable.keywords if keyword.lower() in lowered)
            if score > 0:
                scored_matches.append((score, interactable))

        scored_matches.sort(key=lambda item: item[0], reverse=True)
        top_score = scored_matches[0][0] if scored_matches else 0
        matches = [interactable for score, interactable in scored_matches if score == top_score]

        if not matches:
            return self._record_scene_miss_and_hint(scene)
        if len(matches) > 1:
            return {
                "kind": "clarify",
                "message": f"你想先处理哪一个：{', '.join(item.title for item in matches)}？",
            }

        interactable = matches[0]
        self.adventure_state["scene_miss_count"] = 0

        if interactable.trigger_ids:
            resolution = self._trigger_engine.execute(
                package=self.adventure,
                adventure_state=self.adventure_state,
                event={"kind": "action", "action_id": interactable.id},
                trigger_ids=interactable.trigger_ids,
            )
            summary = resolution.merged_table_summary()
            self._pending_trigger_events.extend(event.__dict__ for event in resolution.events)
            if interactable.judgement == "roll":
                pending_roll = dict(self.adventure_state.get("pending_roll", {}))
                return {
                    "kind": "roll_needed",
                    "message": summary or interactable.prompt_text or f"这里需要一次 {interactable.roll_label or '检定'}。",
                    "roll": {
                        "action": pending_roll.get("action") or interactable.roll_type or "ability_check",
                        "label": pending_roll.get("label") or interactable.roll_label or "Check",
                    },
                    "trigger_events": [event.__dict__ for event in resolution.events],
                }
            return {
                "kind": "auto" if interactable.judgement != "clarify" else "clarify",
                "message": summary or interactable.result_text or scene.summary,
                "guidance": scene.guidance.light_hint if interactable.judgement != "clarify" else "",
                "trigger_events": [event.__dict__ for event in resolution.events],
            }

        if interactable.discover_clue:
            self.record_adventure_clue(interactable.discover_clue)
        if interactable.transition_scene_id:
            self.set_adventure_scene(interactable.transition_scene_id)

        if interactable.judgement == "roll":
            return {
                "kind": "roll_needed",
                "message": interactable.prompt_text or f"这里需要一次 {interactable.roll_label or '检定'}。",
                "roll": {
                    "action": interactable.roll_type or "ability_check",
                    "label": interactable.roll_label or "Check",
                },
            }
        if interactable.judgement == "clarify":
            return {
                "kind": "clarify",
                "message": interactable.prompt_text or f"请先说明你打算怎么处理{interactable.title}。",
            }
        if interactable.transition_scene_id:
            return {
                "kind": "auto",
                "message": f"{interactable.result_text or scene.summary}\n{self.scene_frame_text()}",
                "guidance": "",
            }
        return {
            "kind": "auto",
            "message": interactable.result_text or scene.summary,
            "guidance": scene.guidance.light_hint,
        }

    def _record_scene_miss_and_hint(self, scene) -> dict[str, object]:
        miss_count = int(self.adventure_state.get("scene_miss_count", 0)) + 1
        self.adventure_state["scene_miss_count"] = miss_count
        hint = scene.guidance.rescue_hint if miss_count >= 2 and scene.guidance.rescue_hint else scene.guidance.light_hint
        return {
            "kind": "hint",
            "message": hint or scene.summary,
            "guidance": f"现在最值得留意的是：{'、'.join(scene.guidance.ambient_focus)}。" if scene.guidance.ambient_focus else "",
            "tier": "rescue" if miss_count >= 2 and scene.guidance.rescue_hint else "light",
        }

    def _current_scene_id(self) -> str:
        if self.adventure is None:
            raise RuntimeError("adventure not loaded")
        return str(self.adventure_state.get("scene_id", self.adventure.start_scene_id))

    def _current_location(self):
        if self.adventure is None:
            raise RuntimeError("adventure not loaded")
        return self.adventure.location_by_id(str(self.adventure_state.get("location_id", self.adventure.start_location_id or self.adventure.start_scene_id)))

    def _evaluate_location_connections(self, *, content: str, lowered: str, location) -> dict[str, object] | None:
        scored_connections: list[tuple[int, AdventureLocationConnection]] = []
        for connection in location.connections:
            score = sum(1 for keyword in connection.keywords if keyword.lower() in lowered)
            if score > 0:
                scored_connections.append((score, connection))
        if not scored_connections:
            return None

        scored_connections.sort(key=lambda item: item[0], reverse=True)
        top_score = scored_connections[0][0]
        matches = [connection for score, connection in scored_connections if score == top_score]
        if len(matches) > 1:
            return {
                "kind": "clarify",
                "message": f"你想朝哪边移动：{', '.join(self.adventure.location_by_id(item.to_location_id).title for item in matches)}？",
            }

        connection = matches[0]
        if self._is_observation_only(content):
            if connection.observe_trigger_ids:
                resolution = self._trigger_engine.execute(
                    package=self.adventure,
                    adventure_state=self.adventure_state,
                    event={"kind": "action", "action_id": f"observe:{location.id}->{connection.to_location_id}"},
                    trigger_ids=connection.observe_trigger_ids,
                )
                self._pending_trigger_events.extend(event.__dict__ for event in resolution.events)
                summary = resolution.merged_table_summary()
                if summary:
                    return {"kind": "auto", "message": summary, "guidance": "", "trigger_events": [event.__dict__ for event in resolution.events]}
            return {
                "kind": "auto",
                "message": connection.observe_text or f"你靠近后暂时没有立刻踏进去，而是先观察通往 {self.adventure.location_by_id(connection.to_location_id).title} 的入口。",
                "guidance": "",
            }
        if self._is_travel_intent(content):
            if connection.travel_trigger_ids:
                resolution = self._trigger_engine.execute(
                    package=self.adventure,
                    adventure_state=self.adventure_state,
                    event={"kind": "action", "action_id": f"travel:{location.id}->{connection.to_location_id}"},
                    trigger_ids=connection.travel_trigger_ids,
                )
                self._pending_trigger_events.extend(event.__dict__ for event in resolution.events)
                summary = resolution.merged_table_summary()
                if summary:
                    return {"kind": "auto", "message": summary, "guidance": "", "trigger_events": [event.__dict__ for event in resolution.events]}
            self.set_adventure_location(connection.to_location_id)
            self.adventure_state["scene_miss_count"] = 0
            return {
                "kind": "auto",
                "message": f"{connection.travel_text}\n{self.scene_frame_text()}",
                "guidance": "",
            }
        return None

    def _is_observation_only(self, content: str) -> bool:
        lowered = content.lower()
        if any(marker in lowered for marker in ("不进去", "先不进", "先不进去", "只是打量", "只是观察", "先看看")):
            return True
        observe_verbs = ("看", "观察", "打量", "端详", "试探", "靠近")
        travel_verbs = ("进入", "走进", "进去", "踏入", "迈进", "穿过", "回到", "返回", "离开", "出去")
        return any(verb in content for verb in observe_verbs) and not any(verb in content for verb in travel_verbs)

    def _is_travel_intent(self, content: str) -> bool:
        return any(
            verb in content
            for verb in ("进入", "走进", "进去", "踏入", "迈进", "穿过", "回到", "返回", "离开", "出去", "去")
        )

    def resolve_manual_roll(
        self,
        *,
        actor_name: str,
        expression: str | None = None,
        action: str = "raw_roll",
        label: str = "",
        modifier: int = 0,
        advantage: str = "none",
        damage_type: str = "untyped",
        target_name: str = "",
        target_ac: int = 10,
        attack_bonus: int = 0,
        damage_expression: str = "",
        weapon: str = "unarmed",
    ) -> dict[str, object]:
        actor = StatBlock(name=actor_name or "Unknown", armor_class=10, hit_points=1)
        target = StatBlock(name=target_name, armor_class=target_ac, hit_points=1) if target_name else None
        parameters: dict[str, object]
        if action == "raw_roll":
            parameters = {"expression": expression or ""}
        elif action in {"ability_check", "saving_throw"}:
            parameters = {"label": label, "modifier": modifier, "advantage": advantage}
        elif action == "damage_roll":
            parameters = {"damage_expression": damage_expression or expression or "", "damage_type": damage_type}
        elif action == "attack_roll":
            parameters = {
                "attack_bonus": attack_bonus,
                "damage_expression": damage_expression,
                "weapon": weapon,
                "advantage": advantage,
            }
        else:
            raise RuntimeError(action)
        result = self._rules_engine.execute(
            RuleAction(
                action=action,
                actor=actor,
                target=target,
                parameters=parameters,
            )
        )
        consequence = self._apply_roll_consequences(result)
        if consequence is not None:
            result["consequence_summary"] = consequence.merged_table_summary()
            result["trigger_events"] = [event.__dict__ for event in consequence.events]
            self._pending_trigger_events.extend(event.__dict__ for event in consequence.events)
        return result

    def export_state(self) -> dict[str, object]:
        return {
            "mode": self.mode_state.model_dump(),
            "combat": self.combat.model_dump() if self.combat else None,
            "registry": {
                user_id: character.model_dump()
                for user_id, character in self.registry._characters.items()
            },
            "adventure_state": self.adventure_state,
        }

    def import_state(self, state: dict[str, object]) -> None:
        self.mode_state = GameModeState.model_validate(state.get("mode", {"mode": "dm", "scene_speakers": []}))
        combat = state.get("combat")
        self.combat = CombatEncounter.model_validate(combat) if combat else None
        registry = {}
        for user_id, payload in dict(state.get("registry", {})).items():
            registry[user_id] = CharacterRecord.model_validate(payload)
        self.registry._characters = registry
        self.adventure_state = dict(state.get("adventure_state", {}))
        slug = self.adventure_state.get("adventure_slug")
        if slug:
            from dm_bot.adventures.loader import load_adventure

            self.adventure = load_adventure(str(slug))

    def _apply_roll_consequences(self, result: dict[str, object]):
        if self.adventure is None:
            return None
        pending_roll = dict(self.adventure_state.get("pending_roll", {}))
        if not pending_roll:
            return None
        expected_action = pending_roll.get("action")
        if expected_action and expected_action != result.get("action"):
            return None
        resolution = self._trigger_engine.execute(
            package=self.adventure,
            adventure_state=self.adventure_state,
            event={
                "kind": "roll",
                "pending_roll_id": pending_roll.get("id", ""),
                "roll_action": result.get("action", ""),
                "roll_total": result.get("total"),
            },
        )
        if resolution.matched_trigger_ids:
            self.adventure_state.pop("pending_roll", None)
            return resolution
        return None

    def consume_trigger_events(self) -> list[dict[str, object]]:
        events = list(self._pending_trigger_events)
        self._pending_trigger_events.clear()
        return events

    def resolve_plan(self, plan: TurnPlan) -> list[dict[str, object]]:
        results: list[dict[str, object]] = []
        for call in plan.tool_calls:
            if call.name == "rules.lookup":
                result = self._rules_engine.lookup(LookupAction.model_validate(call.arguments))
            elif call.name == "rules.attack_roll":
                result = self._rules_engine.execute(RuleAction.model_validate(call.arguments))
            elif call.name == "rules.ability_check":
                result = self._rules_engine.execute(RuleAction.model_validate({"action": "ability_check", **call.arguments}))
            elif call.name == "rules.saving_throw":
                result = self._rules_engine.execute(RuleAction.model_validate({"action": "saving_throw", **call.arguments}))
            elif call.name == "rules.damage_roll":
                result = self._rules_engine.execute(RuleAction.model_validate({"action": "damage_roll", **call.arguments}))
            elif call.name == "rules.raw_roll":
                result = self._rules_engine.execute(RuleAction.model_validate({"action": "raw_roll", **call.arguments}))
            else:
                result = {"tool": call.name, "status": "unsupported"}
            results.append(result)
        return results
