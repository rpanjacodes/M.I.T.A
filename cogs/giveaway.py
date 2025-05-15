import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import sqlite3
import random
import pytz
import re

DB_PATH = 'bot.db'

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        now = datetime.utcnow().timestamp()
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS giveaways (
                    guild_id INTEGER,
                    channel_id INTEGER,
                    message_id INTEGER,
                    end_time REAL,
                    required_role TEXT
                )
            ''')
            c.execute('SELECT guild_id, channel_id, message_id, end_time, required_role FROM giveaways')
            rows = c.fetchall()
            for guild_id, channel_id, message_id, end_time, required_role in rows:
                if now >= end_time:
                    try:
                        guild = self.bot.get_guild(guild_id)
                        if not guild:
                            continue
                        channel = guild.get_channel(channel_id)
                        if not channel:
                            continue
                        message = await channel.fetch_message(message_id)
                        if not message.reactions:
                            continue

                        users = [user async for user in message.reactions[0].users()]
                        users = [u for u in users if not u.bot]

                        if required_role:
                            role = guild.get_role(int(required_role))
                            users = [u for u in users if role in u.roles]

                        winner = random.choice(users) if users else None
                        if winner:
                            await channel.send(f"Congratulations {winner.mention}, you won the giveaway!")
                        else:
                            await channel.send("No valid entries, giveaway ended with no winner.")

                        c.execute('DELETE FROM giveaways WHERE message_id = ?', (message_id,))
                        conn.commit()
                    except Exception as e:
                        print(f"[Giveaway Task Error] {e}")

    @app_commands.command(name="giveaway", description="Start a giveaway")
    @app_commands.describe(
        channel="Channel to post the giveaway in",
        duration="Duration (e.g., 1h, 30m, 2d)",
        prize="What is the giveaway prize?",
        image_url="Optional image URL",
        required_role="Role required to enter (optional)",
        timezone="Timezone (e.g., Asia/Kolkata, America/New_York)"
    )
    async def giveaway(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        duration: str,
        prize: str,
        image_url: str = None,
        required_role: discord.Role = None,
        timezone: str = "UTC"
    ):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Permission Denied",
                    description="You need **Manage Server** permission to use this command.",
                    color=discord.Color.red()
                ), ephemeral=True
            )

        try:
            user_tz = pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Invalid Timezone",
                    description="That timezone is not recognized. Please use formats like `Asia/Kolkata`, `America/New_York`, `UTC`, etc.",
                    color=discord.Color.red()
                ), ephemeral=True
            )

        match = re.match(r"(\d+)([smhd])", duration.lower())
        if not match:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Invalid Duration",
                    description="Use formats like `10m`, `1h`, `2d`. (m = minutes, h = hours, d = days)",
                    color=discord.Color.red()
                ), ephemeral=True
            )

        amount = int(match.group(1))
        unit = match.group(2)
        seconds = amount * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
        end_time_utc = datetime.utcnow() + timedelta(seconds=seconds)
        end_time_local = end_time_utc.replace(tzinfo=pytz.utc).astimezone(user_tz)
        end_time_str = end_time_local.strftime("%d %b %Y at %I:%M %p (%Z)")

        embed = discord.Embed(
            title="Giveaway Started!",
            description=f"**Prize:** {prize}\nReact with 🎉 to enter!\nEnds on **{end_time_str}**" +
                        (f"\n**Requirement:** {required_role.mention}" if required_role else ""),
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Started by {interaction.user}")
        if image_url:
            embed.set_image(url=image_url)

        try:
            msg = await channel.send(embed=embed)
            await msg.add_reaction("🎉")
        except discord.Forbidden:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Unable to Post",
                    description=f"I couldn't send a message to {channel.mention}. Do I have permission?",
                    color=discord.Color.red()
                ), ephemeral=True
            )

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO giveaways (guild_id, channel_id, message_id, end_time, required_role)
                VALUES (?, ?, ?, ?, ?)
            ''', (interaction.guild.id, channel.id, msg.id, end_time_utc.timestamp(), str(required_role.id) if required_role else None))
            conn.commit()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Giveaway Created!",
                description=f"Giveaway for **{prize}** posted in {channel.mention} and ends on **{end_time_str}**.",
                color=discord.Color.green()
            ), ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
