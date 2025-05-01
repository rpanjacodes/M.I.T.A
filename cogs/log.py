import discord
from discord.ext import commands
from discord import app_commands
from db import set_log_settings, get_log_channel_id, is_log_enabled

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if is_log_enabled(guild.id):
            channel_id = get_log_channel_id(guild.id)
            channel = guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="🚫 Member Banned",
                    description=f"**{user.name}#{user.discriminator}**",
                    color=discord.Color.red()
                )
                embed.set_footer(text=f"User ID: {user.id}")
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if is_log_enabled(member.guild.id):
            channel_id = get_log_channel_id(member.guild.id)
            channel = member.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="👋 Member Left or Kicked",
                    description=f"**{member.name}#{member.discriminator}**",
                    color=discord.Color.orange()
                )
                embed.set_footer(text=f"User ID: {member.id}")
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    pass

    @app_commands.command(name="set_log_channel", description="Set the channel where logs will be posted.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        try:
            set_log_settings(interaction.guild.id, channel_id=channel.id)
            await interaction.response.send_message(f"✅ Logs will now be posted in {channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Something went wrong: `{e}`", ephemeral=True)

    @app_commands.command(name="toggle_logs", description="Enable or disable log messages.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_logs(self, interaction: discord.Interaction, enabled: bool):
        try:
            set_log_settings(interaction.guild.id, enabled=enabled)
            status = "enabled" if enabled else "disabled"
            await interaction.response.send_message(f"✅ Logging has been **{status}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Something went wrong: `{e}`", ephemeral=True)

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ You need the **Manage Server** permission to use this command.",
                ephemeral=True
            )
        elif isinstance(error, discord.Forbidden):
            await interaction.response.send_message(
                "❌ I don't have permission to do that. Please check my role permissions.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"⚠️ An unexpected error occurred: `{error}`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Logs(bot))
