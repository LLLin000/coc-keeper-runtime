"""清理 Discord 残留旧命令 — 仅 guild sync (快速)。"""

import asyncio, sys
import discord
from discord import app_commands
from dm_bot.config import get_settings
from dm_bot.discord_bot.commands import BotCommands
from dm_bot.store.db import Store
from dm_bot.adventure.loader import AdventureLoader
from dm_bot.narrator.client import SimpleNarrator


async def cleanup() -> None:
    settings = get_settings()
    guild = discord.Object(id=int(settings.discord_guild_id))

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    store = Store("dm_bot.sqlite3")
    loader = AdventureLoader()
    narrator = SimpleNarrator()
    bot_cmds = BotCommands(store=store, loader=loader, narrator=narrator, settings=settings)

    @client.event
    async def on_ready() -> None:
        print(f"Logged in. Clearing guild commands...", flush=True)
        tree.clear_commands(guild=guild)
        bot_cmds.register(tree)
        await tree.sync(guild=guild)
        print("Guild commands synced — old commands removed!", flush=True)
        print("Done!", flush=True)
        await client.close()

    await client.start(settings.discord_token)


asyncio.run(cleanup())
