import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

MAL_CLIENT_ID = "your_client_id_here"  # 🔑 Replace this with your real MAL client ID

class AnimeSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="anime_search", description="Search anime using MyAnimeList API")
    @app_commands.describe(anime_name="Anime name to search")
    async def anime_search(self, interaction: discord.Interaction, anime_name: str):
        await interaction.response.defer(thinking=True)

        headers = {
            "X-MAL-CLIENT-ID": MAL_CLIENT_ID
        }

        url = (
            f"https://api.myanimelist.net/v2/anime?q={anime_name}"
            "&limit=1&fields=id,title,main_picture,synopsis,mean,episodes,genres,start_date,status"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    await interaction.followup.send("⚠️ Failed to fetch anime info from MyAnimeList.")
                    return

                data = await response.json()
                if not data.get("data"):
                    await interaction.followup.send("❌ No anime found.")
                    return

                anime = data["data"][0]["node"]

                embed = discord.Embed(
                    title=anime["title"],
                    description=anime.get("synopsis", "No synopsis provided."),
                    color=discord.Color.blurple()
                )

                # Set image and thumbnail
                if "main_picture" in anime:
                    embed.set_image(url=anime["main_picture"].get("large", anime["main_picture"].get("medium")))

                embed.add_field(name="📺 Episodes", value=str(anime.get("episodes", "N/A")))
                embed.add_field(name="⭐ Score", value=str(anime.get("mean", "N/A")))
                embed.add_field(name="📅 Start Date", value=anime.get("start_date", "N/A"))
                embed.add_field(name="📡 Status", value=anime.get("status", "N/A"), inline=True)

                genres = ", ".join(genre["name"] for genre in anime.get("genres", []))
                embed.add_field(name="🎭 Genres", value=genres or "N/A", inline=False)

                embed.set_footer(text="Data provided by MyAnimeList")
                await interaction.followup.send(embed=embed)

    @app_commands.command(name="anime_character", description="Search anime character (waifu/husbando) using Jikan API")
    @app_commands.describe(name="Character name to search")
    async def anime_character(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(thinking=True)

        url = f"https://api.jikan.moe/v4/characters?q={name}&limit=1"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await interaction.followup.send("⚠️ Failed to fetch character info.")
                    return

                data = await response.json()
                if not data.get("data"):
                    await interaction.followup.send("❌ No character found.")
                    return

                char = data["data"][0]

                embed = discord.Embed(
                    title=char["name"],
                    url=char["url"],
                    description=char.get("about", "No bio available."),
                    color=discord.Color.purple()
                )

                if "images" in char and "jpg" in char["images"]:
                    embed.set_thumbnail(url=char["images"]["jpg"].get("image_url"))

                embed.add_field(name="❤️ Favorites", value=str(char.get("favorites", "N/A")))
                embed.set_footer(text="Powered by Jikan | Data from MyAnimeList")

                await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AnimeSearch(bot))
