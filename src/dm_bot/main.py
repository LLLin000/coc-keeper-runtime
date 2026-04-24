"""Main entry point for Discord AI Keeper."""

import argparse
import asyncio
from pathlib import Path

from dm_bot.config import Settings, get_settings
from dm_bot.discord_bot.commands import BotCommands
from dm_bot.narrator.client import SimpleNarrator
from dm_bot.scene.round import Round
from dm_bot.store.db import Store
from dm_bot.adventure.loader import AdventureLoader


def describe_runtime(settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    token_status = "configured" if settings.discord_token else "missing"
    return (
        f"discord_token={token_status}\n"
        f"narrator_model={settings.narrator_model}\n"
        f"ollama_base_url={settings.ollama_base_url}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dm-bot")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("preflight")
    subparsers.add_parser("run-bot")
    subparsers.add_parser("smoke-check")

    args = parser.parse_args(argv)

    if args.command == "preflight":
        print(describe_runtime())
        return 0

    if args.command == "run-bot":
        settings = get_settings()
        if not settings.discord_token:
            raise RuntimeError("DM_BOT_DISCORD_TOKEN is required to start the Discord bot")

        store = Store("dm_bot.sqlite3")
        loader = AdventureLoader()
        narrator = SimpleNarrator(settings.narrator_model, settings.ollama_base_url)
        bot = BotCommands(store=store, loader=loader, narrator=narrator, settings=settings)
        asyncio.run(bot.start(settings.discord_token))
        return 0

    if args.command == "smoke-check":
        # Basic import check
        try:
            from dm_bot.scene.round import Round
            from dm_bot.scene.state import SceneState
            from dm_bot.character.sheet import CharacterSheet
            from dm_bot.narrator.client import SimpleNarrator
            from dm_bot.store.db import Store
            from dm_bot.discord_bot.commands import BotCommands
            from dm_bot.adventure.loader import AdventureLoader
            print("All core modules import successfully.")
            return 0
        except Exception as e:
            print(f"Smoke check failed: {e}")
            return 1

    print("Error: No command specified. Use: preflight, run-bot, smoke-check")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
