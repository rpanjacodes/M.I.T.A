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
        await user.kick(reason=reason)
        await interaction.response.send_message(f"✅ {user} has been kicked.\nReason: {reason}", ephemeral=True)

    # BAN COMMAND
    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(user="User to ban", reason="Reason for ban")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        await user.ban(reason=reason)
        await interaction.response.send_message(f"✅ {user} has been banned.\nReason: {reason}", ephemeral=True)

    # UNBAN COMMAND
    @app_commands.command(name="unban", description="Unban a previously banned user.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(user_id="The ID of the user to unban")
    async def unban(self, interaction: discord.Interaction, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✅ {user} has been unbanned.", ephemeral=True)

    # TIMEOUT COMMAND
    @app_commands.command(name="timeout", description="Timeout a member.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(user="User to timeout", duration="Timeout duration in minutes", reason="Reason for timeout")
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: int, reason: str = "No reason provided"):
        await user.timeout(timedelta(minutes=duration), reason=reason)
        await interaction.response.send_message(f"✅ {user.mention} has been timed out for {duration} minutes.\nReason: {reason}", ephemeral=True)

    # UNTIMEOUT COMMAND
    @app_commands.command(name="untimeout", description="Remove timeout from a member.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(user="User to remove timeout")
    async def untimeout(self, interaction: discord.Interaction, user: discord.Member):
        await user.timeout(None)
        await interaction.response.send_message(f"✅ Timeout removed from {user.mention}.", ephemeral=True)

    # CUSTOM ERROR HANDLER
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have the required permissions to use this command.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"⚠️ An unexpected error occurred: `{error}`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Moderation(bot))
