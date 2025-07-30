import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import aiohttp

valid_categories = ["boy", "girl", "cat", "dog", "aesthetic", "anime"]

class ImageLooper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_settings = {}  # guild_id -> {"channel_id": ..., "category": ...}
        self.image_loop.start()

    async def cog_load(self):
        # Load settings from DB
        rows = await self.bot.db.get_all_image_settings()
        for row in rows:
            self.active_settings[row["guild_id"]] = {
                "channel_id": row["channel_id"],
                "category": row["category"]
            }

    def cog_unload(self):
        self.image_loop.cancel()

    @app_commands.command(name="image-post", description="Set or toggle image posting")
    @app_commands.describe(option="Type a category (boy/girl/cat...) or 'on'/'off'")
    async def image_post(self, interaction: discord.Interaction, option: str):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ You must be an admin to use this.", ephemeral=True)

        option = option.lower()
        guild_id = interaction.guild.id

        if option in valid_categories:
            await self.bot.db.set_image_setting(guild_id, interaction.channel.id, option)
            self.active_settings[guild_id] = {"channel_id": interaction.channel.id, "category": option}
            await interaction.response.send_message(f"✅ Category set to `{option}`. Use `/image-post on` to start.")
        
        elif option == "on":
            setting = await self.bot.db.get_image_setting(guild_id)
            if not setting:
                return await interaction.response.send_message("❌ Set a category first using `/image-post <category>`.", ephemeral=True)

            self.active_settings[guild_id] = {
                "channel_id": setting["channel_id"],
                "category": setting["category"]
            }
            await interaction.response.send_message(f"🟢 Started posting `{setting['category']}` images every 15 mins.")
        
        elif option == "off":
            await self.bot.db.clear_image_setting(guild_id)
            self.active_settings.pop(guild_id, None)
            await interaction.response.send_message("🛑 Image posting stopped.")
        
        else:
            await interaction.response.send_message("❌ Invalid input. Use a category or `on`/`off`.", ephemeral=True)

    @tasks.loop(minutes=15)
    async def image_loop(self):
        for guild_id, setting in self.active_settings.items():
            try:
                channel = self.bot.get_channel(setting["channel_id"])
                if channel:
                    url = await self.fetch_image(setting["category"])
                    embed = discord.Embed(title=f"Here's a random {setting['category']} image!")
                    embed.set_image(url=url)
                    await channel.send(embed=embed)
            except Exception as e:
                print(f"[image_loop] Error in guild {guild_id}: {e}")

    async def fetch_image(self, category: str) -> str:
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
