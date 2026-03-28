import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import os
from pathlib import Path
import traceback


def _write_startup_marker(line: str) -> None:
    marker_path = os.environ.get("DM_BOT_STARTUP_MARKER_FILE")
    if not marker_path:
        return
    try:
        Path(marker_path).parent.mkdir(parents=True, exist_ok=True)
        with Path(marker_path).open("a", encoding="utf-8") as handle:
            handle.write(f"{line}\n")
    except OSError:
        return


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
        print("SYNC_START", flush=True)
        _write_startup_marker("SYNC_START")
        if self.sync_guild_id:
            guild = discord.Object(id=int(self.sync_guild_id))
            self.tree.copy_global_to(guild=guild)
            self.tree.clear_commands(guild=None)
            global_synced = await self.tree.sync()
            guild_synced = await self.tree.sync(guild=guild)
            print(
                f"SYNC_DONE global={len(global_synced)} guild={len(guild_synced)}",
                flush=True,
            )
            _write_startup_marker(
                f"SYNC_DONE global={len(global_synced)} guild={len(guild_synced)}"
            )
        else:
            synced = await self.tree.sync()
            print(f"SYNC_DONE global={len(synced)}", flush=True)
            _write_startup_marker(f"SYNC_DONE global={len(synced)}")
        if os.environ.get("DM_BOT_SYNC_ONLY") == "1":
            await self.close()
            return

    async def on_connect(self) -> None:
        print("CONNECTED", flush=True)
        _write_startup_marker("CONNECTED")

    async def on_ready(self) -> None:
        if self.user is not None:
            print(f"READY {self.user} {self.user.id}", flush=True)
            _write_startup_marker(f"READY {self.user} {self.user.id}")

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        print(
            f"APP_COMMAND_ERROR name={getattr(interaction.command, 'name', 'unknown')} error={error!r}",
            flush=True,
        )
        traceback.print_exception(type(error), error, error.__traceback__)

    def _register_commands(self) -> None:
        @self.tree.command(name="setup", description="Check runtime setup and model availability")
        async def setup(interaction: discord.Interaction) -> None:
            await self.handlers.setup_check(interaction)

        @self.tree.command(name="bind_campaign", description="Bind a campaign to this channel or thread")
        @app_commands.describe(campaign_id="Campaign identifier")
        async def bind_campaign(interaction: discord.Interaction, campaign_id: str) -> None:
            await self.handlers.bind_campaign(interaction, campaign_id=campaign_id)

        @self.tree.command(name="bind_archive_channel", description="Bind this channel as the archive/profile channel")
        async def bind_archive_channel(interaction: discord.Interaction) -> None:
            await self.handlers.bind_archive_channel(interaction)

        @self.tree.command(name="bind_trace_channel", description="Bind this channel as the keeper trace channel")
        async def bind_trace_channel(interaction: discord.Interaction) -> None:
            await self.handlers.bind_trace_channel(interaction)

        @self.tree.command(name="bind_admin_channel", description="Bind this channel as the admin management channel")
        async def bind_admin_channel(interaction: discord.Interaction) -> None:
            await self.handlers.bind_admin_channel(interaction)

        @self.tree.command(name="join_campaign", description="Join the campaign bound to this channel or thread")
        async def join_campaign(interaction: discord.Interaction) -> None:
            await self.handlers.join_campaign(interaction)

        @self.tree.command(name="leave_campaign", description="Leave the campaign bound to this channel or thread")
        async def leave_campaign(interaction: discord.Interaction) -> None:
            await self.handlers.leave_campaign(interaction)

        @self.tree.command(name="set_role", description="Set your scenario role or template")
        @app_commands.describe(role="Role such as investigator or magical_girl")
        async def set_role(interaction: discord.Interaction, role: str) -> None:
            await self.handlers.set_role(interaction, role=role)

        @self.tree.command(name="start_builder", description="Start conversational COC character creation")
        @app_commands.describe(visibility="private or public")
        async def start_builder(interaction: discord.Interaction, visibility: str = "private") -> None:
            await self.handlers.start_character_builder(interaction, visibility=visibility)

        @self.tree.command(name="builder_reply", description="Answer the current builder question")
        @app_commands.describe(answer="Your answer to the current question")
        async def builder_reply(interaction: discord.Interaction, answer: str) -> None:
            await self.handlers.builder_reply(interaction, answer=answer)

        @self.tree.command(name="profiles", description="List your archive investigator profiles")
        async def profiles(interaction: discord.Interaction) -> None:
            await self.handlers.list_profiles(interaction)

        @self.tree.command(name="profile_detail", description="Show one archive investigator profile in detail")
        @app_commands.describe(profile_id="Archive profile id")
        async def profile_detail(interaction: discord.Interaction, profile_id: str) -> None:
            await self.handlers.profile_detail(interaction, profile_id=profile_id)

        @self.tree.command(name="select_profile", description="Select an archive profile for this campaign")
        @app_commands.describe(profile_id="Archive profile id")
        async def select_profile(interaction: discord.Interaction, profile_id: str) -> None:
            await self.handlers.select_profile(interaction, profile_id=profile_id)

        @self.tree.command(name="archive_profile", description="Archive one of your long-lived profiles")
        @app_commands.describe(profile_id="Archive profile id")
        async def archive_profile(interaction: discord.Interaction, profile_id: str) -> None:
            await self.handlers.archive_profile(interaction, profile_id=profile_id)

        @self.tree.command(name="activate_profile", description="Activate one of your archived profiles")
        @app_commands.describe(profile_id="Archive profile id")
        async def activate_profile(interaction: discord.Interaction, profile_id: str) -> None:
            await self.handlers.activate_profile(interaction, profile_id=profile_id)

        @self.tree.command(name="admin_profiles", description="List all player archive profiles")
        async def admin_profiles(interaction: discord.Interaction) -> None:
            await self.handlers.admin_profiles(interaction)

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

        @self.tree.command(name="ready", description="Mark yourself ready for the loaded adventure")
        @app_commands.describe(character_name="Optional character or role name for this run")
        async def ready(interaction: discord.Interaction, character_name: str = "") -> None:
            await self.handlers.ready_for_adventure(interaction, character_name=character_name)

        @self.tree.command(name="roll", description="Roll a dice expression")
        @app_commands.describe(expression="Dice expression, e.g. 1d20+3")
        async def roll(interaction: discord.Interaction, expression: str) -> None:
            await self.handlers.roll_expression(interaction, expression=expression)

        @self.tree.command(name="check", description="Resolve an ability or skill check")
        @app_commands.describe(label="Check label", modifier="Modifier to add", advantage="none, advantage, or disadvantage")
        async def check(interaction: discord.Interaction, label: str, modifier: int, advantage: str = "none") -> None:
            await self.handlers.check_roll(interaction, label=label, modifier=modifier, advantage=advantage)

        @self.tree.command(name="save", description="Resolve a saving throw")
        @app_commands.describe(label="Save label", modifier="Modifier to add", advantage="none, advantage, or disadvantage")
        async def save(interaction: discord.Interaction, label: str, modifier: int, advantage: str = "none") -> None:
            await self.handlers.save_roll(interaction, label=label, modifier=modifier, advantage=advantage)

        @self.tree.command(name="coc_check", description="Resolve a COC skill check")
        @app_commands.describe(
            label="Skill label",
            value="Target value",
            difficulty="regular, hard, or extreme",
            bonus_dice="Bonus dice count",
            penalty_dice="Penalty dice count",
            pushed="Whether this is a pushed roll",
        )
        async def coc_check(
            interaction: discord.Interaction,
            label: str,
            value: int,
            difficulty: str = "regular",
            bonus_dice: int = 0,
            penalty_dice: int = 0,
            pushed: bool = False,
        ) -> None:
            await self.handlers.coc_check_roll(
                interaction,
                label=label,
                value=value,
                difficulty=difficulty,
                bonus_dice=bonus_dice,
                penalty_dice=penalty_dice,
                pushed=pushed,
            )

        @self.tree.command(name="san_check", description="Resolve a COC sanity check")
        @app_commands.describe(
            current_san="Current SAN value",
            loss_on_success="Loss on success",
            loss_on_failure="Loss on failure",
            bonus_dice="Bonus dice count",
            penalty_dice="Penalty dice count",
        )
        async def san_check(
            interaction: discord.Interaction,
            current_san: int,
            loss_on_success: str = "0",
            loss_on_failure: str = "1d6",
            bonus_dice: int = 0,
            penalty_dice: int = 0,
        ) -> None:
            await self.handlers.san_roll(
                interaction,
                current_san=current_san,
                loss_on_success=loss_on_success,
                loss_on_failure=loss_on_failure,
                bonus_dice=bonus_dice,
                penalty_dice=penalty_dice,
            )

        @self.tree.command(name="attack", description="Resolve an attack roll with optional damage")
        @app_commands.describe(
            target_name="Target name",
            target_ac="Target armor class",
            attack_bonus="Attack bonus",
            damage_expression="Damage expression, e.g. 1d8+3",
            weapon="Weapon name",
            advantage="none, advantage, or disadvantage",
        )
        async def attack(
            interaction: discord.Interaction,
            target_name: str,
            target_ac: int,
            attack_bonus: int,
            damage_expression: str,
            weapon: str = "unarmed",
            advantage: str = "none",
        ) -> None:
            await self.handlers.attack_roll(
                interaction,
                target_name=target_name,
                target_ac=target_ac,
                attack_bonus=attack_bonus,
                damage_expression=damage_expression,
                weapon=weapon,
                advantage=advantage,
            )

        @self.tree.command(name="debug_status", description="Show recent trace-linked runtime events")
        @app_commands.describe(campaign_id="Campaign identifier")
        async def debug_status(interaction: discord.Interaction, campaign_id: str) -> None:
            await self.handlers.debug_status(interaction, campaign_id=campaign_id)

        @self.tree.command(name="coc_assets", description="Show discovered local COC assets")
        async def coc_assets(interaction: discord.Interaction) -> None:
            await self.handlers.coc_assets_summary(interaction)

        @self.tree.command(name="sheet", description="Show your investigator panel")
        async def sheet(interaction: discord.Interaction) -> None:
            await self.handlers.show_sheet(interaction)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.content or message.guild is None:
            return
        async with message.channel.typing():
            await self.handlers.handle_channel_message_stream(message=message)


def create_discord_bot(*, handlers, settings) -> commands.Bot:
    return DiscordDmBot(handlers=handlers, settings=settings)
