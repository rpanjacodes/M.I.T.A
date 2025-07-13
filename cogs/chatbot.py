import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

# --------------------- Config ---------------------

SHAPES_API_KEY = ""  # Your Shapes API Key
SHAPES_API_URL = "https://api.shapes.inc/v1/chat/completions"
SHAPES_MODEL = "shapesinc/m.i.t.a_for_discord"  # Replace with your actual model

# --------------------- PostgreSQL DB Import ---------------------
from db import get_chatbot_channel, set_chatbot_channel, remove_chatbot_channel

# --------------------- Cog ---------------------

class ChatbotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_chatbot", description="Enable chatbot in a channel.")
    @app_commands.describe(channel="Channel where chatbot will reply")
    async def set_chatbot(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        await set_chatbot_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"Chatbot enabled in {channel.mention}.")

    @app_commands.command(name="disable_chatbot", description="Disable chatbot in the server.")
    async def disable_chatbot(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        await remove_chatbot_channel(interaction.guild.id)
        await interaction.response.send_message("Chatbot disabled.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        chatbot_channel_id = await get_chatbot_channel(message.guild.id)
        if not chatbot_channel_id or message.channel.id != chatbot_channel_id:
            return

        await message.channel.typing()

        headers = {
            "Authorization": f"Bearer {SHAPES_API_KEY}",
            "Content-Type": "application/json",
            "X-User-ID": str(message.author.id),
            "X-Channel-ID": str(message.channel.id),
        }

        json_data = {
            "model": SHAPES_MODEL,
            "messages": [{"role": "user", "content": message.content}]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(SHAPES_API_URL, headers=headers, json=json_data) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data['choices'][0]['message']['content']
                        await message.reply(reply)
                    else:
                        error_text = await resp.text()
                        await message.reply(f"Failed to get a response from the chatbot API.\n**Status:** {resp.status}\n**Details:** {error_text}")
        except Exception as e:
            await message.channel.send(f"API error: `{e}`")

# --------------------- Setup ---------------------

async def setup(bot):
    await bot.add_cog(ChatbotCog(bot))
