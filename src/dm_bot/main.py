import argparse
import asyncio
from dataclasses import dataclass
from pathlib import Path

from dm_bot.characters.importer import CharacterImporter
from dm_bot.characters.sources import DicecloudSnapshotSource
from dm_bot.coc.archive import InvestigatorArchiveRepository
from dm_bot.coc.assets import COCAssetLibrary, COCReference
from dm_bot.coc.builder import (
    ConversationalCharacterBuilder,
    ModelGuidedArchiveSemanticExtractor,
    ModelGuidedCharacterSheetSynthesizer,
    ModelGuidedInterviewPlanner,
)
from dm_bot.config import Settings, get_settings
from dm_bot.diagnostics.service import DiagnosticsService
from dm_bot.discord_bot.client import create_discord_bot
from dm_bot.discord_bot.commands import BotCommands
from dm_bot.models.ollama_client import OllamaClient
from dm_bot.narration.service import NarrationService
from dm_bot.orchestrator.gameplay import CharacterRegistry, GameplayOrchestrator
from dm_bot.orchestrator.session_store import SessionStore
from dm_bot.orchestrator.turn_runner import TurnRunner
from dm_bot.orchestrator.turns import TurnCoordinator
from dm_bot.persistence.store import PersistenceStore
from dm_bot.router.service import RouterService
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine
from dm_bot.runtime.app import create_app
from dm_bot.runtime.restart_system import run_restart_system
from dm_bot.runtime.smoke_check import run_local_smoke_check
import uvicorn


@dataclass
class RuntimeBundle:
    settings: Settings
    app: object
    discord_bot: object


def describe_runtime(settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    token_status = "configured" if settings.discord_token else "missing"
    return (
        f"discord_token={token_status}\n"
        f"discord_public_key={'configured' if settings.discord_public_key else 'missing'}\n"
        f"router_model={settings.router_model}\n"
        f"narrator_model={settings.narrator_model}\n"
        f"ollama_base_url={settings.ollama_base_url}\n"
        f"coc_asset_root={settings.coc_asset_root}"
    )


def build_runtime(settings: Settings | None = None) -> RuntimeBundle:
    settings = settings or get_settings()
    model_client = OllamaClient(settings)
    persistence_store = PersistenceStore(Path("dm_bot.sqlite3"))
    coc_assets = build_coc_assets(settings)
    archive_repository = InvestigatorArchiveRepository()
    archive_repository.import_state(persistence_store.load_archive_profiles())
    character_builder = ConversationalCharacterBuilder(
        archive_repository=archive_repository,
        interview_planner=ModelGuidedInterviewPlanner(model_client=model_client),
        semantic_extractor=ModelGuidedArchiveSemanticExtractor(model_client=model_client),
        synthesizer=ModelGuidedCharacterSheetSynthesizer(model_client=model_client),
    )
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
    session_store.load_sessions(persistence_store.load_sessions())
    turn_coordinator = TurnCoordinator(turn_runner=turn_runner, persistence_store=persistence_store)
    handlers = BotCommands(
        settings=settings,
        session_store=session_store,
        turn_coordinator=turn_coordinator,
        gameplay=gameplay,
        diagnostics=DiagnosticsService(
            persistence_store,
            session_store=session_store,
            archive_repository=archive_repository,
        ),
        persistence_store=persistence_store,
        coc_assets=coc_assets,
        archive_repository=archive_repository,
        character_builder=character_builder,
    )
    return RuntimeBundle(
        settings=settings,
        app=create_app(),
        discord_bot=create_discord_bot(handlers=handlers, settings=settings),
    )


def build_coc_assets(settings: Settings) -> COCAssetLibrary:
    root = Path(settings.coc_asset_root)
    if not root.exists():
        return COCAssetLibrary(
            community_references=[
                COCReference(title="克苏鲁公社", url="https://www.cthulhuclub.com", summary="COC 模组、规则与工具入口。")
            ]
        )
    rulebooks = [path for path in root.iterdir() if path.is_file() and path.suffix.lower() == ".pdf"]
    investigator_paths = [path for path in root.rglob("*.pdf") if path.parent != root]
    return COCAssetLibrary.from_paths(
        rulebook_paths=rulebooks,
        investigator_paths=investigator_paths,
        community_references=[
            COCReference(title="克苏鲁公社", url="https://www.cthulhuclub.com", summary="COC 模组、规则与工具入口。")
        ],
    )


async def run_discord_bot(settings: Settings | None = None) -> None:
    bundle = build_runtime(settings)
    if not bundle.settings.discord_token:
        raise RuntimeError("DM_BOT_DISCORD_TOKEN is required to start the Discord bot")
    await bundle.discord_bot.start(bundle.settings.discord_token)


def run_api(settings: Settings | None = None) -> None:
    bundle = build_runtime(settings)
    uvicorn.run(bundle.app, host="127.0.0.1", port=8000)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dm-bot")
    parser.add_argument(
        "command",
        choices=["preflight", "run-api", "run-bot", "smoke-check", "restart-system"],
    )
    args = parser.parse_args(argv)

    if args.command == "preflight":
        print(describe_runtime())
        return 0
    if args.command == "run-api":
        run_api()
        return 0
    if args.command == "run-bot":
        asyncio.run(run_discord_bot())
        return 0
    if args.command == "smoke-check":
        return run_local_smoke_check(cwd=Path.cwd())
    if args.command == "restart-system":
        return run_restart_system(cwd=Path.cwd())
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
