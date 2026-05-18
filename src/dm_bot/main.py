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


def check_store(db_path: str = ":memory:") -> dict:
    """Verify Store can connect and DB is healthy."""
    try:
        store = Store(db_path)
        integrity = store.check_integrity()
        return integrity
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_modules() -> dict:
    """Verify all runtime modules import correctly."""
    mods = [
        "dm_bot.adventure.models", "dm_bot.trigger.models", "dm_bot.trigger.engine",
        "dm_bot.reveal.models", "dm_bot.reveal.checker",
        "dm_bot.publish.models", "dm_bot.publish.publisher", "dm_bot.publish.contract",
        "dm_bot.store.db", "dm_bot.character.sheet", "dm_bot.character.archive",
        "dm_bot.surface.board", "dm_bot.surface.discord_formatter",
    ]
    results = {}
    all_ok = True
    for mod in mods:
        try:
            __import__(mod)
            results[mod] = "ok"
        except Exception as e:
            results[mod] = str(e)
            all_ok = False
    return {"all_ok": all_ok, "modules": results}


def smoke_check() -> int:
    """Comprehensive smoke check — separates module vs runtime failure."""
    mods = check_modules()
    if not mods["all_ok"]:
        failed = [n for n, s in mods["modules"].items() if s != "ok"]
        print(f"Smoke check FAILED — module failures: {failed}")
        return 1
    store_check = check_store()
    if store_check.get("status") != "ok":
        print(f"Smoke check FAILED — store: {store_check}")
        return 1
    print("All core modules import successfully. Store: OK.")
    return 0


def describe_runtime_full(settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    lines = []
    lines.append("=== Discord AI Keeper — Preflight ===")
    lines.append(f"discord_token={'[CONFIGURED]' if settings.discord_token else '[MISSING]'}")
    lines.append(f"narrator_model={settings.narrator_model}")
    lines.append(f"ollama_base_url={settings.ollama_base_url}")
    store_check = check_store()
    lines.append(f"store_integrity={store_check['status']}")
    mods = check_modules()
    lines.append(f"modules={mods['all_ok']}")
    for name, status in mods["modules"].items():
        lines.append(f"  {name}: {status}")
    return "\n".join(lines)


def describe_runtime(settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    token_status = "configured" if settings.discord_token else "missing"

    module_checks = []
    modules = [
        ("adventure.models", "Scene model"),
        ("trigger.models", "Trigger models"),
        ("trigger.engine", "Trigger engine"),
        ("reveal.models", "Reveal models"),
        ("reveal.checker", "Reveal checker"),
        ("publish.models", "Publish models"),
        ("publish.publisher", "Publisher"),
        ("publish.contract", "Renderer contract"),
        ("store.db", "Store"),
    ]
    for mod_path, label in modules:
        try:
            __import__(f"dm_bot.{mod_path}")
            module_checks.append(f"  [OK] {label}")
        except Exception as e:
            module_checks.append(f"  [FAIL] {label}: {e}")

    return (
        f"discord_token={token_status}\n"
        f"narrator_model={settings.narrator_model}\n"
        f"ollama_base_url={settings.ollama_base_url}\n"
        f"module_checks:\n" + "\n".join(module_checks)
    )


async def run_bot_async(token: str) -> None:
    import discord
    from discord import app_commands

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    store = Store("dm_bot.sqlite3")
    loader = AdventureLoader()
    narrator = SimpleNarrator()
    settings = get_settings()
    bot_cmds = BotCommands(store=store, loader=loader, narrator=narrator, settings=settings)

    @client.event
    async def on_ready() -> None:
        assert client.user is not None
        print(f"Bot logged in as {client.user}")
        bot_cmds.register(tree)
        await tree.sync()
        print("Commands synced. Ready!")

    await client.start(token)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dm-bot")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("preflight")
    subparsers.add_parser("run-bot")
    subparsers.add_parser("smoke-check")

    args = parser.parse_args(argv)

    if args.command == "preflight":
        print(describe_runtime_full())
        return 0

    if args.command == "run-bot":
        settings = get_settings()
        if not settings.discord_token:
            raise RuntimeError("DM_BOT_DISCORD_TOKEN is required to start the Discord bot")
        asyncio.run(run_bot_async(settings.discord_token))
        return 0

    if args.command == "smoke-check":
        return smoke_check()

    print("Error: No command specified. Use: preflight, run-bot, smoke-check")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
