"""COC 7th Edition Magic System

Complete magic resolution including:
- Spell casting checks (INT×2 + POW×2 threshold)
- Spellbook management
- Summoning and binding rituals
- MP costs per spell
- Cthulhu Mythos spell prerequisites
- Magic point calculations

Reference: Call of Cthulhu 7th Edition Keeper's Rulebook, Chapter 10
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


# =============================================================================
# Magic Constants
# =============================================================================

# Magic Point cost per spell casting = typically 1/2/3/5/7/10 MP
# Or percentage of caster's MP


# Spell schools/types
class SpellSchool(StrEnum):
    """Schools of magic in COC."""

    CONJURATION = "conjuration"  # Summoning creatures
    DIVINATION = "divination"  # Gaining knowledge
    ENCHANTMENT = "enchantment"  # Influencing minds
    EVOCATION = "evocation"  # Creating effects
    NECROMANCY = "necromancy"  # Death-related
    TRANSMUTATION = "transmutation"  # Changing things
    GENERAL = "general"  # General spells


# Spell type
class SpellType(StrEnum):
    """Types of spells."""

    SPELL = "spell"  # Regular spell
    RITUAL = "ritual"  # Major ritual (takes longer)
    SUMMONING = "summoning"  # Summoning creature
    BINDING = "binding"  # Binding summoned creature
    SUMMONING_BINDING = "summoning_binding"  # Combined summoning+binding


# =============================================================================
# Spell Definition
# =============================================================================


class SpellDefinition(BaseModel):
    """Definition of a COC spell."""

    name: str  # English name
    name_cn: str  # Chinese name
    school: SpellSchool
    spell_type: SpellType
    casting_time: str = "1 round"  # How long to cast
    mp_cost: int  # Base MP cost
    mp_cost_percent: bool = False  # If True, cost is % of caster's MP
    sanity_loss: int = 0  # Sanity loss for casting
    difficulty: Literal["regular", "hard", "extreme"] = "regular"

    # For summoning/binding spells
    creature_type: str = ""  # Type of creature summoned
    binding_difficulty: int = 0  # Required binding roll

    # Prerequisites
    required_skill: str = ""  # Required skill (e.g., "spellcast")
    required_spells: list[str] = Field(
        default_factory=list
    )  # Other spells that must be known
    cthulhu_mythos_min: int = 0  # Minimum Cthulhu Mythos skill

    # Description
    description: str = ""


# =============================================================================
# Common COC Spells (Selected from COC7e)
# =============================================================================

COC_SPELLS: dict[str, SpellDefinition] = {
    # -------------------------------------------------------------------------
    # SUMMONING SPELLS
    # -------------------------------------------------------------------------
    "contact_ghoul": SpellDefinition(
        name="Contact Ghoul",
        name_cn="接触食尸鬼",
        school=SpellSchool.CONJURATION,
        spell_type=SpellType.SUMMONING,
        casting_time="1 hour",
        mp_cost=10,
        sanity_loss=1,
        difficulty="regular",
        creature_type="Ghoul",
        description="Summons a ghoul to communicate with.",
    ),
    "contact_deep_one": SpellDefinition(
        name="Contact Deep One",
        name_cn="接触深潜者",
        school=SpellSchool.CONJURATION,
        spell_type=SpellType.SUMMONING,
        casting_time="1 hour",
        mp_cost=15,
        sanity_loss=2,
        difficulty="hard",
        creature_type="Deep One",
        description="Summons a deep one for communication.",
    ),
    "summon_byakhee": SpellDefinition(
        name="Summon Byakhee",
        name_cn="召唤拜亚基",
        school=SpellSchool.CONJURATION,
        spell_type=SpellType.SUMMONING,
        casting_time="1 hour",
        mp_cost=20,
        sanity_loss=3,
        difficulty="hard",
        creature_type="Byakhee",
        description="Summons byakhee as steeds.",
    ),
    "summon_chthonian": SpellDefinition(
        name="Summon Chthonian",
        name_cn="召唤克苏尼安",
        school=SpellSchool.CONJURATION,
        spell_type=SpellType.SUMMONING,
        casting_time="1 hour",
        mp_cost=25,
        sanity_loss=4,
        difficulty="extreme",
        creature_type="Chthonian",
        description="Summons a chthonian from the depths.",
    ),
    "summon_shantak": SpellDefinition(
        name="Summon Shantak",
        name_cn="召唤深空星之眷属",
        school=SpellSchool.CONJURATION,
        spell_type=SpellType.SUMMONING,
        casting_time="1 hour",
        mp_cost=15,
        sanity_loss=2,
        difficulty="hard",
        creature_type="Shantak",
        description="Summons a shantak as a mount.",
    ),
    "contact_cthulhu": SpellDefinition(
        name="Contact Cthulhu",
        name_cn="接触克苏鲁",
        school=SpellSchool.CONJURATION,
        spell_type=SpellType.SUMMONING,
        casting_time="1 hour",
        mp_cost=30,
        sanity_loss=5,
        difficulty="extreme",
        creature_type="Cthulhu",
        cthulhu_mythos_min=80,
        description="Attempts to contact the sleeping Cthulhu.",
    ),
    # -------------------------------------------------------------------------
    # BINDING SPELLS
    # -------------------------------------------------------------------------
    "binding_ritual": SpellDefinition(
        name="Binding Ritual",
        name_cn="束缚仪式",
        school=SpellSchool.NECROMANCY,
        spell_type=SpellType.BINDING,
        casting_time="1 hour",
        mp_cost=7,
        sanity_loss=2,
        difficulty="hard",
        description="Binds a summoned creature to the caster's will.",
    ),
    "exile_bind": SpellDefinition(
        name="Exile Bind",
        name_cn="驱逐束缚",
        school=SpellSchool.NECROMANCY,
        spell_type=SpellType.BINDING,
        casting_time="30 minutes",
        mp_cost=5,
        sanity_loss=1,
        difficulty="regular",
        description="Forces a creature to leave the area.",
    ),
    # -------------------------------------------------------------------------
    # DIVINATION SPELLS
    # -------------------------------------------------------------------------
    "vision_revealing": SpellDefinition(
        name="Vision Revealing",
        name_cn="揭示幻象",
        school=SpellSchool.DIVINATION,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=3,
        sanity_loss=1,
        difficulty="regular",
        description="Reveals visions related to a question.",
    ),
    "astral_sense": SpellDefinition(
        name="Astral Sense",
        name_cn="星界感知",
        school=SpellSchool.DIVINATION,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=2,
        sanity_loss=0,
        difficulty="regular",
        description="Senses the presence of magical or supernatural beings.",
    ),
    "reveal_alignment": SpellDefinition(
        name="Reveal Alignment",
        name_cn="揭示倾向",
        school=SpellSchool.DIVINATION,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=2,
        sanity_loss=0,
        difficulty="regular",
        description="Reveals whether a being is good or evil.",
    ),
    # -------------------------------------------------------------------------
    # EVOCATION SPELLS
    # -------------------------------------------------------------------------
    "focalization": SpellDefinition(
        name="Focalization",
        name_cn="焦点化",
        school=SpellSchool.EVOCATION,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=1,
        sanity_loss=0,
        difficulty="regular",
        description="Concentrates magical energy into a more powerful form.",
    ),
    "energy_bolt": SpellDefinition(
        name="Energy Bolt",
        name_cn="能量箭",
        school=SpellSchool.EVOCATION,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=5,
        sanity_loss=1,
        difficulty="regular",
        description="Creates a bolt of magical energy that deals 1d6 damage.",
    ),
    "call_lightning": SpellDefinition(
        name="Call Lightning",
        name_cn="召唤闪电",
        school=SpellSchool.EVOCATION,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=10,
        sanity_loss=2,
        difficulty="hard",
        description="Summons a lightning bolt for 2d6 damage.",
    ),
    # -------------------------------------------------------------------------
    # ENCHANTMENT SPELLS
    # -------------------------------------------------------------------------
    "enchant_weapon": SpellDefinition(
        name="Enchant Weapon",
        name_cn="武器附魔",
        school=SpellSchool.ENCHANTMENT,
        spell_type=SpellType.SPELL,
        casting_time="1 hour",
        mp_cost=5,
        sanity_loss=1,
        difficulty="regular",
        description="Enchant a weapon to deal bonus damage against supernatural creatures.",
    ),
    "protection_circle": SpellDefinition(
        name="Protection Circle",
        name_cn="保护圆阵",
        school=SpellSchool.ENCHANTMENT,
        spell_type=SpellType.SPELL,
        casting_time="10 minutes",
        mp_cost=5,
        sanity_loss=1,
        difficulty="regular",
        description="Creates a protective circle that prevents creature entry.",
    ),
    "mind_control": SpellDefinition(
        name="Mind Control",
        name_cn="心灵控制",
        school=SpellSchool.ENCHANTMENT,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=8,
        sanity_loss=2,
        difficulty="hard",
        description="Controls the mind of a target for a short time.",
    ),
    # -------------------------------------------------------------------------
    # NECROMANCY SPELLS
    # -------------------------------------------------------------------------
    "animate_dead": SpellDefinition(
        name="Animate Dead",
        name_cn="活化死者",
        school=SpellSchool.NECROMANCY,
        spell_type=SpellType.RITUAL,
        casting_time="1 hour",
        mp_cost=15,
        sanity_loss=3,
        difficulty="hard",
        description="Creates zombie servants from corpses.",
    ),
    "death_kiss": SpellDefinition(
        name="Death Kiss",
        name_cn="死亡之吻",
        school=SpellSchool.NECROMANCY,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=7,
        sanity_loss=2,
        difficulty="hard",
        description="Energy drains life force, causing 1d6 damage and possibly SAN loss.",
    ),
    "soul_weapon": SpellDefinition(
        name="Soul Weapon",
        name_cn="灵魂武器",
        school=SpellSchool.NECROMANCY,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=5,
        sanity_loss=1,
        difficulty="regular",
        description="Creates a weapon made of spiritual energy.",
    ),
    # -------------------------------------------------------------------------
    # TRANSMUTATION SPELLS
    # -------------------------------------------------------------------------
    "dust_of_sound": SpellDefinition(
        name="Dust of Sound",
        name_cn="静默粉",
        school=SpellSchool.TRANSMUTATION,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=1,
        sanity_loss=0,
        difficulty="regular",
        description="Dulls sound in an area.",
    ),
    "mist_travel": SpellDefinition(
        name="Mist Travel",
        name_cn="薄雾旅行",
        school=SpellSchool.TRANSMUTATION,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=3,
        sanity_loss=0,
        difficulty="regular",
        description="Allows the caster to travel unseen as mist.",
    ),
    "body_rearrangement": SpellDefinition(
        name="Body Rearrangement",
        name_cn="身体重排",
        school=SpellSchool.TRANSMUTATION,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=4,
        sanity_loss=1,
        difficulty="hard",
        description="Allows the caster to rearrange their appearance.",
    ),
    # -------------------------------------------------------------------------
    # GENERAL SPELLS
    # -------------------------------------------------------------------------
    "curse_blight": SpellDefinition(
        name="Curse: Blight",
        name_cn="诅咒: 枯萎",
        school=SpellSchool.GENERAL,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=5,
        sanity_loss=1,
        difficulty="regular",
        description="Brings bad luck and misfortune to a target.",
    ),
    "forget_spell": SpellDefinition(
        name="Forget Spell",
        name_cn="遗忘咒",
        school=SpellSchool.GENERAL,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=3,
        sanity_loss=1,
        difficulty="regular",
        description="Makes the target forget recent events.",
    ),
    "silver_shadow": SpellDefinition(
        name="Silver Shadow",
        name_cn="银影",
        school=SpellSchool.GENERAL,
        spell_type=SpellType.SPELL,
        casting_time="1 round",
        mp_cost=2,
        sanity_loss=0,
        difficulty="regular",
        description="Creates a shadow that can retrieve items.",
    ),
}


# =============================================================================
# Spell Casting Result
# =============================================================================


class SpellCastResult(BaseModel):
    """Result of a spell casting attempt."""

    spell_key: str
    spell_name_cn: str
    caster_name: str
    caster_int: int
    caster_pow: int
    caster_spellcast: int
    caster_cthulhu_mythos: int
    caster_mp: int
    caster_max_mp: int

    casting_threshold: int  # INT×2 + POW×2
    rolled: int
    success: bool
    success_rank: str = "failure"
    critical: bool = False
    fumble: bool = False

    mp_cost: int  # Actual MP spent
    sanity_loss: int = 0
    mp_remaining: int = 0

    # For summoning spells
    summon_success: bool = False
    creature_type: str = ""

    # For binding spells
    binding_roll: int = 0
    binding_success: bool = False

    rendered: str = ""


# =============================================================================
# Spell Casting Resolution
# =============================================================================


def resolve_spell_cast(
    spell_key: str,
    caster_name: str,
    caster_int: int,
    caster_pow: int,
    caster_spellcast: int,
    caster_cthulhu_mythos: int,
    caster_mp: int,
    caster_max_mp: int,
    rolled: int,
    bonus_dice: int = 0,
    penalty_dice: int = 0,
) -> SpellCastResult:
    """Resolve a spell casting attempt.

    COC7e Spell Casting:
    - Casting threshold = INT×2 + POW×2
    - Roll percentile vs threshold
    - Success at regular difficulty = threshold
    - Hard = threshold // 2
    - Extreme = threshold // 5

    Args:
        spell_key: The spell identifier
        caster_name: Caster's name
        caster_int: Caster's INT attribute
        caster_pow: Caster's POW attribute
        caster_spellcast: Caster's Spellcast skill
        caster_cthulhu_mythos: Caster's Cthulhu Mythos skill
        caster_mp: Current magic points
        caster_max_mp: Maximum magic points
        rolled: The d100 roll result
        bonus_dice: Bonus dice for favorable conditions
        penalty_dice: Penalty dice for unfavorable conditions

    Returns:
        SpellCastResult with full outcome
    """
    import random

    spell = COC_SPELLS.get(spell_key)
    if spell is None:
        return SpellCastResult(
            spell_key=spell_key,
            spell_name_cn=f"未知法术({spell_key})",
            caster_name=caster_name,
            caster_int=caster_int,
            caster_pow=caster_pow,
            caster_spellcast=caster_spellcast,
            caster_cthulhu_mythos=caster_cthulhu_mythos,
            caster_mp=caster_mp,
            caster_max_mp=caster_max_mp,
            casting_threshold=0,
            rolled=rolled,
            success=False,
            rendered=f"【施法失败】{caster_name}: 未知法术 {spell_key}",
        )

    # Calculate threshold
    base_threshold = caster_int * 2 + caster_pow * 2

    # Apply difficulty modifier
    if spell.difficulty == "extreme":
        threshold = max(1, base_threshold // 5)
    elif spell.difficulty == "hard":
        threshold = max(1, base_threshold // 2)
    else:
        threshold = base_threshold

    # Check prerequisites
    if (
        spell.required_skill
        and getattr({"spellcast": caster_spellcast}, spell.required_skill, 0) == 0
    ):
        return SpellCastResult(
            spell_key=spell_key,
            spell_name_cn=spell.name_cn,
            caster_name=caster_name,
            caster_int=caster_int,
            caster_pow=caster_pow,
            caster_spellcast=caster_spellcast,
            caster_cthulhu_mythos=caster_cthulhu_mythos,
            caster_mp=caster_mp,
            caster_max_mp=caster_max_mp,
            casting_threshold=threshold,
            rolled=rolled,
            success=False,
            rendered=(
                f"【施法失败】{caster_name} 尝试施放 {spell.name_cn}\n"
                f"缺少前提技能: {spell.required_skill}"
            ),
        )

    if spell.cthulhu_mythos_min > caster_cthulhu_mythos:
        return SpellCastResult(
            spell_key=spell_key,
            spell_name_cn=spell.name_cn,
            caster_name=caster_name,
            caster_int=caster_int,
            caster_pow=caster_pow,
            caster_spellcast=caster_spellcast,
            caster_cthulhu_mythos=caster_cthulhu_mythos,
            caster_mp=caster_mp,
            caster_max_mp=caster_max_mp,
            casting_threshold=threshold,
            rolled=rolled,
            success=False,
            rendered=(
                f"【施法失败】{caster_name} 尝试施放 {spell.name_cn}\n"
                f"克苏鲁神话技能不足: 需要 {spell.cthulhu_mythos_min}, 拥有 {caster_cthulhu_mythos}"
            ),
        )

    # Apply bonus/penalty dice
    effective_roll = rolled
    if bonus_dice and not penalty_dice:
        pool = [rolled] + [random.randint(1, 100) for _ in range(bonus_dice)]
        effective_roll = min(pool)
    elif penalty_dice and not bonus_dice:
        pool = [rolled] + [random.randint(1, 100) for _ in range(penalty_dice)]
        effective_roll = max(pool)

    # Determine success
    critical = rolled == 1
    fumble = rolled == 100 or (caster_spellcast >= 50 and rolled >= 96)

    if critical:
        success = True
        rank = "critical"
    elif fumble:
        success = False
        rank = "fumble"
    else:
        success = effective_roll <= threshold
        if success:
            if effective_roll <= max(1, threshold // 5):
                rank = "extreme"
            elif effective_roll <= max(1, threshold // 2):
                rank = "hard"
            else:
                rank = "regular"
        else:
            rank = "failure"

    # Calculate MP cost
    if spell.mp_cost_percent:
        mp_cost = caster_max_mp * spell.mp_cost // 100
    else:
        mp_cost = spell.mp_cost

    # Check if enough MP
    if caster_mp < mp_cost:
        return SpellCastResult(
            spell_key=spell_key,
            spell_name_cn=spell.name_cn,
            caster_name=caster_name,
            caster_int=caster_int,
            caster_pow=caster_pow,
            caster_spellcast=caster_spellcast,
            caster_cthulhu_mythos=caster_cthulhu_mythos,
            caster_mp=caster_mp,
            caster_max_mp=caster_max_mp,
            casting_threshold=threshold,
            rolled=rolled,
            success=False,
            mp_cost=0,
            rendered=(
                f"【施法失败】{caster_name} 尝试施放 {spell.name_cn}\n"
                f"魔法点不足: 需要 {mp_cost}, 拥有 {caster_mp}"
            ),
        )

    # Build result
    mp_remaining = caster_mp - mp_cost if success else caster_mp

    result = SpellCastResult(
        spell_key=spell_key,
        spell_name_cn=spell.name_cn,
        caster_name=caster_name,
        caster_int=caster_int,
        caster_pow=caster_pow,
        caster_spellcast=caster_spellcast,
        caster_cthulhu_mythos=caster_cthulhu_mythos,
        caster_mp=caster_mp,
        caster_max_mp=caster_max_mp,
        casting_threshold=threshold,
        rolled=rolled,
        success=success,
        success_rank=rank,
        critical=critical,
        fumble=fumble,
        mp_cost=mp_cost if success else 0,
        sanity_loss=spell.sanity_loss if success else 0,
        mp_remaining=mp_remaining,
        creature_type=spell.creature_type
        if spell.spell_type == SpellType.SUMMONING
        else "",
        rendered=(
            f"【施法{('成功' if success else '失败')}】{caster_name} → {spell.name_cn}\n"
            f"阈值: {threshold} | 投掷: {rolled:02d}\n"
            f"结果: {rank.upper()}"
        ),
    )

    if success:
        result.rendered += f"\n消耗MP: {mp_cost} | 剩余MP: {mp_remaining}"
        if spell.sanity_loss > 0:
            result.rendered += f"\n理智损失: {spell.sanity_loss}"
        if spell.spell_type == SpellType.SUMMONING and spell.creature_type:
            result.rendered += f"\n召唤生物: {spell.creature_type}"
    else:
        if fumble:
            result.rendered += "\n大失败！施法反噬！"

    return result


# =============================================================================
# Spellbook Management
# =============================================================================


class SpellbookEntry(BaseModel):
    """An entry in a character's spellbook."""

    spell_key: str
    learned: bool = True
    casting_threshold_override: int = 0  # If > 0, custom threshold
    notes: str = ""


