import discord
from discord.ext import commands
from discord import app_commands
import db  # Ensure all db functions here are async

PLACEHOLDERS = {
    "{user}": lambda m: m.mention,
    "{username}": lambda m: m.name,
    "{server}": lambda m: m.guild.name if m.guild else "",
}

def replace_placeholders(text, member):
    for key, func in PLACEHOLDERS.items():
        text = text.replace(key, func(member))
    return text

class DmGreet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(DMGreetGroup())

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        settings = await db.get_dm_greet_settings(member.guild.id)
        if not settings or not settings["enabled"]:
            return

        title = replace_placeholders(settings["title"], member)
        description = replace_placeholders(settings["description"], member)
        image_url = settings["image_url"]
        footer = settings["footer"]

        embed = discord.Embed(title=title, description=description, color=discord.Color.green())
        if image_url:
            embed.set_image(url=image_url)
        if footer:
            embed.set_footer(text=footer)

        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            print(f"[DM Greet] Couldn't DM {member.display_name}")

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You don't have permission to use this command. (Manage Server required)",
                ephemeral=True
            )
        elif isinstance(error, app_commands.CommandInvokeError):
            await interaction.response.send_message(
                f"An error occurred while executing the command: `{error.original}`",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "An unexpected error occurred. Please try again later.",
                ephemeral=True
            )

class DMGreetGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="dm-greet", description="Manage welcome DM greeting")

    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.command(name="enable", description="Enable welcome DMs")
    async def enable(self, interaction: discord.Interaction):
        await db.set_dm_greet_settings(interaction.guild_id, enabled=True)
        await interaction.response.send_message("DM greeting enabled!", ephemeral=True)

    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.command(name="disable", description="Disable welcome DMs")
    async def disable(self, interaction: discord.Interaction):
        await db.set_dm_greet_settings(interaction.guild_id, enabled=False)
        await interaction.response.send_message("DM greeting disabled.", ephemeral=True)

    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.command(name="set", description="Customize the DM greeting message")
    @app_commands.describe(
        title="Title of the embed",
        description="Description text",
        image_url="Image URL (optional)",
        footer="Footer text (optional)"
    )
    async def set(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        image_url: str = None,
        footer: str = None
    ):
        await db.set_dm_greet_settings(
            interaction.guild_id,
            title=title,
            description=description,
            image_url=image_url,
            footer=footer
        )
        await interaction.response.send_message("DM greeting message updated!", ephemeral=True)

    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.command(name="view", description="Show current DM greeting settings")
    async def view(self, interaction: discord.Interaction):
        settings = await db.get_dm_greet_settings(interaction.guild_id)
        if not settings:
            await interaction.response.send_message("No settings found.", ephemeral=True)
            return

        embed = discord.Embed(title="DM Greet Settings", color=discord.Color.blurple())
        embed.add_field(name="Enabled", value=str(settings["enabled"]))
        embed.add_field(name="Title", value=settings["title"], inline=False)
        embed.add_field(name="Description", value=settings["description"], inline=False)
        embed.add_field(name="Image URL", value=settings["image_url"] or "None", inline=False)
        embed.add_field(name="Footer", value=settings["footer"] or "None", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(DmGreet(bot))
