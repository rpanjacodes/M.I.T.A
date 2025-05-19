# cogs/counting.py

import discord
from discord.ext import commands
from discord import app_commands
from db import (
    set_count_channel, get_count_channel_settings,
    update_count_state, get_count_state
)

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    count_group = app_commands.Group(name="count_channel", description="Manage the counting channel")

    async def is_admin(self, interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    @count_group.command(name="set")
    @app_commands.describe(channel="Channel to use for counting", allow_chat="Allow chatting in the counting channel?")
    async def set_count_channel_cmd(self, interaction: discord.Interaction, channel: discord.TextChannel, allow_chat: bool):
        if not await self.is_admin(interaction):
            await interaction.response.send_message("You need to be an administrator to use this command.", ephemeral=True)
            return

        set_count_channel(interaction.guild.id, channel.id, allow_chat)
        await interaction.response.send_message(
            f"Counting channel set to {channel.mention}. Chatting is {'allowed' if allow_chat else 'not allowed'}.",
            ephemeral=True
        )

    @count_group.command(name="disable")
    async def disable_counting(self, interaction: discord.Interaction):
        if not await self.is_admin(interaction):
            await interaction.response.send_message("You need to be an administrator to use this command.", ephemeral=True)
            return

        set_count_channel(interaction.guild.id, None, False)
        await interaction.response.send_message("Counting has been disabled.", ephemeral=True)

    @count_group.command(name="reset")
    async def reset_counting(self, interaction: discord.Interaction):
        if not await self.is_admin(interaction):
            await interaction.response.send_message("You need to be an administrator to use this command.", ephemeral=True)
            return

        update_count_state(interaction.guild.id, 0, 0)
        await interaction.response.send_message("Counting has been reset to 1.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        settings = get_count_channel_settings(message.guild.id)
        if not settings:
            return

        count_channel_id, allow_chat = settings
        if message.channel.id != count_channel_id:
            return

        # Try parsing number
        try:
            number = int(message.content.strip())
        except ValueError:
            if not allow_chat:
                await message.delete()
            return

        state = get_count_state(message.guild.id)
        last_user_id = None
        last_number = 0

        if state:
            last_user_id, last_number = state

        # Same user or wrong number breaks the count
        if message.author.id == last_user_id or number != last_number + 1:
            await message.delete()
            await message.channel.send("**The count was broken! Start again from 1.**")
            update_count_state(message.guild.id, 0, 0)
            return

        await message.add_reaction("✅")
        update_count_state(message.guild.id, message.author.id, number)

async def setup(bot: commands.Bot):
    await bot.add_cog(Counting(bot))
