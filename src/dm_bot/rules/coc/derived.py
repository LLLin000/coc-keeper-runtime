"""COC 7th Edition Derived Attributes

Complete derived attribute calculations:
- Luck (POW × 5)
- Hit Points ((CON + SIZ) / 10)
- Magic Points (POW / 5)
- Movement Rate (based on STR/DEX/SIZ, affected by age)
- Build (based on STR + SIZ)
- Damage Bonus (based on STR + SIZ)
- Starting Sanity (POW × 5)

Reference: Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 2
"""

import random

from pydantic import BaseModel

from dm_bot.characters.models import COCAttributes


# =============================================================================
# Derived Attribute Calculations
# =============================================================================


def calculate_luck(pow_value: int) -> int:
    """Calculate Luck from POW.

    COC7e: Luck = POW × 5

    Args:
        pow_value: Character's POW attribute

    Returns:
        Luck value
    """
    return pow_value * 5


def calculate_hp(con_value: int, siz_value: int) -> int:
    """Calculate Hit Points from CON and SIZ.

    COC7e: HP = (CON + SIZ) / 10 (round down)

    Args:
        con_value: Character's CON attribute
        siz_value: Character's SIZ attribute

    Returns:
        Maximum Hit Points
    """
    return (con_value + siz_value) // 10


def calculate_mp(pow_value: int) -> int:
    """Calculate Magic Points from POW.

    COC7e: MP = POW / 5 (round down)

    Args:
        pow_value: Character's POW attribute

    Returns:
        Maximum Magic Points
    """
    return pow_value // 5


def calculate_sanity(pow_value: int) -> int:
    """Calculate starting Sanity from POW.

    COC7e: Starting SAN = POW × 5

    Args:
        pow_value: Character's POW attribute

    Returns:
        Starting Sanity
    """
    return pow_value * 5


def calculate_move_rate(
    str_value: int,
    dex_value: int,
    siz_value: int,
    age: int = 0,
) -> int:
    """Calculate Movement Rate from STR, DEX, SIZ, and age.

    COC7e MOV calculation:
    - If STR < SIZ and DEX < SIZ: MOV = 7
    - If STR > SIZ and DEX > SIZ: MOV = 9
    - Otherwise: MOV = 8
    - Age 40-49: -1
    - Age 50-59: -2
    - Age 60-69: -3
    - Age 70+: -4

    Args:
        str_value: Character's STR attribute
        dex_value: Character's DEX attribute
        siz_value: Character's SIZ attribute
        age: Character's age (affects MOV in older ages)

    Returns:
        Movement Rate
    """
    # Base MOV calculation
    if str_value < siz_value and dex_value < siz_value:
        base_mov = 7
    elif str_value > siz_value and dex_value > siz_value:
        base_mov = 9
    else:
        base_mov = 8

    # Age penalty
    if age >= 70:
        base_mov -= 4
    elif age >= 60:
        base_mov -= 3
    elif age >= 50:
        base_mov -= 2
    elif age >= 40:
        base_mov -= 1

    return max(5, base_mov)  # Minimum MOV is 5


