"""Tests for bestiary and creature system."""

import pytest

from dm_bot.coc.bestiary import (
    Bestiary,
    CreatureTemplate,
    CreatureCategory,
    CreatureSize,
    SanLoss,
    CreatureAttributes,
    CreatureAbility,
)
from dm_bot.coc.creature import CreatureInstance, CreatureManager


class TestSanLoss:
    """Test SAN loss mechanics."""

    def test_first_encounter_loss(self):
        """Test SAN loss on first encounter."""
        san_loss = SanLoss(first_encounter=5, subsequent=1)
        assert san_loss.get_loss(is_first=True) == 5
        assert san_loss.get_loss(is_first=False) == 1

    def test_subsequent_encounter_loss(self):
        """Test SAN loss on subsequent encounters."""
        san_loss = SanLoss(first_encounter=5, subsequent=1)
        assert san_loss.get_loss(is_first=False) == 1

    def test_indefinite_insanity(self):
        """Test indefinite insanity flag."""
        san_loss = SanLoss(first_encounter=10, indefinite=True)
        assert san_loss.indefinite is True

    def test_no_indefinite(self):
        """Test non-indefinite creatures."""
        san_loss = SanLoss(first_encounter=5, indefinite=False)
        assert san_loss.indefinite is False


class TestCreatureAttributes:
    """Test creature attribute handling."""

    def test_fixed_attributes(self):
        """Test fixed attribute values."""
        attrs = CreatureAttributes(str=100, con=80, siz=70)
        fixed = attrs.get_fixed()
        assert fixed["str"] == 100
        assert fixed["con"] == 80
        assert fixed["siz"] == 70

    def test_ranged_attributes(self):
        """Test ranged attribute values."""
        attrs = CreatureAttributes(str=(80, 120), con=80)
        fixed = attrs.get_fixed()
        assert fixed["str"] == 100  # Average
        assert fixed["con"] == 80

    def test_roll_random(self):
        """Test random rolling for ranged attributes."""
        attrs = CreatureAttributes(str=(80, 100), con=50)
        for _ in range(10):
            rolled = attrs.roll_random()
            assert 80 <= rolled["str"] <= 100
            assert rolled["con"] == 50


class TestCreatureTemplate:
    """Test creature template functionality."""

    @pytest.fixture
    def deep_one_template(self):
        """Create a Deep One template for testing."""
        return CreatureTemplate(
            id="deep_one",
            name="Deep One",
            name_cn="深潜者",
            category=CreatureCategory.MYTHOS,
            size=CreatureSize.MEDIUM,
            attributes=CreatureAttributes(
                str=100, con=80, siz=70, dex=60, int=70, pow=80
            ),
            hp=15,
            mov=8,
            fighting=50,
            dodge=30,
            armor=1,
            damage_bonus="+1d4",
            san_loss=SanLoss(first_encounter=5, subsequent=1),
        )

    def test_calculate_hp_with_fixed(self, deep_one_template):
        """Test HP calculation with fixed HP."""
        assert deep_one_template.calculate_hp() == 15

    def test_calculate_hp_from_attrs(self):
        """Test HP calculation from attributes."""
        template = CreatureTemplate(
            id="test",
            name="Test",
            name_cn="测试",
            category=CreatureCategory.MONSTER,
            attributes=CreatureAttributes(con=80, siz=70),
            hp=None,  # Calculate from attrs
        )
        assert template.calculate_hp() == 15  # (80+70)//10

    def test_calculate_mov(self, deep_one_template):
        """Test MOV calculation."""
        # Deep One: STR=100, DEX=60, SIZ=70
        # STR > SIZ but DEX < SIZ, so MOV = 8
        assert deep_one_template.calculate_mov() == 8

    def test_to_combatant_stats(self, deep_one_template):
        """Test conversion to combatant stats."""
        stats = deep_one_template.to_combatant_stats()
        assert stats["name"] == "深潜者"
        assert stats["dex"] == 60
        assert stats["fighting"] == 50
        assert stats["dodge"] == 30
        assert stats["hp"] == 15
        assert stats["armor"] == 1

    def test_parse_damage_bonus(self, deep_one_template):
        """Test damage bonus parsing."""
        assert deep_one_template._parse_damage_bonus() == 1  # 1d4 = 1


