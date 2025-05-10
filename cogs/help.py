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

class HelpDropdown(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpSelect())

class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moderation", description="Ban, kick, timeout, etc."),
            discord.SelectOption(label="Anime", description="Anime updates, test post, etc."),
            discord.SelectOption(label="Utility", description="Embed command, server info, etc."),
            discord.SelectOption(label="Setup", description="Configure logs, nickname format, etc."),
        ]
        super().__init__(placeholder="Choose a command category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.blurple())
        if self.values[0] == "Moderation":
            embed.title = "Moderation Commands"
            embed.description = (
                "`/ban` - Ban a user\n"
                "`/kick` - Kick a user\n"
                "`/timeout` - Timeout a user\n"
                "`/move` - Move a user to a voice channel\n"
                "`/moveall` - Move all users to a VC"
            )
        elif self.values[0] == "Anime":
            embed.title = "Anime Commands"
            embed.description = (
                "`/setanimeupdates` - Set channel for anime updates\n"
                "`/removeanimeupdates` - Disable anime updates\n"
                "`/testanimepost` - Send a test anime embed"
            )
        elif self.values[0] == "Utility":
            embed.title = "Utility Commands"
            embed.description = (
                "`/embed` - Send a custom embed\n"
                "`/serverinfo` - Server information\n"
                "`/userinfo` - Information about a user"
            )
        elif self.values[0] == "Setup":
            embed.title = "Setup Commands"
            embed.description = (
                "`/setlogchannel` - Set log channel\n"
                "`/setnickformat` - Set auto nickname format\n"
                "`/setautomod` - Configure automod"
            )

        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all bot commands by category using dropdown.")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Bot Help Menu",
            description="Select a category from the dropdown below to view the available commands.",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=HelpDropdown(), ephemeral=False)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
