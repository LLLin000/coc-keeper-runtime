"""COC 7th Edition Equipment System.

Weapons and armor for Call of Cthulhu.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class WeaponCategory(StrEnum):
    """Weapon categories."""

    MELEE = "melee"
    RANGED = "ranged"
    THROWN = "thrown"


class Weapon(BaseModel):
    """A weapon in COC 7e."""

    # Identity
    id: str
    name: str
    name_cn: str
    category: WeaponCategory

    # Combat stats
    damage: str  # Damage expression, e.g., "1d6", "1d8+DB", "2d6"
    damage_type: str = "physical"  # physical, fire, etc.

    # Range
    range: str = "touch"  # "touch", "2m", "10m", "50m", "100m", etc.

    # For ranged weapons
    ammo_capacity: int | None = None
    malfunction: int | None = None  # Malfunction number

    # Combat
    attacks_per_round: int = 1
    skill: str = "fighting"  # Default skill to use

    # Special
    two_handed: bool = False
    concealable: bool = True

    # Description
    description: str = ""

    def get_damage_expression(self, db: int = 0) -> str:
        """Get damage expression with DB substituted.

        Args:
            db: Damage bonus value

        Returns:
            Damage expression ready to roll
        """
        return self.damage.replace("DB", str(db))


class Armor(BaseModel):
    """Armor in COC 7e."""

    # Identity
    id: str
    name: str
    name_cn: str

    # Protection
    protection: int  # Armor points

    # Coverage
    coverage: list[str] = Field(default_factory=lambda: ["torso"])
    # body parts: head, torso, arms, legs

    # Properties
    bulky: bool = False  # May affect movement
    description: str = ""


class EquipmentDatabase:
    """Database of weapons and armor."""

    def __init__(self) -> None:
        self.weapons: dict[str, Weapon] = {}
        self.armor: dict[str, Armor] = {}

    def add_weapon(self, weapon: Weapon) -> None:
        """Add a weapon to the database."""
        self.weapons[weapon.id] = weapon

    def get_weapon(self, weapon_id: str) -> Weapon | None:
        """Get a weapon by ID."""
        return self.weapons.get(weapon_id)

    def list_weapons(self, category: WeaponCategory | None = None) -> list[Weapon]:
        """List weapons, optionally filtered by category."""
        weapons = list(self.weapons.values())
        if category:
            weapons = [w for w in weapons if w.category == category]
        return weapons

    def add_armor(self, armor: Armor) -> None:
        """Add armor to the database."""
        self.armor[armor.id] = armor

    def get_armor(self, armor_id: str) -> Armor | None:
        """Get armor by ID."""
        return self.armor.get(armor_id)

    def list_armor(self) -> list[Armor]:
        """List all armor."""
        return list(self.armor.values())

    @classmethod
    def load_from_files(
        cls,
        weapons_path: str | None = None,
        armor_path: str | None = None,
    ) -> "EquipmentDatabase":
        """Load equipment from JSON files.

        Args:
            weapons_path: Path to weapons JSON
            armor_path: Path to armor JSON

        Returns:
            Populated EquipmentDatabase
        """
        import json

        db = cls()

        if weapons_path:
            with open(weapons_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for weapon_data in data.get("weapons", []):
                db.add_weapon(Weapon.model_validate(weapon_data))

        if armor_path:
            with open(armor_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for armor_data in data.get("armor", []):
                db.add_armor(Armor.model_validate(armor_data))

        return db


# Common weapon IDs for convenience
COMMON_WEAPONS = {
    "unarmed": "unarmed",
    "knife": "knife",
    "club": "club",
    "pistol": "pistol_light",
    "rifle": "rifle",
    "shotgun": "shotgun",
}

# Common armor IDs
COMMON_ARMOR = {
    "none": "none",
    "leather": "leather_jacket",
    "heavy": "heavy_leather",
}
