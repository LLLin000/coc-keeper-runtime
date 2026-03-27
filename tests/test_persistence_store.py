from pathlib import Path

from dm_bot.characters.importer import CharacterImporter
from dm_bot.characters.sources import DicecloudSnapshotSource
from dm_bot.gameplay.combat import Combatant
from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
from dm_bot.orchestrator.session_store import SessionStore
from dm_bot.persistence.store import PersistenceStore
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine


def build_gameplay() -> GameplayOrchestrator:
    importer = CharacterImporter(
        sources={
            "dicecloud_snapshot": DicecloudSnapshotSource(
                fixtures={
                    "char-1": {
                        "id": "char-1",
                        "name": "林地游侠",
                        "species": "Wood Elf",
                        "classes": [{"name": "Ranger", "level": 3}],
                        "proficiency_bonus": 2,
                        "armor_class": 15,
                        "speed": 35,
                        "hp": {"current": 24, "maximum": 24, "temporary": 0},
                        "abilities": {
                            "strength": 10,
                            "dexterity": 16,
                            "constitution": 14,
                            "intelligence": 12,
                            "wisdom": 15,
                            "charisma": 8,
                        },
                        "skills": {"stealth": 5},
                        "attacks": [{"name": "Longbow", "attack_bonus": 5, "damage": "1d8+3 piercing"}],
                        "spellcasting": {"ability": "wisdom", "save_dc": 12, "attack_bonus": 4},
                        "resources": {"spell_slots_1": 3},
                    }
                }
            )
        }
    )
    return GameplayOrchestrator(
        importer=importer,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={})),
    )


def test_persistence_store_saves_and_restores_campaign_state(tmp_path: Path) -> None:
    gameplay = build_gameplay()
    gameplay.import_character(user_id="user-1", provider="dicecloud_snapshot", external_id="char-1")
    gameplay.enter_scene(speakers=["守卫", "老板"])
    gameplay.start_combat(
        combatants=[
            Combatant(name="Hero", initiative=15, hit_points=20, armor_class=15),
            Combatant(name="Goblin", initiative=12, hit_points=7, armor_class=13),
        ]
    )
    store = PersistenceStore(tmp_path / "campaign.sqlite3")

    store.save_campaign_state("camp-1", gameplay.export_state())
    restored = store.load_campaign_state("camp-1")

    assert restored["mode"]["mode"] == "combat"
    assert restored["combat"]["order"] == ["Hero", "Goblin"]
    assert "user-1" in restored["registry"]


def test_persistence_store_appends_trace_linked_events(tmp_path: Path) -> None:
    store = PersistenceStore(tmp_path / "campaign.sqlite3")

    store.append_event(
        campaign_id="camp-1",
        trace_id="trace-1",
        event_type="turn.completed",
        payload={"reply": "战斗开始。"},
    )

    events = store.list_events("camp-1")

    assert len(events) == 1
    assert events[0]["trace_id"] == "trace-1"


def test_persistence_store_saves_and_restores_campaign_sessions(tmp_path: Path) -> None:
    store = PersistenceStore(tmp_path / "campaign.sqlite3")
    sessions = SessionStore()
    sessions.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
    sessions.join_campaign(channel_id="chan-1", user_id="user-2")
    sessions.bind_character(channel_id="chan-1", user_id="user-1", character_name="Alice")

    store.save_sessions(sessions.dump_sessions())
    restored = store.load_sessions()

    assert restored["chan-1"]["campaign_id"] == "camp-1"
    assert set(restored["chan-1"]["member_ids"]) == {"user-1", "user-2"}
    assert restored["chan-1"]["active_characters"]["user-1"] == "Alice"
