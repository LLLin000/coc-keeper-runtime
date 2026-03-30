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
from dm_bot.router.intent_classifier import IntentClassifier
from dm_bot.router.intent_handler import IntentHandlerRegistry
from dm_bot.router.message_buffer import MessageBuffer
from dm_bot.router.service import RouterService
from dm_bot.rules.compendium import FixtureCompendium
from dm_bot.rules.engine import RulesEngine
from dm_bot.runtime.app import create_app
from dm_bot.runtime.control_service import RuntimeControlService
from dm_bot.runtime.restart_system import run_restart_system
from dm_bot.runtime.smoke_check import run_local_smoke_check
from dm_bot.testing.scenario_runner import ScenarioRunner
from dm_bot.testing.runtime_driver import RuntimeTestDriver
from dm_bot.testing.scenario_dsl import ScenarioRegistry, ScenarioParser
from dm_bot.testing.artifact_writer import ArtifactWriter
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
        semantic_extractor=ModelGuidedArchiveSemanticExtractor(
            model_client=model_client
        ),
        synthesizer=ModelGuidedCharacterSheetSynthesizer(model_client=model_client),
    )
    gameplay = GameplayOrchestrator(
        importer=CharacterImporter(
            sources={"dicecloud_snapshot": DicecloudSnapshotSource(fixtures={})}
        ),
        registry=CharacterRegistry(),
        rules_engine=RulesEngine(
            compendium=FixtureCompendium(baseline="2014", fixtures={})
        ),
    )
    intent_classifier = IntentClassifier(model_client)
    message_buffer = MessageBuffer()
    intent_handler_registry = IntentHandlerRegistry(message_buffer=message_buffer)
    turn_runner = TurnRunner(
        router=RouterService(model_client),
        narrator=NarrationService(model_client),
        gameplay=gameplay,
    )
    session_store = SessionStore()
    session_store.load_sessions(persistence_store.load_sessions())
    turn_coordinator = TurnCoordinator(
        turn_runner=turn_runner, persistence_store=persistence_store
    )
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
        intent_classifier=intent_classifier,
        message_buffer=message_buffer,
        intent_handler_registry=intent_handler_registry,
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
                COCReference(
                    title="克苏鲁公社",
                    url="https://www.cthulhuclub.com",
                    summary="COC 模组、规则与工具入口。",
                )
            ]
        )
    rulebooks = [
        path
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() == ".pdf"
    ]
    investigator_paths = [path for path in root.rglob("*.pdf") if path.parent != root]
    return COCAssetLibrary.from_paths(
        rulebook_paths=rulebooks,
        investigator_paths=investigator_paths,
        community_references=[
            COCReference(
                title="克苏鲁公社",
                url="https://www.cthulhuclub.com",
                summary="COC 模组、规则与工具入口。",
            )
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


def run_control_panel(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    app = create_app(
        control_service=RuntimeControlService(cwd=Path.cwd(), settings=settings)
    )
    uvicorn.run(app, host="127.0.0.1", port=8001)


def run_control_status(*, cwd: Path, settings: Settings | None = None) -> int:
    settings = settings or get_settings()
    state = RuntimeControlService(cwd=cwd, settings=settings).get_state()
    print(state.model_dump_json(indent=2))
    return 0


def run_scenario_cli(
    scenario_path: str | None = None,
    suite: str | None = None,
    run_all: bool = False,
    write_artifacts: bool = True,
    fail_fast: bool = False,
    model_mode: str | None = None,
    seed: int | None = None,
) -> int:
    import asyncio

    registry = ScenarioRegistry()

    if run_all:
        scenarios = registry.scan()
    elif suite:
        scenarios = registry.scan()
        scenarios = {k: v for k, v in scenarios.items() if suite in v.tags}
    elif scenario_path:
        parser = ScenarioParser()
        try:
            scenario = parser.parse(scenario_path)
            scenarios = {scenario.id: scenario}
        except Exception as e:
            print(f"Error parsing scenario: {e}")
            return 1
    else:
        print("Error: Must specify --scenario, --suite, or --all")
        return 1

    if not scenarios:
        print("No scenarios found")
        return 1

    print(f"Found {len(scenarios)} scenario(s)")

    passed = 0
    failed = 0

    for scenario_id, scenario in scenarios.items():
        print(f"\nRunning: {scenario_id}")

        db_path = ":memory:"
        driver = RuntimeTestDriver(
            dice_seed=seed or scenario.fixtures.dice_seed,
            db_path=db_path,
        )

        runner = ScenarioRunner(driver)

        async def run_one() -> None:
            nonlocal passed, failed

            try:
                result = await runner.run(
                    scenario_path=scenario_path or str(scenario.path),
                    write_artifacts=write_artifacts,
                    fail_fast=fail_fast,
                )

                status = "PASSED" if result.passed else "FAILED"
                print(f"  Status: {status}")

                if result.passed:
                    passed += 1
                else:
                    failed += 1
                    if result.failure:
                        print(
                            f"  Failure: {result.failure.code} - {result.failure.message}"
                        )

            except Exception as e:
                print(f"  Error: {e}")
                failed += 1

        asyncio.run(run_one())

        if fail_fast and failed > 0:
            print("\nStopping due to failure (--fail-fast)")
            break

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")

    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dm-bot")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("preflight")
    subparsers.add_parser("run-api")
    subparsers.add_parser("run-bot")
    subparsers.add_parser("smoke-check")
    subparsers.add_parser("restart-system")
    subparsers.add_parser("control-status")
    subparsers.add_parser("run-control-panel")

    run_scenario_parser = subparsers.add_parser("run-scenario")
    run_scenario_parser.add_argument(
        "--scenario", type=str, help="Path to scenario YAML file"
    )
    run_scenario_parser.add_argument(
        "--suite",
        type=str,
        help="Run all scenarios in a suite (acceptance, contract, chaos, recovery)",
    )
    run_scenario_parser.add_argument(
        "--all", action="store_true", help="Run all scenarios"
    )
    run_scenario_parser.add_argument(
        "--write-artifacts", action="store_true", default=True
    )
    run_scenario_parser.add_argument(
        "--no-artifacts", action="store_true", help="Skip writing artifacts"
    )
    run_scenario_parser.add_argument(
        "--fail-fast", action="store_true", help="Stop on first failure"
    )
    run_scenario_parser.add_argument(
        "--keep-db", action="store_true", help="Keep temp DB files after run"
    )
    run_scenario_parser.add_argument(
        "--model-mode",
        type=str,
        choices=["fake_contract", "recorded", "live"],
        help="Override model_mode",
    )
    run_scenario_parser.add_argument("--seed", type=int, help="Override dice_seed")

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
    if args.command == "control-status":
        return run_control_status(cwd=Path.cwd())
    if args.command == "run-control-panel":
        run_control_panel()
        return 0
    if args.command == "run-scenario":
        write_artifacts = not getattr(args, "no_artifacts", False)
        if getattr(args, "all", False):
            write_artifacts = True

        result = run_scenario_cli(
            scenario_path=getattr(args, "scenario", None),
            suite=getattr(args, "suite", None),
            run_all=getattr(args, "all", False),
            write_artifacts=write_artifacts,
            fail_fast=getattr(args, "fail_fast", False),
            model_mode=getattr(args, "model_mode", None),
            seed=getattr(args, "seed", None),
        )
        return result
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
