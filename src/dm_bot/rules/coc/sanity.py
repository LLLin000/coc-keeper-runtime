"""COC 7th Edition Sanity System

Complete sanity resolution including:
- Sanity loss from encounters (COC7 tables)
- Mythos Knowledge gains
- Temporary insanity (Acute trauma response)
- Indefinite insanity (Major psychological breaks)
- Phobia/Mania acquisition
- Sanity recovery through rest, therapy, real-world experiences
- Luck expenditure for avoiding sanity loss

Reference: Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 9
"""

from enum import StrEnum
from typing import Literal
import d20

from pydantic import BaseModel, Field


# =============================================================================
# Sanity Constants
# =============================================================================

# Starting sanity = POW × 5


# Sanity loss types
class SanityLossType(StrEnum):
    """Types of sanity loss."""

    UNKNOWN = "unknown"  # Lost without seeing source
    SEEN = "seen"  # Saw something terrible
    COMBAT = "combat"  # Violence inflicted/seen
    DEATH = "death"  # Death of loved one
    MYTHOS = "mythos"  # Cthulhu Mythos related


# Insanity types
class InsanityType(StrEnum):
    """Types of insanity."""

    NONE = "none"
    TEMPORARY = "temporary"  # Acute trauma response
    INDEFINITE = "indefinite"  # Major psychological break


# =============================================================================
# Phobia/Mania Definitions (COC7e)
# =============================================================================

COMMON_PHOBIAS = [
    "Astrapomancy (Star Wisdom)",
    "Belonephobia (Needles)",
    "Chaetophobia (Hair)",
    "Chronophobia (Time)",
    "Claustrophobia (Enclosed Spaces)",
    "Cynophobia (Dogs)",
    "Dementophobia (Insanity)",
    "Demonophobia (Demons)",
    "Dikephobia (Justice)",
    "Ecophobia (Home)",
    "Galeophobia (Sharks)",
    "Gamophobia (Marriage)",
    "Genuphobia (Knees)",
    "Graphophobia (Writing)",
    "Haptephobia (Touch)",
    "Hemophobia (Blood)",
    "Herpetophobia (Snakes)",
    "Hodophobia (Travel)",
    "Ichthyophobia (Fish)",
    "Kleptophobia (Stealing)",
    "Lachanophobia (Vegetables)",
    "Lepidophobia (Butterflies)",
    "Lyssophobia (Madness)",
    "Mageirocophobia (Cooking)",
    "Megalophobia (Large Objects)",
    "Misophobia (Germs)",
    "Musophobia (Mice)",
    "Necrophobia (Dead Bodies)",
    "Neophobia (New Things)",
    "Noctiphobia (Night)",
    "Nosophobia (Disease)",
    "Nyctophobia (Darkness)",
    "Odontophobia (Teeth)",
    "Ophidiophobia (Snakes)",
    "Ornithophobia (Birds)",
    "Parasitophobia (Parasites)",
    "Pathophobia (Disease)",
    "Pedophobia (Children)",
    "Philophobia (Love)",
    "Phonophobia (Voice)",
    "Piscophobia (Fish)",
    "Pogonophobia (Beards)",
    "Pyrophobia (Fire)",
    "Rugophobia (Wrinkles)",
    "Satanophobia (Satan)",
    "Sciophobia (Shadow)",
    "Siderodromophobia (Trains)",
    "Sitophobia (Food)",
    "Stygiophobia (Hell)",
    "Taphophobia (Graves)",
    "Technophobia (Technology)",
    "Tomophobia (Surgery)",
    "Toxophobia (Poison)",
    "Tremophobia (Trembling)",
    "Triskadekaphobia (13)",
    "Trypanophobia (Injections)",
    "Zoophobia (Animals)",
]

