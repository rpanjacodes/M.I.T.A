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

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Get the avatar of a user.")
    @app_commands.describe(user="The user to get the avatar of")
    async def avatar(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        avatar_url = user.display_avatar.url

        embed = discord.Embed(
            title=f"{user.name}'s Avatar",
            color=discord.Color.blurple()
        )
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Download", url=avatar_url))

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Avatar(bot))
