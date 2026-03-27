import discord
from discord import app_commands
from discord.ext import commands


class DiscordDmBot(commands.Bot):
    def __init__(self, *, handlers) -> None:
        intents = discord.Intents.none()
        super().__init__(command_prefix="!", intents=intents)
        self.handlers = handlers
        self._register_commands()

    def _register_commands(self) -> None:
        @self.tree.command(name="setup", description="Check runtime setup and model availability")
        async def setup(interaction: discord.Interaction) -> None:
            await self.handlers.setup_check(interaction)

        @self.tree.command(name="bind_campaign", description="Bind a campaign to this channel or thread")
        @app_commands.describe(campaign_id="Campaign identifier")
        async def bind_campaign(interaction: discord.Interaction, campaign_id: str) -> None:
            await self.handlers.bind_campaign(interaction, campaign_id=campaign_id)

        @self.tree.command(name="join_campaign", description="Join the campaign bound to this channel or thread")
        async def join_campaign(interaction: discord.Interaction) -> None:
            await self.handlers.join_campaign(interaction)

        @self.tree.command(name="turn", description="Submit a player turn into the active campaign")
        @app_commands.describe(content="Player action text")
        async def turn(interaction: discord.Interaction, content: str) -> None:
            await self.handlers.take_turn(interaction, content=content)

        @self.tree.command(name="import_character", description="Import a snapshot character for the current player")
        @app_commands.describe(provider="Character source provider", external_id="External character identifier")
        async def import_character(interaction: discord.Interaction, provider: str, external_id: str) -> None:
            await self.handlers.import_character(interaction, provider=provider, external_id=external_id)

        @self.tree.command(name="enter_scene", description="Enter multi-character scene mode")
        @app_commands.describe(speakers="Comma-separated speaker list")
        async def enter_scene(interaction: discord.Interaction, speakers: str) -> None:
            await self.handlers.enter_scene(interaction, speakers=speakers)

        @self.tree.command(name="start_combat", description="Start a combat encounter")
        @app_commands.describe(combatants="Comma-separated combatants as name:init:hp:ac")
        async def start_combat(interaction: discord.Interaction, combatants: str) -> None:
            await self.handlers.start_combat(interaction, combatants=combatants)


def create_discord_bot(*, handlers) -> commands.Bot:
    return DiscordDmBot(handlers=handlers)
