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

class VCMove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="move_user", description="Move a user to another voice channel.")
    @app_commands.checks.has_permissions(move_members=True)
    async def move_user(self, interaction: discord.Interaction,
                        member: discord.Member,
                        target_channel: discord.VoiceChannel):
        if not member.voice:
            await interaction.response.send_message(f"{member.display_name} is not in a voice channel.", ephemeral=True)
            return

        try:
            await member.move_to(target_channel)
            await interaction.response.send_message(f"Moved {member.display_name} to {target_channel.name}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to move that member.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ An unexpected error occurred: {e}", ephemeral=True)

    @app_commands.command(name="move_all", description="Move all members from one VC to another.")
    @app_commands.checks.has_permissions(move_members=True)
    async def move_all(self, interaction: discord.Interaction,
                       from_channel: discord.VoiceChannel,
                       to_channel: discord.VoiceChannel):
        if from_channel.id == to_channel.id:
            await interaction.response.send_message("❌ Source and target channels are the same.", ephemeral=True)
            return

        if not from_channel.members:
            await interaction.response.send_message("❌ There are no members in the source VC.", ephemeral=True)
            return

        failed = []
        for member in from_channel.members:
            try:
                await member.move_to(to_channel)
            except:
                failed.append(member.display_name)

        if failed:
            await interaction.response.send_message(
                f"⚠️ Moved others, but failed to move: {', '.join(failed)}", ephemeral=True)
        else:
            await interaction.response.send_message(
                f"✅ Moved all members from {from_channel.name} to {to_channel.name}.", ephemeral=True)

    # Custom error handler
    @move_user.error
    @move_all.error
    async def on_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You need the `Move Members` permission to use this command.", ephemeral=True)
        elif isinstance(error, discord.Forbidden):
            await interaction.response.send_message("❌ I don't have enough permissions to perform that action.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ An unexpected error occurred: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VCMove(bot))

