import discord
from discord.ext import commands
from discord import app_commands
from io import BytesIO
import aiohttp
from PIL import Image, ImageDraw, ImageFont
import db  # your centralized db.py

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_welcome", description="Set welcome message settings.")
    @app_commands.describe(
        channel="Channel to send welcome messages",
        bg_url="Background image URL",
        big_text="Big text on image",
        small_text="Small text on image",
        description="Welcome message (use {user} and {server})"
    )
    async def set_welcome(self, interaction: discord.Interaction, channel: discord.TextChannel, bg_url: str, big_text: str, small_text: str, description: str):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need **Manage Server** permission to use this command.", ephemeral=True)
            return

        db.set_welcome_settings(
            interaction.guild.id, channel.id, bg_url, big_text, small_text, description
        )
        await interaction.response.send_message("✅ Welcome settings updated.", ephemeral=True)

    @app_commands.command(name="toggle_welcome", description="Enable or disable welcome message.")
    async def toggle_welcome(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need **Manage Server** permission to use this command.", ephemeral=True)
            return

        enabled = db.toggle_welcome(interaction.guild.id)
        status = "enabled ✅" if enabled else "disabled ❌"
        await interaction.response.send_message(f"Welcome system is now **{status}**", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        settings = db.get_welcome_settings(member.guild.id)
        if not settings or not settings['enabled']:
            return

        channel = member.guild.get_channel(settings['channel_id'])
        if not channel:
            return

        image = await self.build_welcome_image(member, settings)

        # Use display name instead of mention to avoid breaking when user leaves
        username = member.display_name
        description = settings['description'].replace("{user}", username).replace("{server}", member.guild.name)

        file = discord.File(fp=image, filename="welcome.png")
        embed = discord.Embed(description=description, color=discord.Color.blue())
        embed.set_image(url="attachment://welcome.png")
        await channel.send(file=file, embed=embed)

    async def build_welcome_image(self, member, settings):
        # Download background
        async with aiohttp.ClientSession() as session:
            async with session.get(settings['bg_url']) as resp:
                bg_bytes = await resp.read()
        bg = Image.open(BytesIO(bg_bytes)).convert("RGBA").resize((1280, 480))

        # Download avatar
        async with aiohttp.ClientSession() as session:
            async with session.get(member.display_avatar.url) as resp:
                avatar_bytes = await resp.read()
        avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA").resize((250, 250))

        # Circle crop
        mask = Image.new("L", avatar.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 250, 250), fill=255)
        avatar.putalpha(mask)

        bg.paste(avatar, (60, 115), avatar)

        draw = ImageDraw.Draw(bg)
        font_big = ImageFont.truetype("arial.ttf", 60)
        font_small = ImageFont.truetype("arial.ttf", 36)

        draw.text((350, 150), settings['big_text'], font=font_big, fill="white")
        draw.text((350, 230), settings['small_text'], font=font_small, fill="white")

        output = BytesIO()
        bg.save(output, format="PNG")
        output.seek(0)
        return output

async def setup(bot):
    await bot.add_cog(Welcome(bot))
