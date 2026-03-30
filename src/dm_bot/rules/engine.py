from collections.abc import Callable
from dataclasses import dataclass, field
import d20

from dm_bot.rules.actions import LookupAction, RuleAction
from dm_bot.rules.dice import D20DiceRoller, DiceOutcome, PercentileOutcome
from dm_bot.rules.coc.combat import (
    CombatantStats,
    CombatAction,
    resolve_fighting_attack,
    resolve_shooting_attack,
    resolve_brawl_attack,
    resolve_grapple_attack,
    get_initiative_order,
)
from dm_bot.rules.coc.sanity import (
    resolve_sanity_check,
    roll_insanity_break,
    spend_luck_for_sanity,
    InsanityType,
)
from dm_bot.rules.coc.magic import resolve_spell_cast


@dataclass
class ActionResult:
    """Result of a single action in a batch execution."""

    user_id: str
    character_id: str
    action_text: str
    parsed_intent: str = ""
    rule_outcomes: list[dict] = field(default_factory=list)
    state_changes: dict[str, object] = field(default_factory=dict)
    trigger_effects: list[object] = field(default_factory=list)
    visibility: str = "public"  # Matches Visibility enum from session_store


@dataclass
class BatchResolutionResult:
    """Result of batch action resolution."""

    action_results: list[ActionResult] = field(default_factory=list)
    final_scene: dict[str, object] = field(default_factory=dict)
    audit_log: list[dict] = field(default_factory=list)


class RulesEngineError(RuntimeError):
    pass