def calculate_build(str_value: int, siz_value: int) -> int:
    """Calculate Build from STR + SIZ.

    COC7e Build:
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


def calculate_damage_bonus(str_value: int, siz_value: int) -> tuple[int, str]:
    """Calculate Damage Bonus from STR + SIZ.

    COC7e Damage Bonus:
    - STR + SIZ < 65: DB -2
    - 65-84: DB -1
    - 85-124: DB 0
    - 125-164: DB +1d4
    - 165-204: DB +1d6
    - 205+: DB +2d6

    Args:
        str_value: Character's STR attribute
        siz_value: Character's SIZ attribute

    Returns:
        Tuple of (numeric_db, dice_string)
        - numeric_db: The dice count (e.g., 1 for +1d4, 2 for +1d6)
        - dice_string: Human-readable like "+1d4" or "-1"
    """
    total = str_value + siz_value
    if total < 65:
        return -1, "-1"
    elif total < 85:
        return 0, "0"
    elif total < 125:
        return 0, "0"
    elif total < 165:
        return 1, "+1d4"
    elif total < 205:
        return 1, "+1d6"
    else:
        return 2, "+2d6"


def get_damage_bonus_dice_expression(str_value: int, siz_value: int) -> str:
    """Get the full damage bonus dice expression.

    Args:
        str_value: Character's STR attribute
        siz_value: Character's SIZ attribute

    Returns:
        Dice expression like "+1d4", "-1", or "+2d6"
    """
    _, dice_str = calculate_damage_bonus(str_value, siz_value)
    return dice_str


# =============================================================================
# Combined Derived Attributes
# =============================================================================


class DerivedAttributes(BaseModel):
    """All derived attributes for a COC character."""

    luck: int
    hp: int
    hp_max: int
    mp: int
    mp_max: int
    san: int
    san_max: int
    move_rate: int
    build: int
    damage_bonus: int  # Numeric part
    damage_bonus_str: str  # Display string


def calculate_all_derived_attributes(
    attributes: COCAttributes,
    age: int = 0,
) -> DerivedAttributes:
    """Calculate all derived attributes from base attributes.

    Args:
        attributes: Character's COCAttributes
        age: Character's age (affects MOV)

    Returns:
        DerivedAttributes with all calculated values
    """
    luck = calculate_luck(attributes.pow)
    hp = calculate_hp(attributes.con, attributes.siz)
    mp = calculate_mp(attributes.pow)
    san = calculate_sanity(attributes.pow)
    move_rate = calculate_move_rate(attributes.str, attributes.dex, attributes.siz, age)
    build = calculate_build(attributes.str, attributes.siz)
    db_numeric, db_str = calculate_damage_bonus(attributes.str, attributes.siz)

    return DerivedAttributes(
        luck=luck,
        hp=hp,
        hp_max=hp,
        mp=mp,
        mp_max=mp,
        san=san,
        san_max=san,
        move_rate=move_rate,
        build=build,
        damage_bonus=db_numeric,
        damage_bonus_str=db_str,
    )


# =============================================================================
# Age-Based Modifiers
# =============================================================================

AGE_MODIFIERS = {
    # Age: (STR, CON, DEX, APP, POW, INT, EDU)
    (20, 29): (0, 0, 0, 0, 0, 0, 0),
    (30, 39): (0, 0, 0, 0, 0, +1, +1),
    (40, 49): (-5, -10, -10, -10, 0, +2, +3),
    (50, 59): (-10, -15, -15, -15, 0, +3, +6),
    (60, 69): (-15, -20, -20, -20, 0, +4, +8),
    (70, 79): (-20, -25, -25, -25, 0, +5, +10),
    (80, 89): (-25, -30, -30, -30, 0, +6, +12),
    (90, 99): (-30, -35, -35, -35, 0, +7, +14),
}


def get_age_modifiers(age: int) -> dict[str, int]:
    """Get attribute modifiers due to age.

    Args:
        age: Character's age

    Returns:
        Dictionary of attribute modifiers
    """
    for (min_age, max_age), mods in AGE_MODIFIERS.items():
        if min_age <= age <= max_age:
            return {
                "str": mods[0],
                "con": mods[1],
                "dex": mods[2],
                "app": mods[3],
                "pow": mods[4],
                "int": mods[5],
                "edu": mods[6],
            }
    return {
        "str": 0,
        "con": 0,
        "dex": 0,
        "app": 0,
        "pow": 0,
        "int": 0,
        "edu": 0,
    }


def apply_age_modifiers(
    attributes: COCAttributes,
    age: int,
) -> COCAttributes:
    """Apply age modifiers to attributes.

    Args:
        attributes: Base COCAttributes
        age: Character's age

    Returns:
        Modified COCAttributes with age adjustments
    """
    mods = get_age_modifiers(age)
    return COCAttributes(
        str=max(1, attributes.str + mods["str"]),
        con=max(1, attributes.con + mods["con"]),
        dex=max(1, attributes.dex + mods["dex"]),
        app=max(1, attributes.app + mods["app"]),
        pow=max(1, attributes.pow + mods["pow"]),
        int=max(1, attributes.int + mods["int"]),
        edu=max(1, attributes.edu + mods["edu"]),
        siz=attributes.siz,
    )


# =============================================================================
# Characteristic Rolls (Rolling New Characters)
# =============================================================================


def roll_characteristic() -> int:
    """Roll a single characteristic (3d6).

    Returns:
        Characteristic value (3-18)
    """
    import random

    return sum(random.randint(1, 6) for _ in range(3))


def generate_characteristics() -> dict[str, int]:
    """Generate all seven characteristics by rolling 3d6 each.

    Returns:
        Dictionary of characteristic names to values
    """
    chars = {}
    for attr in ["str", "con", "dex", "app", "pow", "int", "edu"]:
        chars[attr] = roll_characteristic()

    # SIZ is rolled as 2d6+6 (2d6 + half of 12)
    chars["siz"] = sum(random.randint(1, 6) for _ in range(2)) + 6

    return chars


# =============================================================================
# Luck Points System
# =============================================================================


def spend_luck(
    current_luck: int,
    amount: int = 1,
) -> tuple[int, bool]:
    """Spend luck points for a re-roll.

    Args:
        current_luck: Current luck points available
        amount: Amount of luck to spend

    Returns:
        Tuple of (new_luck, success)
    """
    if current_luck < amount:
        return current_luck, False
    return current_luck - amount, True


def recover_luck(
    max_luck: int,
    current_luck: int,
    rest_periods: int = 0,
) -> int:
    """Recover luck points through rest.

    COC7e: Can recover 1 Luck point per full night's rest.

    Args:
        max_luck: Maximum luck (usually POW × 5)
        current_luck: Current luck
        rest_periods: Number of rest periods

    Returns:
        New current luck
    """
    recovered = min(rest_periods, max_luck - current_luck)
    return current_luck + recovered
