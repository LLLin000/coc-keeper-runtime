"""Tests for equipment system."""

import pytest

from dm_bot.coc.equipment import (
    Weapon,
    Armor,
    EquipmentDatabase,
    WeaponCategory,
)
from dm_bot.coc.inventory import Inventory, InventoryManager


class TestWeapon:
    """Test weapon functionality."""

    def test_weapon_creation(self):
        """Test creating a weapon."""
        weapon = Weapon(
            id="test_knife",
            name="Test Knife",
            name_cn="测试匕首",
            category=WeaponCategory.MELEE,
            damage="1d4+DB",
        )
        assert weapon.damage == "1d4+DB"

    def test_damage_expression_with_db(self):
        """Test damage expression substitution."""
        weapon = Weapon(
            id="test",
            name="Test",
            name_cn="测试",
            category=WeaponCategory.MELEE,
            damage="1d6+DB",
        )
        expr = weapon.get_damage_expression(db=2)
        assert expr == "1d6+2"


class TestArmor:
    """Test armor functionality."""

    def test_armor_protection(self):
        """Test armor protection value."""
        armor = Armor(
            id="leather",
            name="Leather",
            name_cn="皮甲",
            protection=2,
        )
        assert armor.protection == 2


class TestEquipmentDatabase:
    """Test equipment database."""

    @pytest.fixture
    def db(self):
        """Create test database."""
        database = EquipmentDatabase()
        database.add_weapon(
            Weapon(
                id="knife",
                name="Knife",
                name_cn="匕首",
                category=WeaponCategory.MELEE,
                damage="1d4+DB",
            )
        )
        database.add_armor(
            Armor(
                id="leather",
                name="Leather",
                name_cn="皮甲",
                protection=2,
            )
        )
        return database

    def test_get_weapon(self, db):
        """Test retrieving weapon."""
        weapon = db.get_weapon("knife")
        assert weapon is not None
        assert weapon.name == "Knife"

    def test_get_armor(self, db):
        """Test retrieving armor."""
        armor = db.get_armor("leather")
        assert armor is not None
        assert armor.protection == 2

    def test_list_weapons_by_category(self, db):
        """Test listing weapons by category."""
        melee = db.list_weapons(WeaponCategory.MELEE)
        assert len(melee) == 1


class TestInventory:
    """Test inventory management."""

    @pytest.fixture
    def inv(self):
        """Create test inventory."""
        return Inventory()

    def test_add_weapon(self, inv):
        """Test adding weapon to inventory."""
        inv.add_weapon("knife")
        assert "knife" in inv.weapons

    def test_equip_weapon(self, inv):
        """Test equipping weapon."""
        inv.add_weapon("knife")
        result = inv.equip_weapon("knife")
        assert result is True
        assert inv.equipped_weapon == "knife"

    def test_equip_weapon_not_owned(self, inv):
        """Test equipping weapon not in inventory."""
        result = inv.equip_weapon("sword")
        assert result is False

    def test_equip_armor(self, inv):
        """Test equipping armor."""
        inv.equip_armor("leather")
        assert inv.armor == "leather"


class TestInventoryManager:
    """Test inventory manager."""

    @pytest.fixture
    def manager(self):
        """Create inventory manager."""
        db = EquipmentDatabase()
        db.add_weapon(
            Weapon(
                id="knife",
                name="Knife",
                name_cn="匕首",
                category=WeaponCategory.MELEE,
                damage="1d4+DB",
            )
        )
        db.add_armor(
            Armor(
                id="leather",
                name="Leather",
                name_cn="皮甲",
                protection=2,
            )
        )
        return InventoryManager(db)

    def test_get_weapon_damage(self, manager):
        """Test getting weapon damage."""
        manager.equip_weapon("char1", "knife")
        damage = manager.get_weapon_damage("char1", db=1)
        assert damage == "1d4+1"

    def test_get_armor_protection(self, manager):
        """Test getting armor protection."""
        inv = manager.get_inventory("char1")
        inv.equip_armor("leather")
        protection = manager.get_armor_protection("char1")
        assert protection == 2
