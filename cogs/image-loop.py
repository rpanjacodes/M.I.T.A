import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import aiohttp

from db import set_image_setting, get_image_setting, clear_image_setting, get_all_image_settings

class ImageLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.image_loop.start()
        self.valid_categories = ["boy", "girl", "cat", "dog", "aesthetic", "anime"]

    @app_commands.command(name="image-post", description="Set or control auto image posting")
    @app_commands.describe(mode="Choose a category or turn on/off image posting")
    async def image_post(self, interaction: discord.Interaction, mode: str):
        guild_id = interaction.guild.id
        channel_id = interaction.channel.id

        if mode.lower() == "off":
            await clear_image_setting(guild_id)
            await interaction.response.send_message("✅ Image posting disabled.", ephemeral=True)
            return

        if mode.lower() == "on":
            setting = await get_image_setting(guild_id)
            if setting:
                await interaction.response.send_message("✅ Image posting enabled.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ No category set. Please run `/image-post <category>` first.", ephemeral=True)
            return

        category = mode.lower()
        if category not in self.valid_categories:
            await interaction.response.send_message(
                f"❌ Invalid category. Choose from: {', '.join(self.valid_categories)}", ephemeral=True
            )
            return

        await set_image_setting(guild_id, channel_id, category)
        await interaction.response.send_message(f"✅ Category set to **{category}** and image posting is now active.", ephemeral=True)

    @tasks.loop(minutes=15)
    async def image_loop(self):
        settings = await get_all_image_settings()
        for setting in settings:
            try:
                guild = self.bot.get_guild(setting["guild_id"])
                if not guild:
                    continue

                channel = guild.get_channel(setting["channel_id"])
                if not channel:
                    continue

                image_url = await self.fetch_random_image(setting["category"])
                if image_url:
                    await channel.send(image_url)
            except Exception as e:
                print(f"[ImageLoop] Error posting image: {e}")

    async def fetch_random_image(self, category):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.waifu.pics/sfw/{category}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("url")
        except Exception as e:
            print(f"[ImageLoop] Failed to fetch image: {e}")
        return None

    @image_loop.before_loop
    async def before_image_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ImageLoop(bot))
