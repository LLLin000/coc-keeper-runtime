import asyncio

from dm_bot.characters.models import (
    CharacterRecord,
    CharacterSourceInfo,
    CharacterSourceLabel,
    COCAttributes,
    COCInvestigatorProfile,
    HitPoints,
    AbilityScores,
)
from dm_bot.discord_bot.commands import BotCommands
from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
from dm_bot.orchestrator.session_store import SessionStore
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine
from tests.fakes.discord import fake_interaction


def build_gameplay() -> GameplayOrchestrator:
    return GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={})
        ),
    )


def test_gameplay_creates_and_updates_investigator_panel() -> None:
    gameplay = build_gameplay()

    panel = gameplay.ensure_investigator_panel(
        user_id="user-1", display_name="Alice", role="investigator"
    )
    gameplay.apply_panel_update(user_id="user-1", san=-3, hp=-1, note="目睹惨案")

    assert panel.role == "investigator"
    snapshot = gameplay.investigator_panel_snapshot("user-1")
    assert snapshot["name"] == "Alice"
    assert snapshot["san"] == 47
    assert snapshot["hp"] == 9
    assert "目睹惨案" in snapshot["journal"][-1]


def test_importing_coc_character_syncs_panel() -> None:
    gameplay = build_gameplay()
    character = CharacterRecord(
        source=CharacterSourceInfo(
            provider="coc_pregen", label=CharacterSourceLabel.COC_PREGEN
        ),
        external_id="jessie",
        name="Jessie Williams",
        species="human",
        hp=HitPoints(current=11, maximum=11, temporary=0),
        abilities=AbilityScores(
            strength=0,
            dexterity=0,
            constitution=0,
            intelligence=0,
            wisdom=0,
            charisma=0,
        ),
        coc=COCInvestigatorProfile(
            occupation="记者",
            age=24,
            san=60,
            hp=11,
            mp=12,
            luck=45,
            attributes=COCAttributes(
                str=45, con=55, dex=70, app=80, pow=60, siz=55, int=75, edu=65
            ),
            skills={"图书馆使用": 60},
        ),
    )

    gameplay.registry.put("user-1", character)
    gameplay.sync_panel_from_character("user-1")

    snapshot = gameplay.investigator_panel_snapshot("user-1")
    assert snapshot["name"] == "Jessie Williams"
    assert snapshot["occupation"] == "记者"
    assert snapshot["skills"]["图书馆使用"] == 60


def test_sheet_command_surfaces_private_knowledge_and_role() -> None:
    store = SessionStore()
    store.bind_campaign(
        campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1"
    )
    gameplay = build_gameplay()
    gameplay.ensure_investigator_panel(
        user_id="user-1", display_name="Alice", role="magical_girl"
    )
    gameplay.adventure_state = {
        "knowledge_log": [
            {"scope": "public", "title": "车祸", "content": "你们都见到了惨烈车祸。"},
            {
                "scope": "player",
                "recipient_user_id": "user-1",
                "title": "论坛照片",
                "content": "你认出了金发少女。",
            },
        ]
    }
    commands = BotCommands(
        settings=None, session_store=store, turn_coordinator=None, gameplay=gameplay
    )
    interaction = fake_interaction()

    asyncio.run(commands.show_sheet(interaction))

    text = interaction.response.messages[0][0]
    assert "Alice" in text
    assert "magical_girl" in text
    assert "论坛照片" in text
