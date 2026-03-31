"""COC 7th Edition Bestiary System.

Creature templates and bestiary management for Call of Cthulhu.
"""

from enum import StrEnum
from typing import Literal, Optional, Union, Dict, List, Any

from pydantic import BaseModel, Field, field_validator, AliasChoices

from dm_bot.characters.models import COCAttributes


class CreatureCategory(StrEnum):
    """Categories of COC creatures."""

    HUMAN = "human"  # Cultists, NPCs
    MONSTER = "monster"  # Ghouls, zombies
    MYTHOS = "mythos"  # Deep Ones, Shoggoths
    BEAST = "beast"  # Animals
    UNDEAD = "undead"  # Zombies, vampires


class CreatureSize(StrEnum):
    """Creature size categories."""

    TINY = "tiny"  # < 1 SIZ
    SMALL = "small"  # 1-15 SIZ
    MEDIUM = "medium"  # 16-30 SIZ
    LARGE = "large"  # 31-60 SIZ
    HUGE = "huge"  # 61-100 SIZ
    COLOSSAL = "colossal"  # > 100 SIZ


class SanLoss(BaseModel):
    """SAN loss from encountering a creature.

    COC 7e: First time seeing vs subsequent encounters.
    Some creatures cause indefinite insanity on first sight.
    """

    first_encounter: int = 0  # SAN loss on first seeing
    subsequent: int = 0  # SAN loss on subsequent encounters
    indefinite: bool = False  # Causes indefinite insanity

    def get_loss(self, is_first: bool = True) -> int:
        """Get SAN loss for encounter."""
        return self.first_encounter if is_first else self.subsequent


class CreatureAttributes(BaseModel):
    """Creature attributes (may have ranges).

    Uses aliases to map JSON field names to Python-safe field names.
    """

    str_val: Union[int, tuple[int, int]] = Field(
        default=50, validation_alias=AliasChoices("str", "str_val")
    )
    con: Union[int, tuple[int, int]] = 50
    siz: Union[int, tuple[int, int]] = 50
    dex: Union[int, tuple[int, int]] = 50
    intel: Union[int, tuple[int, int]] = Field(
        default=50, validation_alias=AliasChoices("int", "intel")
    )
    pow: Union[int, tuple[int, int]] = 50

    def get_fixed(self) -> Dict[str, int]:
        """Get fixed attribute values (use average for ranges)."""
        attrs = {}
        for key, python_key in [
            ("str", "str_val"),
            ("con", "con"),
            ("siz", "siz"),
            ("dex", "dex"),
            ("int", "intel"),
            ("pow", "pow"),
        ]:
            value = getattr(self, python_key)
            if isinstance(value, tuple):
                attrs[key] = (value[0] + value[1]) // 2
            else:
                attrs[key] = value
        return attrs

    def roll_random(self) -> Dict[str, int]:
        """Roll random values for ranged attributes."""
        import random

        attrs = {}
        for key, python_key in [
            ("str", "str_val"),
            ("con", "con"),
            ("siz", "siz"),
            ("dex", "dex"),
            ("int", "intel"),
            ("pow", "pow"),
        ]:
            value = getattr(self, python_key)
            if isinstance(value, tuple):
                attrs[key] = random.randint(value[0], value[1])
            else:
                attrs[key] = value
        return attrs


class CreatureAbility(BaseModel):
    """Special ability a creature has."""

    name: str
    name_cn: str
    description: str
    effect: str = ""  # Mechanical effect


