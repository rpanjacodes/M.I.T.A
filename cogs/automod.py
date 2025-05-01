import discord
from discord.ext import commands
from discord import app_commands
import re
from db import get_automod_settings, set_automod_setting

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        try:
            anti_invite, anti_link, anti_spam = get_automod_settings(message.guild.id)
            content = message.content.lower()

            if anti_invite and re.search(r"(?:https?:\/\/)?(?:www\.)?(discord\.gg|discord\.com\/invite)\/[a-zA-Z0-9]+", content):
                await message.delete()
                return

            if anti_link and re.search(r"https?:\/\/\S+", content):
                await message.delete()
                return

            if anti_spam and message.content.isupper() and len(message.content) > 10:
                await message.delete()
                return

        except discord.Forbidden:
            # Bot lacks permission to delete messages
            channel = message.channel
            try:
                await channel.send("❌ I don't have permission to delete messages. Please check my permissions.", delete_after=5)
            except:
                pass  # Can't even send error
        except Exception as e:
            print(f"[AutoMod Error] {e}")

    # ===== Slash Commands =====

    @app_commands.command(name="toggle_anti_invite", description="Toggle the anti-Discord invite filter.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_anti_invite(self, interaction: discord.Interaction):
        new_state = await self._toggle_setting(interaction.guild.id, "anti_invite")
        await interaction.response.send_message(f"Anti-invite is now **{'enabled' if new_state else 'disabled'}**.", ephemeral=True)

    @app_commands.command(name="toggle_anti_link", description="Toggle the anti-link filter.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_anti_link(self, interaction: discord.Interaction):
        new_state = await self._toggle_setting(interaction.guild.id, "anti_link")
        await interaction.response.send_message(f"Anti-link is now **{'enabled' if new_state else 'disabled'}**.", ephemeral=True)

    @app_commands.command(name="toggle_anti_spam", description="Toggle the anti-spam (capslock) filter.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_anti_spam(self, interaction: discord.Interaction):
        new_state = await self._toggle_setting(interaction.guild.id, "anti_spam")
        await interaction.response.send_message(f"Anti-spam is now **{'enabled' if new_state else 'disabled'}**.", ephemeral=True)

    async def _toggle_setting(self, guild_id: int, key: str) -> bool:
        current = get_automod_settings(guild_id)
        keys = {"anti_invite": 0, "anti_link": 1, "anti_spam": 2}
        index = keys[key]
        new_val = 0 if current[index] else 1
        set_automod_setting(guild_id, key, new_val)
        return new_val

    # ===== Error Handler for Slash Commands =====

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ You need the **Manage Server** permission to use this command.",
                ephemeral=True
            )
        elif isinstance(error, discord.Forbidden):
            await interaction.response.send_message(
                "❌ I don't have the required permissions to perform this action.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"⚠️ An unexpected error occurred: `{error}`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
