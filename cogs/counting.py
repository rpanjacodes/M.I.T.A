import discord
from discord.ext import commands
from discord import app_commands
from db import (
    set_count_channel,
    get_count_channel,
    remove_count_channel,
    get_current_count,
    get_last_counter,
    update_count,
    reset_count
)

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    count_group = app_commands.Group(name="count_channel", description="Manage the counting channel")

    async def is_admin(self, interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    @count_group.command(name="set")
    @app_commands.describe(channel="The channel where counting will happen")
    async def set_count_channel_cmd(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not await self.is_admin(interaction):
            await interaction.response.send_message("You need to be an administrator to use this command.", ephemeral=True)
            return

        await set_count_channel(interaction.guild.id, channel.id)
        await reset_count(interaction.guild.id)
        await interaction.response.send_message(f"✅ Counting channel set to {channel.mention} and counter reset!", ephemeral=True)

    @count_group.command(name="remove")
    async def remove_count_channel_cmd(self, interaction: discord.Interaction):
        if not await self.is_admin(interaction):
            await interaction.response.send_message("You need to be an administrator to use this command.", ephemeral=True)
            return

        await remove_count_channel(interaction.guild.id)
        await reset_count(interaction.guild.id)
        await interaction.response.send_message("🗑️ Counting channel removed and count reset!", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        channel_id = await get_count_channel(message.guild.id)
        if not channel_id or message.channel.id != channel_id:
            return

        try:
            count = int(message.content)
        except ValueError:
            await message.delete()
            return

        current = await get_current_count(message.guild.id)
        expected = current + 1
        last_user = await get_last_counter(message.guild.id)

        if count != expected:
            await message.delete()
            return

        if last_user == message.author.id:
            await message.delete()
            return

        await update_count(message.guild.id, expected, message.author.id)
        await message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(Counting(bot))
