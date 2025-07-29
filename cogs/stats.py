import discord
from discord.ext import commands
from discord import app_commands
import time

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    def get_uptime(self):
        seconds = int(time.time() - self.start_time)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return f"{days}d {hours}h {minutes}m {seconds}s"

    @app_commands.command(name="stats", description="View bot stats")
    async def stats(self, interaction: discord.Interaction):
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        total_guilds = len(self.bot.guilds)
        latency = round(self.bot.latency * 1000)  # in ms
        uptime = self.get_uptime()

        embed = discord.Embed(title="📊 Bot Statistics", color=discord.Color.green())
        embed.add_field(name="🧠 Servers", value=str(total_guilds), inline=True)
        embed.add_field(name="👥 Members", value=str(total_members), inline=True)
        embed.add_field(name="📶 Ping", value=f"{latency}ms", inline=True)
        embed.add_field(name="⏱️ Uptime", value=uptime, inline=False)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))
