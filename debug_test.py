import asyncio
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "tests")

from tests.fakes.discord import FakeDiscordClient, FakeUser, FakeDMChannel


async def test():
    # Create a client and user
    client = FakeDiscordClient()
    user = client.add_user("1001", "Player1")

    print("user:", user)
    print("user.dm_channel:", user.dm_channel)
    print("user.dm_channel type:", type(user.dm_channel))
    print("user.dm_channel.messages:", user.dm_channel.messages)
    print("user.dm_channel.embeds:", user.dm_channel.embeds)

    # Call send
    import discord

    embed = discord.Embed(title="Test")
    print("embed:", embed)
    print("embed type:", type(embed))
    print("bool(embed):", bool(embed))

    print("Calling user.send(embed=embed)...")
    await user.send(embed=embed)
    print("After send, user.dm_channel.messages:", user.dm_channel.messages)
    print("After send, user.dm_channel.embeds:", user.dm_channel.embeds)


asyncio.run(test())