class RulesEngine:
    def __init__(
        self,
        *,
        compendium,
        roll_resolver: Callable[[str], int] | None = None,
        dice_roller=None,
    ) -> None:
        self._compendium = compendium
        if dice_roller is not None:
            self._dice_roller = dice_roller
        elif roll_resolver is not None:
            self._dice_roller = _LegacyDiceRoller(roll_resolver)
        else:
            self._dice_roller = D20DiceRoller()

    def lookup(self, action: LookupAction) -> dict[str, object]:
        try:
            return self._compendium.lookup(action)
        except (ValueError, KeyError) as exc:
            raise RulesEngineError(str(exc)) from exc

    def execute(self, action: RuleAction) -> dict[str, object]:
        if action.action == "attack_roll":
            return self._execute_attack_roll(action)
        if action.action == "ability_check":
            return self._execute_check_like(action, kind="ability_check")
        if action.action == "saving_throw":
            return self._execute_check_like(action, kind="saving_throw")
        if action.action == "damage_roll":
            return self._execute_damage_roll(action)
        if action.action == "raw_roll":
            return self._execute_raw_roll(action)
        if action.action == "coc_skill_check":
            return self._execute_coc_skill_check(action)
        if action.action == "coc_sanity_check":
            return self._execute_coc_sanity_check(action)
        if action.action == "coc_fighting_attack":
            return self._execute_coc_fighting_attack(action)
        if action.action == "coc_shooting_attack":
            return self._execute_coc_shooting_attack(action)
        if action.action == "coc_brawl_attack":
            return self._execute_coc_brawl_attack(action)
        if action.action == "coc_dodge":
            return self._execute_coc_dodge(action)
        if action.action == "coc_grapple_attack":
            return self._execute_coc_grapple_attack(action)
        if action.action == "coc_cast_spell":
            return self._execute_coc_cast_spell(action)
        raise RulesEngineError(f"unsupported action: {action.action}")

    def execute_batch(
        self,
        actions: list,
        scene_snapshot: dict[str, object],
        *,
        dex_order: bool = False,
    ) -> BatchResolutionResult:
        """Execute a batch of actions in order.

        Args:
            actions: List of ActionBatchEntry objects to execute
            scene_snapshot: Current scene state snapshot
            dex_order: If True, sort actions by dex_value descending

        Returns:
            BatchResolutionResult with all action results and final scene
        """
        import copy

        # 1. Sort by submission time (default) or DEX order if enabled
        sorted_actions = list(actions)
        if dex_order:
            sorted_actions = sorted(
                sorted_actions,
                key=lambda a: getattr(a, "dex_value", 0) or 0,
                reverse=True,
            )

        # 2. Execute each action in order
        results: list[ActionResult] = []
        current_scene = copy.deepcopy(scene_snapshot)
        audit_log: list[dict] = []

        for entry in sorted_actions:
            # Parse action text into intent and outcomes
            result = ActionResult(
                user_id=entry.user_id,
                character_id=entry.character_id,
                action_text=entry.action_text,
                visibility=getattr(entry, "visibility", "public"),
            )

            # Simple intent parsing - classify action type from text
            action_lower = entry.action_text.lower()
            if "roll" in action_lower or "检定" in action_lower:
                result.parsed_intent = "action"
            elif "attack" in action_lower or "攻击" in action_lower:
                result.parsed_intent = "attack"
            elif "cast" in action_lower or "施法" in action_lower:
                result.parsed_intent = "cast"
            elif "move" in action_lower or "移动" in action_lower:
                result.parsed_intent = "movement"
            elif (
                "speak" in action_lower
                or "说话" in action_lower
                or "说" in action_lower
            ):
                result.parsed_intent = "dialogue"
            else:
                result.parsed_intent = "misc"

            # Apply state changes to current scene
            if result.state_changes:
                current_scene.update(result.state_changes)

            # Build audit log entry
            audit_entry = {
                "user_id": entry.user_id,
                "character_id": entry.character_id,
                "action_text": entry.action_text,
                "parsed_intent": result.parsed_intent,
                "rule_outcomes": result.rule_outcomes,
            }
            audit_log.append(audit_entry)
            results.append(result)

        return BatchResolutionResult(
            action_results=results,
            final_scene=current_scene,
            audit_log=audit_log,
        )

    def _execute_attack_roll(self, action: RuleAction) -> dict[str, object]:
        if action.target is None:
            raise RulesEngineError("attack_roll requires a target")

        if "attack_bonus" not in action.parameters:
            raise RulesEngineError("attack_roll requires attack_bonus")

        attack_bonus = int(action.parameters["attack_bonus"])
        advantage = str(action.parameters.get("advantage", "none"))
        attack_roll = self._roll(f"1d20+{attack_bonus}", advantage=advantage)
        damage_expression = str(action.parameters.get("damage_expression", "0"))
        damage_roll = (
            self._roll(damage_expression)
            if attack_roll.total >= action.target.armor_class
            else None
        )
        return {
            "action": "attack_roll",
            "actor": action.actor.name,
            "target": action.target.name,
            "weapon": action.parameters.get("weapon", "unarmed"),
            "roll": attack_roll.rendered,
            "attack_bonus": attack_bonus,
            "total": attack_roll.total,
            "damage": damage_roll.total if damage_roll else 0,
            "damage_roll": damage_roll.rendered if damage_roll else None,
            "advantage": advantage,
            "hit": attack_roll.total >= action.target.armor_class,
        }

    def _execute_check_like(
        self, action: RuleAction, *, kind: str
    ) -> dict[str, object]:
        modifier = int(action.parameters.get("modifier", 0))
        advantage = str(action.parameters.get("advantage", "none"))
        label = str(action.parameters.get("label", kind))
        outcome = self._roll(f"1d20+{modifier}", advantage=advantage)
        return {
            "action": kind,
            "actor": action.actor.name,
            "label": label,
            "modifier": modifier,
            "advantage": advantage,
            "roll": outcome.rendered,
            "total": outcome.total,
        }

    def _execute_damage_roll(self, action: RuleAction) -> dict[str, object]:
        expression = str(action.parameters.get("damage_expression", ""))
        if not expression:
            raise RulesEngineError("damage_roll requires damage_expression")
        outcome = self._roll(expression)
        return {
            "action": "damage_roll",
            "actor": action.actor.name,
            "damage_type": str(action.parameters.get("damage_type", "untyped")),
            "roll": outcome.rendered,
            "total": outcome.total,
        }

    def _execute_raw_roll(self, action: RuleAction) -> dict[str, object]:
        expression = str(action.parameters.get("expression", ""))
        if not expression:
            raise RulesEngineError("raw_roll requires expression")
        outcome = self._roll(expression)
        return {
            "action": "raw_roll",
            "actor": action.actor.name,
            "roll": outcome.rendered,
            "total": outcome.total,
        }

    def _execute_coc_skill_check(self, action: RuleAction) -> dict[str, object]:
        label = str(action.parameters.get("label", "技能检定"))
        value = int(action.parameters.get("value", 0))
        if value <= 0:
            raise RulesEngineError("coc_skill_check requires positive value")
        difficulty = str(action.parameters.get("difficulty", "regular"))
        bonus_dice = int(action.parameters.get("bonus_dice", 0))
        penalty_dice = int(action.parameters.get("penalty_dice", 0))
        pushed = bool(action.parameters.get("pushed", False))
        outcome = self._roll_percentile(
            value=value,
            difficulty=difficulty,
            bonus_dice=bonus_dice,
            penalty_dice=penalty_dice,
            pushed=pushed,
        )
        # Pushed roll re-roll: if pushed=True and first roll failed, roll again
        if pushed and not outcome.success:
            outcome = self._roll_percentile(
                value=value,
                difficulty=difficulty,
                bonus_dice=bonus_dice,
                penalty_dice=penalty_dice,
                pushed=False,  # Second roll is not pushed
            )
        return {
            "action": "coc_skill_check",
            "actor": action.actor.name,
            "label": label,
            "value": value,
            "difficulty": difficulty,
            "bonus_dice": bonus_dice,
            "penalty_dice": penalty_dice,
            "pushed": pushed,
            "rolled": outcome.rolled,
            "success": outcome.success,
            "success_rank": outcome.success_rank,
            "critical": outcome.critical,
            "fumble": outcome.fumble,
            "roll": outcome.rendered,
            "total": outcome.rolled,
        }

    def _execute_coc_sanity_check(self, action: RuleAction) -> dict[str, object]:
        # Extract parameters
        current_san = int(action.parameters.get("current_san", 0))
        max_san = int(action.parameters.get("max_san", current_san))
        bonus_dice = int(action.parameters.get("bonus_dice", 0))
        penalty_dice = int(action.parameters.get("penalty_dice", 0))
        loss_on_success_str = str(action.parameters.get("loss_on_success", "0"))
        loss_on_failure_str = str(action.parameters.get("loss_on_failure", "1"))
        encounter_type = str(action.parameters.get("encounter_type", ""))
        luck_available = int(action.parameters.get("luck_available", 0))

        # Roll dice expressions for sanity loss
        loss_on_success = (
            d20.roll(loss_on_success_str).total
            if isinstance(loss_on_success_str, str)
            and not loss_on_success_str.isdigit()
            else int(loss_on_success_str)
        )
        loss_on_failure = (
            d20.roll(loss_on_failure_str).total
            if isinstance(loss_on_failure_str, str)
            and not loss_on_failure_str.isdigit()
            else int(loss_on_failure_str)
        )

        if current_san <= 0:
            raise RulesEngineError("coc_sanity_check requires current_san")

        # Roll percentile
        outcome = self._roll_percentile(
            value=current_san,
            difficulty="regular",
            bonus_dice=bonus_dice,
            penalty_dice=penalty_dice,
            pushed=False,
        )

        # Call resolve_sanity_check with rolled value
        result = resolve_sanity_check(
            actor_name=action.actor.name,
            current_san=current_san,
            max_san=max_san,
            rolled=outcome.rolled,
            bonus_dice=bonus_dice,
            penalty_dice=penalty_dice,
            loss_on_success=loss_on_success,
            loss_on_failure=loss_on_failure,
            encounter_type=encounter_type,
        )

        # Build response dict
        san_loss_str = loss_on_success_str if outcome.success else loss_on_failure_str
        response = {
            "action": "coc_sanity_check",
            "actor": action.actor.name,
            "current_san": current_san,
            "max_san": max_san,
            "rolled": outcome.rolled,
            "success": outcome.success,
            "success_rank": outcome.success_rank,
            "critical": outcome.rolled == 1,
            "fumble": outcome.rolled == 100,
            "roll": outcome.rendered,
            "total": outcome.rolled,
            "san_loss": san_loss_str,
            "san_loss_value": result.sanity_loss,
            "sanity_loss": result.sanity_loss,  # PR test compat
            "mythos_gain": result.mythos_gain,
            "loss_on_success": loss_on_success,
            "loss_on_failure": loss_on_failure,
            "luck_spent": 0,
            "luck_explanation": "",
        }

        # Add insanity info if triggered
        if result.insanity_triggered != InsanityType.NONE:
            response["insanity_triggered"] = result.insanity_triggered.value
            if result.insanity_triggered == InsanityType.TEMPORARY:
                # Need to get insanity break details - call roll_insanity_break again to get details
                insanity_break = roll_insanity_break(
                    action.actor.name,
                    max(0, current_san - result.sanity_loss),
                    max_san,
                    f"SAN检定: {encounter_type}",
                )
                response["acute_response"] = insanity_break.acute_response
                response["duration_rounds"] = insanity_break.duration_rounds
            else:  # INDEFINITE
                insanity_break = roll_insanity_break(
                    action.actor.name, 0, max_san, f"SAN归零: {encounter_type}"
                )
                response["acquired_phobia"] = insanity_break.acquired_phobia
                response["acquired_mania"] = insanity_break.acquired_mania

        # Handle Luck expenditure for failed checks
        if luck_available > 0 and not result.success:
            luck_spent, adjusted_loss, luck_explanation = spend_luck_for_sanity(
                actor_name=action.actor.name,
                current_san=current_san,
                max_san=max_san,
                luck_available=luck_available,
                sanity_loss=result.sanity_loss,
                rolled=outcome.rolled,
            )
            if luck_spent > 0:
                result.sanity_loss = adjusted_loss
                response["luck_spent"] = luck_spent
                response["luck_explanation"] = luck_explanation
                response["sanity_loss"] = adjusted_loss
                response["roll"] += f"\n{luck_explanation}"

        return response

    def _build_combatant_stats(self, actor, params: dict) -> CombatantStats:
        """Build CombatantStats from actor and parameters dict."""
        return CombatantStats(
            name=actor.name,
            dex=int(params.get("dex", 0)),
            fighting=int(params.get("fighting", 0)),
            shooting=int(params.get("shooting", 0)),
            brawl=int(params.get("brawl", 0)),
            dodge=int(params.get("dodge", 0)),
            grapple=int(params.get("grapple", 0)),
            hp=int(params.get("hp", 0)),
            hp_max=int(params.get("hp_max", 0)),
            armor=int(params.get("armor", 0)),
            armor_piercing=bool(params.get("armor_piercing", False)),
            build=int(params.get("build", 0)),
            damage_bonus=int(params.get("damage_bonus", 0)),
            weapon_name=str(params.get("weapon_name", "")),
            weapon_type=params.get("weapon_type", "melee"),
            weapon_damage=str(params.get("weapon_damage", "")),
        )

    def _build_target_stats(self, params: dict) -> CombatantStats:
        """Build CombatantStats for target from parameters with target_ prefix."""
        target_name = params.get("target_name", "target")
        return CombatantStats(
            name=target_name,
            dex=int(params.get("target_dex", 0)),
            fighting=int(params.get("target_fighting", 0)),
            shooting=int(params.get("target_shooting", 0)),
            brawl=int(params.get("target_brawl", 0)),
            dodge=int(params.get("target_dodge", 0)),
            grapple=int(params.get("target_grapple", 0)),
            hp=int(params.get("target_hp", 0)),
            hp_max=int(params.get("target_hp_max", 0)),
            armor=int(params.get("target_armor", 0)),
            armor_piercing=bool(params.get("target_armor_piercing", False)),
            build=int(params.get("target_build", 0)),
            damage_bonus=int(params.get("target_damage_bonus", 0)),
            weapon_name=str(params.get("target_weapon_name", "")),
            weapon_type=params.get("target_weapon_type", "melee"),
            weapon_damage=str(params.get("target_weapon_damage", "")),
        )

    def _roll_raw_percentile(self) -> int:
        """Roll 1d100 for combat checks."""
        outcome = self._dice_roller.roll_percentile(
            value=0, difficulty="regular", bonus_dice=0, penalty_dice=0
        )
        if isinstance(outcome, dict):
            return outcome["rolled"]
        return outcome.rolled

    def _execute_coc_fighting_attack(self, action: RuleAction) -> dict[str, object]:
        """Execute a Fighting attack (opposed check vs Dodge)."""
        actor_stats = self._build_combatant_stats(action.actor, action.parameters)
        target_stats = self._build_target_stats(action.parameters)
        attacker_roll = self._roll_raw_percentile()
        defender_roll = self._roll_raw_percentile()
        result = resolve_fighting_attack(
            actor_stats, target_stats, attacker_roll, defender_roll
        )
        return result.model_dump()

    def _execute_coc_shooting_attack(self, action: RuleAction) -> dict[str, object]:
        """Execute a Shooting attack."""
        actor_stats = self._build_combatant_stats(action.actor, action.parameters)
        target_stats = self._build_target_stats(action.parameters)
        attacker_roll = self._roll_raw_percentile()
        range_modifier = int(action.parameters.get("range_modifier", 0))
        recoil_modifier = int(action.parameters.get("recoil_modifier", 0))
        result = resolve_shooting_attack(
            actor_stats, target_stats, attacker_roll, range_modifier, recoil_modifier
        )
        return result.model_dump()

    def _execute_coc_brawl_attack(self, action: RuleAction) -> dict[str, object]:
        """Execute a Brawl (unarmed) attack."""
        actor_stats = self._build_combatant_stats(action.actor, action.parameters)
        target_stats = self._build_target_stats(action.parameters)
        attacker_roll = self._roll_raw_percentile()
        defender_roll = self._roll_raw_percentile()
        result = resolve_brawl_attack(
            actor_stats, target_stats, attacker_roll, defender_roll
        )
        return result.model_dump()

    def _execute_coc_dodge(self, action: RuleAction) -> dict[str, object]:
        """Execute a Dodge (defensive action)."""
        actor_stats = self._build_combatant_stats(action.actor, action.parameters)
        target_stats = self._build_target_stats(action.parameters)
        attacker_roll = self._roll_raw_percentile()
        defender_roll = self._roll_raw_percentile()
        # Dodge is defensive - swap roles
        result = resolve_fighting_attack(
            target_stats, actor_stats, defender_roll, attacker_roll
        )
        result.action = CombatAction.DODGE
        return result.model_dump()

    def _execute_coc_grapple_attack(self, action: RuleAction) -> dict[str, object]:
        """Execute a Grapple attack."""
        actor_stats = self._build_combatant_stats(action.actor, action.parameters)
        target_stats = self._build_target_stats(action.parameters)
        attacker_roll = self._roll_raw_percentile()
        defender_roll = self._roll_raw_percentile()
        result = resolve_grapple_attack(
            actor_stats, target_stats, attacker_roll, defender_roll
        )
        return result.model_dump()

    def _execute_coc_cast_spell(self, action: RuleAction) -> dict[str, object]:
        """Execute a spell casting attempt."""
        # Extract caster parameters
        spell_key = str(action.parameters.get("spell_key", ""))
        caster_int = int(action.parameters.get("caster_int", 0))
        caster_pow = int(action.parameters.get("caster_pow", 0))
        caster_spellcast = int(action.parameters.get("caster_spellcast", 0))
        caster_cthulhu_mythos = int(action.parameters.get("caster_cthulhu_mythos", 0))
        caster_mp = int(action.parameters.get("caster_mp", 0))
        caster_max_mp = int(action.parameters.get("caster_max_mp", caster_mp))
        bonus_dice = int(action.parameters.get("bonus_dice", 0))
        penalty_dice = int(action.parameters.get("penalty_dice", 0))

        if not spell_key:
            raise RulesEngineError("coc_cast_spell requires spell_key")

        # Roll percentile for casting
        rolled = self._roll_raw_percentile()

        # Call resolve_spell_cast
        result = resolve_spell_cast(
            spell_key=spell_key,
            caster_name=action.actor.name,
            caster_int=caster_int,
            caster_pow=caster_pow,
            caster_spellcast=caster_spellcast,
            caster_cthulhu_mythos=caster_cthulhu_mythos,
            caster_mp=caster_mp,
            caster_max_mp=caster_max_mp,
            rolled=rolled,
            bonus_dice=bonus_dice,
            penalty_dice=penalty_dice,
        )

        # Build response dict
        response = result.model_dump()
        response["action"] = "coc_cast_spell"
        return response

    def roll_initiative(self, combatants: list[tuple[str, int]]) -> list[dict]:
        """Roll initiative for combatants using COC7 DEX×2 + 1d100.

        Args:
            combatants: List of (character_name, dex_value) tuples

        Returns:
            List of dicts with name, dex, initiative_roll, initiative_total
        """
        results = []
        for name, dex in combatants:
            initiative_base = dex * 2  # COC7: DEX × 2
            roll = self._roll_raw_percentile()
            total = initiative_base + roll
            results.append(
                {
                    "name": name,
                    "dex": dex,
                    "initiative_roll": roll,
                    "initiative_total": total,
                }
            )
        # Sort descending by total
        results.sort(key=lambda x: x["initiative_total"], reverse=True)
        return results

    def _roll(self, expression: str, *, advantage: str = "none") -> DiceOutcome:
        try:
            return self._dice_roller.roll(expression, advantage=advantage)
        except Exception as exc:
            raise RulesEngineError(str(exc)) from exc

    def _roll_percentile(
        self,
        *,
        value: int,
        difficulty: str,
        bonus_dice: int,
        penalty_dice: int,
        pushed: bool,
    ):
        try:
            outcome = self._dice_roller.roll_percentile(
                value=value,
                difficulty=difficulty,
                bonus_dice=bonus_dice,
                penalty_dice=penalty_dice,
                pushed=pushed,
            )
        except TypeError:
            outcome = self._dice_roller.roll_percentile(
                value=value,
                difficulty=difficulty,
                bonus_dice=bonus_dice,
                penalty_dice=penalty_dice,
            )
        if isinstance(outcome, dict):
            return PercentileOutcome.model_validate(outcome)
        return outcome