class TestBestiary:
    """Test bestiary management."""

    @pytest.fixture
    def bestiary(self):
        """Create test bestiary."""
        b = Bestiary()
        b.add(
            CreatureTemplate(
                id="ghoul",
                name="Ghoul",
                name_cn="食尸鬼",
                category=CreatureCategory.MONSTER,
                attributes=CreatureAttributes(),
            )
        )
        b.add(
            CreatureTemplate(
                id="deep_one",
                name="Deep One",
                name_cn="深潜者",
                category=CreatureCategory.MYTHOS,
                attributes=CreatureAttributes(),
            )
        )
        return b

    def test_add_creature(self, bestiary):
        """Test adding a creature."""
        creature = CreatureTemplate(
            id="zombie",
            name="Zombie",
            name_cn="僵尸",
            category=CreatureCategory.UNDEAD,
            attributes=CreatureAttributes(),
        )
        bestiary.add(creature)
        assert bestiary.get("zombie") is not None

    def test_get_creature(self, bestiary):
        """Test retrieving creature by ID."""
        creature = bestiary.get("ghoul")
        assert creature is not None
        assert creature.name_cn == "食尸鬼"

    def test_get_nonexistent(self, bestiary):
        """Test retrieving non-existent creature."""
        assert bestiary.get("nonexistent") is None

    def test_list_all(self, bestiary):
        """Test listing all creatures."""
        creatures = bestiary.list_all()
        assert len(creatures) == 2

    def test_list_by_category(self, bestiary):
        """Test listing creatures by category."""
        monsters = bestiary.list_by_category(CreatureCategory.MONSTER)
        assert len(monsters) == 1
        assert monsters[0].id == "ghoul"

        mythos = bestiary.list_by_category(CreatureCategory.MYTHOS)
        assert len(mythos) == 1
        assert mythos[0].id == "deep_one"

    def test_export_state(self, bestiary):
        """Test exporting bestiary state."""
        state = bestiary.export_state()
        assert "ghoul" in state
        assert "deep_one" in state


class TestBestiaryLoadFromFile:
    """Test loading bestiary from JSON file."""

    def test_load_from_creatures_json(self):
        """Test loading creatures from JSON file."""
        import os

        path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "data",
            "bestiary",
            "creatures.json",
        )
        if os.path.exists(path):
            bestiary = Bestiary.load_from_file(path)
            assert len(bestiary.list_all()) >= 10  # At least 10 creatures

            # Check Deep One exists
            deep_one = bestiary.get("deep_one")
            assert deep_one is not None
            assert deep_one.name_cn == "深潜者"
            assert deep_one.category == CreatureCategory.MYTHOS


class TestCreatureManager:
    """Test creature instance management."""

    @pytest.fixture
    def manager(self):
        """Create creature manager with test bestiary."""
        bestiary = Bestiary()
        bestiary.add(
            CreatureTemplate(
                id="ghoul",
                name="Ghoul",
                name_cn="食尸鬼",
                category=CreatureCategory.MONSTER,
                attributes=CreatureAttributes(
                    str=60, con=50, siz=50, dex=70, int=40, pow=50
                ),
                hp=10,
                fighting=40,
                dodge=35,
                armor=1,
                damage_bonus="+0",
            )
        )
        return CreatureManager(bestiary)

    def test_spawn_creature(self, manager):
        """Test spawning a creature instance."""
        instance = manager.spawn("ghoul")
        assert instance.template_id == "ghoul"
        assert instance.hp == 10
        assert instance.hp_max == 10
        assert instance.is_alive()
        assert instance.name == "食尸鬼"

    def test_spawn_with_custom_name(self, manager):
        """Test spawning with custom name."""
        instance = manager.spawn("ghoul", name="饥饿的食尸鬼")
        assert instance.name == "饥饿的食尸鬼"

    def test_spawn_with_hp_modifier(self, manager):
        """Test spawning with HP modifier."""
        instance = manager.spawn("ghoul", hp_modifier=5)
        assert instance.hp == 15
        assert instance.hp_max == 15

    def test_spawn_invalid_template(self, manager):
        """Test spawning with invalid template."""
        with pytest.raises(ValueError):
            manager.spawn("invalid_template")

    def test_get_instance(self, manager):
        """Test getting a creature instance."""
        instance = manager.spawn("ghoul")
        retrieved = manager.get(instance.instance_id)
        assert retrieved is not None
        assert retrieved.instance_id == instance.instance_id

    def test_remove_instance(self, manager):
        """Test removing a creature instance."""
        instance = manager.spawn("ghoul")
        manager.remove(instance.instance_id)
        assert manager.get(instance.instance_id) is None

    def test_take_damage(self, manager):
        """Test creature taking damage."""
        instance = manager.spawn("ghoul")
        damage = instance.take_damage(5)
        assert damage == 5
        assert instance.hp == 5

    def test_take_excess_damage(self, manager):
        """Test creature taking more damage than HP."""
        instance = manager.spawn("ghoul")
        damage = instance.take_damage(20)
        assert damage == 10  # Only 10 HP to take
        assert instance.hp == 0
        assert not instance.is_alive()

    def test_heal(self, manager):
        """Test creature healing."""
        instance = manager.spawn("ghoul")
        instance.take_damage(8)
        healed = instance.heal(3)
        assert healed == 3
        assert instance.hp == 5

    def test_heal_caps_at_max(self, manager):
        """Test healing doesn't exceed max HP."""
        instance = manager.spawn("ghoul")
        instance.take_damage(5)
        healed = instance.heal(20)
        assert healed == 5  # Only 5 HP to heal
        assert instance.hp == 10

    def test_creature_death(self, manager):
        """Test creature death."""
        instance = manager.spawn("ghoul")
        instance.take_damage(20)
        assert not instance.is_alive()

    def test_mark_seen(self, manager):
        """Test marking creature as seen."""
        instance = manager.spawn("ghoul")
        is_first = instance.mark_seen_by("player1")
        assert is_first is True

        is_first_again = instance.mark_seen_by("player1")
        assert is_first_again is False

    def test_has_seen(self, manager):
        """Test checking if player has seen creature."""
        instance = manager.spawn("ghoul")
        assert not instance.has_seen("player1")
        instance.mark_seen_by("player1")
        assert instance.has_seen("player1")

    def test_list_alive(self, manager):
        """Test listing alive creatures."""
        instance1 = manager.spawn("ghoul")
        instance2 = manager.spawn("ghoul")
        instance1.take_damage(20)

        alive = manager.list_alive()
        assert len(alive) == 1
        assert alive[0].instance_id == instance2.instance_id

    def test_list_by_template(self, manager):
        """Test listing creatures by template."""
        instance1 = manager.spawn("ghoul")
        instance2 = manager.spawn("ghoul")

        by_template = manager.list_by_template("ghoul")
        assert len(by_template) == 2

    def test_clear_dead(self, manager):
        """Test clearing dead creatures."""
        instance1 = manager.spawn("ghoul")
        instance2 = manager.spawn("ghoul")
        instance1.take_damage(20)

        removed = manager.clear_dead()
        assert removed == 1
        assert len(manager.list_alive()) == 1


