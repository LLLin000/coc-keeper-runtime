from pathlib import Path

from dm_bot.characters.importer import CharacterImporter
from dm_bot.characters.sources import DicecloudSnapshotSource
from dm_bot.coc.archive import InvestigatorArchiveRepository
from dm_bot.gameplay.combat import Combatant
from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
from dm_bot.orchestrator.session_store import (
    CampaignRole,
    CampaignMember,
    CampaignCharacterInstance,
    SessionStore,
)
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
                        "attacks": [
                            {
                                "name": "Longbow",
                                "attack_bonus": 5,
                                "damage": "1d8+3 piercing",
                            }
                        ],
                        "spellcasting": {
                            "ability": "wisdom",
                            "save_dc": 12,
                            "attack_bonus": 4,
                        },
                        "resources": {"spell_slots_1": 3},
                    }
                }
            )
        }
    )
    return GameplayOrchestrator(
        importer=importer,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={})
        ),
    )


def test_persistence_store_saves_and_restores_campaign_state(tmp_path: Path) -> None:
    gameplay = build_gameplay()
    gameplay.import_character(
        user_id="user-1", provider="dicecloud_snapshot", external_id="char-1"
    )
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
    sessions.bind_campaign(
        campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1"
    )
    sessions.join_campaign(channel_id="chan-1", user_id="user-2")
    sessions.bind_character(
        channel_id="chan-1", user_id="user-1", character_name="Alice"
    )
    sessions.bind_archive_channel(guild_id="guild-1", channel_id="archive-1")
    sessions.bind_admin_channel(guild_id="guild-1", channel_id="admin-1")
    sessions.select_archive_profile(
        channel_id="chan-1", user_id="user-1", profile_id="profile-1"
    )

    store.save_sessions(sessions.dump_sessions())
    restored = store.load_sessions()

    assert restored["chan-1"]["campaign_id"] == "camp-1"
    assert set(restored["chan-1"]["member_ids"]) == {"user-1", "user-2"}
    assert restored["chan-1"]["active_characters"]["user-1"] == "Alice"
    assert restored["chan-1"]["selected_profiles"]["user-1"] == "profile-1"
    assert restored["_meta"]["archive_channels"]["guild-1"] == "archive-1"
    assert restored["_meta"]["admin_channels"]["guild-1"] == "admin-1"


def test_persistence_store_saves_and_restores_archive_profiles(tmp_path: Path) -> None:
    store = PersistenceStore(tmp_path / "campaign.sqlite3")
    repo = InvestigatorArchiveRepository()
    profile = repo.create_profile(
        user_id="user-1",
        name="林秋",
        occupation="记者",
        age=26,
        background="夜班记者",
        disposition="冷静",
        favored_skills=["图书馆使用", "聆听"],
        generation={
            "str": 50,
            "con": 55,
            "dex": 60,
            "app": 65,
            "pow": 70,
            "siz": 50,
            "int": 75,
            "edu": 80,
            "luck": 45,
        },
    )

    store.save_archive_profiles(repo.export_state())
    restored = InvestigatorArchiveRepository()
    restored.import_state(store.load_archive_profiles())

    restored_profile = restored.get_profile("user-1", profile.profile_id)
    assert restored_profile.name == "林秋"
    assert restored_profile.coc.occupation == "记者"
    assert restored_profile.status == "active"


def test_archive_repository_imports_older_profile_payload_with_new_defaults() -> None:
    repo = InvestigatorArchiveRepository()
    legacy_payload = {
        "user-1": {
            "profile-1": {
                "profile_id": "profile-1",
                "user_id": "user-1",
                "name": "林秋",
                "occupation": "记者",
                "age": 26,
                "background": "夜班记者",
                "disposition": "冷静",
                "favored_skills": ["图书馆使用", "聆听"],
                "portrait_summary": "夜班记者。",
                "status": "active",
                "finishing": {
                    "recommended_occupation_skills": [],
                    "recommended_interest_skills": [],
                    "allowed_adjustments": [],
                    "rules_note": "",
                },
                "coc": {
                    "occupation": "记者",
                    "age": 26,
                    "san": 70,
                    "hp": 10,
                    "mp": 14,
                    "luck": 45,
                    "build": 0,
                    "damage_bonus": "0",
                    "move_rate": 8,
                    "attributes": {
                        "str": 50,
                        "con": 55,
                        "dex": 60,
                        "app": 65,
                        "pow": 70,
                        "siz": 50,
                        "int": 75,
                        "edu": 80,
                    },
                    "skills": {"图书馆使用": 50, "聆听": 50},
                },
            }
        }
    }

    repo.import_state(legacy_payload)
    profile = repo.get_profile("user-1", "profile-1")

    assert profile.schema_version == 2
    assert profile.birthplace == ""
    assert profile.residence == ""
    assert profile.family == ""
    assert profile.education_background == ""


