# react.py
# M.I.T.A - Discord Bot Project
# Copyright (C) 2025 M.I.T.A Bot Team

import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

VALID_TAGS = [
    "smile", "wave", "wink", "hug", "dance", "blush", "happy",
    "thumbsup", "highfive", "pat", "poke", "slap", "yeet",
    "cry", "handhold", "sleepy", "nom", "bite", "kick", "punch"
]

class React(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="react", description="Send a random anime image based on a tag.")
    @app_commands.describe(tag="Reaction type like smile, hug, slap, etc.")
    async def react(self, interaction: discord.Interaction, tag: str):
        tag = tag.lower()
        if tag not in VALID_TAGS:
            return await interaction.response.send_message(
                f"Invalid tag. Valid tags are:\n`{', '.join(VALID_TAGS)}`",
                ephemeral=True
            )

        url = f"https://api.waifu.pics/sfw/{tag}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await interaction.response.send_message("Failed to fetch image. Try again later.", ephemeral=True)
                data = await resp.json()
        
        embed = discord.Embed(title=f"{tag.title()} Reaction", color=discord.Color.blurple())
        embed.set_image(url=data["url"])
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(React(bot))
