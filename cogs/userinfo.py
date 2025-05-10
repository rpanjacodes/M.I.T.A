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
from badge import get_badges  # Import badge function

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Shows detailed information about a user.")
    @app_commands.describe(user="The user to get information about (optional)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user

        embed = discord.Embed(
            title=f"User Info - {user}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)

        embed.add_field(name="Username", value=f"{user.name}#{user.discriminator}", inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Display Name", value=user.display_name, inline=True)

        embed.add_field(name="Bot?", value=user.bot, inline=True)
        embed.add_field(name="Top Role", value=user.top_role.mention, inline=True)
        embed.add_field(name="Status", value=str(user.status).title(), inline=True)

        embed.add_field(name="Created At", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Joined At", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S") if user.joined_at else "N/A", inline=False)

        # Add custom badges if any
        badges = get_badges(user.id)
        if badges:
            embed.add_field(name="Badges", value=" ".join(badges), inline=False)

        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))
