import discord
from discord.ext import commands
from discord import app_commands
from db import set_log_settings, get_log_channel_id, is_log_enabled  # Replace if you unify into one function

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
                await channel.send(embed=embed)

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
                await channel.send(embed=embed)

    @app_commands.command(name="set_log_channel", description="Set the channel where logs will be posted.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        set_log_settings(interaction.guild.id, channel_id=channel.id)
        await interaction.response.send_message(f"✅ Logs will now be posted in {channel.mention}", ephemeral=True)

    @app_commands.command(name="toggle_logs", description="Enable or disable log messages.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_logs(self, interaction: discord.Interaction, enabled: bool):
        set_log_settings(interaction.guild.id, enabled=enabled)
        status = "enabled" if enabled else "disabled"
        await interaction.response.send_message(f"✅ Logging has been **{status}**.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Logs(bot))
