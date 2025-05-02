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

# When the bot joins a new guild
@bot.event
async def on_guild_join(guild: discord.Guild):
    embed = discord.Embed(
        title="Thanks for adding me!",
        description=(
            "I'm **Sarah** – your all-in-one moderation, anime, utility, and customization assistant.\n\n"
            "Use `/help` to explore my features.\n"
            "Need setup help? Configure nickname format, logging, anime alerts, and more!\n\n"
            "**Get started with `/setlogchannel`, `/nicknameformat`, and `/setanimeupdates`.**"
        ),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Feel free to ask for help anytime!")

    # Try system channel first
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        await guild.system_channel.send(embed=embed)
    else:
        # Fallback: first text channel where bot can send messages
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(embed=embed)
                break

# When the bot is ready
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

# Load all cogs from the /cogs folder
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

# Main function to start the bot
async def main():
    async with bot:
        await load_cogs()
        await bot.start("bot_token")  # Replace with your real token

# Run the bot
asyncio.run(main())
