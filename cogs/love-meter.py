import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import random
import aiohttp
import io

class LoveMeter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lovemeter", description="Check love percentage between two users!")
    @app_commands.describe(person1="First person", person2="Second person")
    @app_commands.checks.cooldown(rate=1, per=10.0)
    async def lovemeter(self, interaction: discord.Interaction, person1: discord.Member, person2: discord.Member):
        await interaction.response.defer()

        percent = random.randint(1, 100)

        if percent <= 30:
            heart_path = "assets/low_heart.png"
        elif percent <= 70:
            heart_path = "assets/half_heart.png"
        else:
            heart_path = "assets/full_heart.png"

        bg = Image.open("assets/background.png").convert("RGBA")
        heart = Image.open(heart_path).resize((128, 128)).convert("RGBA")

        async with aiohttp.ClientSession() as session:
            async with session.get(str(person1.avatar.url)) as resp1:
                avatar1 = Image.open(io.BytesIO(await resp1.read())).resize((300, 300)).convert("RGBA")
            async with session.get(str(person2.avatar.url)) as resp2:
                avatar2 = Image.open(io.BytesIO(await resp2.read())).resize((300, 300)).convert("RGBA")

        bg.paste(avatar1, (180, 230), avatar1)
        bg.paste(avatar2, (960, 230), avatar2)
        bg.paste(heart, (610, 100), heart)

        draw = ImageDraw.Draw(bg)
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            font = ImageFont.load_default()

        draw.text((230, 550), person1.display_name, font=font, fill="white")
        draw.text((1010, 550), person2.display_name, font=font, fill="white")

        buffer = io.BytesIO()
        bg.save(buffer, format="PNG")
        buffer.seek(0)

        await interaction.followup.send(
            content=f"💘 **Love Meter:** {person1.mention} ❤️ {person2.mention} = `{percent}%`",
            file=discord.File(buffer, filename="lovemeter.png")
        )

    # Error handler for cooldown
    @lovemeter.error
    async def on_lovemeter_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏳ Slow down! Try again in `{round(error.retry_after, 1)}s`.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(LoveMeter(bot))
