#main.py
# M.I.T.A - Discord Bot Project
# Copyright (C) 2025 M.I.T.A Bot Team
# 
# This file is part of M.I.T.A.
# 
# M.I.T.A is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# M.I.T.A is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
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
        title="<:kirtikaze_impressed:1360665116399636650> Thanks for adding me!",
        description=(
            "<:kirtikaze_hii:1360664781761151196> I'm **M.I.T.A** – I Have Many Useful Features That Many Bots Doesn't Have. \n\n"
            "<a:arr:1371326929042407435> Use `/help` to explore my features.\n"
            "<a:arr:1371326929042407435> I Can Talk To You ! Just Type ``/set_channel`` And I Am Ready \n\n"
            "**Less Gooo !**"
        ),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="(⁠☞⁠^⁠o⁠^⁠)⁠ ⁠☞ Made With ❤️ By Kirtikaze Team")

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
        activity=discord.Game("「 M.I.T.A For You ❤️ 」")
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
        await bot.start("MTM0MjE3MDI0ODAyMjk4Njg2Ng.GhBdE1.Ywwkw6pexA8U7g37hJC0cdpkVdYybu9SMOg-kQ")  # Replace with your real token

# Run the bot
asyncio.run(main())
