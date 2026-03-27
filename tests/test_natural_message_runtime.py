import asyncio

from dm_bot.discord_bot.commands import BotCommands
from dm_bot.gameplay.combat import Combatant
from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
from dm_bot.orchestrator.session_store import SessionStore
from dm_bot.persistence.store import PersistenceStore
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine


class StubTurnCoordinator:
    def __init__(self, reply: str = "DM reply") -> None:
        self.reply = reply
        self.calls: list[tuple[str, str, str, str]] = []

    async def handle_turn(self, *, campaign_id: str, channel_id: str, user_id: str, content: str):
        self.calls.append((campaign_id, channel_id, user_id, content))
        return type("Result", (), {"reply": self.reply})()


def build_gameplay() -> GameplayOrchestrator:
    return GameplayOrchestrator(
        importer=None,
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={})),
    )


def test_natural_message_is_forwarded_for_joined_member() -> None:
    store = SessionStore()
    store.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
    coordinator = StubTurnCoordinator()
    commands = BotCommands(settings=None, session_store=store, turn_coordinator=coordinator, gameplay=build_gameplay())

    reply = asyncio.run(
        commands.handle_channel_message(
            channel_id="chan-1",
            guild_id="guild-1",
            user_id="user-1",
            content="我推开门看看里面有什么。",
            mention_count=0,
        )
    )

    assert reply == "DM reply"
    assert coordinator.calls == [("camp-1", "chan-1", "user-1", "我推开门看看里面有什么。")]


def test_natural_message_ignored_for_ooc_text() -> None:
    store = SessionStore()
    store.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
    coordinator = StubTurnCoordinator()
    commands = BotCommands(settings=None, session_store=store, turn_coordinator=coordinator, gameplay=build_gameplay())

    reply = asyncio.run(
        commands.handle_channel_message(
            channel_id="chan-1",
            guild_id="guild-1",
            user_id="user-1",
            content="//先等一下",
            mention_count=0,
        )
    )

    assert reply is None
    assert coordinator.calls == []


def test_natural_message_rejects_non_active_combatant() -> None:
    store = SessionStore()
    store.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
    store.join_campaign(channel_id="chan-1", user_id="user-2")
    store.bind_character(channel_id="chan-1", user_id="user-1", character_name="Hero")
    store.bind_character(channel_id="chan-1", user_id="user-2", character_name="Rogue")
    gameplay = build_gameplay()
    gameplay.start_combat(
        combatants=[
            Combatant(name="Hero", initiative=15, hit_points=20, armor_class=15),
            Combatant(name="Rogue", initiative=10, hit_points=18, armor_class=14),
        ]
    )
    coordinator = StubTurnCoordinator()
    commands = BotCommands(settings=None, session_store=store, turn_coordinator=coordinator, gameplay=gameplay)

    reply = asyncio.run(
        commands.handle_channel_message(
            channel_id="chan-1",
            guild_id="guild-1",
            user_id="user-2",
            content="我朝哥布林射箭。",
            mention_count=0,
        )
    )

    assert "当前轮到" in reply
    assert "Hero" in reply
    assert coordinator.calls == []


def test_natural_message_works_after_session_restore(tmp_path) -> None:
    persistence = PersistenceStore(tmp_path / "runtime.sqlite3")
    original_store = SessionStore()
    original_store.bind_campaign(campaign_id="camp-1", channel_id="chan-1", guild_id="guild-1", owner_id="user-1")
    persistence.save_sessions(original_store.dump_sessions())

    restored_store = SessionStore()
    restored_store.load_sessions(persistence.load_sessions())
    coordinator = StubTurnCoordinator()
    commands = BotCommands(
        settings=None,
        session_store=restored_store,
        turn_coordinator=coordinator,
        gameplay=build_gameplay(),
        persistence_store=persistence,
    )

    reply = asyncio.run(
        commands.handle_channel_message(
            channel_id="chan-1",
            guild_id="guild-1",
            user_id="user-1",
            content="我检查钟表。",
            mention_count=0,
        )
    )

    assert reply == "DM reply"
    assert coordinator.calls == [("camp-1", "chan-1", "user-1", "我检查钟表。")]