class CreatureTemplate(BaseModel):
    """Template for a COC creature from the bestiary.

    This is the static data from the rulebook.
    For runtime instances, see CreatureInstance.
    """

    # Identity
    id: str  # Unique identifier (e.g., "deep_one")
    name: str  # English name
    name_cn: str  # Chinese name
    category: CreatureCategory
    size: CreatureSize = CreatureSize.MEDIUM

    # Attributes (typical values or ranges)
    attributes: CreatureAttributes

    # Derived stats (calculated from attributes or fixed)
    hp: Optional[int] = None  # None = calculate from CON + SIZ
    mov: Optional[int] = None  # None = calculate from STR/DEX/SIZ

    # Combat
    fighting: int = 25
    shooting: int = 0
    dodge: int = 25
    armor: int = 0  # Armor points
    damage_bonus: str = "+0"  # e.g., "+1d4", "+1d6"

    # Attacks
    attacks: List[dict] = Field(default_factory=list)
    # Example: [{"name": "Claw", "damage": "1d6+DB", "skill": "fighting"}]

    # Sanity
    san_loss: SanLoss = Field(default_factory=SanLoss)

    # Special
    abilities: List[CreatureAbility] = Field(default_factory=list)
    spells: List[str] = Field(default_factory=list)
    immunities: List[str] = Field(default_factory=list)  # e.g., ["poison", "disease"]

    # Description
    description: str = ""
    tactics: str = ""

    def calculate_hp(self, attrs: Optional[Dict[str, int]] = None) -> int:
        """Calculate HP from attributes."""
        if self.hp is not None:
            return self.hp
        attrs = attrs or self.attributes.get_fixed()
        con = attrs.get("con", 50)
        siz = attrs.get("siz", 50)
        return (con + siz) // 10

    def calculate_mov(self, attrs: Optional[Dict[str, int]] = None) -> int:
        """Calculate MOV from attributes."""
        if self.mov is not None:
            return self.mov
        attrs = attrs or self.attributes.get_fixed()
        str_v = attrs.get("str", 50)
        dex_v = attrs.get("dex", 50)
        siz_v = attrs.get("siz", 50)

        if str_v < siz_v and dex_v < siz_v:
            return 7
        elif str_v > siz_v and dex_v > siz_v:
            return 9
        else:
            return 8

    def to_combatant_stats(self, attrs: Optional[Dict[str, int]] = None) -> Dict:
        """Convert to CombatantStats-compatible dict."""
        attrs = attrs or self.attributes.get_fixed()
        return {
            "name": self.name_cn,
            "dex": attrs["dex"],
            "fighting": self.fighting,
            "dodge": self.dodge,
            "hp": self.calculate_hp(attrs),
            "hp_max": self.calculate_hp(attrs),
            "armor": self.armor,
            "damage_bonus": self._parse_damage_bonus(),
        }

    def _parse_damage_bonus(self) -> int:
        """Parse damage bonus string to integer."""
        db = self.damage_bonus
        if db.startswith("+"):
            db = db[1:]
        if "d" in db.lower():
            # Extract number before 'd' as multiplier
            import re

            match = re.search(r"(\d+)d", db.lower())
            if match:
                return int(match.group(1))
        try:
            return int(db)
        except ValueError:
            return 0


class Bestiary:
    """Collection of creature templates."""

    def __init__(self) -> None:
        self._creatures: Dict[str, CreatureTemplate] = {}

    def add(self, creature: CreatureTemplate) -> None:
        """Add a creature to the bestiary."""
        self._creatures[creature.id] = creature

    def get(self, creature_id: str) -> Optional[CreatureTemplate]:
        """Get a creature by ID."""
        return self._creatures.get(creature_id)

    def list_all(self) -> List[CreatureTemplate]:
        """List all creatures."""
        return list(self._creatures.values())

    def list_by_category(self, category: CreatureCategory) -> List[CreatureTemplate]:
        """List creatures by category."""
        return [c for c in self._creatures.values() if c.category == category]

    def export_state(self) -> Dict:
        """Export bestiary state."""
        return {cid: creature.model_dump() for cid, creature in self._creatures.items()}

    @classmethod
    def load_from_file(cls, path: str) -> "Bestiary":
        """Load bestiary from JSON file."""
        import json

        bestiary = cls()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for creature_data in data.get("creatures", []):
            creature = CreatureTemplate.model_validate(creature_data)
            bestiary.add(creature)
        return bestiary