def test_persistence_round_trip_campaign_members(tmp_path: Path) -> None:
    store = PersistenceStore(tmp_path / "campaign.sqlite3")
    sessions = SessionStore()
    sessions.bind_campaign(
        campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1"
    )
    sessions.join_campaign(channel_id="chan-1", user_id="user-2")
    sessions.bind_character(
        channel_id="chan-1", user_id="user-1", character_name="Alice"
    )
    sessions.select_archive_profile(
        channel_id="chan-1", user_id="user-1", profile_id="prof-1"
    )

    store.save_sessions(sessions.dump_sessions())
    restored_payload = store.load_sessions()

    restored = SessionStore()
    restored.load_sessions(restored_payload)

    session = restored.get_by_channel("chan-1")
    assert session is not None

    assert "user-1" in session.members
    assert "user-2" in session.members
    assert session.members["user-1"].role == CampaignRole.OWNER
    assert session.members["user-2"].role == CampaignRole.MEMBER
    assert session.members["user-1"].active_character_name == "Alice"
    assert session.members["user-1"].selected_profile_id == "prof-1"

    assert session.member_ids == {"user-1", "user-2"}
    assert session.active_characters["user-1"] == "Alice"
    assert session.selected_profiles["user-1"] == "prof-1"


def test_persistence_legacy_format_reconstructs_members(tmp_path: Path) -> None:
    store = PersistenceStore(tmp_path / "campaign.sqlite3")
    sessions = SessionStore()
    sessions.bind_campaign(
        campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1"
    )
    sessions.join_campaign(channel_id="chan-1", user_id="user-2")

    payload = sessions.dump_sessions()
    del payload["chan-1"]["members"]
    del payload["chan-1"]["character_instances"]

    restored = SessionStore()
    restored.load_sessions(payload)

    session = restored.get_by_channel("chan-1")
    assert session is not None
    assert "user-1" in session.members
    assert "user-2" in session.members
    assert session.members["user-1"].role == CampaignRole.OWNER
    assert session.members["user-2"].role == CampaignRole.MEMBER


# --- :memory: mode tests (E88) ---


def test_memory_mode_tables_exist_after_init() -> None:
    """Prove all four tables are created and queryable in :memory: mode."""
    store = PersistenceStore(":memory:")
    conn = store._connect()
    rows = conn.execute(
        "select name from sqlite_master where type='table' order by name"
    ).fetchall()
    table_names = {row[0] for row in rows}
    expected = {
        "archive_profiles",
        "campaign_events",
        "campaign_sessions",
        "campaign_state",
    }
    assert expected.issubset(table_names), f"Missing tables: {expected - table_names}"
    store.close()


def test_memory_mode_save_and_load_campaign_state() -> None:
    """Prove save/load campaign_state works across the same :memory: database."""
    store = PersistenceStore(":memory:")
    store.save_campaign_state("camp-1", {"key": "value"})
    result = store.load_campaign_state("camp-1")
    assert result == {"key": "value"}
    store.close()


def test_memory_mode_save_and_load_sessions() -> None:
    """Prove save/load sessions works across the same :memory: database."""
    store = PersistenceStore(":memory:")
    store.save_sessions({"s1": {"members": []}})
    result = store.load_sessions()
    assert result == {"s1": {"members": []}}
    store.close()


def test_memory_mode_multiple_operations_share_connection() -> None:
    """Prove all CRUD operations use the same shared database."""
    store = PersistenceStore(":memory:")
    store.save_campaign_state("camp-1", {"phase": "onboarding"})
    store.save_sessions({"chan-1": {"campaign_id": "camp-1", "member_ids": []}})
    store.append_event(
        campaign_id="camp-1",
        trace_id="t1",
        event_type="session.started",
        payload={"user": "alice"},
    )

    state = store.load_campaign_state("camp-1")
    assert state["phase"] == "onboarding"

    sessions = store.load_sessions()
    assert sessions["chan-1"]["campaign_id"] == "camp-1"

    events = store.list_events("camp-1")
    assert len(events) == 1
    assert events[0]["event_type"] == "session.started"
    store.close()


def test_memory_mode_close_releases_connection() -> None:
    """Prove close() releases the shared connection."""
    store = PersistenceStore(":memory:")
    assert store._conn is not None
    store.close()
    assert store._conn is None
