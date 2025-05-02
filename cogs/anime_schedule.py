import discord
from discord import app_commands
from discord.ext import tasks, commands
import aiohttp
import asyncio
import sqlite3
from datetime import datetime, timezone, timedelta

class AnimeSchedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('anime_schedule.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS anime_channels (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS posted_eps (
                mal_id INTEGER,
                episode INTEGER,
                PRIMARY KEY (mal_id, episode)
            )
        ''')
        self.conn.commit()
        self.check_new_episodes.start()

    def cog_unload(self):
        self.check_new_episodes.cancel()
        self.conn.close()

    @app_commands.command(name="setanimeupdates", description="Set the channel to post new anime episode updates.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_anime_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.cursor.execute("REPLACE INTO anime_channels (guild_id, channel_id) VALUES (?, ?)", (interaction.guild_id, channel.id))
        self.conn.commit()
        await interaction.response.send_message(f"Anime updates will now be posted in {channel.mention}", ephemeral=True)

    @app_commands.command(name="removeanimeupdates", description="Stop posting anime episode updates in this server.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def remove_anime_channel(self, interaction: discord.Interaction):
        self.cursor.execute("DELETE FROM anime_channels WHERE guild_id = ?", (interaction.guild_id,))
        self.conn.commit()
        await interaction.response.send_message("Anime episode updates have been disabled for this server.", ephemeral=True)

    @app_commands.command(name="testanimepost", description="Send a test anime episode post to your configured channel.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def test_anime_post(self, interaction: discord.Interaction):
        self.cursor.execute("SELECT channel_id FROM anime_channels WHERE guild_id = ?", (interaction.guild_id,))
        row = self.cursor.fetchone()
        if not row:
            await interaction.response.send_message("Anime updates are not set up for this server.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(row[0])
        if not channel:
            await interaction.response.send_message("Configured channel not found. Please run /setanimeupdates again.", ephemeral=True)
            return

        embed = discord.Embed(
            title="One Piece - New Episode!",
            description=f"Just aired: <t:{int(datetime.now(timezone.utc).timestamp())}:R>",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url="https://cdn.myanimelist.net/images/anime/6/73245.jpg")
        embed.set_footer(text="Jikan Anime Updates (Test Post)")

        try:
            await channel.send(embed=embed)
            await interaction.response.send_message(f"Test post sent in {channel.mention}", ephemeral=True)
        except Exception as e:
            print(f"[DEBUG] Failed to send test post: {e}")
            await interaction.response.send_message("Failed to send test post. Check my permissions.", ephemeral=True)

    @set_anime_channel.error
    @remove_anime_channel.error
    @test_anime_post.error
    async def permissions_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You need **Manage Server** permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)

    @tasks.loop(minutes=5)
    async def check_new_episodes(self):
        now = datetime.now(timezone.utc)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.jikan.moe/v4/schedules") as resp:
                    if resp.status != 200:
                        print(f"[DEBUG] Failed to fetch Jikan schedule: {resp.status}")
                        return
                    data = await resp.json()
        except Exception as e:
            print(f"[DEBUG] Jikan schedule API error: {e}")
            return

        self.cursor.execute("SELECT guild_id, channel_id FROM anime_channels")
        servers = self.cursor.fetchall()

        for anime in data.get("data", []):
            mal_id = anime.get("mal_id")
            title = anime.get("title")
            image_url = anime.get("images", {}).get("jpg", {}).get("image_url")
            ep_num = anime.get("episodes") or "?"
            aired = anime.get("aired", {}).get("from")

            if not aired:
                continue

            try:
                aired_time = datetime.fromisoformat(aired.replace("Z", "+00:00"))
            except Exception:
                continue

            if now - timedelta(minutes=10) <= aired_time <= now:
                if self.is_posted(mal_id, ep_num):
                    continue

                embed = discord.Embed(
                    title=f"{title} - New Episode!",
                    description=f"Just aired: <t:{int(aired_time.timestamp())}:R>",
                    color=discord.Color.blurple()
                )
                if image_url:
                    embed.set_thumbnail(url=image_url)
                embed.set_footer(text="Jikan Anime Updates")

                for guild_id, channel_id in servers:
                    guild = self.bot.get_guild(guild_id)
                    if guild:
                        channel = guild.get_channel(channel_id)
                        if channel:
                            try:
                                await channel.send(embed=embed)
                            except Exception as e:
                                print(f"[DEBUG] Failed to send in {guild.name}: {e}")

                self.mark_posted(mal_id, ep_num)

    def is_posted(self, mal_id, ep_num):
        self.cursor.execute("SELECT 1 FROM posted_eps WHERE mal_id = ? AND episode = ?", (mal_id, ep_num))
        return self.cursor.fetchone() is not None

    def mark_posted(self, mal_id, ep_num):
        self.cursor.execute("INSERT OR IGNORE INTO posted_eps (mal_id, episode) VALUES (?, ?)", (mal_id, ep_num))
        self.conn.commit()

async def setup(bot):
    await bot.add_cog(AnimeSchedule(bot))
