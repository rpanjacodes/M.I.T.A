# M.I.T.A - Discord Bot Project
# Copyright (C) 2025 M.I.T.A Bot Team
# 
# This file is part of M.I.T.A.
# 
# M.I.T.A is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# M.I.T.A is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Shows detailed information about this server.")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild

        embed = discord.Embed(
            title=f"Server Info - {guild.name}",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

        embed.add_field(name="Server Name", value=guild.name, inline=True)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "N/A", inline=True)

        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=f"{len(guild.text_channels)} Text / {len(guild.voice_channels)} Voice", inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)

        embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
        embed.add_field(name="Boost Tier", value=f"Level {guild.premium_tier}", inline=True)

        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