COMMON_MANIAS = [
    "Abasiophilia (Cripples)",
    "Absinthe Drinking",
    "Aichmomania (Needles/Points)",
    "Anthomania (Flowers)",
    " Bibliomania (Books)",
    "Bromidrosomania (Body Odor)",
    "Choreomania (Dancing)",
    "Cleptomania (Stealing)",
    "Cynomania (Dogs)",
    "Dipsomania (Drink)",
    "Doromania (Fur)",
    "Eccedentesiomania (Fake Smiles)",
    "Erotomania (Love)",
    "Escheatomania (Inheritance)",
    "Graphomania (Writing)",
    "Gynomania (Women)",
    "Hedonomania (Pleasure)",
    "Hippomania (Horses)",
    "Hypsomania (Insanity)",
    "Kleptomania (Stealing)",
    "Logomania (Words)",
    "Lygophilia (Broken Things)",
    "Melomania (Music)",
    "Mithasophobia (Friendship)",
    "Monomania (Single Idea)",
    "Musicomania (Music)",
    "Mythomania (Lying)",
    "Nosomania (Illness Delusion)",
    "Oniomania (Buying)",
    "Ophthalmomania (Eyes)",
    "Opium",
    "Parasitomania (Parasites)",
    "Phonomania (Voice)",
    "Pyromania (Fire)",
    "Satyromania (Sexual Desire)",
    "Suicide",
    "Taphomania (Graves)",
    "Thanatomania (Death)",
    "Theatre",
    "Toxomania (Poison)",
    "Trichomania (Hair)",
    "Xenomania (Foreigners)",
]


# =============================================================================
# Sanity Check Result
# =============================================================================


class SanityCheckResult(BaseModel):
    """Result of a sanity check."""

    actor_name: str
    current_san: int
    max_san: int
    rolled: int
    success: bool
    success_rank: str = "failure"
    sanity_loss: int = 0
    loss_type: SanityLossType = SanityLossType.UNKNOWN
    mythos_gain: int = 0  # Mythos knowledge gained on failure
    insanity_triggered: InsanityType = InsanityType.NONE
    phobia_or_mania: str = ""  # If acquired during breakdown
    temporary_insanity_duration: int = 0  # Rounds/minutes for acute
    luck_spent: int = 0  # Luck points used to reduce loss
    rendered: str = ""


# =============================================================================
# Sanity Loss Tables (COC 7e Reference)
# =============================================================================

# Standard sanity loss for various encounters (1d6 or fixed values)
# These are reference values - actual loss depends on encounter

SANITY_LOSS_REFERENCES: dict[str, tuple[int, int]] = {
    # Format: (min_loss, max_loss) or (fixed, fixed) if same
    # Creatures and monsters (COC7e Keeper's Rulebook)
    "mi_go": (1, 6),
    "deep_one": (1, 6),
    "ghoul": (1, 6),
    "ghost": (1, 6),
    "zombie": (1, 6),
    "mummy": (1, 6),
    "byakhee": (1, 6),
    "dimensional_shambler": (1, 6),
    "fire_vampire": (1, 6),
    "nightgaunt": (1, 6),
    "serpent_people": (1, 6),
    "shantak": (1, 6),
    "star_spawn": (1, 6),
    "ying": (1, 6),
    # Greater horrors
    "cthulhu": (1, 10),
    "hastur": (1, 10),
    "nyarlathotep": (1, 10),
    "yog_sothoth": (1, 10),
    "shub_niggurath": (1, 10),
    # Supernatural phenomena
    "eldritch_location": (0, 3),
    "ritual_horror": (1, 6),
    "book_of_shadows": (1, 6),
    # Violence and death
    "witness_death": (0, 3),
    "inflict_violence": (1, 3),
    "see_corpse": (1, 3),
    # Failed sanity check (pushed roll consequence)
    "sanity_check_failed": (1, 3),
}


# =============================================================================
# Mythos Knowledge Gains
# =============================================================================

MYTHOS_GAIN_REFERENCES: dict[str, int] = {
    # Fixed Mythos gains for various sources
    "cthulhu": 8,
    "hastur": 8,
    "nyarlathotep": 8,
    "yog_sothoth": 8,
    "shub_niggurath": 8,
    "book_of_shadows": 5,
    "tome_of_shadows": 10,
    "cursed_text": 3,
}


def get_mythos_gain_for_encounter(encounter_type: str) -> int:
    """Get Mythos knowledge gain for an encounter.

    Args:
        encounter_type: Type of mythos encounter

    Returns:
        Mythos gain percentage (0-99)
    """
    return MYTHOS_GAIN_REFERENCES.get(encounter_type, 1)


def get_sanity_loss_for_encounter(
    encounter_type: str, rolled_loss: int | None = None
) -> int:
    """Calculate sanity loss for an encounter.

    Args:
        encounter_type: Type of encounter
        rolled_loss: Pre-rolled loss value (for fixed rolls)

    Returns:
        Sanity loss amount
    """
    if encounter_type not in SANITY_LOSS_REFERENCES:
        return 1  # Default minimum

    min_loss, max_loss = SANITY_LOSS_REFERENCES[encounter_type]

    if rolled_loss is not None:
        return max(min_loss, min(max_loss, rolled_loss))

    # Would need to roll - return max for planning
    return max_loss