class TestCreatureCombat:
    """Test creature combat integration."""

    @pytest.fixture
    def ghoul_instance(self):
        """Create a ghoul instance for combat testing."""
        return CreatureInstance(
            instance_id="test-ghoul",
            template_id="ghoul",
            name="Test Ghoul",
            hp=10,
            hp_max=10,
            attributes={
                "str": 60,
                "con": 50,
                "siz": 50,
                "dex": 70,
                "int": 40,
                "pow": 50,
                "fighting": 40,
                "dodge": 35,
                "armor": 1,
            },
        )

    def test_creature_to_combatant(self, ghoul_instance):
        """Test converting creature to combatant."""
        from dm_bot.rules.coc.combat import creature_to_combatant

        combatant = creature_to_combatant(ghoul_instance)
        assert combatant.name == "Test Ghoul"
        assert combatant.dex == 70
        assert combatant.fighting == 40
        assert combatant.dodge == 35
        assert combatant.hp == 10
        assert combatant.armor == 1

    def test_resolve_creature_attack(self, ghoul_instance):
        """Test resolving creature attack."""
        from dm_bot.rules.coc.combat import (
            creature_to_combatant,
            resolve_creature_attack,
            CombatantStats,
        )

        target = CombatantStats(
            name="Investigator",
            dex=50,
            fighting=25,
            dodge=25,
            hp=20,
            hp_max=20,
            armor=0,
        )

        result, updated_target = resolve_creature_attack(
            ghoul_instance,
            target,
            attacker_roll=30,
            defender_roll=50,
        )

        assert result.creature_name == "Test Ghoul"
        assert result.hit is True  # 30 < 50
        assert updated_target.hp < 20


class TestCreatureSanityIntegration:
    """Test creature sanity integration."""

    def test_creature_encounter_sanity_first_time(self):
        """Test SAN loss on first creature encounter."""
        from dm_bot.rules.coc.sanity import resolve_creature_encounter_sanity

        template = CreatureTemplate(
            id="ghoul",
            name="Ghoul",
            name_cn="食尸鬼",
            category=CreatureCategory.MONSTER,
            attributes=CreatureAttributes(),
            san_loss=SanLoss(first_encounter=6, subsequent=1),
        )

        result = resolve_creature_encounter_sanity(
            template,
            investigator_san=50,
            has_seen_before=False,
        )

        assert result.sanity_loss == 6
        assert result.current_san == 50

    def test_creature_encounter_sanity_subsequent(self):
        """Test SAN loss on subsequent creature encounter."""
        from dm_bot.rules.coc.sanity import resolve_creature_encounter_sanity

        template = CreatureTemplate(
            id="ghoul",
            name="Ghoul",
            name_cn="食尸鬼",
            category=CreatureCategory.MONSTER,
            attributes=CreatureAttributes(),
            san_loss=SanLoss(first_encounter=6, subsequent=1),
        )

        result = resolve_creature_encounter_sanity(
            template,
            investigator_san=50,
            has_seen_before=True,
        )

        assert result.sanity_loss == 1

    def test_creature_indefinite_insanity(self):
        """Test indefinite insanity trigger on first encounter."""
        from dm_bot.rules.coc.sanity import resolve_creature_encounter_sanity

        template = CreatureTemplate(
            id="shoggoth",
            name="Shoggoth",
            name_cn="修格斯",
            category=CreatureCategory.MYTHOS,
            attributes=CreatureAttributes(),
            san_loss=SanLoss(first_encounter=10, subsequent=2, indefinite=True),
        )

        result = resolve_creature_encounter_sanity(
            template,
            investigator_san=50,
            has_seen_before=False,
        )

        assert result.sanity_loss == 10
        assert result.insanity_triggered.value in ["temporary", "indefinite"]
