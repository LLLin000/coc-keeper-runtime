"""COC 7th Edition Combat System

Complete combat resolution including:
- Initiative (DEX-based)
- Fighting, Shooting, Dodge, Brawl, Grapple
- Damage with DB (Damage Bonus)
- Armor and armor piercing
- Critical hits and impales
- Fumbles

Reference: Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 7
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


# =============================================================================
# Combat Constants
# =============================================================================


# Combat action types
class CombatAction(StrEnum):
    """Types of combat actions."""

    FIGHT = "fighting"
    SHOOT = "shooting"
    BRAWL = "brawl"
    DODGE = "dodge"
    GRAPPLE = "grapple"
    THROW = "throw"
    RETREAT = "retreat"
    GUARD = "guard"
    RELOAD = "reload"
    SWITCH_WEAPON = "switch_weapon"
    USE_ITEM = "use_item"


# Weapon types
class WeaponType(StrEnum):
    """Weapon categories."""

    MELEE = "melee"  # Fists, knives, swords, etc.
    RANGED = "ranged"  # Guns, bows, etc.
    THROWN = "thrown"  # Thrown weapons


# =============================================================================
# Combatant Model
# =============================================================================


class CombatantStats(BaseModel):
    """Stats relevant for combat."""

    name: str
    dex: int  # Dexterity for initiative
    fighting: int = 0
    shooting: int = 0
    brawl: int = 0
    dodge: int = 0
    grapple: int = 0
    throw: int = 0
    hp: int
    hp_max: int
    armor: int = 0  # Armor points
    armor_piercing: bool = False
    build: int = 0
    damage_bonus: int = 0  # Numeric part only (e.g., 4 from "+1d4")
    major_wound_threshold: int = Field(default=0)  # HP ≤ 0 = major wound

    # Optional weapon stats
    weapon_name: str = ""
    weapon_type: WeaponType = WeaponType.MELEE
    weapon_damage: str = ""  # e.g., "1d6+DB"
    weapon_range: str = ""  # e.g., "10m", "50m"
    weapon_attack_skill: int = 0  # Skill value to use for attacks
    weapon_hardpoint: int = 0  # For firearms
    weapon_recoil: int = 0  # For automatic weapons


# =============================================================================
# Initiative System
# =============================================================================


def roll_initiative(dex_value: int) -> int:
    """Roll initiative based on DEX.

    COC 7th Edition: Initiative = DEX × 2 (round down)
    Roll 1d100 and compare to initiative value.

    Args:
        dex_value: The character's DEX attribute (typically 1-100)

    Returns:
        Initiative roll result (1-100)
    """
    import random

    return random.randint(1, 100)


def get_initiative_order(
    combatants: list[tuple[str, int]],
) -> list[tuple[str, int, int]]:
    """Determine combat initiative order.

    Args:
        combatants: List of (name, dex_value) tuples

    Returns:
        List of (name, dex_value, initiative_roll) tuples, sorted by initiative
    """
    import random

    results = []
    for name, dex in combatants:
        initiative_base = dex * 2  # COC 7e: DEX × 2
        roll = random.randint(1, 100)
        total = initiative_base + roll
        results.append((name, dex, total))

    # Sort by initiative total descending
    results.sort(key=lambda x: x[2], reverse=True)
    return results


# =============================================================================
# Combat Resolution
# =============================================================================


class CombatCheckResult(BaseModel):
    """Result of a combat action check."""

    action: CombatAction
    actor_name: str
    target_name: str
    actor_skill_value: int
    target_skill_value: int = 0
    rolled: int
    success: bool
    success_rank: str = "failure"
    critical: bool = False
    fumble: bool = False
    damage: int = 0
    damage_roll: str = ""
    damage_bonus: int = 0
    armor_absorbed: int = 0
    penetration: int = 0
    final_damage: int = 0
    impale: bool = False
    major_wound: bool = False
    target_hp_before: int = 0
    target_hp_after: int = 0
    rendered: str = ""


def resolve_fighting_attack(
    attacker: CombatantStats,
    defender: CombatantStats,
    attacker_roll: int,
    defender_roll: int,
) -> CombatCheckResult:
    """Resolve a Fighting attack vs Dodge.

    Fighting is an opposed check:
    - Attacker rolls Fighting vs defender's Dodge
    - Success means hit; compare rolled values for degree

    Args:
        attacker: Attacker's combat stats
        defender: Defender's combat stats
        attacker_roll: Attacker's roll (1-100)
        defender_roll: Defender's roll (1-100)

    Returns:
        CombatCheckResult with full resolution
    """
    # Check for fumble/critical
    attacker_critical = attacker_roll == 1
    defender_critical = defender_roll == 1
    attacker_fumble = attacker_roll == 100 or (
        attacker.fighting >= 50 and attacker_roll >= 96
    )
    defender_fumble = defender_roll == 100 or (
        defender.dodge >= 50 and defender_roll >= 96
    )

    # Determine success
    if attacker_critical:
        success = True
        rank = "critical"
    elif defender_critical:
        success = False
        rank = "defender_critical"
    elif attacker_fumble:
        success = False
        rank = "fumble"
    elif defender_fumble:
        success = True
        rank = "defender_fumble"
    else:
        # Normal opposed check - compare who rolled lower (better)
        # Attacker success if their roll is lower than defender's roll
        success = attacker_roll < defender_roll
        diff = abs(attacker_roll - defender_roll)

        if diff <= 5:
            rank = "regular"
        elif diff <= 15:
            rank = "hard"
        elif diff <= 30:
            rank = "extreme"
        else:
            rank = "regular"

        if not success:
            rank = "failure"

    # Calculate damage if hit
    damage = 0
    damage_roll_str = ""
    final_damage = 0
    impale = False
    major_wound = False
    armor_absorbed = 0
    penetration = 0

    if success and not defender_critical:
        # Calculate damage: STR + SIZ + DB + weapon damage
        # Base damage from attributes
        base_damage = (attacker.build + 1) * 5  # Build affects damage
        db_value = attacker.damage_bonus

        # Roll weapon damage if specified
        if attacker.weapon_damage:
            import d20

            weapon_result = d20.roll(
                attacker.weapon_damage.replace("DB", str(db_value))
            )
            damage = weapon_result.total
        else:
            # Default unarmed: 1d3 + DB
            import d20

            unarmed_result = d20.roll(f"1d3+{db_value}")
            damage = unarmed_result.total

        damage_roll_str = f"{attacker.weapon_damage or '1d3'}+DB({db_value})"

        # Check for impale (Fighting only, on extreme+ success with weapon)
        if rank in ("extreme", "critical") and attacker.weapon_type == WeaponType.MELEE:
            impale = True
            # Impale: max damage + roll again
            import d20

            extra_damage = d20.roll(f"1d6+{db_value}")
            damage += extra_damage.total
            damage_roll_str += f" [impale: +1d6+{db_value}]"

        # Armor penetration
        if attacker.armor_piercing:
            penetration = 0  # Full armor works
        else:
            # Reduce damage by armor
            penetration = max(0, damage - defender.armor)
            armor_absorbed = damage - penetration

        final_damage = max(0, penetration)

        # Check for major wound (damage > HP remaining triggers major wound)
        if defender.hp - final_damage <= 0:
            major_wound = True

    # Build result
    target_hp_after = defender.hp - final_damage if success else defender.hp

    rendered = (
        f"【格斗攻击】{attacker.name} vs {defender.name}\n"
        f"攻击: {attacker_roll:02d} (格斗 {attacker.fighting}) | "
        f"防御: {defender_roll:02d} (闪避 {defender.dodge})\n"
        f"结果: {rank.upper()} | {'命中' if success else '未命中'}\n"
    )

    if success and final_damage > 0:
        rendered += (
            f"伤害: {damage} (防具吸收 {armor_absorbed}) → 最终 {final_damage}\n"
            f"目标HP: {defender.hp} → {target_hp_after}"
        )
        if impale:
            rendered += " | 穿刺！"
        if major_wound:
            rendered += " | 重伤！"

    return CombatCheckResult(
        action=CombatAction.FIGHT,
        actor_name=attacker.name,
        target_name=defender.name,
        actor_skill_value=attacker.fighting,
        target_skill_value=defender.dodge,
        rolled=attacker_roll,
        success=success,
        success_rank=rank,
        critical=attacker_critical or attacker_roll == 1,
        fumble=attacker_fumble,
        damage=damage,
        damage_roll=damage_roll_str,
        damage_bonus=attacker.damage_bonus,
        armor_absorbed=armor_absorbed,
        penetration=penetration,
        final_damage=final_damage,
        impale=impale,
        major_wound=major_wound,
        target_hp_before=defender.hp,
        target_hp_after=target_hp_after,
        rendered=rendered,
    )


def resolve_shooting_attack(
    attacker: CombatantStats,
    defender: CombatantStats,
    attacker_roll: int,
    range_modifier: int = 0,
    recoil_modifier: int = 0,
) -> CombatCheckResult:
    """Resolve a Shooting attack.

    Args:
        attacker: Attacker's combat stats
        defender: Defender's combat stats
        attacker_roll: Attacker's roll (1-100)
        range_modifier: Range penalty (positive = harder)
        recoil_modifier: Recoil penalty for automatic weapons

    Returns:
        CombatCheckResult with full resolution
    """
    # Effective difficulty
    effective_difficulty = attacker.shooting - range_modifier - recoil_modifier

    # Check for fumble/critical
    critical = attacker_roll == 1
    fumble = attacker_roll == 100 or (attacker.shooting >= 50 and attacker_roll >= 96)

    if critical:
        success = True
        rank = "critical"
    elif fumble:
        success = False
        rank = "fumble"
    else:
        # Success if roll ≤ effective skill
        success = attacker_roll <= effective_difficulty
        if success:
            if attacker_roll <= attacker.shooting // 5:
                rank = "extreme"
            elif attacker_roll <= attacker.shooting // 2:
                rank = "hard"
            else:
                rank = "regular"
        else:
            rank = "failure"

    # Calculate damage
    damage = 0
    damage_roll_str = ""
    final_damage = 0
    major_wound = False
    armor_absorbed = 0
    penetration = 0

    if success:
        # Roll weapon damage
        if attacker.weapon_damage:
            import d20

            db_value = attacker.damage_bonus
            damage_expr = attacker.weapon_damage.replace("DB", str(db_value))
            damage_result = d20.roll(damage_expr)
            damage = damage_result.total
            damage_roll_str = damage_expr
        else:
            damage = 0

        # Armor penetration
        if attacker.armor_piercing:
            penetration = damage
        else:
            penetration = max(0, damage - defender.armor)
            armor_absorbed = damage - penetration

        final_damage = max(0, penetration)

        # Major wound check
        if defender.hp - final_damage <= 0:
            major_wound = True

    target_hp_after = defender.hp - final_damage if success else defender.hp

    rendered = (
        f"【射击攻击】{attacker.name} → {defender.name}\n"
        f"攻击: {attacker_roll:02d} (射击 {attacker.shooting})"
    )
    if range_modifier or recoil_modifier:
        rendered += f" [射程{-range_modifier}, 后座力{-recoil_modifier}]"
    rendered += f"\n结果: {rank.upper()} | {'命中' if success else '未命中'}\n"

    if success and final_damage > 0:
        rendered += (
            f"伤害: {damage} (防具吸收 {armor_absorbed}) → 最终 {final_damage}\n"
            f"目标HP: {defender.hp} → {target_hp_after}"
        )
        if major_wound:
            rendered += " | 重伤！"

    return CombatCheckResult(
        action=CombatAction.SHOOT,
        actor_name=attacker.name,
        target_name=defender.name,
        actor_skill_value=attacker.shooting,
        target_skill_value=0,
        rolled=attacker_roll,
        success=success,
        success_rank=rank,
        critical=critical,
        fumble=fumble,
        damage=damage,
        damage_roll=damage_roll_str,
        damage_bonus=attacker.damage_bonus,
        armor_absorbed=armor_absorbed,
        penetration=penetration,
        final_damage=final_damage,
        impale=False,
        major_wound=major_wound,
        target_hp_before=defender.hp,
        target_hp_after=target_hp_after,
        rendered=rendered,
    )


def resolve_brawl_attack(
    attacker: CombatantStats,
    defender: CombatantStats,
    attacker_roll: int,
    defender_roll: int,
) -> CombatCheckResult:
    """Resolve a Brawl (unarmed) attack.

    Similar to Fighting but with different damage:
    - 1d3 + DB damage (no weapon)
    - Cannot impale

    Args:
        attacker: Attacker's combat stats
        defender: Defender's combat stats
        attacker_roll: Attacker's roll (1-100)
        defender_roll: Defender's roll (1-100)

    Returns:
        CombatCheckResult with full resolution
    """
    # Same as Fighting but without impale
    result = resolve_fighting_attack(attacker, defender, attacker_roll, defender_roll)
    result.action = CombatAction.BRAWL

    # Override damage - Brawl is always 1d3 + DB
    if result.success:
        import d20

        db_value = attacker.damage_bonus
        damage_result = d20.roll(f"1d3+{db_value}")
        result.damage = damage_result.total
        result.damage_roll = f"1d3+DB({db_value})"

        # Recalculate final damage
        penetration = max(0, result.damage - defender.armor)
        result.armor_absorbed = result.damage - penetration
        result.final_damage = max(0, penetration)
        result.target_hp_after = defender.hp - result.final_damage

        if result.target_hp_after <= 0:
            result.major_wound = True

    return result


def resolve_grapple_attack(
    attacker: CombatantStats,
    defender: CombatantStats,
    attacker_roll: int,
    defender_roll: int,
) -> CombatCheckResult:
    """Resolve a Grapple attack.

    Grapple is an opposed check:
    - Attacker rolls Grapple vs defender's Grapple or Dodge
    - Success means defender is grappled

    Args:
        attacker: Attacker's combat stats
        defender: Defender's combat stats
        attacker_roll: Attacker's roll (1-100)
        defender_roll: Defender's roll (1-100)

    Returns:
        CombatCheckResult with grapple-specific resolution
    """
    # Check for fumble/critical
    attacker_critical = attacker_roll == 1
    defender_critical = defender_roll == 1
    attacker_fumble = attacker_roll == 100 or (
        attacker.grapple >= 50 and attacker_roll >= 96
    )
    defender_fumble = defender_roll == 100 and defender.grapple >= 50

    if attacker_critical:
        success = True
        rank = "critical"
    elif defender_critical:
        success = False
        rank = "defender_critical"
    elif attacker_fumble:
        success = False
        rank = "fumble"
        # Fumble on grapple - attacker hurts themselves
        import d20

        self_damage = d20.roll("1d6").total
        attacker_hp_after = attacker.hp - self_damage
    elif defender_fumble:
        success = True
        rank = "defender_fumble"
    else:
        # Normal opposed check
        success = attacker_roll < defender_roll
        if success:
            if abs(attacker_roll - defender_roll) <= 10:
                rank = "regular"
            else:
                rank = "hard"
        else:
            rank = "failure"

    rendered = (
        f"【摔跤攻击】{attacker.name} vs {defender.name}\n"
        f"攻击: {attacker_roll:02d} (摔跤 {attacker.grapple}) | "
        f"防御: {defender_roll:02d} (摔跤 {defender.grapple} / 闪避 {defender.dodge})\n"
        f"结果: {rank.upper()} | {'成功' if success else '失败'}\n"
    )

    if attacker_fumble:
        rendered += f"笨拙！攻击者自伤: {self_damage} HP"

    result = CombatCheckResult(
        action=CombatAction.GRAPPLE,
        actor_name=attacker.name,
        target_name=defender.name,
        actor_skill_value=attacker.grapple,
        target_skill_value=max(defender.grapple, defender.dodge),
        rolled=attacker_roll,
        success=success,
        success_rank=rank,
        critical=attacker_critical,
        fumble=attacker_fumble,
        damage=0,
        major_wound=False,
        target_hp_before=defender.hp,
        target_hp_after=defender.hp,
        rendered=rendered,
    )

    if attacker_fumble:
        result.damage = self_damage
        result.target_hp_after = attacker.hp - self_damage

    return result


# =============================================================================
# Damage Bonus Calculator
# =============================================================================


def calculate_build(str_value: int, siz_value: int) -> int:
    """Calculate Build from STR + SIZ.

    COC 7th Edition Build:
    - STR + SIZ < 65: Build -2
    - 65-84: Build -1
    - 85-124: Build 0
    - 125-164: Build 1
    - 165-204: Build 2
    - 205+: Build 3

    Args:
        str_value: Character's STR attribute
        siz_value: Character's SIZ attribute

    Returns:
        Build value (-2 to 3)
    """
    total = str_value + siz_value
    if total < 65:
        return -2
    elif total < 85:
        return -1
    elif total < 125:
        return 0
    elif total < 165:
        return 1
    elif total < 205:
        return 2
    else:
        return 3


def calculate_damage_bonus(str_value: int, siz_value: int) -> int:
    """Calculate Damage Bonus (DB) from STR + SIZ.

    COC 7th Edition DB:
    - STR + SIZ < 65: DB -2
    - 65-84: DB -1
    - 85-124: DB 0
    - 125-164: DB +1d4
    - 165-204: DB +1d6
    - 205+: DB +2d6

    Returns:
        Damage bonus as integer (the dice is rolled separately)
    """
    total = str_value + siz_value
    if total < 65:
        return -2
    elif total < 85:
        return -1
    elif total < 125:
        return 0
    elif total < 165:
        return 1  # +1d4
    elif total < 205:
        return 2  # +1d6
    else:
        return 3  # +2d6


def get_damage_bonus_string(str_value: int, siz_value: int) -> str:
    """Get damage bonus as a dice expression string.

    Returns:
        Damage bonus string like "+1d4", "-1", or "+2d6"
    """
    db = calculate_damage_bonus(str_value, siz_value)
    if db <= 0:
        return str(db)
    elif db == 1:
        return "+1d4"
    elif db == 2:
        return "+1d6"
    else:
        return "+2d6"


# =============================================================================
# Range Modifiers for Shooting
# =============================================================================

RANGE_MODIFIERS: dict[str, int] = {
    "point_blank": 0,  # Adjacent
    "close": -20,  # Within comfortable range
    "normal": 0,  # Normal range
    "long": 20,  # At upper limit
    "extreme": 40,  # Beyond normal range
}


def get_range_modifier(weapon_range: str, actual_distance: int) -> int:
    """Calculate range penalty for shooting.

    Args:
        weapon_range: Weapon's maximum effective range in meters
        actual_distance: Actual distance to target in meters

    Returns:
        Modifier (positive = harder check)
    """
    if actual_distance <= weapon_range * 0.5:
        return RANGE_MODIFIERS["close"]
    elif actual_distance <= weapon_range:
        return RANGE_MODIFIERS["normal"]
    elif actual_distance <= weapon_range * 1.5:
        return RANGE_MODIFIERS["long"]
    else:
        return RANGE_MODIFIERS["extreme"]