# =============================================================================
# Insanity Break & Recovery
# =============================================================================


class InsanityBreakResult(BaseModel):
    """Result of an insanity break."""

    actor_name: str
    insanity_type: InsanityType
    trigger_event: str

    # For temporary insanity
    acute_response: str = ""  # What the character does
    duration_rounds: int = 0  # For acute response

    # For indefinite insanity
    acquired_phobia: str = ""
    acquired_mania: str = ""
    indefinite_duration: str = "Indefinite"  # Until treated

    rendered: str = ""


ACUTE_TRAUMA_RESPONSES = [
    "Hysterical paralysis",
    "Panic-flee",
    "Violent outburst",
    "Catatonic stupor",
    "Confusion/disorientation",
    "Automatic hiding",
    "Fawning compliance",
    "Psychosomatic blindness",
    "Psychosomatic deafness",
    "Seizure",
    "Vomiting",
    "Fainting",
    "Heart attack symptoms",
]


def roll_insanity_break(
    actor_name: str,
    current_san: int,
    max_san: int,
    trigger_event: str,
) -> InsanityBreakResult:
    """Roll for insanity break when SAN reaches 0.

    COC7e: When SAN reaches 0, character becomes indefinitely insane.
    If SAN drops below (max_san / 5), temporary insanity may occur.

    Args:
        actor_name: Character name
        current_san: Current sanity points
        max_san: Maximum sanity points
        trigger_event: What triggered the break

    Returns:
        InsanityBreakResult with break details
    """
    import random

    # Determine insanity type
    # If SAN drops to 0: Indefinite insanity
    if current_san <= 0:
        insanity_type = InsanityType.INDEFINITE

        # Roll for acquired phobia/mania
        roll = random.randint(1, 100)
        if roll <= 50:
            acquired_phobia = random.choice(COMMON_PHOBIAS)
            acquired_mania = ""
        else:
            acquired_phobia = ""
            acquired_mania = random.choice(COMMON_MANIAS)

        result = InsanityBreakResult(
            actor_name=actor_name,
            insanity_type=insanity_type,
            trigger_event=trigger_event,
            acquired_phobia=acquired_phobia,
            acquired_mania=acquired_mania,
            rendered=(
                f"【不定性疯狂】{actor_name}\n"
                f"触发: {trigger_event}\n"
                f"SAN降至0！角色陷入不定性疯狂。\n"
            ),
        )
        if acquired_phobia:
            result.rendered += f"获得恐惧症: {acquired_phobia}"
        if acquired_mania:
            result.rendered += f"获得躁狂症: {acquired_mania}"

        return result

    # If SAN drops below (max_san / 5): Temporary insanity
    threshold = max_san // 5
    if current_san < threshold:
        insanity_type = InsanityType.TEMPORARY
        acute_response = random.choice(ACUTE_TRAUMA_RESPONSES)
        duration_rounds = random.randint(1, 10)

        return InsanityBreakResult(
            actor_name=actor_name,
            insanity_type=insanity_type,
            trigger_event=trigger_event,
            acute_response=acute_response,
            duration_rounds=duration_rounds,
            rendered=(
                f"【临时性疯狂】{actor_name}\n"
                f"触发: {trigger_event}\n"
                f"SAN低于{threshold}！角色遭受急性创伤反应。\n"
                f"反应: {acute_response}\n"
                f"持续: {duration_rounds}轮"
            ),
        )

    # SAN above threshold - no insanity
    return InsanityBreakResult(
        actor_name=actor_name,
        insanity_type=InsanityType.NONE,
        trigger_event=trigger_event,
        rendered=f"【理智检定】{actor_name} — SAN {current_san}/{max_san}，无需疯狂检定",
    )


# =============================================================================
# Sanity Check Resolution
# =============================================================================


