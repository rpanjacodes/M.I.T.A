import discord
from discord import app_commands
from discord.ext import commands

class EmbedSay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Send a custom embedded message.")
    @app_commands.describe(title="Title of the embed", description="Description text of the embed")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def embed(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str
    ):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Sent by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("Embed sent successfully.", ephemeral=True)

    @embed.error
    async def embed_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "You need the **Manage Channels** permission to use this command.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "An unexpected error occurred while processing your embed.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(EmbedSay(bot))