class Spellbook(BaseModel):
    """A character's spellbook containing learned spells."""

    entries: dict[str, SpellbookEntry] = Field(default_factory=dict)

    def add_spell(self, spell_key: str, notes: str = "") -> bool:
        """Add a spell to the spellbook.

        Args:
            spell_key: The spell to add
            notes: Optional notes about the spell

        Returns:
            True if added, False if spell doesn't exist
        """
        if spell_key not in COC_SPELLS:
            return False

        self.entries[spell_key] = SpellbookEntry(
            spell_key=spell_key,
            learned=True,
            notes=notes,
        )
        return True

    def remove_spell(self, spell_key: str) -> bool:
        """Remove a spell from the spellbook.

        Args:
            spell_key: The spell to remove

        Returns:
            True if removed, False if not in spellbook
        """
        if spell_key in self.entries:
            del self.entries[spell_key]
            return True
        return False

    def has_spell(self, spell_key: str) -> bool:
        """Check if spell is in spellbook."""
        return spell_key in self.entries

    def get_spell_cost(self, spell_key: str, caster_max_mp: int) -> int:
        """Get the MP cost for a spell.

        Args:
            spell_key: The spell key
            caster_max_mp: Caster's maximum MP

        Returns:
            MP cost, or 0 if spell not found
        """
        spell = COC_SPELLS.get(spell_key)
        if spell is None:
            return 0

        if spell.mp_cost_percent:
            return caster_max_mp * spell.mp_cost // 100
        return spell.mp_cost


# =============================================================================
# Magic Point Calculations
# =============================================================================


def calculate_mp(pow_value: int) -> int:
    """Calculate Magic Points from POW.

    COC7e: MP = POW / 5 (round down)

    Args:
        pow_value: Character's POW attribute

    Returns:
        Maximum magic points
    """
    return pow_value // 5


def get_mp_for_level(pow_value: int, level: int) -> int:
    """Calculate MP at a specific power level.

    Used for beings with variable MP (e.g., creatures).

    Args:
        pow_value: Base POW
        level: Power level (1-5)

    Returns:
        MP at that power level
    """
    base_mp = pow_value // 5
    return base_mp * level
