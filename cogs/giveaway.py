import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import pytz
import random
import db

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()
        self.bot.giveaway_winners = {}

    def cog_unload(self):
        self.check_giveaways.cancel()

    @app_commands.command(name="giveaway", description="Start a giveaway with timezone support.")
    @app_commands.describe(
        duration="Duration in minutes",
        prize="What is the prize?",
        timezone="Your timezone (e.g., Europe/London, Asia/Kolkata)",
        winners="Number of winners (default: 1)",
        image_url="Optional image URL",
        required_role="Role required to join (optional)"
    )
    async def giveaway(
        self,
        interaction: discord.Interaction,
        duration: int,
        prize: str,
        timezone: str,
        winners: int = 1,
        image_url: str = None,
        required_role: discord.Role = None
    ):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You need the **Manage Messages** permission to start a giveaway.",
                ephemeral=True
            )
            return

        perms = interaction.channel.permissions_for(interaction.guild.me)
        if not perms.send_messages or not perms.embed_links or not perms.add_reactions:
            await interaction.response.send_message(
                "I need the following permissions: **Send Messages**, **Embed Links**, **Add Reactions**.",
                ephemeral=True
            )
            return

        if duration <= 0 or winners <= 0:
            await interaction.response.send_message("Duration and winners must be greater than 0.", ephemeral=True)
            return

        try:
            tz = pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            await interaction.response.send_message("Invalid timezone format.", ephemeral=True)
            return

        end_time = datetime.now(pytz.utc) + timedelta(minutes=duration)

        embed = discord.Embed(
            title="🎉 Giveaway Started!",
            description=f"**Prize:** {prize}\n"
                        f"**Winners:** {winners}\n"
                        f"Ends <t:{int(end_time.timestamp())}:R>\n"
                        f"React with 🎉 to enter!",
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

        db.store_giveaway(
            guild_id=interaction.guild.id,
            message_id=message.id,
            channel_id=message.channel.id,
            image_url=image_url,
            end_time=end_time.timestamp(),
            required_role=required_role.id if required_role else None
        )

        self.bot.giveaway_winners[message.id] = winners

    @app_commands.command(name="reroll", description="Reroll a giveaway by message ID.")
    @app_commands.describe(message_id="The message ID of the giveaway to reroll")
    async def reroll(self, interaction: discord.Interaction, message_id: int):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You need the **Manage Messages** permission to reroll a giveaway.",
                ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True)

        for row in db.get_active_giveaways():
            if row[1] == message_id:
                await interaction.followup.send("This giveaway is still active.")
                return

        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if not channel.permissions_for(guild.me).read_message_history:
                    continue
                try:
                    msg = await channel.fetch_message(message_id)
                    if not msg:
                        continue

                    reaction = discord.utils.get(msg.reactions, emoji="🎉")
                    if not reaction:
                        continue

                    users = await reaction.users().flatten()
                    users = [u for u in users if not u.bot]

                    if not users:
                        await interaction.followup.send("No users to reroll.")
                        return

                    winners = self.bot.giveaway_winners.get(message_id, 1)
                    chosen = random.sample(users, min(winners, len(users)))
                    await interaction.followup.send(f"🎉 New winner(s): {', '.join(u.mention for u in chosen)}")
                    return
                except:
                    continue

        await interaction.followup.send("Giveaway message not found.")

    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        now = datetime.now(pytz.utc).timestamp()
        giveaways = db.get_active_giveaways()

        for guild_id, message_id, channel_id, image_url, end_time, required_role_id in giveaways:
            if now < end_time:
                continue

            guild = self.bot.get_guild(guild_id)
            if not guild:
                db.remove_giveaway(guild_id, message_id)
                continue

            channel = guild.get_channel(channel_id)
            if not channel or not channel.permissions_for(guild.me).read_message_history:
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
                users = [u for u in users if not u.bot]
            except:
                db.remove_giveaway(guild_id, message_id)
                continue

            if required_role_id:
                role = guild.get_role(required_role_id)
                users = [u for u in users if role in getattr(guild.get_member(u.id), "roles", [])]

            winners_count = self.bot.giveaway_winners.get(message_id, 1)

            if users:
                winners = random.sample(users, min(winners_count, len(users)))
                mentions = ", ".join(u.mention for u in winners)
                prize_line = message.embeds[0].description.splitlines()[0]
                prize = prize_line.split("**")[1] if "**" in prize_line else "a prize"

                embed = discord.Embed(
                    title="🎉 Giveaway Ended!",
                    description=f"Congrats {mentions}, you won **{prize}**!",
                    color=discord.Color.gold()
                )
                embed.set_footer(text=message.embeds[0].footer.text, icon_url=message.embeds[0].footer.icon_url)
                if image_url:
                    embed.set_image(url=image_url)

                try:
                    await message.edit(embed=embed)
                except:
                    await channel.send(f"Giveaway ended! Winners: {mentions}")
            else:
                await channel.send("Giveaway ended, but no one joined.")

            db.remove_giveaway(guild_id, message_id)

    @check_giveaways.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
