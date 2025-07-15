import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import asyncio
import feedparser
import re

from db import (
    add_follow_entry,
    set_follow_toggle,
    get_all_active_follows,
    get_last_video_id,
    set_last_video_id
)

# ------------------- API Keys -------------------
API_KEY_YT = "AIzaSyDkUqPE6eg3lUQpNh6Iqjz0qG8I4IacEIc"  # Replace this
API_BSKY_USERNAME = "rurustrm.bsky.social"
API_BSKY_APP_PASSWORD = "xyz23rjjb"

VALID_PLATFORMS = ["yt", "bsky"]

class FollowSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_follows.start()

    def cog_unload(self):
        self.check_follows.cancel()

    @app_commands.command(name="follow", description="Follow a YouTube or Bluesky account and notify on new posts.")
    @app_commands.describe(
        channel="Channel to send notifications to",
        platform="Platform to follow: yt, bsky",
        link="Link or ID of the account",
        message="Custom message to send when a new post is detected"
    )
    async def follow(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        platform: str,
        link: str,
        message: str
    ):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need `Manage Server` permission to use this command.", ephemeral=True)
            return

        if platform not in VALID_PLATFORMS:
            await interaction.response.send_message("❌ Invalid platform. Choose from: yt, bsky", ephemeral=True)
            return

        try:
            await add_follow_entry(
                guild_id=interaction.guild.id,
                channel_id=channel.id,
                platform=platform,
                link=link,
                message=message
            )
            await interaction.response.send_message(
                f"✅ Now watching `{platform}` account: <{link}>\n"
                f"Notifications will be sent in {channel.mention} with the message:\n```{message}```",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Error saving follow: {e}", ephemeral=True)

    @app_commands.command(name="follow_toggle", description="Enable or disable all follow notifications.")
    @app_commands.describe(state="Enable or disable follow system")
    @app_commands.choices(state=[
        app_commands.Choice(name="Enable", value="on"),
        app_commands.Choice(name="Disable", value="off")
    ])
    async def follow_toggle(self, interaction: discord.Interaction, state: app_commands.Choice[str]):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need `Manage Server` permission to use this command.", ephemeral=True)
            return

        try:
            await set_follow_toggle(interaction.guild.id, state.value == "on")
            await interaction.response.send_message(f"🔁 Follow system has been `{state.name}`.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error updating toggle: {e}", ephemeral=True)

    @tasks.loop(minutes=3)
    async def check_follows(self):
        print("[FollowChecker] Running check...")
        all_follows = await get_all_active_follows()
        for follow in all_follows:
            guild_id = follow['guild_id']
            channel_id = follow['channel_id']
            platform = follow['platform']
            link = follow['link']
            message = follow['custom_message']

            try:
                latest_id, thumbnail_url = await self.fetch_latest_id(platform, link)
                if not latest_id:
                    continue

                last_saved_id = await get_last_video_id(guild_id, platform)
                if latest_id != last_saved_id:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        embed = discord.Embed(
                            title="📢 New Post Detected!",
                            description=message,
                            color=discord.Color.green()
                        )
                        embed.add_field(name="Platform", value=platform.upper())
                        embed.add_field(name="Link", value=f"[Click Here]({link})", inline=False)
                        if thumbnail_url:
                            embed.set_image(url=thumbnail_url)
                        embed.set_footer(text="M.I.T.A Follow System ❤️")
                        await channel.send(embed=embed)
                        await set_last_video_id(guild_id, platform, latest_id)

                await asyncio.sleep(1.5)
            except Exception as e:
                print(f"[FollowChecker] Error checking {platform}: {e}")

    async def fetch_latest_id(self, platform: str, link: str):
        try:
            if platform == "yt":
                channel_id = self.extract_yt_channel_id(link)
                if not channel_id:
                    return None, None
                feed = feedparser.parse(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")
                if feed.entries:
                    video = feed.entries[0]
                    video_id = video.id.split(":")[-1]
                    thumbnail = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
                    return video.id, thumbnail

            elif platform == "bsky":
                handle = self.extract_bsky_handle(link)
                if not handle:
                    return None, None

                async with aiohttp.ClientSession() as session:
                    login_payload = {"identifier": API_BSKY_USERNAME, "password": API_BSKY_APP_PASSWORD}
                    async with session.post("https://bsky.social/xrpc/com.atproto.server.createSession", json=login_payload) as login_res:
                        print(f"[Bluesky] Login status: {login_res.status}")
                        if login_res.status != 200:
                            return None, None
                        login_data = await login_res.json()
                        token = login_data.get("accessJwt")

                    headers = {"Authorization": f"Bearer {token}"}
                    url = f"https://bsky.social/xrpc/app.bsky.feed.getAuthorFeed?actor={handle}"
                    async with session.get(url, headers=headers) as res:
                        print(f"[Bluesky] Feed fetch status: {res.status}")
                        if res.status != 200:
                            return None, None
                        data = await res.json()
                        post_uri = data.get("feed", [{}])[0].get("post", {}).get("uri")
                        return post_uri, None
        except Exception as e:
            print(f"[fetch_latest_id] Error: {e}")
        return None, None

    def extract_yt_channel_id(self, url: str):
        if "/channel/" in url:
            return url.split("/channel/")[1].split("/")[0]
        elif "/@" in url:
            return None  # Optional: YouTube handle support via API if needed
        elif re.fullmatch(r"[A-Za-z0-9_-]{24}", url):
            return url  # Direct channel ID
        return None

    def extract_bsky_handle(self, url: str):
        match = re.search(r"(bsky\.(social|app)/)(@?[\w.-]+)", url)
        handle = match.group(3) if match else url
        if handle.startswith("@"):
            handle = handle[1:]
        if not handle.endswith(".bsky.social"):
            handle += ".bsky.social"
        return handle

async def setup(bot):
    await bot.add_cog(FollowSettings(bot))
