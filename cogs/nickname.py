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
# along with this program. If not, see <https://www.gnu.org/licenses/>
import discord
from discord.ext import commands
from discord import app_commands
from db import get_nick_setting, set_nick_setting, set_nick_format

class Nickname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="toggle_nickname", description="Toggle nickname change on member join.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_nickname(self, interaction: discord.Interaction):
        try:
            enabled, _ = get_nick_setting(interaction.guild.id)
            new_val = 0 if enabled else 1
            set_nick_setting(interaction.guild.id, new_val)
            status = "enabled" if new_val else "disabled"
            await interaction.response.send_message(f"Nickname auto-change has been **{status}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error toggling nickname setting: {e}", ephemeral=True)

    @toggle_nickname.error
    async def toggle_nickname_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You need `Manage Server` permission to use this command.", ephemeral=True)

    @app_commands.command(name="set_nick_format", description="Set the nickname format (use {username})")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(format_str="Example: FS | {username}")
    async def set_nick_format_cmd(self, interaction: discord.Interaction, format_str: str):
        if "{username}" not in format_str:
            await interaction.response.send_message("Format must include `{username}`.", ephemeral=True)
            return

        try:
            set_nick_format(interaction.guild.id, format_str.strip())
            await interaction.response.send_message(f"Nickname format updated to:\n`{format_str}`", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error setting nickname format: {e}", ephemeral=True)

    @set_nick_format_cmd.error
    async def set_nick_format_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You need `Manage Server` permission to use this command.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            enabled, format_str = get_nick_setting(member.guild.id)
            if enabled:
                new_nick = format_str.replace("{username}", member.name)
                await member.edit(nick=new_nick)
        except discord.Forbidden:
            pass
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(Nickname(bot))
