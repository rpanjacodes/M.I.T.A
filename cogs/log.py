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
from db import set_log_settings, get_log_channel_id, is_log_enabled

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Member banned log
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if is_log_enabled(guild.id):
            channel_id = get_log_channel_id(guild.id)
            channel = guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="🚫 Member Banned",
                    description=f"**{user}**",
                    color=discord.Color.red()
                )
                embed.set_footer(text=f"User ID: {user.id}")
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    pass

    # Member left/kicked log
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if is_log_enabled(member.guild.id):
            channel_id = get_log_channel_id(member.guild.id)
            channel = member.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="👋 Member Left or Kicked",
                    description=f"**{member}**",
                    color=discord.Color.orange()
                )
                embed.set_footer(text=f"User ID: {member.id}")
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    pass

    # Set log channel
    @app_commands.command(name="set_log_channel", description="Set the channel where logs will be posted.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        try:
            set_log_settings(interaction.guild.id, channel_id=channel.id)
            await interaction.response.send_message(f"✅ Logs will now be posted in {channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Something went wrong: `{e}`", ephemeral=True)

    @set_log_channel.error
    async def set_log_channel_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ You need `Manage Server` permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ Error: `{error}`", ephemeral=True)

    # Toggle logging
    @app_commands.command(name="toggle_logs", description="Enable or disable log messages.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_logs(self, interaction: discord.Interaction, enabled: bool):
        try:
            set_log_settings(interaction.guild.id, enabled=enabled)
            status = "enabled" if enabled else "disabled"
            await interaction.response.send_message(f"✅ Logging has been **{status}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Something went wrong: `{e}`", ephemeral=True)

    @toggle_logs.error
    async def toggle_logs_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ You need `Manage Server` permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ Error: `{error}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Logs(bot))
