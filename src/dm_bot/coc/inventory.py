"""Inventory management for COC characters."""

from pydantic import BaseModel, Field

from dm_bot.coc.equipment import Weapon, Armor, EquipmentDatabase


class Inventory(BaseModel):
    """Character inventory."""

    # Weapons
    weapons: list[str] = Field(default_factory=list)  # Weapon IDs
    equipped_weapon: str | None = None

    # Armor
    armor: str | None = None  # Armor ID

    # Other items
    items: list[str] = Field(default_factory=list)

    # Money
    cash: float = 0.0
    assets: float = 0.0

    def equip_weapon(
        self, weapon_id: str, equipment_db: EquipmentDatabase | None = None
    ) -> bool:
        """Equip a weapon.

        Args:
            weapon_id: The weapon ID to equip
            equipment_db: Equipment database to validate weapon exists (optional)

        Returns:
            True if equipped, False if weapon doesn't exist
        """
        # "unarmed" is always valid
        if weapon_id == "unarmed":
            self.equipped_weapon = weapon_id
            return True

        # Check if weapon is in inventory or in equipment database
        if weapon_id in self.weapons:
            self.equipped_weapon = weapon_id
            return True

        # If equipment_db provided, check if weapon exists in database
        if equipment_db is not None and equipment_db.get_weapon(weapon_id) is not None:
            self.equipped_weapon = weapon_id
            return True

        return False

    def unequip_weapon(self) -> None:
        """Unequip current weapon (revert to unarmed)."""
        self.equipped_weapon = None

    def equip_armor(self, armor_id: str) -> bool:
        """Equip armor.

        Args:
            armor_id: The armor ID

        Returns:
            True if equipped
        """
        self.armor = armor_id
        return True

    def unequip_armor(self) -> None:
        """Remove armor."""
        self.armor = None

    def add_weapon(self, weapon_id: str) -> None:
        """Add a weapon to inventory."""
        if weapon_id not in self.weapons:
            self.weapons.append(weapon_id)

    def remove_weapon(self, weapon_id: str) -> bool:
        """Remove a weapon from inventory.

        Returns:
            True if removed, False if not found
        """
        if weapon_id in self.weapons:
            self.weapons.remove(weapon_id)
            if self.equipped_weapon == weapon_id:
                self.equipped_weapon = None
            return True
        return False

    def add_item(self, item: str) -> None:
        """Add an item to inventory."""
        self.items.append(item)

    def remove_item(self, item: str) -> bool:
        """Remove an item from inventory."""
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def get_equipped_weapon(self, equipment_db: EquipmentDatabase) -> Weapon | None:
        """Get the currently equipped weapon.

        Args:
            equipment_db: Equipment database

        Returns:
            Equipped weapon or None
        """
        weapon_id = self.equipped_weapon or "unarmed"
        return equipment_db.get_weapon(weapon_id)

    def get_equipped_armor(self, equipment_db: EquipmentDatabase) -> Armor | None:
        """Get the currently equipped armor.

        Args:
            equipment_db: Equipment database

        Returns:
            Equipped armor or None
        """
        if not self.armor:
            return None
        return equipment_db.get_armor(self.armor)

    def get_protection(self, equipment_db: EquipmentDatabase) -> int:
        """Get total armor protection.

        Args:
            equipment_db: Equipment database

        Returns:
            Armor protection value
        """
        armor = self.get_equipped_armor(equipment_db)
        if armor:
            return armor.protection
        return 0


class InventoryManager:
    """Manages inventories for multiple characters."""

    def __init__(self, equipment_db: EquipmentDatabase) -> None:
        self.equipment_db = equipment_db
        self.inventories: dict[str, Inventory] = {}

    def get_inventory(self, character_id: str) -> Inventory:
        """Get or create inventory for a character."""
        if character_id not in self.inventories:
            self.inventories[character_id] = Inventory()
        return self.inventories[character_id]

    def set_inventory(self, character_id: str, inventory: Inventory) -> None:
        """Set inventory for a character."""
        self.inventories[character_id] = inventory

    def equip_weapon(self, character_id: str, weapon_id: str) -> bool:
        """Equip a weapon for a character."""
        inv = self.get_inventory(character_id)
        return inv.equip_weapon(weapon_id, self.equipment_db)

    def get_weapon_damage(self, character_id: str, db: int = 0) -> str:
        """Get damage expression for character's weapon.

        Args:
            character_id: The character ID
            db: Damage bonus

        Returns:
            Damage expression
        """
        inv = self.get_inventory(character_id)
        weapon = inv.get_equipped_weapon(self.equipment_db)
        if weapon:
            return weapon.get_damage_expression(db)
        return f"1d3+{db}"  # Default unarmed

    def get_armor_protection(self, character_id: str) -> int:
        """Get armor protection for a character."""
        inv = self.get_inventory(character_id)
        return inv.get_protection(self.equipment_db)
