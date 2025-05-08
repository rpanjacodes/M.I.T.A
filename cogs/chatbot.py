import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import aiohttp

# --------------------- Config ---------------------

SHAPES_API_KEY = "your_api_key_here"  # Put your API key directly here
SHAPES_API_URL = "https://api.shapes.inc/v1/chat/completions"
DB_PATH = "bot.db"

# --------------------- Database Utils ---------------------

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS chatbot_settings (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER
            )
        ''')

def set_chatbot_channel(guild_id, channel_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO chatbot_settings (guild_id, channel_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET channel_id = excluded.channel_id
        ''', (guild_id, channel_id))

def disable_chatbot_channel(guild_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM chatbot_settings WHERE guild_id = ?', (guild_id,))

def get_chatbot_channel(guild_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT channel_id FROM chatbot_settings WHERE guild_id = ?', (guild_id,))
        row = c.fetchone()
        return row[0] if row else None

# --------------------- Cog ---------------------

class ChatbotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        init_db()

    @app_commands.command(name="set_chatbot", description="Enable chatbot in a channel.")
    @app_commands.describe(channel="Channel where chatbot will reply")
    async def set_chatbot(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        set_chatbot_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"Chatbot enabled in {channel.mention}.")

    @app_commands.command(name="disable_chatbot", description="Disable chatbot in the server.")
    async def disable_chatbot(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        disable_chatbot_channel(interaction.guild.id)
        await interaction.response.send_message("Chatbot disabled.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        chatbot_channel_id = get_chatbot_channel(message.guild.id)
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
            "model": "shapes-small-alpha",
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
                        await message.reply("Failed to get a response from the chatbot API.")
        except Exception as e:
            await message.channel.send(f"API error: {e}")

# --------------------- Setup ---------------------

async def setup(bot):
    await bot.add_cog(ChatbotCog(bot))
