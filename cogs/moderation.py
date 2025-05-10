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
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.describe(user="User to kick", reason="Reason for kick")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        await interaction.response.defer(ephemeral=True)
        try:
            await user.kick(reason=reason)
            await interaction.followup.send(f"✅ {user} has been kicked.\nReason: {reason}")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to kick that user.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ An unexpected error occurred: `{e}`")

    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message("❌ You need `Kick Members` permission to use this command.", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(user="User to ban", reason="Reason for ban")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        await interaction.response.defer(ephemeral=True)
        try:
            await user.ban(reason=reason)
            await interaction.followup.send(f"✅ {user} has been banned.\nReason: {reason}")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to ban that user.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ An unexpected error occurred: `{e}`")

    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message("❌ You need `Ban Members` permission to use this command.", ephemeral=True)

    @app_commands.command(name="unban", description="Unban a previously banned user.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(user_id="The ID of the user to unban")
    async def unban(self, interaction: discord.Interaction, user_id: int):
        await interaction.response.defer(ephemeral=True)
        try:
            user = await self.bot.fetch_user(user_id)
            await interaction.guild.unban(user)
            await interaction.followup.send(f"✅ {user} has been unbanned.")
        except discord.NotFound:
            await interaction.followup.send("❌ This user is not banned or the ID is incorrect.")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to unban this user.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ An unexpected error occurred: `{e}`")

    @unban.error
    async def unban_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message("❌ You need `Ban Members` permission to use this command.", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a member.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(user="User to timeout", duration="Timeout duration in minutes", reason="Reason for timeout")
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: int, reason: str = "No reason provided"):
        await interaction.response.defer(ephemeral=True)
        try:
            await user.timeout(timedelta(minutes=duration), reason=reason)
            await interaction.followup.send(f"✅ {user.mention} has been timed out for {duration} minutes.\nReason: {reason}")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to timeout that user.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ An unexpected error occurred: `{e}`")

    @timeout.error
    async def timeout_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message("❌ You need `Moderate Members` permission to use this command.", ephemeral=True)

    @app_commands.command(name="untimeout", description="Remove timeout from a member.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(user="User to remove timeout")
    async def untimeout(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer(ephemeral=True)
        try:
            await user.timeout(None)
            await interaction.followup.send(f"✅ Timeout removed from {user.mention}.")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to untimeout that user.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ An unexpected error occurred: `{e}`")

    @untimeout.error
    async def untimeout_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message("❌ You need `Moderate Members` permission to use this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
