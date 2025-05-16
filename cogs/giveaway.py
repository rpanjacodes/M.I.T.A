import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import pytz
import asyncio
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
    async def giveaway(self, interaction: discord.Interaction, duration: int, prize: str, timezone: str, image_url: str = None, required_role: discord.Role = None):
        try:
            tz = pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            await interaction.response.send_message("Invalid timezone. Please use a valid TZ database name like `Europe/London` or `Asia/Kolkata`.", ephemeral=True)
            return

        end_time = datetime.now(pytz.utc) + timedelta(minutes=duration)

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
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        await message.add_reaction("🎉")

        db.add_giveaway(
            message_id=message.id,
            channel_id=message.channel.id,
            guild_id=interaction.guild.id,
            end_time=end_time.timestamp(),
            prize=prize,
            required_role_id=required_role.id if required_role else None
        )

    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        giveaways = db.get_active_giveaways()
        now = datetime.now(pytz.utc).timestamp()

        for giveaway in giveaways:
            if now >= giveaway['end_time']:
                guild = self.bot.get_guild(giveaway['guild_id'])
                if not guild:
                    db.remove_giveaway(giveaway['message_id'])
                    continue

                channel = guild.get_channel(giveaway['channel_id'])
                if not channel:
                    db.remove_giveaway(giveaway['message_id'])
                    continue

                try:
                    message = await channel.fetch_message(giveaway['message_id'])
                except discord.NotFound:
                    db.remove_giveaway(giveaway['message_id'])
                    continue

                reaction = discord.utils.get(message.reactions, emoji="🎉")
                if not reaction:
                    db.remove_giveaway(giveaway['message_id'])
                    continue

                users = await reaction.users().flatten()
                users = [u for u in users if not u.bot]

                if giveaway['required_role_id']:
                    users = [
                        u for u in users
                        if discord.utils.get(guild.get_member(u.id).roles, id=giveaway['required_role_id'])
                    ]

                if users:
                    winner = random.choice(users)
                    await channel.send(f"🎉 Congrats {winner.mention}, you won **{giveaway['prize']}**!")
                else:
                    await channel.send(f"Nobody joined the giveaway for **{giveaway['prize']}**.")

                db.remove_giveaway(giveaway['message_id'])

    @check_giveaways.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
