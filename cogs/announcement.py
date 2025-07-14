import discord
from discord.ext import commands
from discord import app_commands
import asyncio

OWNER_ID = 123456789012345678  # Replace with your actual Discord ID

class SecretAnnounce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="announce_all", description="(Owner-only) DM all server owners with an announcement.")
    @app_commands.describe(
        message="The announcement message",
        image_url="Optional image URL to include in the embed"
    )
    async def announce_all(self, interaction: discord.Interaction, message: str, image_url: str = None):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)
            return

        await interaction.response.send_message(
            "📬 Starting DM announcement to all server owners. This may take a while...",
            ephemeral=True
        )

        embed = discord.Embed(
            title="📢 M.I.T.A Bot Update",
            description=message,
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Made with ❤️ by the Kirtikaze Team")

        if image_url:
            embed.set_image(url=image_url)

        success = 0
        failed = 0

        for guild in self.bot.guilds:
            owner = guild.owner
            if not owner:
                continue

            try:
                await owner.send(embed=embed)
                success += 1
            except Exception as e:
                print(f"[Announce Error] Could not DM {owner}: {e}")
                failed += 1

            await asyncio.sleep(2.5)  # Delay to prevent rate limits

        # DM final result to the owner
        try:
            owner_user = await self.bot.fetch_user(OWNER_ID)
            await owner_user.send(
                f"✅ Announcement complete!\n\n"
                f"📨 Sent to: **{success}** owners\n"
                f"❌ Failed to DM: **{failed}**"
            )
        except Exception as e:
            print(f"[Notify Error] Could not DM bot owner: {e}")

        # Also send result to interaction followup
        await interaction.followup.send(
            f"✅ Done! Message sent to `{success}` owners.\n❌ Failed: `{failed}`",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(SecretAnnounce(bot))
