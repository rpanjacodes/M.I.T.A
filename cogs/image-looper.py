import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import aiohttp

class ImageLooper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_settings = {}  # {guild_id: {"channel_id": ..., "category": ...}}
        self.image_loop.start()

    def cog_unload(self):
        self.image_loop.cancel()

    async def cog_load(self):
        # Load saved settings from database
        rows = await self.bot.db.get_all_image_settings()
        for row in rows:
            self.active_settings[row["guild_id"]] = {
                "channel_id": row["channel_id"],
                "category": row["category"]
            }

    @app_commands.command(name="image", description="Control image loop")
    @app_commands.describe(option="Type a category or turn it on/off")
    async def image(self, interaction: discord.Interaction, option: str):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ You must be an admin to use this command.", ephemeral=True)

        option = option.lower()
        valid_categories = ["boys", "girls", "cat", "dog", "aesthetic", "anime"]
        guild_id = interaction.guild.id

        if option in valid_categories:
            # Set category, wait for 'on'
            await self.bot.db.set_image_setting(guild_id, interaction.channel.id, option)
            self.active_settings[guild_id] = {"channel_id": interaction.channel.id, "category": option}
            await interaction.response.send_message(f"✅ Image category set to `{option}`. Use `/image on` to start.")
        elif option == "on":
            setting = await self.bot.db.get_image_setting(guild_id)
            if not setting:
                await interaction.response.send_message("❌ First set a category using `/image <category>`", ephemeral=True)
            else:
                self.active_settings[guild_id] = {
                    "channel_id": setting["channel_id"],
                    "category": setting["category"]
                }
                await interaction.response.send_message(f"🟢 Now sending `{setting['category']}` images every 15 minutes!")
        elif option == "off":
            await self.bot.db.clear_image_setting(guild_id)
            self.active_settings.pop(guild_id, None)
            await interaction.response.send_message("🛑 Image sending stopped.")
        else:
            await interaction.response.send_message("❌ Invalid option. Use a category or `on`/`off`.", ephemeral=True)

    @tasks.loop(minutes=15)
    async def image_loop(self):
        for guild_id, setting in self.active_settings.items():
            try:
                channel = self.bot.get_channel(setting["channel_id"])
                if channel:
                    url = await self.get_image_url(setting["category"])
                    embed = discord.Embed(title=f"Random {setting['category'].title()} Image")
                    embed.set_image(url=url)
                    await channel.send(embed=embed)
            except Exception as e:
                print(f"[ImageLooper] Error sending image for guild {guild_id}: {e}")

    async def get_image_url(self, category):
        if category == "cat":
            async with aiohttp.ClientSession() as session:
                async with session.get("https://some-random-api.ml/img/cat") as r:
                    return (await r.json())["link"]
        elif category == "dog":
            async with aiohttp.ClientSession() as session:
                async with session.get("https://some-random-api.ml/img/dog") as r:
                    return (await r.json())["link"]
        else:
            return f"https://source.unsplash.com/600x400/?{category}"

async def setup(bot):
    await bot.add_cog(ImageLooper(bot))
