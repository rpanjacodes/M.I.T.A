import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random

class BotRole(commands.Cog):  # Renamed class to match the filename
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="assignrole_bots", description="Assign a role to all bot members.")
    @app_commands.describe(role="The role to assign to all bots.")
    async def assignrole_bots(self, interaction: discord.Interaction, role: discord.Role):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need the **Manage Server** permission to use this command.",
                ephemeral=True
            )
            return

        members = [m for m in interaction.guild.members if m.bot and role not in m.roles]
        total = len(members)

        if total == 0:
            await interaction.response.send_message("✅ All bots already have that role.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"⏳ Starting to assign **{role.name}** to **{total}** bot(s)...", ephemeral=True
        )

        success = 0
        for i, member in enumerate(members, 1):
            try:
                await member.add_roles(role, reason="Mass bot role assignment")
                success += 1
                await asyncio.sleep(1)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = getattr(e, "retry_after", 5)
                    await asyncio.sleep(retry_after + random.uniform(1, 3))
                else:
                    print(f"HTTP error on {member}: {e}")
            except Exception as e:
                print(f"Unexpected error on {member}: {e}")

        await interaction.followup.send(
            f"✅ Finished assigning role **{role.name}** to **{success}** bot(s)."
        )

async def setup(bot):
    await bot.add_cog(BotRole(bot))  # Make sure this matches the class name
