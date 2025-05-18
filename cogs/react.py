# react.py - M.I.T.A React Command
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import random

class React(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Supported tags per API
        self.waifu_tags = [
            "smile", "hug", "wave", "highfive", "wink", "blush", "pat", "happy", "cry", "dance", "bonk", "handhold", "poke"
        ]
        self.nekos_tags = [
            "bite", "poke", "pat", "smile", "wink", "cry", "blush", "stare", "wave", "happy", "kick", "hug", "laugh", "dance"
        ]
        self.hisoka_tags = [
            "baka", "bite", "blush", "bored", "cry", "cuddle", "dance", "facepalm", "happy", "highfive", "hug",
            "kick", "kiss", "laugh", "pat", "poke", "pout", "sad", "shrug", "sleepy", "smile", "stare", "wave", "wink"
        ]

    async def fetch_image(self, tag: str):
        sources = [self.from_waifu_pics, self.from_nekos_best, self.from_hisoka17]
        random.shuffle(sources)  # Randomize order of API calls

        for source in sources:
            image_url = await source(tag)
            if image_url:
                return image_url
        return None

    async def from_waifu_pics(self, tag):
        if tag not in self.waifu_tags:
            return None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.waifu.pics/sfw/{tag}") as resp:
                    data = await resp.json()
                    return data.get("url")
        except:
            return None

    async def from_nekos_best(self, tag):
        if tag not in self.nekos_tags:
            return None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://nekos.best/api/v2/{tag}") as resp:
                    data = await resp.json()
                    return data["results"][0]["url"]
        except:
            return None

    async def from_hisoka17(self, tag):
        if tag not in self.hisoka_tags:
            return None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.hisoka17.repl.co/sfw/{tag}") as resp:
                    data = await resp.json()
                    return data.get("url")
        except:
            return None

    @app_commands.command(name="react", description="Send a random anime reaction (e.g. smile, hug, cry, etc.)")
    @app_commands.describe(tag="Reaction tag (e.g. smile, hug, cry, etc.)")
    async def react(self, interaction: discord.Interaction, tag: str):
        await interaction.response.defer()
        image_url = await self.fetch_image(tag.lower())
        if image_url:
            embed = discord.Embed(title=f"{interaction.user.display_name} reacts with '{tag}'", color=discord.Color.purple())
            embed.set_image(url=image_url)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"Couldn't find any reaction image for the tag **{tag}**.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(React(bot))
