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

        # Avoid errors if bot lacks permissions
        if not message.guild.me.guild_permissions.manage_messages:
            return

        try:
            anti_invite, anti_link, anti_spam = get_automod_settings(message.guild.id) or (0, 0, 0)
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
            try:
                await message.channel.send("❌ I don't have permission to delete messages. Please check my permissions.", delete_after=5)
            except:
                pass
        except Exception as e:
            print(f"[AutoMod Error] {e}")

    # ===== Slash Commands =====

    @app_commands.command(name="toggle_anti_invite", description="Toggle the anti-Discord invite filter.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_anti_invite(self, interaction: discord.Interaction):
        await self._handle_toggle(interaction, "anti_invite", "Anti-invite")

    @app_commands.command(name="toggle_anti_link", description="Toggle the anti-link filter.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_anti_link(self, interaction: discord.Interaction):
        await self._handle_toggle(interaction, "anti_link", "Anti-link")

    @app_commands.command(name="toggle_anti_spam", description="Toggle the anti-spam (capslock) filter.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_anti_spam(self, interaction: discord.Interaction):
        await self._handle_toggle(interaction, "anti_spam", "Anti-spam")

    async def _handle_toggle(self, interaction: discord.Interaction, key: str, label: str):
        try:
            current = get_automod_settings(interaction.guild.id) or (0, 0, 0)
            index = {"anti_invite": 0, "anti_link": 1, "anti_spam": 2}[key]
            new_val = 0 if current[index] else 1
            set_automod_setting(interaction.guild.id, key, new_val)
            status = "enabled" if new_val else "disabled"
            await interaction.response.send_message(f"{label} is now **{status}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Something went wrong: `{e}`", ephemeral=True)

    # ===== Error Handler =====

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        try:
            send = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message

            if isinstance(error, app_commands.errors.MissingPermissions):
                await send("❌ You need the **Manage Server** permission to use this command.", ephemeral=True)
            elif isinstance(error, discord.Forbidden):
                await send("❌ I don't have the required permissions to perform this action.", ephemeral=True)
            else:
                await send(f"⚠️ An unexpected error occurred: `{error}`", ephemeral=True)
        except Exception as e:
            print(f"[AutoMod Command Error] {e}")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