class _LegacyDiceRoller:
    def __init__(self, resolver: Callable[[str], int] | None) -> None:
        self._resolver = resolver or (lambda expr: 10)

    def roll(self, expression: str, *, advantage: str = "none") -> DiceOutcome:
        total = int(self._resolve_expression(expression))
        return DiceOutcome(
            expression=expression,
            total=total,
            rendered=f"{expression} = `{total}`",
        )

    def roll_percentile(
        self,
        *,
        value: int,
        difficulty: str = "regular",
        bonus_dice: int = 0,
        penalty_dice: int = 0,
        pushed: bool = False,
    ) -> dict[str, object]:
        rolled = max(1, min(100, int(self._resolver("1d100"))))
        thresholds = {
            "regular": value,
            "hard": value // 2,
            "extreme": value // 5,
        }
        success = rolled <= thresholds[difficulty]
        rank = "failure"
        if success:
            if rolled <= thresholds["extreme"]:
                rank = "extreme"
            elif rolled <= thresholds["hard"]:
                rank = "hard"
            else:
                rank = "regular"
        return {
            "value": value,
            "difficulty": difficulty,
            "rolled": rolled,
            "success": success,
            "success_rank": rank,
            "critical": rolled == 1,
            "fumble": rolled == 100,
            "bonus_dice": bonus_dice,
            "penalty_dice": penalty_dice,
            "pushed": pushed,
            "rendered": f"{rolled:02d} / {value}",
        }

    def _resolve_expression(self, expression: str) -> int:
        if expression.startswith("1d20+") or expression.startswith("1d20-"):
            modifier = int(expression[4:])
            return int(self._resolver("1d20")) + modifier
        return int(self._resolver(expression))
