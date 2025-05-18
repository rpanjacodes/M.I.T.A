# react.py - M.I.T.A React Command
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import random

# === Configure your Tenor API key here ===
TENOR_API_KEY = "YOUR_TENOR_API_KEY"

class React(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        self.all_tags = sorted(set(self.waifu_tags + self.nekos_tags + self.hisoka_tags))

    async def fetch_image(self, tag: str):
        sources = [self.from_waifu_pics, self.from_nekos_best, self.from_hisoka17]
        random.shuffle(sources)

        for source in sources:
            image_url = await source(tag)
            if image_url:
                return image_url

        return await self.from_tenor(tag)

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

    async def from_tenor(self, tag):
        if not TENOR_API_KEY:
            return None
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": tag,
                    "key": TENOR_API_KEY,
                    "limit": 1,
                    "media_filter": "minimal",
                    "contentfilter": "high"
                }
                async with session.get("https://tenor.googleapis.com/v2/search", params=params) as resp:
                    data = await resp.json()
                    if data.get("results"):
                        return data["results"][0]["media_formats"]["gif"]["url"]
        except:
            return None

    async def react_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=tag, value=tag)
            for tag in self.all_tags if current.lower() in tag.lower()
        ][:25]

    @app_commands.command(name="react", description="Send a random anime reaction (e.g. smile, hug, cry, etc.)")
    @app_commands.describe(
        tag="Reaction tag (e.g. smile, hug, cry, etc.)",
        user="User to mention (optional)"
    )
    @app_commands.autocomplete(tag=react_autocomplete)
    @app_commands.checks.cooldown(rate=1, per=10.0, key=lambda i: i.user.id)
    async def react(self, interaction: discord.Interaction, tag: str, user: discord.User = None):
        await interaction.response.defer()
        image_url = await self.fetch_image(tag.lower())

        if image_url:
            if user:
                title = f"{interaction.user.display_name} {tag}s {user.display_name}"
            else:
                title = f"{interaction.user.display_name} reacts with '{tag}'"

            embed = discord.Embed(title=title, color=discord.Color.purple())
            embed.set_image(url=image_url)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"Couldn't find any reaction image for the tag **{tag}**.", ephemeral=True)

    @react.error
    async def react_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.CommandOnCooldown):
            await interaction.response.send_message(
                f"You're on cooldown! Try again in {error.retry_after:.1f}s.",
                ephemeral=True
            )
        else:
            raise error  # Re-raise other errors

async def setup(bot):
    await bot.add_cog(React(bot))
