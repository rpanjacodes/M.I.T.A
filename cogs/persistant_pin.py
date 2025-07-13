import discord
from discord.ext import commands
from discord import app_commands
import db  # <- make sure your db.py uses asyncpg
import time

class PersistentPin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.cooldowns = {}  # channel_id: timestamp

    @app_commands.command(name="setbottommessage", description="Set a message that will always stay at the bottom.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(message="The message to keep at the bottom.")
    async def setbottommessage(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(thinking=True, ephemeral=True)

        channel = interaction.channel
        guild_id = interaction.guild.id
        channel_id = channel.id

        try:
            _, old_id = await db.get_pin_message(guild_id, channel_id)
            if old_id:
                try:
                    old_msg = await channel.fetch_message(old_id)
                    await old_msg.delete()
                except discord.NotFound:
                    pass

            new_msg = await channel.send(f"**{message}**")
            self.cache[channel_id] = new_msg.id
            await db.set_pin_message(guild_id, channel_id, message, new_msg.id)
            await db.set_pin_enabled(guild_id, channel_id, True)

            await interaction.followup.send("Bottom-pinned message set and enabled.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

    @setbottommessage.error
    async def setbottommessage_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You need `Manage Messages` permission.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Unexpected error: {error}", ephemeral=True)

    @app_commands.command(name="togglebottommessage", description="Enable or disable the bottom message.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.choices(state=[
        discord.app_commands.Choice(name="Enable", value="enable"),
        discord.app_commands.Choice(name="Disable", value="disable"),
    ])
    async def togglebottommessage(self, interaction: discord.Interaction, state: discord.app_commands.Choice[str]):
        await interaction.response.defer(thinking=True, ephemeral=True)

        try:
            guild_id = interaction.guild.id
            channel_id = interaction.channel.id
            enable = state.value == "enable"

            await db.set_pin_enabled(guild_id, channel_id, enable)
            await interaction.followup.send(
                f"Bottom message has been {'enabled' if enable else 'disabled'} for this channel.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild:
            return

        # Skip your own bot messages only
        if message.author.bot and message.author.id == self.bot.user.id:
            return

        guild_id = message.guild.id
        channel_id = message.channel.id

        if not await db.is_pin_enabled(guild_id, channel_id):
            return

        now = time.time()
        last = self.cooldowns.get(channel_id, 0)
        if now - last < 5:  # 5-second cooldown
            return
        self.cooldowns[channel_id] = now

        message_text, old_id = await db.get_pin_message(guild_id, channel_id)
        if not message_text:
            return

        try:
            if old_id:
                try:
                    old_msg = await message.channel.fetch_message(old_id)
                    await old_msg.delete()
                except discord.NotFound:
                    pass

            new_msg = await message.channel.send(f"**{message_text}**")
            self.cache[channel_id] = new_msg.id
            await db.set_pin_message(guild_id, channel_id, message_text, new_msg.id)
        except Exception as e:
            print(f"[PersistentPin] Error keeping message at bottom: {e}")

async def setup(bot):
    await bot.add_cog(PersistentPin(bot))
