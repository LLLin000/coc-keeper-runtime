"""CHAR-01/03: Character creation and archive persistence tests."""

import pytest
from pathlib import Path
from dm_bot.characters.models import (
    CharacterRecord,
    CharacterSourceInfo,
    CharacterSourceLabel,
    COCInvestigatorProfile,
    COCAttributes,
)
from dm_bot.persistence.store import PersistenceStore


def test_character_record_full_coc_profile():
    """CHAR-01: CharacterRecord can be created with full COCInvestigatorProfile."""
    profile = COCInvestigatorProfile(
        occupation="记者",
        age=34,
        san=65,
        hp=12,
        mp=8,
        luck=45,
        build=1,
        damage_bonus="1d4",
        move_rate=7,
        attributes=COCAttributes(
            str=55, con=60, dex=70, app=65, pow=75, siz=50, int=80, edu=85
        ),
        skills={"图书馆使用": 60, "说服": 55, "闪避": 50},
    )
    record = CharacterRecord(
        source=CharacterSourceInfo(
            provider="coc_pereg", label=CharacterSourceLabel.COC_PREGEN
        ),
        external_id="inv-001",
        name="张记者",
        species="人类",
        coc=profile,
    )
    assert record.name == "张记者"
    assert record.coc.san == 65
    assert record.coc.skills["图书馆使用"] == 60


def test_character_record_skills_from_coc_profile():
    """CHAR-01: CharacterRecord skills dict populated from COCInvestigatorProfile."""
    profile = COCInvestigatorProfile(
        occupation="私家侦探",
        age=40,
        san=60,
        hp=14,
        mp=10,
        luck=50,
        build=0,
        damage_bonus="0",
        move_rate=8,
        attributes=COCAttributes(
            str=50, con=55, dex=65, app=60, pow=70, siz=55, int=85, edu=80
        ),
        skills={"侦查": 65, "跟踪": 50, "说服": 55},
    )
    record = CharacterRecord(
        source=CharacterSourceInfo(
            provider="coc_pereg", label=CharacterSourceLabel.COC_PREGEN
        ),
        external_id="inv-002",
        name="王侦探",
        species="人类",
        coc=profile,
    )
    assert record.coc is not None
    assert "侦查" in record.coc.skills
    assert record.coc.skills["侦查"] == 65


def test_character_record_source_info():
    """CHAR-01: CharacterRecord with COC source has correct CharacterSourceInfo."""
    record = CharacterRecord(
        source=CharacterSourceInfo(
            provider="beyond", label=CharacterSourceLabel.COC_PREGEN
        ),
        external_id="beyond-123",
        name="王侦探",
        species="人类",
    )
    assert record.source.provider == "beyond"
    assert record.source.label == CharacterSourceLabel.COC_PREGEN


def test_character_record_round_trip():
    """CHAR-01: CharacterRecord can be serialized to dict and back without data loss."""
    record = CharacterRecord(
        source=CharacterSourceInfo(
            provider="coc_pereg", label=CharacterSourceLabel.COC_PREGEN
        ),
        external_id="inv-001",
        name="张记者",
        species="人类",
        coc=COCInvestigatorProfile(
            occupation="记者",
            age=34,
            san=65,
            hp=12,
            mp=8,
            luck=45,
            build=1,
            damage_bonus="1d4",
            move_rate=7,
            attributes=COCAttributes(
                str=55, con=60, dex=70, app=65, pow=75, siz=50, int=80, edu=85
            ),
            skills={"图书馆使用": 60},
        ),
    )
    data = record.model_dump()
    restored = CharacterRecord.model_validate(data)
    assert restored.name == record.name
    assert restored.coc.san == record.coc.san
    assert restored.coc.occupation == record.coc.occupation


def test_archive_persistence_save_load(tmp_path):
    """CHAR-03: save_archive_profiles persists CharacterRecord list and load retrieves it."""
    store = PersistenceStore(tmp_path / "test_archive1.db")
    profiles = {
        "inv-001": {"name": "张记者", "coc": {"san": 65, "hp": 12}},
        "inv-002": {"name": "王侦探", "coc": {"san": 50, "hp": 10}},
    }
    store.save_archive_profiles(profiles)
    loaded = store.load_archive_profiles()
    assert "inv-001" in loaded
    assert loaded["inv-001"]["name"] == "张记者"
    assert loaded["inv-001"]["coc"]["san"] == 65
    assert "inv-002" in loaded
    assert loaded["inv-002"]["name"] == "王侦探"


def test_archive_empty_loads_as_empty_dict(tmp_path):
    """CHAR-03: Empty archive loads as empty dict."""
    store = PersistenceStore(tmp_path / "test_archive2.db")
    loaded = store.load_archive_profiles()
    assert loaded == {}


def test_archive_round_trip_without_data_loss(tmp_path):
    """CHAR-03: Archive round-trips through save/load without data loss."""
    store = PersistenceStore(tmp_path / "test_archive3.db")
    original = {
        "inv-001": {
            "name": "张记者",
            "coc": {"san": 65, "hp": 12, "mp": 8, "luck": 45},
            "source": {"provider": "coc_pereg", "label": "coc_pregen"},
        },
        "inv-002": {
            "name": "王侦探",
            "coc": {"san": 50, "hp": 10, "mp": 9, "luck": 40},
            "source": {"provider": "beyond", "label": "coc_pregen"},
        },
    }
    store.save_archive_profiles(original)
    loaded = store.load_archive_profiles()
    assert loaded == original
