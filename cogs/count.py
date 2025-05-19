import discord
from discord.ext import commands
from discord import app_commands
from db import (
    set_count_channel,
    get_count_channel_settings,
    update_count_state,
    reset_count_state,
    get_current_count_message_id,
    set_current_count_message_id
)

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Set counting channel
    @app_commands.command(name="count_channel", description="Set a counting channel")
    @app_commands.describe(channel="Channel to count in", allow_chat="Allow chatting in the channel?")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def count_channel(self, interaction: discord.Interaction, channel: discord.TextChannel, allow_chat: bool = False):
        set_count_channel(interaction.guild_id, channel.id, allow_chat)
        reset_count_state(interaction.guild_id)
        await interaction.response.send_message(f"Counting channel set to {channel.mention}. Chatting allowed: `{allow_chat}`", ephemeral=True)

    # Reset counter manually
    @app_commands.command(name="reset_count", description="Reset the counter manually")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def reset_count(self, interaction: discord.Interaction):
        reset_count_state(interaction.guild_id)
        await interaction.response.send_message("Count has been reset.", ephemeral=True)

    # Handle counting logic
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        settings = get_count_channel_settings(message.guild.id)
        if not settings:
            return

        channel_id, allow_chat, last_user_id, last_number = settings
        if message.channel.id != channel_id:
            return

        try:
            number = int(message.content.strip())
        except ValueError:
            if not allow_chat:
                await message.delete()
            return

        if message.author.id == last_user_id or number != last_number + 1:
            await message.add_reaction("❌")
            await message.delete()
        else:
            await message.add_reaction("✅")
            update_count_state(message.guild.id, message.author.id, number)
            set_current_count_message_id(message.guild.id, message.id)

    # Reset count if valid message is deleted
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        settings = get_count_channel_settings(message.guild.id)
        if not settings:
            return

        current_message_id = get_current_count_message_id(message.guild.id)
        if current_message_id == message.id:
            reset_count_state(message.guild.id)
            channel = message.channel
            try:
                await channel.send("Count has been reset because the last valid number was deleted.")
            except:
                pass

    # Error handler for slash command permission issues
    @count_channel.error
    @reset_count.error
    async def permissions_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You don’t have permission to use this command (Manage Server required).", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Something went wrong while executing the command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Counting(bot))
