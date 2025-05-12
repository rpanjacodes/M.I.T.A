import discord
from discord.ext import commands
from discord import app_commands

class ClearChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear_chat", description="Delete a number of messages from the current channel.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_chat(self, interaction: discord.Interaction, amount: int):
        if amount <= 0 or amount > 100:
            await interaction.response.send_message("❌ Please specify a number between 1 and 100.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)  # Prevent "application didn't respond"

        try:
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f"✅ Deleted {len(deleted)} messages.")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete messages.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    @clear_chat.error
    async def clear_chat_error(self, interaction: discord.Interaction, error):
        if interaction.response.is_done():
            send = interaction.followup.send
        else:
            send = interaction.response.send_message

        if isinstance(error, app_commands.errors.MissingPermissions):
            await send("❌ You need `Manage Messages` permission to use this command.", ephemeral=True)
        else:
            await send(f"⚠️ Error: `{error}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClearChat(bot))
