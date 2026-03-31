"""Visibility dispatcher for sending batch action results to Discord.

Dispatches consequences to different audiences based on visibility:
- PUBLIC: Send to entire channel
- PRIVATE: DM to specific player
- GROUP: DM to all group members
- KEEPER: Log only, no Discord message
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from discord import Client
    from discord import TextChannel
    from discord import User


logger = logging.getLogger(__name__)


class VisibilityDispatcher:
    """Dispatches aggregated consequences to Discord based on visibility.

    Visibility levels:
    - PUBLIC: Posted to the game channel for all to see
    - PRIVATE: Direct message to the acting player only
    - GROUP: Direct message to all members of the player's group
    - KEEPER: Internal log only, never sent to Discord
    """

    def __init__(
        self,
        discord_client: "Client | None" = None,
        campaign_channel_id: int | None = None,
    ) -> None:
        """Initialize dispatcher with optional Discord client.

        Args:
            discord_client: Discord client for sending messages
            campaign_channel_id: Channel ID for public game channel
        """
        self._client = discord_client
        self._campaign_channel_id = campaign_channel_id

    async def dispatch(
        self,
        aggregated,
        character_to_user: dict[str, str],
    ) -> None:
        """Dispatch aggregated consequences to appropriate Discord recipients.

        Args:
            aggregated: AggregatedConsequences from ConsequenceAggregator
            character_to_user: Mapping of character_id -> discord user_id
        """
        from dm_bot.orchestrator.session_store import Visibility

        for visibility_str, group in aggregated.groups.items():
            visibility = (
                Visibility(visibility_str)
                if isinstance(visibility_str, str)
                else visibility_str
            )

            if visibility == Visibility.PUBLIC:
                await self._send_public(group.consequences)
            elif visibility == Visibility.PRIVATE:
                await self._send_private(group.consequences, character_to_user)
            elif visibility == Visibility.GROUP:
                await self._send_group(group.consequences, character_to_user)
            elif visibility == Visibility.KEEPER:
                self._log_keeper_only(group.consequences)

    async def _get_campaign_channel(self) -> discord.TextChannel | None:
        """Get the campaign channel for public messages.

        Returns:
            Discord TextChannel or None if not available
        """
        if not self._client or not self._campaign_channel_id:
            return None
        try:
            channel = await self._client.fetch_channel(self._campaign_channel_id)
            if isinstance(channel, discord.TextChannel):
                return channel
            return None
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return None

    async def _send_public(
        self,
        consequences: list,
    ) -> None:
        """Send consequences to the public channel.

        Args:
            consequences: List of AggregatedConsequence objects
        """
        if not consequences:
            return

        if not self._client:
            logger.warning("No Discord client available for public dispatch")
            return

        # Format the public message as an embed
        embed = discord.Embed(
            title="场景回合结果",
            description=f"本轮共有 {len(consequences)} 个事件",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )

        # Group consequences by character for better readability
        by_character: dict[str, list[str]] = {}
        for consequence in consequences:
            char_id = consequence.character_id
            if char_id not in by_character:
                by_character[char_id] = []
            by_character[char_id].append(consequence.content)

        # Add fields for each character
        for char_id, contents in by_character.items():
            content_text = "\n".join(f"• {c}" for c in contents[:5])  # Limit to 5 items
            if len(contents) > 5:
                content_text += f"\n*还有 {len(contents) - 5} 个事件...*"
            embed.add_field(name=char_id, value=content_text or "无", inline=False)

        # Get the campaign channel and send
        channel = await self._get_campaign_channel()
        if channel:
            try:
                await channel.send(embed=embed)
                logger.info(
                    f"PUBLIC dispatch sent: {len(consequences)} consequences to {channel.id}"
                )
            except discord.Forbidden:
                logger.error(f"Forbidden: Cannot send to channel {channel.id}")
            except discord.HTTPException as e:
                logger.error(f"HTTP error sending public message: {e}")
        else:
            logger.warning("No campaign channel available for public dispatch")

    async def _send_private(
        self,
        consequences: list,
        character_to_user: dict[str, str],
    ) -> None:
        """Send private consequences as DMs to the acting player.

        Args:
            consequences: List of AggregatedConsequence objects
            character_to_user: Mapping of character_id -> discord user_id
        """
        if not consequences or not self._client:
            return

        # Group consequences by character
        by_character: dict[str, list] = {}
        for consequence in consequences:
            char_id = consequence.character_id
            if char_id not in by_character:
                by_character[char_id] = []
            by_character[char_id].append(consequence)

        # Send DM to each affected player
        for character_id, char_consequences in by_character.items():
            user_id = character_to_user.get(character_id)
            if not user_id:
                logger.warning(f"No user mapping for character {character_id}")
                continue

            # Fetch Discord user
            try:
                user = await self._client.fetch_user(int(user_id))
                if not user:
                    logger.warning(
                        f"Could not fetch user {user_id} for character {character_id}"
                    )
                    continue
            except (ValueError, discord.NotFound) as e:
                logger.error(f"Error fetching user {user_id}: {e}")
                continue

            # Build embed
            embed = discord.Embed(
                title=f"私有信息 ({character_id})",
                description=f"你有 {len(char_consequences)} 条私有消息",
                color=discord.Color.purple(),
                timestamp=datetime.now(),
            )

            for consequence in char_consequences[:10]:  # Limit to 10
                embed.add_field(
                    name="事件",
                    value=consequence.content[:1024],  # Discord field limit
                    inline=False,
                )

            # Send DM
            try:
                await user.send(embed=embed)
                logger.info(
                    f"PRIVATE dispatch to {user_id}: {len(char_consequences)} consequences"
                )
            except discord.Forbidden:
                logger.warning(f"Cannot send DM to user {user_id} (DMs disabled)")
            except discord.HTTPException as e:
                logger.error(f"HTTP error sending DM to {user_id}: {e}")

    async def _send_group(
        self,
        consequences: list,
        character_to_user: dict[str, str],
    ) -> None:
        """Send group consequences as DMs to all group members.

        Args:
            consequences: List of AggregatedConsequence objects
            character_to_user: Mapping of character_id -> discord user_id
        """
        if not consequences or not self._client:
            return

        # Group consequences by character
        by_character: dict[str, list] = {}
        for consequence in consequences:
            char_id = consequence.character_id
            if char_id not in by_character:
                by_character[char_id] = []
            by_character[char_id].append(consequence)

        # Collect all unique users who should receive the group message
        target_users: set[str] = set()
        for character_id in by_character.keys():
            user_id = character_to_user.get(character_id)
            if user_id:
                target_users.add(user_id)

        # Build the group message embed
        embed = discord.Embed(
            title="团体信息",
            description=f"共有 {len(consequences)} 条团体消息",
            color=discord.Color.gold(),
            timestamp=datetime.now(),
        )

        for character_id, char_consequences in by_character.items():
            content_text = "\n".join(f"• {c.content}" for c in char_consequences[:3])
            embed.add_field(name=character_id, value=content_text, inline=False)

        # Send to each group member
        for user_id in target_users:
            try:
                user = await self._client.fetch_user(int(user_id))
                if not user:
                    continue

                await user.send(embed=embed)
                logger.info(f"GROUP dispatch to {user_id}")
            except discord.Forbidden:
                logger.warning(f"Cannot send group DM to user {user_id}")
            except discord.HTTPException as e:
                logger.error(f"HTTP error sending group DM to {user_id}: {e}")

    def _log_keeper_only(
        self,
        consequences: list,
    ) -> None:
        """Log keeper-only consequences internally.

        Args:
            consequences: List of AggregatedConsequence objects
        """
        for consequence in consequences:
            logger.info(
                f"KEEPER ONLY | {consequence.character_id}: {consequence.content}"
            )
