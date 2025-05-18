import discord
from discord import app_commands
from discord.ext import commands

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="giveaway", description="Start a giveaway (currently unavailable).")
    async def giveaway(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "⚠️ The `/giveaway` command is currently postponed and no longer available. Please check back later.",
            ephemeral=True
        )

    @app_commands.command(name="reroll", description="Reroll a giveaway (currently unavailable).")
    async def reroll(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "⚠️ The `/reroll` command is currently postponed and no longer available. Please check back later.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
