import discord
from discord import app_commands
from discord.ext import commands


class DiscordDmBot(commands.Bot):
    def __init__(self, *, handlers, settings) -> None:
        intents = discord.Intents.none()
        intents.guilds = True
        intents.messages = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.handlers = handlers
        self.sync_guild_id = settings.discord_guild_id
        self._register_commands()

    async def setup_hook(self) -> None:
        if self.sync_guild_id:
            guild = discord.Object(id=int(self.sync_guild_id))
            self.tree.copy_global_to(guild=guild)
            self.tree.clear_commands(guild=None)
            await self.tree.sync()
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

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

        @self.tree.command(name="leave_campaign", description="Leave the campaign bound to this channel or thread")
        async def leave_campaign(interaction: discord.Interaction) -> None:
            await self.handlers.leave_campaign(interaction)

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

        @self.tree.command(name="end_scene", description="Return from scene mode to DM mode")
        async def end_scene(interaction: discord.Interaction) -> None:
            await self.handlers.end_scene(interaction)

        @self.tree.command(name="start_combat", description="Start a combat encounter")
        @app_commands.describe(combatants="Comma-separated combatants as name:init:hp:ac")
        async def start_combat(interaction: discord.Interaction, combatants: str) -> None:
            await self.handlers.start_combat(interaction, combatants=combatants)

        @self.tree.command(name="show_combat", description="Show current combat summary")
        async def show_combat(interaction: discord.Interaction) -> None:
            await self.handlers.show_combat(interaction)

        @self.tree.command(name="next_turn", description="Advance to the next combatant")
        async def next_turn(interaction: discord.Interaction) -> None:
            await self.handlers.next_turn(interaction)

        @self.tree.command(name="load_adventure", description="Load a packaged starter adventure")
        @app_commands.describe(adventure_id="Adventure identifier")
        async def load_adventure(interaction: discord.Interaction, adventure_id: str) -> None:
            await self.handlers.load_adventure(interaction, adventure_id=adventure_id)

        @self.tree.command(name="debug_status", description="Show recent trace-linked runtime events")
        @app_commands.describe(campaign_id="Campaign identifier")
        async def debug_status(interaction: discord.Interaction, campaign_id: str) -> None:
            await self.handlers.debug_status(interaction, campaign_id=campaign_id)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.content or message.guild is None:
            return
        reply = await self.handlers.handle_channel_message(
            channel_id=str(message.channel.id),
            guild_id=str(message.guild.id),
            user_id=str(message.author.id),
            content=message.content,
            mention_count=len(message.mentions),
        )
        if reply:
            await message.channel.send(reply)


def create_discord_bot(*, handlers, settings) -> commands.Bot:
    return DiscordDmBot(handlers=handlers, settings=settings)