def resolve_sanity_check(
    actor_name: str,
    current_san: int,
    max_san: int,
    rolled: int,
    bonus_dice: int = 0,
    penalty_dice: int = 0,
    loss_on_success: int = 0,
    loss_on_failure: int = 0,
    encounter_type: str = "",
) -> SanityCheckResult:
    """Resolve a sanity check.

    Args:
        actor_name: Character name
        current_san: Current sanity points
        max_san: Maximum sanity points
        rolled: The d100 roll result
        bonus_dice: Bonus dice (for favorable conditions)
        penalty_dice: Penalty dice (for unfavorable conditions)
        loss_on_success: Sanity loss if check succeeds
        loss_on_failure: Sanity loss if check fails
        encounter_type: Type of mythos encounter for reference

    Returns:
        SanityCheckResult with full outcome
    """
    import random

    # Apply bonus/penalty dice
    effective_roll = rolled
    if bonus_dice and not penalty_dice:
        # Keep lowest (best for player)
        pool = [rolled] + [random.randint(1, 100) for _ in range(bonus_dice)]
        effective_roll = min(pool)
    elif penalty_dice and not bonus_dice:
        # Keep highest (worst for player)
        pool = [rolled] + [random.randint(1, 100) for _ in range(penalty_dice)]
        effective_roll = max(pool)

    # Determine success
    success = effective_roll <= current_san
    if rolled == 1:
        success = True  # Critical always succeeds
    elif rolled == 100:
        success = False  # Fumble always fails

    # Determine success rank
    if rolled == 1:
        rank = "critical"
    elif rolled == 100:
        rank = "fumble"
    elif effective_roll <= current_san // 5:
        rank = "extreme"
    elif effective_roll <= current_san // 2:
        rank = "hard"
    elif success:
        rank = "regular"
    else:
        rank = "failure"

    # Determine sanity loss
    if success:
        san_loss = loss_on_success
    else:
        san_loss = loss_on_failure

    # Mythos gain on failure
    mythos_gain = 0
    if not success and encounter_type:
        mythos_gain = get_mythos_gain_for_encounter(encounter_type)
        # Mythos gain is permanent and doesn't reduce SAN
        # It increases Cthulhu Mythos skill and makes future SAN checks harder

    # Insanity check if SAN would drop significantly
    new_san = max(0, current_san - san_loss)
    insanity_triggered = InsanityType.NONE

    if new_san < max_san // 5:
        # Below threshold - check for temporary insanity
        insanity_break = roll_insanity_break(
            actor_name, new_san, max_san, f"SAN检定失败: {encounter_type}"
        )
        insanity_triggered = insanity_break.insanity_type

    # Build rendered output
    rendered = (
        f"【理智检定】{actor_name}\nSAN: {current_san}/{max_san} | 投掷: {rolled:02d}"
    )
    if bonus_dice or penalty_dice:
        rendered += f" (有效: {effective_roll:02d})"
    rendered += f"\n结果: {rank.upper()} | {'成功' if success else '失败'}\n"

    if san_loss > 0:
        rendered += f"理智损失: {san_loss}"
        if mythos_gain > 0:
            rendered += f" | 神话知识 +{mythos_gain}%"
        rendered += f"\n剩余SAN: {new_san}"
    else:
        rendered += "无理智损失"

    if insanity_triggered != InsanityType.NONE:
        rendered += f"\n⚠️ 触发{insanity_triggered.value}！"

    return SanityCheckResult(
        actor_name=actor_name,
        current_san=current_san,
        max_san=max_san,
        rolled=rolled,
        success=success,
        success_rank=rank,
        sanity_loss=san_loss,
        loss_type=SanityLossType.COMBAT
        if "combat" in encounter_type
        else SanityLossType.SEEN,
        mythos_gain=mythos_gain,
        insanity_triggered=insanity_triggered,
        rendered=rendered,
    )


# =============================================================================
# Sanity Recovery
# =============================================================================


def calculate_sanity_recovery(
    current_san: int,
    max_san: int,
    rest_periods: int = 0,
    therapy_sessions: int = 0,
    real_world_experiences: int = 0,
) -> int:
    """Calculate sanity recovery from various sources.

    COC7e Sanity Recovery:
    - Rest: 1 SAN per full night's sleep (once per冒险)
    - Therapy: 1d6 SAN per session with psychoanalyst
    - Real-world experiences: 1 SAN per significant real-world connection

    Args:
        current_san: Current sanity
        max_san: Maximum sanity
        rest_periods: Number of rest periods
        therapy_sessions: Number of therapy sessions
        real_world_experiences: Number of real-world experiences

    Returns:
        Total sanity recovered
    """
    recovered = 0

    # Rest: 1 SAN per full night's rest (once per adventure)
    recovered += min(1, rest_periods)

    # Therapy: 1d6 per session
    for _ in range(therapy_sessions):
        therapy_gain = d20.roll("1d6").total
        recovered += therapy_gain

    # Real-world experiences: 1 SAN each
    recovered += real_world_experiences

    return min(recovered, max_san - current_san)


