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
from discord import app_commands
from discord.ext import commands

class EmbedSay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Send a custom embedded message.")
    @app_commands.describe(title="Title of the embed", description="Description text of the embed")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def embed(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str
    ):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Sent by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("Embed sent successfully.", ephemeral=True)

    @embed.error
    async def embed_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "You need the **Manage Channels** permission to use this command.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "An unexpected error occurred while processing your embed.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(EmbedSay(bot))
