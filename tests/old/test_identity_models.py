from __future__ import annotations

import pytest
from datetime import datetime

from dm_bot.orchestrator.session_store import (
    CampaignRole,
    CampaignMember,
    CampaignCharacterInstance,
)


def test_campaign_member_constructs_with_defaults() -> None:
    member = CampaignMember(user_id="u1", campaign_id="c1")
    assert member.role == CampaignRole.MEMBER
    assert member.ready is False
    assert member.selected_profile_id is None
    assert member.active_character_name is None
    assert member.joined_at is not None


def test_campaign_member_owner_role() -> None:
    member = CampaignMember(user_id="u1", campaign_id="c1", role=CampaignRole.OWNER)
    assert member.role == CampaignRole.OWNER


def test_campaign_member_admin_role() -> None:
    member = CampaignMember(user_id="u1", campaign_id="c1", role=CampaignRole.ADMIN)
    assert member.role == CampaignRole.ADMIN


def test_campaign_member_serializes_to_dict() -> None:
    member = CampaignMember(user_id="u1", campaign_id="c1", role=CampaignRole.ADMIN)
    data = member.model_dump()
    assert data["user_id"] == "u1"
    assert data["role"] == "admin"


def test_campaign_member_deserializes_from_dict() -> None:
    data = {
        "user_id": "u1",
        "campaign_id": "c1",
        "joined_at": "2026-03-29T10:00:00",
        "role": "admin",
        "ready": True,
        "selected_profile_id": "p1",
        "active_character_name": "Alice",
    }
    member = CampaignMember.model_validate(data)
    assert member.ready is True
    assert member.active_character_name == "Alice"


def test_character_instance_constructs_with_defaults() -> None:
    inst = CampaignCharacterInstance(
        campaign_id="c1", user_id="u1", character_name="Alice"
    )
    assert inst.source == "archive"
    assert inst.archive_profile_id is None
    assert inst.panel_id is None
    assert inst.created_at is not None


def test_character_instance_serializes_to_dict() -> None:
    inst = CampaignCharacterInstance(
        campaign_id="c1",
        user_id="u1",
        character_name="Alice",
        archive_profile_id="prof-1",
        source="archive",
    )
    data = inst.model_dump()
    assert data["archive_profile_id"] == "prof-1"
    assert data["source"] == "archive"


def test_character_instance_deserializes_from_dict() -> None:
    data = {
        "campaign_id": "c1",
        "user_id": "u1",
        "character_name": "Alice",
        "archive_profile_id": None,
        "panel_id": None,
        "created_at": "2026-03-29T10:00:00",
        "source": "ad_hoc",
    }
    inst = CampaignCharacterInstance.model_validate(data)
    assert inst.source == "ad_hoc"
