"""Visibility dispatcher for sending batch action results to Discord.

Dispatches consequences to different audiences based on visibility:
- PUBLIC: Send to entire channel
- PRIVATE: DM to specific player
- GROUP: DM to all group members
- KEEPER: Log only, no Discord message
"""

import logging
from typing import TYPE_CHECKING

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

    def __init__(self, discord_client: "Client | None" = None) -> None:
        """Initialize dispatcher with optional Discord client.

        Args:
            discord_client: Discord client for sending messages
        """
        self._client = discord_client

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

        # Format the public message
        lines = ["**--- 场景回合结果 ---**"]
        for consequence in consequences:
            lines.append(f"• {consequence.content}")

        content = "\n".join(lines)
        logger.info(f"PUBLIC dispatch: {len(consequences)} consequences")

        # TODO: Send to actual Discord channel when integrated with runtime
        # For now, just log
        if self._client:
            # Will be integrated with campaign channel
            pass

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

            lines = [f"**私有信息 ({character_id}):**"]
            for consequence in char_consequences:
                lines.append(f"• {consequence.content}")

            content = "\n".join(lines)
            logger.info(
                f"PRIVATE dispatch to {user_id}: {len(char_consequences)} consequences"
            )

            # TODO: Fetch user and send DM when integrated with runtime

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

        # For each character, send to their group (same DM to all relevant players)
        for character_id, char_consequences in by_character.items():
            lines = [f"**团体信息 ({character_id}):**"]
            for consequence in char_consequences:
                lines.append(f"• {consequence.content}")

            content = "\n".join(lines)
            logger.info(
                f"GROUP dispatch for {character_id}: {len(char_consequences)} consequences"
            )

            # TODO: Identify group members and send DMs when integrated with runtime

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
