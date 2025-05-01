import discord
from discord.ext import commands
import asyncio
import os
from db import init_db  # Handles all DB tables

# Initialize the database
init_db()

# Bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

# Create the bot
bot = commands.Bot(command_prefix=None, intents=intents)

# Help Slash Command
@bot.tree.command(name="help", description="Shows the bot help menu.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Help Menu", color=discord.Color.blurple())
    embed.add_field(name="/pinbotmessage", value="Keep a message always at the bottom.", inline=False)
    embed.add_field(name="/nicknameformat", value="Set a custom nickname format like `FS | {username}`.", inline=False)
    embed.add_field(name="/moveall", value="Move all members from one VC to another.", inline=False)
    embed.set_footer(text="Use slash commands for best experience and Many Cmds not Listed Here.")
    embed.set_image(url="https://cdn.discordapp.com/attachments/1359128965444272324/1367226585886883900/Screenshot_2025-04-30-22-29-26-046_com.HoYoverse.Nap.jpg")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# When bot is ready
@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Game("With Your Fate")
    )
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Load cogs from /cogs folder
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

# Main bot run logic
async def main():
    async with bot:
        await load_cogs()
        await bot.start("token_only")  # Replace with your bot token

# Run the bot
asyncio.run(main())
