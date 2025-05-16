import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import pytz
import random
import db  # your database handler module

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @app_commands.command(name="giveaway", description="Start a giveaway with timezone support.")
    @app_commands.describe(
        duration="Duration in minutes",
        prize="What is the prize?",
        timezone="Your timezone (e.g., Europe/London, Asia/Kolkata)",
        image_url="Optional image URL",
        required_role="Role required to join (optional)"
    )
    async def giveaway(
        self,
        interaction: discord.Interaction,
        duration: int,
        prize: str,
        timezone: str,
        image_url: str = None,
        required_role: discord.Role = None
    ):
        # Permission check: Must have Manage Messages
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You need the **Manage Messages** permission to start a giveaway.",
                ephemeral=True
            )
            return

        if duration <= 0:
            await interaction.response.send_message("Duration must be greater than 0 minutes.", ephemeral=True)
            return

        try:
            tz = pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            await interaction.response.send_message(
                "Invalid timezone. Use names like `Europe/London` or `Asia/Kolkata`.",
                ephemeral=True
            )
            return

        end_time = datetime.now(pytz.utc) + timedelta(minutes=duration)

        # Create embed
        embed = discord.Embed(
            title="🎉 Giveaway Started!",
            description=f"**Prize:** {prize}\nEnds <t:{int(end_time.timestamp())}:R>\nReact with 🎉 to enter!",
            color=discord.Color.green()
        )
        if required_role:
            embed.add_field(name="Required Role", value=required_role.mention, inline=False)
        if image_url:
            embed.set_image(url=image_url)

        embed.set_footer(text=f"Hosted by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        # Send message
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("🎉")

        # Store in DB
        db.store_giveaway(
            guild_id=interaction.guild.id,
            message_id=message.id,
            channel_id=message.channel.id,
            image_url=image_url,
            end_time=end_time.timestamp(),
            required_role=required_role.id if required_role else None
        )

    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        giveaways = db.get_active_giveaways()
        now = datetime.now(pytz.utc).timestamp()

        for giveaway in giveaways:
            guild_id, message_id, channel_id, image_url, end_time, required_role_id = giveaway

            if now < end_time:
                continue

            guild = self.bot.get_guild(guild_id)
            if not guild:
                db.remove_giveaway(guild_id, message_id)
                continue

            channel = guild.get_channel(channel_id)
            if not channel:
                db.remove_giveaway(guild_id, message_id)
                continue

            try:
                message = await channel.fetch_message(message_id)
            except discord.NotFound:
                db.remove_giveaway(guild_id, message_id)
                continue

            reaction = discord.utils.get(message.reactions, emoji="🎉")
            if not reaction:
                db.remove_giveaway(guild_id, message_id)
                continue

            try:
                users = await reaction.users().flatten()
            except Exception as e:
                print(f"[Giveaway] Error fetching users: {e}")
                db.remove_giveaway(guild_id, message_id)
                continue

            users = [u for u in users if not u.bot]

            if required_role_id:
                role = guild.get_role(required_role_id)
                users = [
                    u for u in users
                    if (member := guild.get_member(u.id)) and role in member.roles
                ]

            if users:
                winner = random.choice(users)
                embed = discord.Embed(
                    title="🎉 Giveaway Ended!",
                    description=f"Congrats {winner.mention}, you won **{message.embeds[0].description.splitlines()[0][9:]}**!",
                    color=discord.Color.gold()
                )
                await channel.send(embed=embed)
            else:
                await channel.send("Nobody joined the giveaway.")

            db.remove_giveaway(guild_id, message_id)

    @check_giveaways.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