# =============================================================================
# Luck Expenditure
# =============================================================================


def spend_luck_for_sanity(
    actor_name: str,
    current_san: int,
    max_san: int,
    luck_available: int,
    sanity_loss: int,
    rolled: int,
) -> tuple[int, int, str]:
    """Attempt to spend Luck to reduce sanity loss.

    COC7e: Can spend 1 Luck point to re-roll a failed Sanity check.

    Args:
        actor_name: Character name
        current_san: Current sanity
        max_san: Maximum sanity
        luck_available: Available Luck points
        sanity_loss: The sanity loss to potentially reduce
        rolled: The original roll

    Returns:
        Tuple of (luck_spent, new_sanity_loss, explanation)
    """
    if luck_available <= 0:
        return 0, sanity_loss, f"【运气消耗】{actor_name}: 无可用运气"

    if rolled > 1:  # Only for failures
        return 0, sanity_loss, f"【运气消耗】{actor_name}: 检定成功，无需消耗运气"

    # Spend 1 Luck to re-roll
    import random

    new_roll = random.randint(1, 100)

    # Re-roll: success if new_roll <= current_san
    success = new_roll <= current_san

    luck_spent = 1

    if success:
        new_loss = 0  # Success eliminates loss for most sanity checks
        explanation = (
            f"【运气消耗】{actor_name} 消耗1点运气重投SAN检定\n"
            f"原始: {rolled:02d} → 新: {new_roll:02d}\n"
            f"检定成功！理智损失降至0"
        )
    else:
        new_loss = sanity_loss  # Loss remains the same
        explanation = (
            f"【运气消耗】{actor_name} 消耗1点运气重投SAN检定\n"
            f"原始: {rolled:02d} → 新: {new_roll:02d}\n"
            f"仍然失败，理智损失不变: {sanity_loss}"
        )

    return luck_spent, new_loss, explanation


# =============================================================================
# Creature Encounter Sanity Loss (E81: Bestiary)
# =============================================================================


def resolve_creature_encounter_sanity(
    creature_template: "CreatureTemplate",
    investigator_san: int,
    has_seen_before: bool = False,
) -> SanityCheckResult:
    """Resolve SAN loss from encountering a creature.

    Args:
        creature_template: The creature's template
        investigator_san: Current SAN of the investigator
        has_seen_before: Whether they've seen this creature type before

    Returns:
        SanityCheckResult with loss amount
    """
    from dm_bot.coc.bestiary import CreatureTemplate

    san_loss = creature_template.san_loss.get_loss(not has_seen_before)

    # Check for indefinite insanity
    indefinite = creature_template.san_loss.indefinite and not has_seen_before

    # Apply SAN loss
    new_san = max(0, investigator_san - san_loss)

    # Determine if insanity occurs
    insanity_type = InsanityType.NONE
    if indefinite:
        # Creature causes indefinite insanity on first encounter
        insanity_type = InsanityType.INDEFINITE
    elif new_san < investigator_san // 5 and investigator_san > 0:
        # Below threshold - roll for temporary insanity
        insanity_break = roll_insanity_break(
            "Investigator",
            new_san,
            investigator_san,
            f"遭遇怪物: {creature_template.name_cn}",
        )
        insanity_type = insanity_break.insanity_type

    # Build rendered output
    rendered = (
        f"【怪物遭遇】{creature_template.name_cn} ({creature_template.name})\n"
        f"当前SAN: {investigator_san} | "
    )
    if has_seen_before:
        rendered += f"再次目击理智损失: {san_loss}\n"
    else:
        rendered += f"首次目击理智损失: {san_loss}\n"

    rendered += f"剩余SAN: {new_san}"

    if indefinite:
        rendered += " | 触发不定性疯狂！"
    elif insanity_type != InsanityType.NONE:
        rendered += f" | 触发{insanity_type.value}！"

    return SanityCheckResult(
        actor_name="Investigator",
        current_san=investigator_san,
        max_san=investigator_san,  # Original max SAN before loss
        rolled=0,  # Creature encounters use fixed loss
        success=True,  # Fixed loss is not a check
        success_rank="creature_encounter",
        sanity_loss=san_loss,
        loss_type=SanityLossType.SEEN,
        insanity_triggered=insanity_type,
        rendered=rendered,
    )
