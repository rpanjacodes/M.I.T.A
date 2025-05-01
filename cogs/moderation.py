import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # KICK COMMAND
    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.describe(user="User to kick", reason="Reason for kick")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        try:
            await user.kick(reason=reason)
            await interaction.response.send_message(f"✅ {user} has been kicked.\nReason: {reason}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to kick that user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ An unexpected error occurred: `{e}`", ephemeral=True)

    # BAN COMMAND
    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(user="User to ban", reason="Reason for ban")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        try:
            await user.ban(reason=reason)
            await interaction.response.send_message(f"✅ {user} has been banned.\nReason: {reason}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to ban that user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ An unexpected error occurred: `{e}`", ephemeral=True)

    # UNBAN COMMAND
    @app_commands.command(name="unban", description="Unban a previously banned user.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(user_id="The ID of the user to unban")
    async def unban(self, interaction: discord.Interaction, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ {user} has been unbanned.", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("❌ This user is not banned or the ID is incorrect.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ An unexpected error occurred: `{e}`", ephemeral=True)

    # TIMEOUT COMMAND
    @app_commands.command(name="timeout", description="Timeout a member.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(user="User to timeout", duration="Timeout duration in minutes", reason="Reason for timeout")
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: int, reason: str = "No reason provided"):
        try:
            await user.timeout(timedelta(minutes=duration), reason=reason)
            await interaction.response.send_message(f"✅ {user.mention} has been timed out for {duration} minutes.\nReason: {reason}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to timeout that user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ An unexpected error occurred: `{e}`", ephemeral=True)

    # UNTIMEOUT COMMAND
    @app_commands.command(name="untimeout", description="Remove timeout from a member.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(user="User to remove timeout")
    async def untimeout(self, interaction: discord.Interaction, user: discord.Member):
        try:
            await user.timeout(None)
            await interaction.response.send_message(f"✅ Timeout removed from {user.mention}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to untimeout that user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ An unexpected error occurred: `{e}`", ephemeral=True)

    # GENERIC ERROR HANDLER
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have the required permissions to use this command.",
                ephemeral=True
            )
        elif isinstance(error, discord.Forbidden):
            await interaction.response.send_message(
                "❌ I don’t have enough permissions to do that.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"⚠️ An unexpected error occurred: `{error}`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Moderation(bot))
