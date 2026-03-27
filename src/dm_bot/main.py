from dataclasses import dataclass

from dm_bot.characters.importer import CharacterImporter
from dm_bot.characters.sources import DicecloudSnapshotSource
from dm_bot.config import Settings, get_settings
from dm_bot.discord_bot.client import create_discord_bot
from dm_bot.discord_bot.commands import BotCommands
from dm_bot.models.ollama_client import OllamaClient
from dm_bot.narration.service import NarrationService
from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
from dm_bot.orchestrator.session_store import SessionStore
from dm_bot.orchestrator.turn_runner import TurnRunner
from dm_bot.orchestrator.turns import TurnCoordinator
from dm_bot.router.service import RouterService
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine
from dm_bot.runtime.app import create_app


@dataclass
class RuntimeBundle:
    settings: Settings
    app: object
    discord_bot: object


def build_runtime(settings: Settings | None = None) -> RuntimeBundle:
    settings = settings or get_settings()
    model_client = OllamaClient(settings)
    gameplay = GameplayOrchestrator(
        importer=CharacterImporter(sources={"dicecloud_snapshot": DicecloudSnapshotSource(fixtures={})}),
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(compendium=FixtureCompendium(baseline="2014", fixtures={})),
    )
    turn_runner = TurnRunner(
        router=RouterService(model_client),
        narrator=NarrationService(model_client),
        gameplay=gameplay,
    )
    session_store = SessionStore()
    turn_coordinator = TurnCoordinator(turn_runner=turn_runner)
    handlers = BotCommands(
        settings=settings,
        session_store=session_store,
        turn_coordinator=turn_coordinator,
        gameplay=gameplay,
    )
    return RuntimeBundle(
        settings=settings,
        app=create_app(),
        discord_bot=create_discord_bot(handlers=handlers),
    )
